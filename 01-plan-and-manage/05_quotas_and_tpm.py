# Run: uv run python 01-plan-and-manage/05_quotas_and_tpm.py
"""List Cognitive Services quotas — TPM allocation + rate-limit status.

Uses CognitiveServicesManagementClient (management-plane SDK).
Account name and location are derived from FOUNDRY_ENDPOINT — no extra env vars needed.
"""
from urllib.parse import urlparse

from azure.identity import DefaultAzureCredential
from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient

from _shared.config import settings


def _account_name(endpoint: str) -> str:
    return (urlparse(endpoint).hostname or "").split(".")[0]


def main() -> None:
    s = settings()
    if not s.azure_subscription_id or not s.azure_resource_group:
        raise SystemExit("Set AZURE_SUBSCRIPTION_ID and AZURE_RESOURCE_GROUP in .env.")

    account = _account_name(s.foundry_endpoint)
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
