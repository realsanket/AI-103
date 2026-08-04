# Run: uv run python 01-plan-and-manage/03_deploy_model.py
"""Deploy an Azure OpenAI model into your Foundry account (via SDK).

Beginner note:
  Azure has two "planes":
    - Control plane = manage RESOURCES (create/delete deployments, set SKUs).
    - Data plane    = USE resources (send prompts, get completions).
  Deploying a model is control-plane, so you can't use AIProjectClient (which
  is data-plane only — it has no `.deployments.create()`). You use
  CognitiveServicesManagementClient from `azure-mgmt-cognitiveservices`.

  Portal shortcut: Foundry portal → Models → pick one → Deploy. This file
  does the same thing programmatically so you can script it in CI/CD.

Prereqs in .env:
  AZURE_SUBSCRIPTION_ID, AZURE_RESOURCE_GROUP, FOUNDRY_ENDPOINT.
  Account name is derived from the FOUNDRY_ENDPOINT subdomain.

What to watch:
  Success prints `state: Succeeded`. If already deployed, the SDK just returns
  the existing deployment idempotently.
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
