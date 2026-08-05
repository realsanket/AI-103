"""Offline production-platform asset checks. Never calls Azure by default."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
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
ENTRYPOINTS = {
    "bicep": ("bicep/main.bicep", "bicep/main.bicepparam"),
    "terraform": ("terraform/main.tf", "terraform/terraform.tfvars.example"),
    "policy": (
        "bicep/policy.bicep",
        "bicep/policy-assignment.bicep",
        "policy/deny-unapproved-foundry-connections.json",
    ),
    "cicd": ("github/workflows/production-platform.yml",),
    "diagnostics": ("bicep/main.bicep", "terraform/main.tf"),
    "ha-dr": ("README.md",),
}


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


def entrypoint_preflight(topic: str) -> list[str]:
    """Validate one numbered lab's local source assets."""
    files = [ROOT / relative for relative in ENTRYPOINTS[topic]]
    missing = [str(path.relative_to(ROOT)) for path in files if not path.is_file()]
    if missing:
        raise ValueError(f"missing required assets: {', '.join(missing)}")

    if topic in REQUIRED:
        messages = preflight(topic)
    elif topic == "policy":
        policy = json.loads((ROOT / "policy/deny-unapproved-foundry-connections.json").read_text())
        definition = (ROOT / "bicep/policy.bicep").read_text()
        assignment = (ROOT / "bicep/policy-assignment.bicep").read_text()
        if policy["policyRule"]["then"]["effect"] != "Deny":
            raise ValueError("policy must deny unapproved Foundry connections")
        if "targetScope = 'subscription'" not in definition or "policyAssignments" not in assignment:
            raise ValueError("policy definition and resource-group assignment are required")
        messages = ["Policy definition, assignment, and Deny effect validated locally"]
    elif topic == "cicd":
        workflow = files[0].read_text()
        required = ("workflow_dispatch:", "default: false", "Offline preflight", "azure/login@v2")
        missing = [marker for marker in required if marker not in workflow]
        if missing:
            raise ValueError(f"CI/CD workflow missing: {', '.join(missing)}")
        messages = ["Reference workflow keeps manual apply disabled and uses OIDC variables"]
    elif topic == "diagnostics":
        required = ("Audit", "RequestResponse", "AzureOpenAIRequestUsage", "AllMetrics")
        missing = [
            marker
            for marker in required
            if any(marker not in path.read_text() for path in files)
        ]
        if missing:
            raise ValueError(f"diagnostic categories missing: {', '.join(missing)}")
        messages = ["Bicep and Terraform configure reviewed Foundry diagnostic categories"]
    else:
        readme = files[0].read_text()
        required = ("Foundry has no automatic failover", "Warm standby", "two supported regions")
        missing = [marker for marker in required if marker not in readme]
        if missing:
            raise ValueError(f"HA/DR guidance missing: {', '.join(missing)}")
        messages = ["HA/DR guidance requires independent regional cells and a tested traffic switch"]

    return [*messages, "No cloud calls made."]


def apply_command(topic: str, args: argparse.Namespace) -> list[str]:
    """Build guarded resource-mutation command for deployable assets only."""
    if topic == "bicep":
        required = ("resource_group", "location", "prefix")
        missing = [name for name in required if not getattr(args, name)]
        if missing:
            raise ValueError(
                "Bicep --apply requires: "
                + ", ".join("--" + name.replace("_", "-") for name in missing)
            )
        return [
            sys.executable,
            str(ROOT / "scripts/deploy.py"),
            "--engine",
            "bicep",
            "--apply",
            "--resource-group",
            args.resource_group,
            "--location",
            args.location,
            "--prefix",
            args.prefix,
            "--project-name",
            args.project_name,
        ]
    if topic == "terraform":
        return [
            sys.executable,
            str(ROOT / "scripts/deploy.py"),
            "--engine",
            "terraform",
            "--apply",
        ]
    if topic == "policy":
        required = ("resource_group", "location", "allowed_category")
        missing = [name for name in required if not getattr(args, name)]
        if missing:
            raise ValueError(
                "Policy --apply requires: "
                + ", ".join("--" + name.replace("_", "-") for name in missing)
            )
        return [
            "az",
            "deployment",
            "sub",
            "create",
            "--location",
            args.location,
            "--template-file",
            str(ROOT / "bicep/policy.bicep"),
            "--parameters",
            f"resourceGroupName={args.resource_group}",
            f"allowedCategories={json.dumps(args.allowed_category)}",
        ]
    raise ValueError(f"{topic} has no automated apply; follow its reviewed operational guidance.")


def entrypoint_main(topic: str, argv: list[str] | None = None) -> None:
    """Run a local numbered preflight, or explicitly apply a deployable asset."""
    parser = argparse.ArgumentParser(description=f"Production-platform {topic} preflight.")
    parser.add_argument("--apply", action="store_true", help="Allow persistent Azure changes.")
    parser.add_argument("--resource-group")
    parser.add_argument("--location")
    parser.add_argument("--prefix")
    parser.add_argument("--project-name", default="production")
    parser.add_argument("--allowed-category", action="append")
    args = parser.parse_args(argv)
    if not args.apply:
        print("\n".join(entrypoint_preflight(topic)))
        return
    try:
        command = apply_command(topic, args)
    except ValueError as error:
        parser.error(str(error))
    print("+", " ".join(command))
    subprocess.run(command, check=True, cwd=ROOT)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", choices=sorted(REQUIRED), default="bicep")
    args = parser.parse_args(argv)
    print("\n".join(preflight(args.engine)))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"Preflight failed: {error}", file=sys.stderr)
        raise SystemExit(1)
