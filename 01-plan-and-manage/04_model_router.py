# Run: uv run python 01-plan-and-manage/04_model_router.py
"""Model Router — use Responses API and let Foundry select model per prompt.

Beginner note:
  Instead of hard-coding "use gpt-5-mini here, gpt-4.1 there", you deploy a
  single `model-router` from the catalog. Send any prompt to it; the router
  decides which underlying model handles it (cheap nano for trivia, frontier
  for hard reasoning). You still see which model actually ran — the response's
  `model` field reveals it.

The Responses API supports `model-router`. Pass the router deployment name in
`model`; `response.model` identifies the model that handled each request.

This script uses the project-scoped client. It needs Microsoft Entra ID access
to the Foundry project, normally the Foundry User role. Direct Azure OpenAI
resource calls instead require a suitable Cognitive Services inference role.

What to watch:
  Each prompt line prints `[picked: <model>]` showing which model the router
  chose. Trivial prompts go to nano/mini; complex ones to full-size models.
"""
from _shared.config import settings
from _shared.foundry_client import project_client

_PROMPTS = [
    "What is 2 + 2?",                                                              # trivial → nano
    "Summarize the plot of Hamlet in one paragraph.",                              # medium
    "Design a distributed consensus protocol tolerant of Byzantine failures.",     # hard → frontier
]


def main() -> None:
    client = project_client().get_openai_client()
    router = settings().model_router_deployment
    for prompt in _PROMPTS:
        r = client.responses.create(
            model=router,
            input=prompt,
        )
        picked = r.model or "?"
        content = r.output_text
        print(f"[picked: {picked}]  prompt: {prompt[:60]}")
        print(f"  → {content[:120]}\n")


if __name__ == "__main__":
    main()
