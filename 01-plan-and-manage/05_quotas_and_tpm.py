# Run: uv run python 01-plan-and-manage/05_quotas_and_tpm.py
"""List quotas — how much throughput each deployment has, and what's used.

Beginner note:
  Quota answers "how fast can I send tokens?". Two numbers matter:
    - TPM  (tokens per minute) — the per-deployment throughput budget.
    - RPM  (requests per minute) — request-count limit.
  Blow past either and you get HTTP 429 (Too Many Requests). Lesson 06 shows
  the retry pattern. This file just shows what your current limits look like.

  Standard quota is assigned per subscription, region, model, and deployment
  type. Deployment `capacity` maps to TPM/RPM in model-specific units; don't
  assume a capacity value has one fixed TPM conversion.

  Provisioned capacity is measured in PTUs. PTU-to-TPM ratios and minimum
  deployment sizes vary by model. Provisioned capacity improves predictability,
  but a saturated deployment can still return 429; configure spillover if
  supported and required.

Prereqs in .env:
  AZURE_SUBSCRIPTION_ID, AZURE_RESOURCE_GROUP, FOUNDRY_ENDPOINT.

What to watch:
  Each deployment row shows model / SKU / capacity. Usage table shows
  consumed/limit per quota bucket (per model family, per region).
"""
from azure.identity import DefaultAzureCredential
from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient

from _shared.config import settings
from _shared.foundry_management import foundry_account_name


def main() -> None:
    s = settings()
    if not s.azure_subscription_id or not s.azure_resource_group:
        raise SystemExit("Set AZURE_SUBSCRIPTION_ID and AZURE_RESOURCE_GROUP in .env.")

    account = foundry_account_name(s.foundry_endpoint)
    client = CognitiveServicesManagementClient(DefaultAzureCredential(), s.azure_subscription_id)

    # Get account location (needed for usages.list)
    acct = client.accounts.get(s.azure_resource_group, account)
    location = acct.location

    print(f"Account: {account}  location: {location}\n")

    print("Deployments:")
    for d in client.deployments.list(s.azure_resource_group, account):
        model = d.properties.model.name if d.properties and d.properties.model else "?"
        capacity = d.sku.capacity if d.sku else "?"
        sku_name = d.sku.name if d.sku else "?"
        print(f"  {d.name:<32}  model={model:<20}  sku={sku_name:<20}  capacity={capacity}")

    print("\nUsage quotas for this location:")
    for u in client.usages.list(location):
        if u.current_value or u.limit:
            name = u.name.value if u.name else "?"
            print(f"  {name:<48}  {u.current_value}/{u.limit} {u.unit}")


if __name__ == "__main__":
    main()
