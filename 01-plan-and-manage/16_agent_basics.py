# Run: uv run python 01-plan-and-manage/16_agent_basics.py
"""Responses API basics — code-defined instructions and linked turns.

This script doesn't create, register, or deploy a Foundry agent. It makes
ordinary project-scoped Responses API calls, supplying instructions in code and
using `previous_response_id` to link turns. Use a registered prompt or hosted
agent when you need an Agent Service resource, lifecycle, tools, or endpoint.
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
