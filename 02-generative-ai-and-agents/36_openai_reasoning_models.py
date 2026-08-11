# Run: uv run python 02-generative-ai-and-agents/36_openai_reasoning_models.py [--apply --model <o-deployment>] [--effort low|medium|high]
"""Call an o-series reasoning model and observe thinking token usage.

Reasoning models (o1, o3, o3-mini) generate an internal chain of thought before
producing a final answer. The reasoning budget is controlled by reasoning_effort
(low/medium/high). Thinking tokens appear in usage.output_tokens_details.reasoning_tokens
and are billed at the same rate as output tokens — they do NOT appear in output_text.

Default preflight explains reasoning model concepts. --apply sends a multi-step
math problem and prints the final answer plus thinking token count. This proves:
(1) the model processes reasoning internally, (2) thinking tokens are tracked
separately, (3) higher effort = more reasoning tokens + better accuracy.

Code path:
  --apply: openai_client().responses.create(model=O_MODEL, input=prompt,
  reasoning={"effort": effort}) → output_text + usage.output_tokens_details.

What to watch. reasoning_tokens > 0 on a complex prompt confirms reasoning is
active. Increase effort if the answer is wrong on hard problems.

Prerequisites / env vars:
  PROJECT_ENDPOINT  — Foundry project HTTPS URL
  O_MODEL           — o-series deployment name (o3-mini, o1, o3)
  DEFAULT_MODEL     — fallback if O_MODEL not set
  --model           — override deployment name
  --effort          — low | medium | high (default: medium)
  --apply           — send request to o-series model
"""
import argparse
import os

from _shared.config import settings
from _shared.openai_client import openai_client

_PROMPT = (
    "A farmer has 17 sheep. All but 9 die. How many sheep does the farmer have left? "
    "Show your reasoning step by step, then state the final answer clearly."
)


def preflight() -> None:
    model = os.environ.get("O_MODEL") or settings().default_model or "o3-mini"
    print("Reasoning model preflight (no cloud calls).")
    print(f"- target deployment: {model}")
    print("- reasoning_effort: controls thinking-token budget (low/medium/high)")
    print("- thinking tokens: billed same as output tokens, not shown in output_text")
    print("- usage.output_tokens_details.reasoning_tokens shows internal work count")
    print("Run --apply to see reasoning token count on a multi-step problem.")


def apply(model: str, effort: str) -> None:
    client = openai_client()
    print(f"Sending to {model!r} with reasoning_effort={effort!r} ...")
    response = client.responses.create(
        model=model,
        input=_PROMPT,
        reasoning={"effort": effort},
    )
    usage = response.usage
    detail = getattr(getattr(usage, "output_tokens_details", None), "reasoning_tokens", None)
    print(f"\nAnswer:\n{response.output_text}")
    print()
    print("Token usage:")
    print(f"  input_tokens:     {usage.input_tokens}")
    print(f"  output_tokens:    {usage.output_tokens}")
    print(f"  reasoning_tokens: {detail if detail is not None else 'not reported by this deployment'}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Call o-series reasoning model, show thinking tokens.")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--model", default=os.environ.get("O_MODEL") or settings().default_model or "o3-mini")
    parser.add_argument("--effort", default="medium", choices=["low", "medium", "high"])
    args = parser.parse_args(argv)
    if not args.apply:
        preflight()
        return
    apply(args.model, args.effort)


if __name__ == "__main__":
    main()
