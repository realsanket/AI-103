"""Conversation threads — server-managed history via `client.conversations.create()`.

Same conversation id across two `responses.create` calls → the agent has
context for the follow-up. New conversation id = blank slate.
"""
from _shared.foundry_client import project_client

AGENT_NAME = "cloudxeus-support-agent-conv"


def _ref() -> dict:
    return {"type": "agent_reference", "name": AGENT_NAME}


def main() -> None:
    project = project_client()
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
