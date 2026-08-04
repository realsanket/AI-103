# Run: uv run python 01-plan-and-manage/04_model_router.py
"""Model Router — one deployment, router picks the underlying model per prompt.

Beginner note:
  Instead of hard-coding "use gpt-5-mini here, gpt-4.1 there", you deploy a
  single `model-router` from the catalog. Send any prompt to it; the router
  decides which underlying model handles it (cheap nano for trivia, frontier
  for hard reasoning). You still see which model actually ran — the response's
  `model` field reveals it.

Two gotchas that will bite you:
  1. Model router uses **Chat Completions** (`chat.completions.create`), NOT
     the Responses API. Calling `responses.create` returns 400.
  2. You need the `Foundry User` role on the Foundry resource — otherwise 401.

What to watch:
  Each prompt line prints `[picked: <model>]` showing which model the router
  chose. Trivial prompts go to nano/mini; complex ones to full-size models.
"""
from _shared.openai_client import openai_client
from _shared.config import settings

_PROMPTS = [
    "What is 2 + 2?",                                                              # trivial → nano
    "Summarize the plot of Hamlet in one paragraph.",                              # medium
    "Design a distributed consensus protocol tolerant of Byzantine failures.",     # hard → frontier
]


def main() -> None:
    client = openai_client()
    router = settings().model_router_deployment
    for prompt in _PROMPTS:
        r = client.chat.completions.create(
            model=router,
            messages=[{"role": "user", "content": prompt}],
        )
        picked = r.model or "?"
        content = r.choices[0].message.content or ""
        print(f"[picked: {picked}]  prompt: {prompt[:60]}")
        print(f"  → {content[:120]}\n")


if __name__ == "__main__":
    main()
