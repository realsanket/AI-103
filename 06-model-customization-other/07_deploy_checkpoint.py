# Run: uv run python 06-model-customization-other/07_deploy_checkpoint.py --model-id ftchkpt-... --name northwind-ft --apply
"""Deploy a chosen fine-tuned model or checkpoint only with --apply."""
from __future__ import annotations

import argparse

from azure.identity import DefaultAzureCredential
from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient
from azure.mgmt.cognitiveservices.models import Deployment, DeploymentModel, DeploymentProperties, Sku

from _shared.config import settings
from _shared.foundry_management import foundry_account_name
from lab_common import print_preflight


def deploy(args: argparse.Namespace) -> None:
    current = settings()
    required = ("AZURE_SUBSCRIPTION_ID", "AZURE_RESOURCE_GROUP", "FOUNDRY_ENDPOINT")
    missing = [name for name in required if not getattr(current, name.lower())]
    if missing:
        raise SystemExit(f"Set {', '.join(missing)} in .env.")
    account = foundry_account_name(current.foundry_endpoint)
    client = CognitiveServicesManagementClient(DefaultAzureCredential(), current.azure_subscription_id)
    result = client.deployments.begin_create_or_update(
        current.azure_resource_group,
        account,
        args.name,
        Deployment(
            sku=Sku(name=args.sku, capacity=args.capacity),
            properties=DeploymentProperties(
                model=DeploymentModel(format="OpenAI", name=args.model_id, version="1")
            ),
        ),
    ).result()
    print(f"Deployment: {result.name}\nState: {result.properties.provisioning_state}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Deploy a selected fine-tuned model/checkpoint.")
    parser.add_argument("--model-id", required=True, help="Fine-tuned model or ftchkpt identifier.")
    parser.add_argument("--name", required=True, help="New deployment name.")
    parser.add_argument("--sku", default="Standard", help="Supported target SKU, verified before apply.")
    parser.add_argument("--capacity", type=int, default=1)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    if not args.apply:
        print_preflight([
            f"Would create/update deployment {args.name} for {args.model_id}.",
            f"Requested SKU/capacity: {args.sku}/{args.capacity}.",
            "Verify model/SKU support, quota, capacity, hosting cost, and deployment replacement impact first.",
        ])
        return
    deploy(args)


if __name__ == "__main__":
    main()
