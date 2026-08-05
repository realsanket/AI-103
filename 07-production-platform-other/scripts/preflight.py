"""Offline production-platform asset checks. Never calls Azure."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "bicep": (
        "bicep/main.bicep",
        "bicep/main.bicepparam",
        "policy/deny-unapproved-foundry-connections.json",
    ),
    "terraform": (
        "terraform/main.tf",
        "terraform/variables.tf",
        "terraform/outputs.tf",
        "terraform/terraform.tfvars.example",
        "policy/deny-unapproved-foundry-connections.json",
    ),
}
CONTROLS = (
    "publicNetworkAccess: 'Disabled'",
    "enablePurgeProtection: true",
    "Key Vault Crypto User",
    "privateDnsZones",
    "networkInjections",
    "diagnosticSettings",
    "CanNotDelete",
)


def preflight(engine: str) -> list[str]:
    """Validate local asset presence and control markers without cloud access."""
    files = [ROOT / relative for relative in REQUIRED[engine]]
    missing = [str(path.relative_to(ROOT)) for path in files if not path.is_file()]
    if missing:
        raise ValueError(f"missing required assets: {', '.join(missing)}")

    policy_path = ROOT / "policy/deny-unapproved-foundry-connections.json"
    policy = json.loads(policy_path.read_text())
    if policy["policyRule"]["then"]["effect"] != "Deny":
        raise ValueError("policy must deny unapproved Foundry connections")

    bicep = (ROOT / "bicep/main.bicep").read_text()
    missing_controls = [control for control in CONTROLS if control not in bicep]
    if missing_controls:
        raise ValueError(f"Bicep baseline missing: {', '.join(missing_controls)}")

    return [
        f"{engine}: {len(files)} required assets found",
        "Policy JSON parses and denies unapproved Foundry connection categories",
        "Bicep baseline includes private access, CMK identity, diagnostics, and delete locks",
        "Offline preflight passed; no Azure requests or changes made",
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", choices=sorted(REQUIRED), default="bicep")
    args = parser.parse_args()
    print("\n".join(preflight(args.engine)))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"Preflight failed: {error}", file=sys.stderr)
        raise SystemExit(1)
