# Run: uv run python 01-plan-and-manage/04_model_router.py
"""Model Router — one endpoint, router picks the underlying model per prompt.

Deploy `model-router` from the catalog once, then call it like any chat model.
Model router uses Chat Completions API (not Responses API).
The `model` field on the response reveals which underlying model was picked.
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
