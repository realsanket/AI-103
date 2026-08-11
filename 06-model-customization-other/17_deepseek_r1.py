# Run: uv run python 06-model-customization-other/17_deepseek_r1.py [--apply] [--model <deployment>]
"""Call DeepSeek R1 via the Foundry Models catalog and observe its reasoning chain.

DeepSeek R1 is a partner reasoning model in the Foundry Models catalog. Like
o-series models, it generates an internal chain of thought — surfaced in
<think>...</think> tags in the response text. It is accessed via the standard
Responses API using the same openai_client() as Azure OpenAI models; only the
deployment name differs. Billing flows through Azure Marketplace.

Default preflight checks DEEPSEEK_MODEL env var. --apply sends a proof-by-induction
problem and splits the response into thinking block vs final answer.

Code path:
  --apply: openai_client().responses.create(model=DEEPSEEK_MODEL, input=prompt)
  → parse <think>...</think> from output_text using re.search
  → print thinking block length + final answer text.

What to watch. Non-empty <think> block = reasoning chain exposed by model.
Text after </think> = final answer. Empty output = deployment name wrong or
model version does not expose reasoning tags.

Prerequisites / env vars:
  PROJECT_ENDPOINT  — Foundry project HTTPS URL (used by openai_client())
  DEEPSEEK_MODEL    — DeepSeek R1 deployment name
  --model           — override deployment name
  --apply           — send request and parse reasoning chain
"""
import argparse
import os
import re

from _shared.openai_client import openai_client

_PROMPT = (
    "Prove by induction that the sum of the first n positive integers equals n*(n+1)/2. "
    "Show every step clearly."
)


def preflight() -> None:
    model = os.environ.get("DEEPSEEK_MODEL", "")
    print("DeepSeek R1 preflight (no cloud calls).")
    print(f"- DEEPSEEK_MODEL: {model or 'MISSING — set to your DeepSeek R1 deployment name'}")
    print("- Same Responses API as Azure OpenAI — only the deployment name differs.")
    print("- Billing via Azure Marketplace (separate from Azure OpenAI quota).")
    print("- <think>...</think> in output_text = model's internal reasoning chain.")
    print("Run --apply to see the reasoning chain on a proof-by-induction problem.")


def apply(model: str) -> None:
    client = openai_client()
    print(f"Sending to {model!r} ...")
    response = client.responses.create(model=model, input=_PROMPT)
    text = response.output_text or ""
    match = re.search(r"<think>(.*?)</think>", text, re.DOTALL)
    if match:
        thinking = match.group(1).strip()
        answer = text[match.end():].strip()
        print(f"=== Thinking chain ({len(thinking)} chars) ===")
        print(thinking[:600] + ("..." if len(thinking) > 600 else ""))
        print()
        print("=== Final answer ===")
        print(answer)
    else:
        print("(No <think> tags — model may not expose reasoning in this version)")
        print(text)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Call DeepSeek R1 and parse reasoning chain.")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--model", default=os.environ.get("DEEPSEEK_MODEL", ""))
    args = parser.parse_args(argv)
    if not args.apply:
        preflight()
        return
    if not args.model:
        raise SystemExit("Set DEEPSEEK_MODEL env var or pass --model.")
    apply(args.model)


if __name__ == "__main__":
    main()
