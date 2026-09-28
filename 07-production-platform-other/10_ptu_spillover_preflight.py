# Run: uv run python 07-production-platform-other/10_ptu_spillover_preflight.py [--apply --deployment <name>]
"""Validate PTU spillover traffic management configuration on an Azure OpenAI deployment.

PTU (Provisioned Throughput Unit) deployments guarantee reserved capacity for
predictable latency. When PTU capacity is exhausted, without spillover the API
returns HTTP 429. Spillover routes excess traffic to a standard pay-per-token
deployment instead of rejecting it. Spillover is configured per-deployment and
requires a spillover_deployment_name in the deployment properties.

Default preflight checks required env vars. --apply reads the named PTU deployment
via CognitiveServicesManagementClient and verifies spillover is configured.

Code path:
  --apply: CognitiveServicesManagementClient(cred, sub).deployments.get(rg, account, deployment)
  → deployment.sku.name (should be "ProvisionedManaged" or "Provisioned")
  → deployment.sku.capacity (PTU count)
  → deployment.properties.spillover_deployment_name (PASS if set, FAIL if None).

What to watch. spillover_deployment_name not None = overflow goes to pay-per-token.
None = any PTU overflow returns 429. Set in portal: Deployment → Edit → Spillover.

Prerequisites / env vars:
  AZURE_SUBSCRIPTION_ID    — subscription
  AZURE_RESOURCE_GROUP     — resource group of the AI Services account
  AZURE_COGNITIVE_ACCOUNT  — AI Services account name
  --deployment             — PTU deployment name to check
  --apply                  — read deployment and verify spillover config
"""
import argparse
import os

from _shared.config import load_env


def preflight() -> None:
    checks = {
        "AZURE_SUBSCRIPTION_ID set": bool(os.environ.get("AZURE_SUBSCRIPTION_ID")),
        "AZURE_RESOURCE_GROUP set": bool(os.environ.get("AZURE_RESOURCE_GROUP")),
        "AZURE_COGNITIVE_ACCOUNT set": bool(os.environ.get("AZURE_COGNITIVE_ACCOUNT")),
    }
    print("PTU spillover preflight (no cloud calls).")
    for check, passed in checks.items():
        print(f"  [{'PASS' if passed else 'FAIL'}] {check}")
    print()
    print("PTU spillover: when PTU queue is full, route to standard deployment instead of 429.")
    print("Configure: AI Services → Deployments → (PTU deployment) → Edit → Spillover deployment.")
    print("Run --apply --deployment <name> to verify spillover on a specific PTU deployment.")


def apply(deployment: str) -> None:
    from azure.identity import DefaultAzureCredential
    from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient

    sub = os.environ.get("AZURE_SUBSCRIPTION_ID", "")
    rg = os.environ.get("AZURE_RESOURCE_GROUP", "")
    account = os.environ.get("AZURE_COGNITIVE_ACCOUNT", "")
    if not (sub and rg and account):
        raise SystemExit("Set AZURE_SUBSCRIPTION_ID, AZURE_RESOURCE_GROUP, AZURE_COGNITIVE_ACCOUNT.")

    client = CognitiveServicesManagementClient(DefaultAzureCredential(), sub)
    d = client.deployments.get(rg, account, deployment)
    sku = d.sku
    sku_name = getattr(sku, "name", "unknown") if sku else "unknown"
    capacity = getattr(sku, "capacity", None)
    props = d.properties
    spillover = (
        getattr(props, "spillover_deployment_name", None)
        or getattr(props, "spilloverDeploymentName", None)
    )
    print(f"Deployment: {deployment}")
    print(f"  sku:      {sku_name}, capacity={capacity} PTU")
    if spillover:
        print(f"  spillover: [PASS] → {spillover!r}")
    else:
        print("  spillover: [MISSING] — set spillover deployment to avoid 429 on PTU overflow")


def main(argv: list[str] | None = None) -> None:
    load_env()
    parser = argparse.ArgumentParser(description="Verify PTU spillover configuration on a deployment.")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--deployment", default="", help="PTU deployment name to check.")
    args = parser.parse_args(argv)
    if not args.apply:
        preflight()
        return
    if not args.deployment:
        parser.error("--apply requires --deployment <name>.")
    apply(args.deployment)


if __name__ == "__main__":
    main()
