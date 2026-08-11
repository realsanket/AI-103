# Run: uv run python 02-generative-ai-and-agents/33_openai_prompt_caching.py [--apply]
"""Prove Azure OpenAI prompt caching by sending same long prefix twice; compare tokens.

Prompt caching reduces cost + latency for repeated long prompt prefixes
(system instructions, RAG context blocks, few-shot examples). Cached prefix
tokens are cheaper (typically ~50%) than input tokens. Enabled by default
on supported models; result surfaces via `usage.cached_tokens`.

Default preflight explains behavior. `--apply` sends TWO Responses calls
with the same long system prompt + different user queries. Second call
should report `cached_tokens > 0`. Cache lifetime is minutes — first call
seeds cache, second call hits it.

Long prefix must exceed model-specific minimum (~1024 tokens for gpt-4o).
Below threshold no caching happens. Prefix must be identical (byte-exact).

Code path:
  --apply: call 1 with system prompt + user query A → usage. Wait 2s.
  call 2 with SAME system prompt + user query B → usage. Print each usage,
  highlight cached_tokens on call 2.

What to watch. Call 1: `cached_tokens: 0` (cold). Call 2: `cached_tokens > 0`
(warm — savings kick in). If call 2 also shows 0, prefix too short or
between-call gap too long (cache expired).

Prerequisites / env vars:
  AZURE_OPENAI_ENDPOINT  — Azure OpenAI resource URL
  DEFAULT_MODEL          — model supporting prompt caching (gpt-4o+, o1+)
  --apply                — send 2 billable requests
"""
import argparse
import time

from _shared.config import settings
from _shared.openai_client import openai_client

_LONG_SYSTEM = (
    "You are Northwind support assistant. Follow these rules strictly:\n"
    + "\n".join(f"Rule {i}: Do not discuss competitor products, pricing plans, or internal roadmap." for i in range(1, 60))
    + "\n\nRespond in one sentence."
)


def preflight() -> None:
    print("Prompt caching preflight (no cloud calls).")
    print(f"- System-prefix length: {len(_LONG_SYSTEM)} chars.")
    print("- Cache hit surfaces in response.usage.cached_tokens on second call.")
    print("- Prefix must exceed model minimum (~1024 tokens); identical byte-exact.")


def _call(user_input: str) -> dict:
    response = openai_client().responses.create(
        model=settings().require("DEFAULT_MODEL"),
        input=[{"role": "system", "content": _LONG_SYSTEM}, {"role": "user", "content": user_input}],
    )
    usage = response.usage
    return {
        "input_tokens": getattr(usage, "input_tokens", 0),
        "output_tokens": getattr(usage, "output_tokens", 0),
        "cached_tokens": getattr(getattr(usage, "input_tokens_details", None), "cached_tokens", 0),
    }


def apply() -> None:
    print("Call 1 (cold, seeds cache):")
    u1 = _call("What's the refund window?")
    print(f"  {u1}")
    time.sleep(2)
    print("Call 2 (warm, should hit cache):")
    u2 = _call("How do I contact billing?")
    print(f"  {u2}")
    if u2["cached_tokens"] > 0:
        print(f"Cache HIT: {u2['cached_tokens']} tokens cached (~50% cheaper).")
    else:
        print("Cache MISS: prefix too short, cache expired, or model doesn't support.")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Prove prompt caching.")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    if not args.apply:
        preflight()
        return
    apply()


if __name__ == "__main__":
    main()
