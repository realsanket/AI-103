# Run: uv run python 06-model-customization-other/14_foundry_models_list.py [--apply] [--kind <openai|claude|all>]
"""List models available in the Foundry model catalog for this account.

Foundry Models catalog groups models by publisher: Azure OpenAI models
(sold directly by Azure), partner models (Claude via Marketplace/direct),
and open-source. Default preflight explains structure; `--apply` calls
`CognitiveServicesManagementClient.resource_skus.list()` with a filter for
`Microsoft.CognitiveServices/accounts` to enumerate models visible in the
subscription region, then filters by kind flag.

Useful before lesson 05 (custom-model deployment) or 07 (deploy checkpoint)
to confirm model IDs + supported SKUs + regions for your subscription.

Code path:
  --apply: CognitiveServicesManagementClient(cred, sub).resource_skus.list()
  → filter to CognitiveServices resource type → group by family + kind →
  print (name, kind, tier, locations).

What to watch. `--apply`: table of model families with supported SKU tiers
and locations. Empty = no models visible in subscription or wrong filter.
`--kind claude` prints only Claude partner models where available.

Prerequisites / env vars:
  AZURE_SUBSCRIPTION_ID  — target subscription
  --apply                — perform subscription-wide SKU read (read-only)
  --kind                 — openai | claude | all (default: all)
"""
import argparse

from azure.identity import DefaultAzureCredential
from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient

from _shared.config import settings


def preflight() -> None:
    print("Foundry Models catalog preflight (no cloud calls).")
    print("- Models: Azure OpenAI (sold directly), Claude (partner), open-source.")
    print("- `--apply` reads resource_skus to enumerate available model families.")
    print("- Compare with Foundry portal: Foundry → Model catalog → filter by provider.")


def apply(kind_filter: str) -> None:
    sub = settings().require("AZURE_SUBSCRIPTION_ID")
    client = CognitiveServicesManagementClient(DefaultAzureCredential(), sub)
    print(f"{'name':<45} {'kind':<15} {'tier':<20} {'locations'}")
    print("-" * 100)
    seen: set[str] = set()
    for sku in client.resource_skus.list():
        if sku.resource_type != "accounts":
            continue
        name = sku.name or ""
        kind = sku.kind or ""
        if kind_filter == "openai" and kind != "OpenAI":
            continue
        if kind_filter == "claude" and "claude" not in name.lower() and "anthropic" not in kind.lower():
            continue
        key = f"{name}:{kind}"
        if key in seen:
            continue
        seen.add(key)
        tiers = ",".join(r.tier for r in (sku.restrictions or [])[:2]) if sku.restrictions else "Standard"
        locations = ",".join((sku.locations or [])[:3])
        print(f"{name:<45} {kind:<15} {tiers:<20} {locations}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="List Foundry Models catalog entries.")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--kind", choices=["openai", "claude", "all"], default="all")
    args = parser.parse_args(argv)
    if not args.apply:
        preflight()
        return
    apply(args.kind)


if __name__ == "__main__":
    main()
