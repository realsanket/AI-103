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
  AZURE_SUBSCRIPTION_ID, AZURE_RESOURCE_GROUP, FOUNDRY_ENDPOINT,
  DEPLOYMENT_NAME, DEPLOYMENT_MODEL_NAME. DEPLOYMENT_MODEL_VERSION is optional.
  Account name is derived from the FOUNDRY_ENDPOINT subdomain.

What to watch:
  Success prints `state: Succeeded`. If already deployed, the SDK just returns
  the existing deployment idempotently.
"""
from azure.identity import DefaultAzureCredential
from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient
from azure.mgmt.cognitiveservices.models import (
    Deployment,
    DeploymentModel,
    DeploymentProperties,
    Sku,
)

from _shared.config import settings
from _shared.foundry_management import foundry_account_name


def main() -> None:
    s = settings()
    if not s.azure_subscription_id or not s.azure_resource_group:
        raise SystemExit("Set AZURE_SUBSCRIPTION_ID and AZURE_RESOURCE_GROUP in .env.")

    required = (
        "FOUNDRY_ENDPOINT",
        "DEPLOYMENT_NAME",
        "DEPLOYMENT_MODEL_NAME",
    )
    missing = [name for name in required if not getattr(s, name.lower())]
    if missing:
        raise SystemExit(f"Set {', '.join(missing)} in .env.")

    account = foundry_account_name(s.foundry_endpoint)

    client = CognitiveServicesManagementClient(
        DefaultAzureCredential(), s.azure_subscription_id
    )

    print(
        f"Deploying {s.deployment_model_name!r} → {s.deployment_name!r} "
        f"on account {account!r} ..."
    )
    model = {"format": "OpenAI", "name": s.deployment_model_name}
    if s.deployment_model_version:
        model["version"] = s.deployment_model_version

    d = client.deployments.begin_create_or_update(
        resource_group_name=s.azure_resource_group,
        account_name=account,
        deployment_name=s.deployment_name,
        deployment=Deployment(
            sku=Sku(name="GlobalStandard", capacity=1),
            properties=DeploymentProperties(model=DeploymentModel(**model)),
        ),
    ).result()

    print(f"state:    {d.properties.provisioning_state}")
    print(f"model:    {d.properties.model.name}  v{d.properties.model.version}")
    print(f"sku:      {d.sku.name}  capacity={d.sku.capacity}")


if __name__ == "__main__":
    main()
