# Run: uv run python 06-model-customization-other/00_customization_preflight.py
"""Local readiness check for Microsoft Foundry customization labs."""
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
