# Run: uv run python 01-plan-and-manage/28_guardrail_policy_preflight.py [--policy-file <path>] [--guardrail-name <name> [--apply]]
# Practice-question coverage: Q63.
"""Build a guardrail for every intervention point and validate its compliance policy.

Two reviewable artifacts, both local by default:

1. Guardrail (RAI policy) body. A Foundry guardrail is an account-level
   `Microsoft.CognitiveServices/accounts/raiPolicies` resource. Each control
   names a risk, an intervention point, and an action. Intervention points:
     User input            → source `Prompt`
     Tool call (preview)    → source `PreToolCall`   (agents only)
     Tool response (preview)→ source `PostToolCall`  (agents only)
     Output                 → source `Completion`
   The tool sources need management API version 2026-01-15-preview, and they
   only take effect for tools that support moderation (Azure AI Search, Azure
   Functions, OpenAPI, SharePoint, Fabric data agent, Bing, Browser Automation).
   `blocking: true` is "Annotate and block"; `false` is "Annotate only".

2. Control Plane compliance policy (Operate → Compliance → Create policy),
   built on Azure Policy. It audits or denies model deployments that lack a
   guardrail. Validation checks: (1) `mode`, (2) `policyRule.if/then`,
   (3) `then.effect` — a literal or a `[parameters('...')]` reference whose
   default and allowed values are Audit/Deny/Modify/... — and (4) a guardrail
   reference such as `raiPolicyName`.

Code path:
  guardrail_body() → print JSON. --apply → PUT the RAI policy through ARM.
  validate_policy(sample or --policy-file) → print result. Never contacts
  Azure Policy.

Attach the guardrail after creation:
  model deployment → `properties.raiPolicyName` (lesson 03 body)
  prompt agent     → `PromptAgentDefinition(..., rai_config=RaiConfig(rai_policy_name=<ARM ID>))`
  hosted agent     → Domain 2 lesson 48 (`rai_config` on HostedAgentDefinition)

Prerequisites for --apply:
  AZURE_SUBSCRIPTION_ID, AZURE_RESOURCE_GROUP, FOUNDRY_ENDPOINT and the
  Foundry Account Owner (or higher) role on the Foundry resource. Creating a
  guardrail does not change traffic until you assign it; assign to a
  nonproduction deployment or agent first.
"""
import argparse
import json
from pathlib import Path
import re

from _shared.config import settings

REQUIRED_TOP = ("properties",)
REQUIRED_PROPS = ("policyRule", "mode", "parameters")
VALID_EFFECTS = {"Audit", "Deny", "Modify", "AuditIfNotExists", "DeployIfNotExists", "Disabled"}
GUARDRAIL_MARKERS = ("raiPolicyName", "contentSafety", "promptShield", "protectedMaterial", "jailbreak", "pii")

RAI_API_VERSION = "2026-01-15-preview"
INTERVENTION_POINTS = {
    "user_input": "Prompt",
    "tool_call": "PreToolCall",
    "tool_response": "PostToolCall",
    "output": "Completion",
}
_HARM_CATEGORIES = ("Hate", "Sexual", "Selfharm", "Violence")
_PARAMETER_REF = re.compile(r"^\[parameters\('([^']+)'\)\]$")
_NAME = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_.-]*$")


def guardrail_body(*, block: bool = True, severity: str = "Medium") -> dict:
    """RAI policy with harm controls at all four points plus point-specific risks."""
    if severity not in {"Low", "Medium", "High"}:
        raise ValueError("severity must be Low, Medium, or High")
    controls = [
        {"name": category, "enabled": True, "blocking": block, "severityThreshold": severity, "source": source}
        for category in _HARM_CATEGORIES
        for source in INTERVENTION_POINTS.values()
    ]
    controls += [
        # User input attacks can only be scanned where they enter: the user input.
        {"name": "Jailbreak", "enabled": True, "blocking": block, "source": INTERVENTION_POINTS["user_input"]},
        # Indirect prompt injection arrives in the payload a tool returns.
        {"name": "Indirect Attack", "enabled": True, "blocking": block, "source": INTERVENTION_POINTS["tool_response"]},
        {"name": "Protected Material Text", "enabled": True, "blocking": block, "source": INTERVENTION_POINTS["output"]},
        {"name": "Protected Material Code", "enabled": True, "blocking": block, "source": INTERVENTION_POINTS["output"]},
    ]
    return {"properties": {"basePolicyName": "Microsoft.DefaultV2", "contentFilters": controls}}


def intervention_summary(body: dict) -> dict[str, list[str]]:
    """Group enabled controls by intervention point for review."""
    by_source = {source: point for point, source in INTERVENTION_POINTS.items()}
    summary: dict[str, list[str]] = {point: [] for point in INTERVENTION_POINTS}
    for control in body["properties"]["contentFilters"]:
        if control.get("enabled"):
            summary[by_source[control["source"]]].append(control["name"])
    return summary


