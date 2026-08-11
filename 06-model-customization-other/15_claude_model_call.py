# Run: uv run python 06-model-customization-other/15_claude_model_call.py [--apply --model <claude-deployment>]
"""Call a Claude partner model via Azure Foundry using the Responses API.

Claude models (Anthropic) are available in Foundry as partner models via
Azure Marketplace or direct. Same Responses API client as Azure OpenAI
deployments — just a different deployment name pointing to a Claude model.
No separate SDK required when calling through the Foundry project endpoint.

Default preflight explains Claude vs OpenAI deployment differences.
`--apply` sends ONE Responses API call to the named Claude deployment and
prints the response. Prove-the-API-shape: same `responses.create()`,
same `output_text` — but different model family characteristics (reasoning
style, safety policy, context window).

Requires a Claude deployment in your Foundry project. Billing is through
Azure Marketplace terms, not OpenAI per-token pricing.

Code path:
  --apply: openai_client().responses.create(model=claude_deployment,
  input="Summarize your capabilities in one sentence.") → print
  response.model + output_text.

What to watch. `response.model` confirms which Claude variant answered.
`output_text` shows Anthropic-style response. Same client, different
billing terms and capability profile than Azure OpenAI models.

Prerequisites / env vars:
  AZURE_OPENAI_ENDPOINT  — Foundry resource URL
  --model NAME           — Claude deployment name (required with --apply)
  --apply                — send one billable request
"""
import argparse

from _shared.openai_client import openai_client


def preflight() -> None:
    print("Claude model call preflight (no cloud calls).")
    print("- Claude available via Azure Marketplace + Foundry model catalog.")
    print("- Billing: Azure Marketplace terms (not Azure OpenAI per-token pricing).")
    print("- Same responses.create() client; just different deployment name.")


def apply(model: str) -> None:
    response = openai_client().responses.create(
        model=model, input="Summarize your capabilities in one sentence."
    )
    print(f"model: {response.model}")
    print(f"output: {response.output_text}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Call a Claude partner model via Responses API.")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--model", help="Claude deployment name.")
    args = parser.parse_args(argv)
    if not args.apply:
        preflight()
        return
    if not args.model:
        parser.error("--apply requires --model.")
    apply(args.model)


if __name__ == "__main__":
    main()
