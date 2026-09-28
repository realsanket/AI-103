# Run: uv run python 06-model-customization-other/18_huggingface_models_preflight.py [--apply]
# Practice-question coverage: Q132, Q152.
"""Discover HuggingFace-origin models available in the Foundry Models catalog.

Foundry Models catalog includes curated open-source models from HuggingFace
(Phi, Mistral, Llama, Falcon, Qwen, Gemma, etc.) deployed as serverless
or managed compute endpoints. They appear alongside Azure OpenAI and partner
models in resource_skus.list(). Once deployed, they use the same Responses
API endpoint — only the deployment name differs.

Default preflight explains the catalog structure. --apply uses
CognitiveServicesManagementClient.resource_skus.list() filtered to model
family keywords and prints the list of available HuggingFace-origin models
in the subscription's catalog.

Code path:
  --apply: CognitiveServicesManagementClient(DefaultAzureCredential(), sub)
  .resource_skus.list()
  → filter resource_type=="accounts" + name contains HF model family keyword
  → print name, kind, locations.

What to watch. Models with "phi", "mistral", "llama", "meta", "qwen" in name
= HuggingFace-origin. Locations shows deployment regions for that model.

Prerequisites / env vars:
  AZURE_SUBSCRIPTION_ID  — subscription to query
  --apply                — list HuggingFace-origin models from catalog
"""
import argparse
import os

from _shared.config import load_env

_HF_KEYWORDS = ("phi", "mistral", "llama", "meta", "falcon", "bloom", "qwen", "gemma", "deepseek", "jais")


def preflight() -> None:
    print("HuggingFace models preflight (no cloud calls).")
    print(f"- AZURE_SUBSCRIPTION_ID: {'configured' if os.environ.get('AZURE_SUBSCRIPTION_ID') else 'MISSING'}")
    print(f"- HF model families searched: {', '.join(_HF_KEYWORDS)}")
    print("- Once deployed, call via same openai_client().responses.create() as Azure OpenAI.")
    print("- Serverless endpoints: pay-per-token, no PTU reservation needed.")
    print("Run --apply to list available HuggingFace models in catalog.")


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
        name = (sku.name or "").lower()
        if any(kw in name for kw in _HF_KEYWORDS):
            locations = ", ".join(sku.locations or [])
            found.append((sku.name or "", sku.kind or "", locations))
    if not found:
        print("No HuggingFace-origin models found for this subscription.")
        return
    print(f"HuggingFace-origin models ({len(found)} found):")
    for name, kind, locations in sorted(found):
        print(f"  {name:<50} kind={kind} locations={locations[:60]}")


def main(argv: list[str] | None = None) -> None:
    load_env()
    parser = argparse.ArgumentParser(description="List HuggingFace models in Foundry catalog.")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    if not args.apply:
        preflight()
        return
    apply()


if __name__ == "__main__":
    main()
