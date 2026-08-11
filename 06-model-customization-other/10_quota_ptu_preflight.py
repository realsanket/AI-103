# Run: uv run python 06-model-customization-other/10_quota_ptu_preflight.py
"""Plan Standard, Priority, Batch, and PTU delivery without a cloud call by default.

Two-mode lesson. Default prints a delivery-choice decision aid (Standard vs
Priority vs Batch vs PTU vs Instant) with no cloud call. `--apply` reads the
resource region, its deployments, and location quota usage via
management-plane APIs — inspection only, no writes.

Quota ≠ capacity. Quota is a policy limit assigned per subscription/region/
model/type. Capacity is currently deployable supply. PTU quota does not
reserve capacity; verify capacity in Foundry portal or the model capacities
API immediately before deployment. PTU sizing depends on request rate, I/O
shape, cache rate, model params, and minimum size — use the PTU calculator,
not a fixed TPM conversion.

Code path:
  --apply: CognitiveServicesManagementClient(cred, sub).accounts.get(rg,
  account) → print region. .deployments.list(rg, account) → per deployment:
  name, model, sku, capacity. .usages.list(location) → per bucket:
  name.value, current_value/limit, unit (skip zero entries).

What to watch. Region name, per-deployment SKU + capacity, per-quota-bucket
current_value/limit. A limit close to current_value signals imminent 429s.

Prerequisites / env vars:
  --apply  — read resource, deployments, quota (control-plane role required)
  AZURE_SUBSCRIPTION_ID, AZURE_RESOURCE_GROUP, FOUNDRY_ENDPOINT
"""
from __future__ import annotations

import argparse

from azure.identity import DefaultAzureCredential
from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient

from _shared.config import settings
from _shared.foundry_management import foundry_account_name
from lab_common import print_preflight


def inspect() -> None:
    current = settings()
    if not current.azure_subscription_id or not current.azure_resource_group or not current.foundry_endpoint:
        raise SystemExit("Set AZURE_SUBSCRIPTION_ID, AZURE_RESOURCE_GROUP, and FOUNDRY_ENDPOINT.")
    account = foundry_account_name(current.foundry_endpoint)
    client = CognitiveServicesManagementClient(DefaultAzureCredential(), current.azure_subscription_id)
    resource = client.accounts.get(current.azure_resource_group, account)
    print(f"Resource: {account}\nRegion: {resource.location}\n\nDeployments:")
    for deployment in client.deployments.list(current.azure_resource_group, account):
        model = deployment.properties.model.name if deployment.properties and deployment.properties.model else "?"
        sku = deployment.sku.name if deployment.sku else "?"
        capacity = deployment.sku.capacity if deployment.sku else "?"
        print(f"- {deployment.name}: model={model}, sku={sku}, capacity={capacity}")
    print("\nQuota usage:")
    for usage in client.usages.list(resource.location):
        if usage.current_value or usage.limit:
            print(f"- {usage.name.value}: {usage.current_value}/{usage.limit} {usage.unit}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Inspect quota and current delivery deployments.")
    parser.add_argument("--apply", action="store_true", help="Read resource, deployments, and location quota.")
    args = parser.parse_args(argv)
    if not args.apply:
        print_preflight([
            "Standard: variable/predictability-balanced online traffic.",
            "Priority: latency-sensitive traffic; same quota as Standard where supported.",
            "Global Batch: asynchronous bulk work; separate enqueued-token quota.",
            "PTU: dedicated capacity; quota does not guarantee available capacity.",
            "Instant access: preview convenience option; verify current region, model, and global quota separately.",
        ])
        return
    inspect()


if __name__ == "__main__":
    main()
