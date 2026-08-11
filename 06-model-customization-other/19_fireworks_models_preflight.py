# Run: uv run python 06-model-customization-other/19_fireworks_models_preflight.py [--apply]
"""Check Fireworks AI model availability in the Foundry Models catalog.

Fireworks.ai is an Azure Marketplace partner providing optimized inference
for open-source models (Llama, Mixtral, etc.) at high throughput and
competitive cost. In Foundry, Fireworks models appear as marketplace
deployments. Billing flows through Azure Marketplace — separate from
Azure OpenAI quota. This lesson discovers whether Fireworks models are
available in your subscription's catalog.

Default preflight explains Fireworks integration. --apply lists Fireworks
models in the catalog and checks if any are registered in the subscription.

Code path:
  --apply: CognitiveServicesManagementClient(DefaultAzureCredential(), sub)
  .resource_skus.list()
  → filter name or kind containing "fireworks"
  → print model name + kind + locations.

What to watch. Zero results = Fireworks not enabled for subscription.
Enable in Foundry portal: Model Catalog → Fireworks.ai → Enable partner.

Prerequisites / env vars:
  AZURE_SUBSCRIPTION_ID  — subscription to query
  --apply                — list Fireworks models in catalog
"""
import argparse
import os


def preflight() -> None:
    print("Fireworks AI models preflight (no cloud calls).")
    print(f"- AZURE_SUBSCRIPTION_ID: {'configured' if os.environ.get('AZURE_SUBSCRIPTION_ID') else 'MISSING'}")
    print("- Fireworks models: Llama, Mixtral variants optimized for throughput.")
    print("- Billing: Azure Marketplace (not Azure OpenAI TPM quota).")
    print("- Enable: Foundry portal → Model Catalog → filter Fireworks → Enable.")
    print("Run --apply to check Fireworks model availability in your subscription.")


def apply() -> None:
    from azure.identity import DefaultAzureCredential
    from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient

    sub = os.environ.get("AZURE_SUBSCRIPTION_ID", "")
    if not sub:
        raise SystemExit("Set AZURE_SUBSCRIPTION_ID.")
    client = CognitiveServicesManagementClient(DefaultAzureCredential(), sub)
    found: list[tuple[str, str, str]] = []
    for sku in client.resource_skus.list():
        if sku.resource_type != "accounts":
            continue
        name_lower = (sku.name or "").lower()
        kind_lower = (sku.kind or "").lower()
        if "fireworks" in name_lower or "fireworks" in kind_lower:
            locations = ", ".join(sku.locations or [])
            found.append((sku.name or "", sku.kind or "", locations))
    if not found:
        print("No Fireworks models found in catalog for this subscription.")
        print("Enable: Foundry portal → Model Catalog → Fireworks.ai → Enable partner.")
        return
    print(f"Fireworks AI models ({len(found)} found):")
    for name, kind, locations in sorted(found):
        print(f"  {name:<55} kind={kind} locations={locations[:60]}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Check Fireworks AI model availability in Foundry.")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    if not args.apply:
        preflight()
        return
    apply()


if __name__ == "__main__":
    main()
