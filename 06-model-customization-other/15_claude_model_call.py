# Run: uv run python 06-model-customization-other/15_claude_model_call.py [--apply] [--model <claude-deployment>] [--effort low|medium|high]
"""Call a Claude partner model in Foundry through the Anthropic Messages API.

Claude models are Foundry Models from partners: you deploy them from the model
catalog (Azure Marketplace subscription, Global Standard or Data Zone), then
call them with the Anthropic SDK's `AnthropicFoundry` client — the Claude
Messages API, not the OpenAI Responses or Chat Completions client.

  base URL : https://<resource>.services.ai.azure.com/anthropic
             (derived from FOUNDRY_ENDPOINT + "/anthropic")
  auth     : Microsoft Entra ID token for https://ai.azure.com/.default
             (Cognitive Services User on the resource); API keys also work
             but stay out of this repository.
  model    : your Claude DEPLOYMENT name.

Reasoning is steered with `thinking={"type": "adaptive"}` and
`output_config={"effort": ...}`. Check `stop_reason`: "refusal" means Claude
declined for safety; "max_tokens" means the answer was cut off.

Default preflight prints the request shape; `--apply` sends ONE billable call.
Billing follows Azure Marketplace terms for the Claude offer.

Prerequisites / env vars:
  FOUNDRY_ENDPOINT   — https://<resource>.services.ai.azure.com
  CLAUDE_DEPLOYMENT  — Claude deployment name (or pass --model)
"""
import argparse
import json

from _shared.config import env, settings

PROMPT = "In two sentences, when should a support team escalate a refund dispute to a human?"


def anthropic_base_url(foundry_endpoint: str) -> str:
    from _shared.foundry_management import foundry_account_name

    foundry_account_name(foundry_endpoint)  # validates *.services.ai.azure.com
    return f"{foundry_endpoint.rstrip('/')}/anthropic"


def request_body(model: str, effort: str = "medium", max_tokens: int = 1024) -> dict:
    if effort not in {"low", "medium", "high"}:
        raise ValueError("effort must be low, medium, or high")
    return {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": PROMPT}],
        "thinking": {"type": "adaptive"},
        "output_config": {"effort": effort},
    }


def answer_text(message) -> str:
    """Join text blocks; thinking blocks are internal and not printed."""
    return "".join(block.text for block in message.content if getattr(block, "type", "") == "text")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--apply", action="store_true", help="Send one billable request.")
    parser.add_argument("--model", default=env("CLAUDE_DEPLOYMENT"), help="Claude deployment name.")
    parser.add_argument("--effort", choices=("low", "medium", "high"), default="medium")
    args = parser.parse_args(argv)

    body = request_body(args.model or "<CLAUDE_DEPLOYMENT>", args.effort)
    if not args.apply:
        endpoint = settings().foundry_endpoint
        print("Claude Messages API preflight (no cloud calls).")
        print(f"- base_url: {anthropic_base_url(endpoint) if endpoint else '<FOUNDRY_ENDPOINT>/anthropic'}")
        print("- client: anthropic.AnthropicFoundry(azure_ad_token_provider=..., base_url=...)")
        print("- request: client.messages.create(**body)")
        print(json.dumps(body, indent=2))
        return
    if not args.model:
        raise SystemExit("Set CLAUDE_DEPLOYMENT or pass --model.")

    from anthropic import AnthropicFoundry
    from azure.identity import DefaultAzureCredential, get_bearer_token_provider

    client = AnthropicFoundry(
        azure_ad_token_provider=get_bearer_token_provider(DefaultAzureCredential(), "https://ai.azure.com/.default"),
        base_url=anthropic_base_url(settings().require("FOUNDRY_ENDPOINT")),
    )
    message = client.messages.create(**body)
    print(f"model: {message.model}  stop_reason: {message.stop_reason}")
    if message.stop_reason == "refusal":
        print("Claude declined this request for safety reasons; do not retry it unchanged.")
        return
    print(answer_text(message))
    print(f"usage: input={message.usage.input_tokens} output={message.usage.output_tokens}")


if __name__ == "__main__":
    main()
