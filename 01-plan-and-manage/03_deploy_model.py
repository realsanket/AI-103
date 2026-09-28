# Run: uv run python 01-plan-and-manage/03_deploy_model.py [--sku Standard] [--version-upgrade-option NoAutoUpgrade] [--apply]
# Practice-question coverage: Q166.
"""Plan, then deploy, a model into your Foundry account through the management plane.

Beginner note:
  Azure has two "planes":
    - Control plane = manage RESOURCES (create/delete deployments, set SKUs).
    - Data plane    = USE resources (send prompts, get completions).
  Deploying a model is control-plane, so you can't use AIProjectClient (which
  is data-plane only — it has no `.deployments.create()`). You use
  CognitiveServicesManagementClient from `azure-mgmt-cognitiveservices`.

  Portal shortcut: Foundry portal → Models → pick one → Deploy. This file
  does the same thing programmatically so you can script it in CI/CD.

Two settings decide where inference runs and when the model changes:
  --sku                     Deployment type. `Standard` keeps inference in the
                            deployment region; `GlobalStandard` may process in
                            any Azure region; `DataZoneStandard` stays in the
                            US/EU/APAC data zone. Provisioned SKUs reserve PTUs.
  --version-upgrade-option  `OnceNewDefaultVersionAvailable` upgrades when a new
                            default version ships. `OnceCurrentVersionExpired`
                            (also what an unset value means) upgrades at
                            retirement. `NoAutoUpgrade` opts out: you upgrade
                            manually, and the deployment stops working when its
                            pinned version retires. The policy applies to
                            Standard deployment types.

Prereqs in .env:
  AZURE_SUBSCRIPTION_ID, AZURE_RESOURCE_GROUP, FOUNDRY_ENDPOINT,
  DEPLOYMENT_NAME, DEPLOYMENT_MODEL_NAME. DEPLOYMENT_MODEL_VERSION is optional
  unless you pass `--version-upgrade-option NoAutoUpgrade`.
  Account name is derived from the FOUNDRY_ENDPOINT subdomain.
  `--apply` needs a control-plane role such as Cognitive Services Contributor
  or Foundry Account Owner; neither proves data-plane inference access.

What to watch:
  Without --apply the lesson prints the ARM request body and makes no calls.
  With --apply, success prints `state: Succeeded`. Re-running with the same
  body updates the deployment in place (PUT semantics), so it is idempotent.
"""
import argparse
import json

from azure.mgmt.cognitiveservices.models import (
    Deployment,
    DeploymentModel,
    DeploymentModelVersionUpgradeOption,
    DeploymentProperties,
    Sku,
)

from _shared.config import settings
from _shared.foundry_management import foundry_account_name

SKUS = (
    "GlobalStandard",
    "DataZoneStandard",
    "Standard",
    "GlobalProvisionedManaged",
    "DataZoneProvisionedManaged",
    "ProvisionedManaged",
    "GlobalBatch",
    "DataZoneBatch",
    "DeveloperTier",
)
UPGRADE_OPTIONS = tuple(option.value for option in DeploymentModelVersionUpgradeOption)
REGIONAL_SKUS = {"Standard", "ProvisionedManaged"}


def deployment_body(
    *,
    model_name: str,
    model_version: str = "",
    model_format: str = "OpenAI",
    sku: str = "GlobalStandard",
    capacity: int = 1,
    version_upgrade_option: str = "",
) -> dict:
    """Return the ARM deployment body. Validates choices before any cloud call."""
    if not model_name:
        raise ValueError("DEPLOYMENT_MODEL_NAME is required.")
    if sku not in SKUS:
        raise ValueError(f"Unsupported SKU {sku!r}. Choose from {', '.join(SKUS)}.")
    if capacity < 1:
        raise ValueError("--capacity must be at least 1.")
    if version_upgrade_option and version_upgrade_option not in UPGRADE_OPTIONS:
        raise ValueError(f"Choose --version-upgrade-option from {', '.join(UPGRADE_OPTIONS)}.")
    if version_upgrade_option == "NoAutoUpgrade" and not model_version:
        raise ValueError("NoAutoUpgrade pins a version: set DEPLOYMENT_MODEL_VERSION.")

    model = {"format": model_format, "name": model_name}
    if model_version:
        model["version"] = model_version
    properties: dict = {"model": model}
    if version_upgrade_option:
        properties["versionUpgradeOption"] = version_upgrade_option
    return {"sku": {"name": sku, "capacity": capacity}, "properties": properties}


def to_sdk_deployment(body: dict) -> Deployment:
    properties = body["properties"]
    return Deployment(
        sku=Sku(**body["sku"]),
        properties=DeploymentProperties(
            model=DeploymentModel(**properties["model"]),
            version_upgrade_option=properties.get("versionUpgradeOption"),
        ),
    )


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--sku", choices=SKUS, default="GlobalStandard", help="Deployment type (ARM SKU name).")
    parser.add_argument(
        "--capacity",
        type=int,
        default=1,
        help="Standard types: units of 1,000 TPM. Provisioned types: PTUs (model minimums apply).",
    )
    parser.add_argument("--version-upgrade-option", choices=UPGRADE_OPTIONS, default="")
    parser.add_argument("--model-format", default="OpenAI", help="Catalog format, for example OpenAI.")
    parser.add_argument("--apply", action="store_true", help="Create or update the deployment.")
    args = parser.parse_args(argv)

    s = settings()
    try:
        body = deployment_body(
            model_name=s.deployment_model_name or "<DEPLOYMENT_MODEL_NAME>",
            model_version=s.deployment_model_version,
            model_format=args.model_format,
            sku=args.sku,
            capacity=args.capacity,
            version_upgrade_option=args.version_upgrade_option,
        )
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    required = (
        "AZURE_SUBSCRIPTION_ID",
        "AZURE_RESOURCE_GROUP",
        "FOUNDRY_ENDPOINT",
        "DEPLOYMENT_NAME",
        "DEPLOYMENT_MODEL_NAME",
    )
    missing = [name for name in required if not getattr(s, name.lower())]

    print(f"Deployment {s.deployment_name or '<DEPLOYMENT_NAME>'!r} request body:")
    print(json.dumps(body, indent=2))
    if args.sku not in REGIONAL_SKUS:
        print("Note: inference can run outside the deployment region for this SKU.")
    if not args.apply:
        print("Missing: " + (", ".join(missing) if missing else "none"))
        print("Preflight only: no deployment created. Re-run with --apply after review.")
        return
    if missing:
        raise SystemExit(f"Set {', '.join(missing)} in .env before --apply.")

    from azure.identity import DefaultAzureCredential
    from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient

    account = foundry_account_name(s.foundry_endpoint)
    client = CognitiveServicesManagementClient(DefaultAzureCredential(), s.azure_subscription_id)
    print(f"Deploying on account {account!r} ...")
    d = client.deployments.begin_create_or_update(
        resource_group_name=s.azure_resource_group,
        account_name=account,
        deployment_name=s.deployment_name,
        deployment=to_sdk_deployment(body),
    ).result()

    print(f"state:    {d.properties.provisioning_state}")
    print(f"model:    {d.properties.model.name}  v{d.properties.model.version}")
    print(f"sku:      {d.sku.name}  capacity={d.sku.capacity}")
    print(f"upgrade:  {d.properties.version_upgrade_option or 'OnceCurrentVersionExpired (default)'}")


if __name__ == "__main__":
    main()
