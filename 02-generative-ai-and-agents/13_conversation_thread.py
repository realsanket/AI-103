"""Conversation threads — server-managed history via `client.conversations.create()`.

Beginner note:
  Same `conversation.id` across two `responses.create` calls → the agent has
  full context on the second turn. New id = blank slate. Foundry keeps the
  transcript server-side; you never resend the previous messages yourself.

  This lesson creates the required Prompt Agent inline (self-contained). Run
  cold — no portal setup needed.
"""
from azure.ai.projects.models import PromptAgentDefinition

from _shared.config import settings
from _shared.foundry_client import project_client

AGENT_NAME = "northwind-support-agent-conv"

_INSTRUCTIONS = (
    "You are Northwind customer support. Answer briefly and professionally. "
    "If asked about a specific order, remember the order id across turns."
)


def _ref() -> dict:
    return {"type": "agent_reference", "name": AGENT_NAME}


def _ensure_agent(project) -> None:
    """Create-or-update the agent — safe to run every time; version bumps."""
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

    sara = openai.conversations.create()
    print(f"conversation.id: {sara.id}")

    first = openai.responses.create(
        conversation=sara.id,
        input="My order #4521 is late.",
        extra_body={"agent_reference": _ref()},
    )
    print("\nturn 1:", first.output_text)

    followup = openai.responses.create(
        conversation=sara.id,
        input="Any update on it?",  # relies on server-side history to know which order
        extra_body={"agent_reference": _ref()},
    )
    print("\nturn 2:", followup.output_text)


if __name__ == "__main__":
    main()
