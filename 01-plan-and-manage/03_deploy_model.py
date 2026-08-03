"""Programmatically deploy a model into a Foundry project.

The deployments surface on `AIProjectClient` handles create/update. Exact SDK
methods vary; use the portal for one-off creates and this pattern for CI/CD.
"""
from _shared.config import settings
from _shared.foundry_client import project_client


def main() -> None:
    client = project_client()
    # The exact create method varies by azure-ai-projects version. This shape
    # matches >= 1.0.0b10; adjust `sku_name` / `capacity` per your quota.
    deployment_name = f"{settings().default_model}-deploy"
    try:
        d = client.deployments.begin_deploy(
            name=deployment_name,
            model=settings().default_model,
            deployment_type="GlobalStandard",
            capacity=100,  # TPM in thousands, service-dependent
        ).result()
        print(f"deployed: {d.name} → {d.model}")
    except AttributeError:
        # Fallback: create via management SDK if project SDK doesn't expose deployments.begin_deploy
        print(
            "This SDK version doesn't expose deployments.begin_deploy(). "
            "Use the Foundry portal or `az cognitiveservices account deployment create` "
            "in a CI/CD pipeline. See .context/azure-ai-docs/articles/foundry/how-to/"
            "model-deployment-policy.md"
        )


if __name__ == "__main__":
    main()