def _resolve_effect(effect: str, parameters: dict) -> set[str]:
    match = _PARAMETER_REF.match(effect)
    if not match:
        return {effect}
    parameter = parameters.get(match.group(1))
    if not isinstance(parameter, dict):
        raise ValueError(f"then.effect references undefined parameter {match.group(1)!r}")
    values = set(parameter.get("allowedValues", []))
    if "defaultValue" in parameter:
        values.add(parameter["defaultValue"])
    if not values:
        raise ValueError(f"parameter {match.group(1)!r} needs a defaultValue or allowedValues")
    return values


def validate_policy(policy: dict) -> list[str]:
    for key in REQUIRED_TOP:
        if key not in policy:
            raise ValueError(f"missing top-level key: {key}")
    props = policy["properties"]
    for key in REQUIRED_PROPS:
        if key not in props:
            raise ValueError(f"missing properties.{key}")
    if props["mode"] not in {"All", "Indexed"}:
        raise ValueError("properties.mode must be All or Indexed")
    rule = props["policyRule"]
    if "if" not in rule or "then" not in rule:
        raise ValueError("policyRule must contain 'if' and 'then'")
    effects = _resolve_effect(rule["then"].get("effect", ""), props["parameters"])
    invalid = sorted(effects - VALID_EFFECTS)
    if invalid:
        raise ValueError(f"then.effect must resolve to {sorted(VALID_EFFECTS)}, got {invalid}")
    rule_text = json.dumps(rule).lower()
    return [m for m in GUARDRAIL_MARKERS if m.lower() in rule_text]


def sample_policy() -> dict:
    return {
        "properties": {
            "displayName": "Require a guardrail on Foundry model deployments",
            "policyType": "Custom",
            "mode": "All",
            "parameters": {
                "effect": {"type": "String", "defaultValue": "Audit", "allowedValues": ["Audit", "Deny", "Disabled"]}
            },
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


def rai_policy_url(subscription_id: str, resource_group: str, account: str, name: str) -> str:
    if not _NAME.match(name):
        raise ValueError("guardrail name may contain letters, digits, '_', '.', and '-' only")
    return (
        f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}"
        f"/providers/Microsoft.CognitiveServices/accounts/{account}/raiPolicies/{name}"
        f"?api-version={RAI_API_VERSION}"
    )


def apply_guardrail(name: str, body: dict) -> dict:
    import httpx
    from azure.identity import DefaultAzureCredential

    from _shared.foundry_management import foundry_account_name

    s = settings()
    url = rai_policy_url(
        s.require("AZURE_SUBSCRIPTION_ID"),
        s.require("AZURE_RESOURCE_GROUP"),
        foundry_account_name(s.require("FOUNDRY_ENDPOINT")),
        name,
    )
    token = DefaultAzureCredential().get_token("https://management.azure.com/.default").token
    response = httpx.put(url, json=body, headers={"Authorization": f"Bearer {token}"}, timeout=60)
    response.raise_for_status()
    return response.json()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--policy-file", type=Path, help="Validate this Azure Policy JSON instead of the sample.")
    parser.add_argument("--guardrail-name", default="northwind-agent-guardrail")
    parser.add_argument("--annotate-only", action="store_true", help="Annotate instead of annotate-and-block.")
    parser.add_argument("--apply", action="store_true", help="PUT the guardrail (RAI policy) through ARM.")
    args = parser.parse_args(argv)

    body = guardrail_body(block=not args.annotate_only)
    print(f"Guardrail {args.guardrail_name!r} (RAI policy, api-version {RAI_API_VERSION}):")
    for point, risks in intervention_summary(body).items():
        print(f"  {point:<14} {INTERVENTION_POINTS[point]:<13} {', '.join(risks)}")
    print(json.dumps(body, indent=2))

    policy = json.loads(args.policy_file.read_text(encoding="utf-8")) if args.policy_file else sample_policy()
    matched = validate_policy(policy)
    print(f"\nCompliance policy ({args.policy_file or 'sample'}) is structurally valid.")
    print(f"Guardrail references detected: {matched or 'none — reference raiPolicyName or a guardrail control'}")
    if not args.policy_file:
        print(json.dumps(sample_policy(), indent=2))

    if not args.apply:
        print("\nPreflight only: nothing created. Re-run with --apply to create the guardrail.")
        return
    result = apply_guardrail(args.guardrail_name, body)
    print(f"\nCreated or updated guardrail: {result.get('id')}")
    print("Assign it to a nonproduction deployment or agent, then send a test prompt.")


if __name__ == "__main__":
    main()
