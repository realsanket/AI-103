# Run: uv run python 01-plan-and-manage/10_5_agent_basics.py
"""Foundry Agent basics — ephemeral agent pattern via the Responses API.

Three agent types in Foundry Agent Service:
  1. Ephemeral   — definition lives in your code, no portal, no persistence     ← this file
  2. Prompt      — registered in Foundry portal, called via agent_reference      ← L09-L12 use this
  3. Hosted      — your code in a container, Foundry manages the endpoint        ← Domain 2

Ephemeral agents ARE full Foundry agents. They get the same:
  - Foundry models from the catalog
  - Project-level guardrails and content filters
  - Observability and tracing
  - Built-in tools (file search, web search, code interpreter, MCP)
The only difference: the definition ships with your code instead of being a
persisted Foundry resource.

Only L11 uses agent_reference (northwind-support-rag-agent). L09, L10, L12
use the Content Safety API or openai_client() directly — no agent needed.
"""
from _shared.config import settings
from _shared.foundry_client import project_client


_SYSTEM = (
    "You are Northwind Support, a friendly customer support agent for "
    "Northwind Inc. Answer questions about refund policies, subscriptions, "
    "and billing. Keep answers brief and professional."
)

_QUESTIONS = [
    "What is your refund policy for Pro plan subscribers?",
    "Can I get a refund after 60 days?",
]


def single_turn(openai_client, model: str, question: str) -> str:
    """Ephemeral agent: instructions + input in one call. No state persisted."""
    r = openai_client.responses.create(
        model=model,
        instructions=_SYSTEM,
        input=question,
    )
    return r.output_text


def multi_turn(openai_client, model: str, questions: list[str]) -> None:
    """Multi-turn conversation via previous_response_id — state lives in Foundry."""
    prev_id = None
    for q in questions:
        kwargs = {"model": model, "instructions": _SYSTEM, "input": q}
        if prev_id:
            kwargs["previous_response_id"] = prev_id
        r = openai_client.responses.create(**kwargs)
        prev_id = r.id
        print(f"Q: {q}")
        print(f"A: {r.output_text}\n")


def main() -> None:
    client = project_client()
    oc = client.get_openai_client()
    model = settings().default_model

    print("=== Single-turn ephemeral agent ===")
    answer = single_turn(oc, model, _QUESTIONS[0])
    print(f"Q: {_QUESTIONS[0]}")
    print(f"A: {answer}\n")

    print("=== Multi-turn (context preserved via previous_response_id) ===")
    multi_turn(oc, model, _QUESTIONS)


if __name__ == "__main__":
    main()
