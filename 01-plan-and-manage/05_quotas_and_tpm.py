"""List Cognitive Services quotas — TPM allocation + rate-limit status.

Uses the management SDK, which requires a subscription-scoped credential.
Provide SUBSCRIPTION_ID + RESOURCE_GROUP in .env if you want to run it — this
lesson mainly exists to show the shape of the API you'd hook a dashboard to.
"""
import os

from azure.identity import DefaultAzureCredential
from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient


def main() -> None:
    sub = os.environ.get("AZURE_SUBSCRIPTION_ID")
    rg = os.environ.get("AZURE_RESOURCE_GROUP")
    account = os.environ.get("AZURE_FOUNDRY_ACCOUNT")
    if not (sub and rg and account):
        raise SystemExit(
            "Set AZURE_SUBSCRIPTION_ID / AZURE_RESOURCE_GROUP / AZURE_FOUNDRY_ACCOUNT in .env "
            "to run this lesson."
        )

    client = CognitiveServicesManagementClient(DefaultAzureCredential(), sub)
    for d in client.deployments.list(rg, account):
        cap = d.sku.capacity if d.sku else None
        print(f"{d.name:<32}  model={d.properties.model.name:<20}  capacity={cap}")

    print("\nUsages (per deployment type):")
    for u in client.usages.list(location="eastus", filter="name/value eq 'gpt-4.1-mini'"):
        print(f"  {u.name.value}: {u.current_value}/{u.limit} ({u.unit})")


if __name__ == "__main__":
    main()
