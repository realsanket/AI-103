# Run: uv run python 01-plan-and-manage/03_deploy_model.py
"""Deploy a standard Azure OpenAI model into a Foundry account.

Management-plane operation: AIProjectClient is data-plane only (inference,
agents) — it has no deployment CRUD. Use CognitiveServicesManagementClient.

Requires AZURE_SUBSCRIPTION_ID + AZURE_RESOURCE_GROUP in .env.
Account name is derived from FOUNDRY_ENDPOINT (the subdomain part).
"""
from urllib.parse import urlparse

from azure.identity import DefaultAzureCredential
from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient
from azure.mgmt.cognitiveservices.models import (
    Deployment,
    DeploymentModel,
    DeploymentProperties,
    Sku,
)

from _shared.config import settings


def _account_name(endpoint: str) -> str:
    # "https://vscode-mvp.services.ai.azure.com" → "vscode-mvp"
    host = urlparse(endpoint).hostname or ""
    return host.split(".")[0]


def main() -> None:
    s = settings()
    if not s.azure_subscription_id or not s.azure_resource_group:
        raise SystemExit("Set AZURE_SUBSCRIPTION_ID and AZURE_RESOURCE_GROUP in .env.")

    account = _account_name(s.foundry_endpoint)
    deployment_name = f"{s.default_model}-deploy"

    client = CognitiveServicesManagementClient(
        DefaultAzureCredential(), s.azure_subscription_id
    )

    print(f"Deploying {s.default_model!r} → {deployment_name!r} on account {account!r} ...")
    d = client.deployments.begin_create_or_update(
        resource_group_name=s.azure_resource_group,
        account_name=account,
        deployment_name=deployment_name,
        deployment=Deployment(
            sku=Sku(name="GlobalStandard", capacity=1),
            properties=DeploymentProperties(
                model=DeploymentModel(
                    format="OpenAI",
                    name=s.default_model
                ),
            ),
        ),
    ).result()

    print(f"state:    {d.properties.provisioning_state}")
    print(f"model:    {d.properties.model.name}  v{d.properties.model.version}")
    print(f"sku:      {d.sku.name}  capacity={d.sku.capacity}")


if __name__ == "__main__":
    main()
