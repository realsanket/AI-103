"""Foundry Memory — persistent, cross-session knowledge for an agent.

Beginner note:
  Two conversations, same `user_id`. Turn 1 tells the agent something durable
  ("I'm allergic to dairy"); turn 2, in a brand-new conversation, asks a
  question that should recall the fact if memory extraction + retrieval fired.

  IMPORTANT: This lesson creates the agent inline — but the MEMORY feature
  itself needs to be enabled on the agent in the Foundry portal:
    Foundry portal → your project → Agents → this agent → Memory tab → Enable.
  Without that portal toggle, both turns run but memory won't persist across
  conversations. There's no SDK-only path today (Memory is preview).
"""
from azure.ai.projects.models import PromptAgentDefinition

from _shared.config import settings
from _shared.foundry_client import project_client

AGENT_NAME = "northwind-support-with-memory"

_INSTRUCTIONS = (
    "You are Northwind customer support. Remember relevant user facts "
    "(dietary restrictions, preferences, contact preferences) so you can "
    "reference them in later conversations for the same user."
)

_USER_ID = "user-sarah-chen"
_TURN_1 = "For the record: I'm allergic to dairy. Please note it on my account."
_TURN_2 = "Later, in a NEW conversation:  what dietary restrictions should our on-site team know about?"


def _ref() -> dict:
    return {"type": "agent_reference", "name": AGENT_NAME}


def _ensure_agent(project) -> None:
    project.agents.create_version(
        agent_name=AGENT_NAME,
        definition=PromptAgentDefinition(
            model=settings().default_model,
            instructions=_INSTRUCTIONS,
        ),
    )


def main() -> None:
    project = project_client()
    _ensure_agent(project)

    openai = project.get_openai_client()

    # --- Conversation 1: teach the agent something durable ---
    conv1 = openai.conversations.create(metadata={"user_id": _USER_ID})
    r1 = openai.responses.create(
        conversation=conv1.id,
        input=_TURN_1,
        extra_body={"agent_reference": _ref(), "user_id": _USER_ID},
    )
    print("[conv 1]", r1.output_text)

    # --- Conversation 2: brand new thread; memory retrieval should surface the fact ---
    conv2 = openai.conversations.create(metadata={"user_id": _USER_ID})
    r2 = openai.responses.create(
        conversation=conv2.id,
        input=_TURN_2,
        extra_body={"agent_reference": _ref(), "user_id": _USER_ID},
    )
    print("\n[conv 2]", r2.output_text)
    print(
        "\nTip: if conv 2 didn't recall the allergy, enable Memory on the agent in "
        "the Foundry portal (Agents → this agent → Memory → Enable), then re-run."
    )


if __name__ == "__main__":
    main()
