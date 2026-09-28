# Run: uv run python 06-model-customization-other/17_deepseek_reasoning.py [--apply] [--model <deployment>]
"""Call a DeepSeek reasoning model sold by Azure and separate its reasoning from the answer.

DeepSeek-V4-Pro is a Foundry Model sold directly by Azure (GA). It is called
through the Azure OpenAI v1 endpoint with the standard OpenAI client and
`chat.completions.create()` — only the deployment name differs. It supports
text chat completions but not tool calling. DeepSeek-R1 and R1-0528 were
retired in 2026 (R1 on 2026-08-13); Microsoft's listed replacement is
DeepSeek-V4-Pro.

Reasoning output: the model may put its chain of thought inside
`<think>...</think>` at the start of `message.content` (some versions return
`message.reasoning_content` instead). Show the answer to users; log or drop the
reasoning, and never append it to later turns. Reasoning models ignore
`temperature`/`top_p`; limit output with `max_tokens`.

Default preflight prints the request; `--apply` sends one billable request.

Prerequisites / env vars:
  AZURE_OPENAI_ENDPOINT — Foundry resource endpoint (used by openai_client())
  DEEPSEEK_MODEL        — DeepSeek deployment name (for example DeepSeek-V4-Pro)
  Role: Cognitive Services User on the Foundry resource.
"""
import argparse
import json
import re

from _shared.config import env

PROMPT = "Prove by induction that the sum of the first n positive integers equals n*(n+1)/2."
_THINK = re.compile(r"\s*<think>(.*?)</think>(.*)", re.DOTALL)


def split_reasoning(message) -> tuple[str, str]:
    """Return (reasoning, answer) from a chat completion message."""
    content = message.content or ""
    reasoning = getattr(message, "reasoning_content", None) or ""
    match = _THINK.match(content)
    if match:
        return (reasoning or match.group(1)).strip(), match.group(2).strip()
    return reasoning.strip(), content.strip()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--apply", action="store_true", help="Send one billable request.")
    parser.add_argument("--model", default=env("DEEPSEEK_MODEL"), help="DeepSeek deployment name.")
    parser.add_argument("--max-tokens", type=int, default=2000)
    args = parser.parse_args(argv)

    request = {
        "model": args.model or "<DEEPSEEK_MODEL>",
        "messages": [{"role": "user", "content": PROMPT}],
        "max_tokens": args.max_tokens,
    }
    if not args.apply:
        print("DeepSeek reasoning preflight (no cloud calls).")
        print("openai_client().chat.completions.create(**request) with:")
        print(json.dumps(request, indent=2))
        return
    if not args.model:
        raise SystemExit("Set DEEPSEEK_MODEL or pass --model.")

    from _shared.openai_client import openai_client

    response = openai_client().chat.completions.create(**request)
    reasoning, answer = split_reasoning(response.choices[0].message)
    print(f"model: {response.model}")
    print(f"=== Reasoning ({len(reasoning)} chars; not for end users) ===")
    print(reasoning[:600] + ("..." if len(reasoning) > 600 else "") if reasoning else "(none returned)")
    print("\n=== Answer ===")
    print(answer)
    usage = response.usage
    print(f"\nusage: prompt={usage.prompt_tokens} completion={usage.completion_tokens} total={usage.total_tokens}")


if __name__ == "__main__":
    main()
