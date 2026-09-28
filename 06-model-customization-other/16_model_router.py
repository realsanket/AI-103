# Run: uv run python 06-model-customization-other/16_model_router.py [--apply] [--model <router-deployment>]
"""Route prompts through the Foundry Model Router and observe which model was selected.

The Model Router is a special deployment that automatically selects the best model
from a configured pool based on prompt complexity, cost, and quality settings. A
simple prompt routes to a fast/cheap model; a complex one routes to a more capable
model. The selected backing model is visible in response.model. Router configuration
(which models, routing policy) is managed in the Foundry portal or via Bicep.

Default preflight shows the router deployment (MODEL_ROUTER_DEPLOYMENT, the same
setting Domain 1 lesson 04 uses). --apply sends two prompts — one trivial, one
complex — and shows which backing model each request selected.

Code path:
  --apply: openai_client().responses.create(model=MODEL_ROUTER_DEPLOYMENT, input=prompt) × 2
  → response.model shows the backing model the router selected per request.

What to watch. response.model differs between simple and complex prompts when router
has multiple backing models. Same model for both = single backing model configured,
or router not yet in your subscription/region.

Prerequisites / env vars:
  AZURE_OPENAI_ENDPOINT   — Azure OpenAI endpoint (used by openai_client())
  MODEL_ROUTER_DEPLOYMENT — model router deployment name (default model-router)
  --model                 — override deployment name
  --apply           — send two prompts and print routing decisions
"""
import argparse

from _shared.config import settings
from _shared.openai_client import openai_client

_SIMPLE = "What is 2 + 2?"
_COMPLEX = (
    "Analyze the trade-offs between transformer self-attention and state-space models "
    "for long-context sequence modeling. Include time complexity, memory usage, "
    "and deployment considerations for production AI systems at scale."
)


def preflight() -> None:
    model = settings().model_router_deployment
    print("Model router preflight (no cloud calls).")
    print(f"- MODEL_ROUTER_DEPLOYMENT: {model}")
    print("- Router selects backing model per request based on complexity + cost policy.")
    print("- response.model shows the actual model that handled each request.")
    print("- Configure routing policy in Foundry portal → Deployments → Model Router.")
    print("Run --apply to see routing decisions for a simple vs complex prompt.")


def apply(router_model: str) -> None:
    client = openai_client()
    for label, prompt in [("simple", _SIMPLE), ("complex", _COMPLEX)]:
        response = client.responses.create(model=router_model, input=prompt)
        print(f"[{label}]")
        print(f"  routed to:  {response.model!r}")
        print(f"  prompt:     {prompt[:70]}...")
        print(f"  answer:     {response.output_text[:120]}")
        print()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Test model router deployment, observe routing decisions.")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--model", default=settings().model_router_deployment)
    args = parser.parse_args(argv)
    if not args.apply:
        preflight()
        return
    if not args.model:
        raise SystemExit("Set MODEL_ROUTER_DEPLOYMENT or pass --model.")
    apply(args.model)


if __name__ == "__main__":
    main()
