# Run: uv run python 07-production-platform-other/questions/01_security_operations_preflight.py
"""Question supplement: security-operations signal routing.

Maps PDF question 70. It is a local design preflight only: centralized SOC
correlation needs Microsoft Sentinel/Log Analytics plus authorized diagnostic
exports from Foundry, Defender, and Entra. It neither enables diagnostics nor
changes a Sentinel workspace.
"""
from __future__ import annotations


def security_operations_plan(signal_sources: list[str]) -> dict[str, object]:
    expected = {"Foundry", "Defender", "Entra"}
    missing = sorted(expected - set(signal_sources))
    return {
        "sink": "Microsoft Sentinel on a Log Analytics workspace",
        "provided_sources": sorted(set(signal_sources)),
        "missing_sources": missing,
        "ready_for_correlation": not missing,
        "review": ["RBAC", "retention", "cost", "content minimization", "incident owner"],
    }


def main() -> None:
    print("No cloud calls made. Security operations plan:")
    print(security_operations_plan(["Foundry", "Defender", "Entra"]))


if __name__ == "__main__":
    main()
