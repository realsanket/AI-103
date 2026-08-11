# Run: uv run python 01-plan-and-manage/28_guardrail_policy_preflight.py [--policy-file <path>]
"""Validate a Foundry Control Plane guardrail policy JSON structure locally.

Control Plane compliance policies (Operate → Compliance → Create policy) are
built on Azure Policy. This lab validates the JSON structure your reviewer
would upload before actual policy creation. No cloud call.

Portal creation flow is documented — this lab focuses on the reviewable
artifact: a JSON policy definition specifying required guardrail controls
(content safety, prompt injection, protected materials) that model
deployments must have configured to be compliant.

Validation checks: (1) `mode` is All/Indexed, (2) `policyRule` contains
`if`/`then`, (3) `then.effect` is Audit/Deny/Modify, (4) at least one
guardrail control referenced in `parameters` or rule expression.

Code path:
  Read JSON file → assert required top-level keys (properties.policyRule,
  properties.mode, properties.parameters). Validate rule structure. Warn on
  missing guardrail-control references. Never contacts Azure Policy.

What to watch. All checks pass → `Policy JSON is structurally valid for
Control Plane compliance policy`. Failure names missing/invalid section.
Portal upload + assignment remain manual reviewed steps.

Prerequisites / env vars:
  --policy-file PATH  — JSON policy file (default: sample structure printed)
"""
import argparse
import json
from pathlib import Path

REQUIRED_TOP = ("properties",)
REQUIRED_PROPS = ("policyRule", "mode", "parameters")
VALID_EFFECTS = {"Audit", "Deny", "Modify", "AuditIfNotExists", "DeployIfNotExists"}
GUARDRAIL_MARKERS = ("contentSafety", "promptShield", "protectedMaterial", "jailbreak", "pii")


def validate_policy(policy: dict) -> list[str]:
    for key in REQUIRED_TOP:
        if key not in policy:
            raise ValueError(f"missing top-level key: {key}")
    props = policy["properties"]
    for key in REQUIRED_PROPS:
        if key not in props:
            raise ValueError(f"missing properties.{key}")
    rule = props["policyRule"]
    if "if" not in rule or "then" not in rule:
        raise ValueError("policyRule must contain 'if' and 'then'")
    effect = rule["then"].get("effect", "")
    if effect not in VALID_EFFECTS:
        raise ValueError(f"then.effect must be one of {VALID_EFFECTS}, got {effect!r}")
    rule_text = json.dumps(rule).lower()
    matched = [m for m in GUARDRAIL_MARKERS if m.lower() in rule_text]
    return matched


def sample_policy() -> dict:
    return {
        "properties": {
            "displayName": "Require content-safety on Foundry deployments",
            "policyType": "Custom",
            "mode": "All",
            "parameters": {"effect": {"type": "String", "defaultValue": "Audit"}},
            "policyRule": {
                "if": {
                    "allOf": [
                        {"field": "type", "equals": "Microsoft.CognitiveServices/accounts/deployments"},
                        {"field": "Microsoft.CognitiveServices/accounts/deployments/raiPolicyName", "exists": "false"},
                    ]
                },
                "then": {"effect": "[parameters('effect')]"},
            },
        }
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Validate a Control Plane guardrail policy JSON.")
    parser.add_argument("--policy-file", type=Path, help="Path to a JSON policy definition.")
    args = parser.parse_args(argv)
    if args.policy_file:
        policy = json.loads(args.policy_file.read_text(encoding="utf-8"))
        matched = validate_policy(policy)
        print(f"Policy JSON is structurally valid for Control Plane compliance policy.")
        print(f"Guardrail markers detected: {matched or 'none — add at least one guardrail control reference'}")
    else:
        print("No --policy-file supplied. Sample structure:")
        print(json.dumps(sample_policy(), indent=2))
        print("\nSave this shape as a JSON file and re-run with --policy-file <path> to validate.")


if __name__ == "__main__":
    main()
