"""Foundry Memory — persistent, cross-session knowledge for an agent.

Two conversations, same user. Turn 1 tells the agent something ("I'm allergic
to dairy"); turn 2, in a fresh conversation, asks a question that should
recall that fact if memory extraction/retrieval fired.

Enabling Memory on an agent is a portal setting (Agent → Memory → Enable) —
this script exercises the runtime side.
"""
from _shared.foundry_client import project_client

AGENT_NAME = "northwind-support-with-memory"

_USER_ID = "user-sarah-chen"
_TURN_1 = "For the record: I'm allergic to dairy. Please note it on my account."
_TURN_2 = "Later, in a NEW conversation:  what dietary restrictions should our on-site team know about?"


def _ref() -> dict:
    return {"type": "agent_reference", "name": AGENT_NAME}


def main() -> None:
    project = project_client()
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


if __name__ == "__main__":
    main()
