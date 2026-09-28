# Run: uv run python 06-model-customization-other/00_customization_preflight.py
"""Local readiness check for Microsoft Foundry customization labs.

Confirms the env vars every lesson in this domain reads. Runs no cloud call.
Prints which of AZURE_OPENAI_ENDPOINT, FOUNDRY_ENDPOINT, AZURE_SUBSCRIPTION_ID,
AZURE_RESOURCE_GROUP, and DEFAULT_MODEL are set. Only proves configuration is
present — not that the caller has permissions, that models exist, or that
quota is available in the target region.

Run before any lesson to catch missing config early. Never use `--apply`
elsewhere until this passes cleanly.

Code path:
  settings() → dict of five boolean checks → print each as configured/missing.

What to watch. Every check should print `configured`. `missing` items must be
fixed in .env before running lessons 05, 07, 09, 10, 11, or 12 with --apply.

Prerequisites / env vars:
  AZURE_OPENAI_ENDPOINT   — https://<resource>.openai.azure.com
  FOUNDRY_ENDPOINT        — https://<resource>.services.ai.azure.com
  AZURE_SUBSCRIPTION_ID   — sub containing the Foundry resource
  AZURE_RESOURCE_GROUP    — RG for management-plane calls
  DEFAULT_MODEL           — base deployment name for inference labs
"""
from __future__ import annotations

from _shared.config import settings


def preflight() -> dict[str, bool]:
    current = settings()
    return {
        "azure_openai_endpoint": bool(current.azure_openai_endpoint),
        "foundry_resource_endpoint": bool(current.foundry_endpoint),
        "subscription": bool(current.azure_subscription_id),
        "resource_group": bool(current.azure_resource_group),
        "base_inference_deployment": bool(current.default_model),
    }


def main() -> None:
    print("Customization preflight (local only; no cloud calls)")
    for name, ready in preflight().items():
        print(f"- {name}: {'configured' if ready else 'missing'}")
    print("\nBefore apply: use a nonproduction resource; verify model/method/region support,")
    print("quota and capacity, Foundry User/Owner or required deployment permission, and data governance.")
    print("Training, generation, hosting, evaluation, priority, and batch requests can bill.")


if __name__ == "__main__":
    main()
