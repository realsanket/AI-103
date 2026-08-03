"""Invoke the IT HelpDesk agent + execute its function-tool requests locally.

The agent decides which tool to call; this app is the executor. Round-trips the
tool outputs back into the same conversation so the final answer is grounded
in what we returned.
"""
import json

from _shared.foundry_client import project_client
from _shared.helpdesk_functions import (
    get_password_reset_steps,
    get_software_install_guide,
    get_vpn_troubleshooting_steps,
)

AGENT_NAME = "IT-HelpDesk-Agent"
AGENT_VERSION = "1"  # bump after each create_version run

_LOCAL_FUNCTIONS = {
    "get_password_reset_steps": lambda **_: get_password_reset_steps(),
    "get_vpn_troubleshooting_steps": lambda **_: get_vpn_troubleshooting_steps(),
    "get_software_install_guide": lambda software_name: get_software_install_guide(software_name),
}


def _run_local(name: str, arguments: dict) -> str:
    fn = _LOCAL_FUNCTIONS.get(name)
    return fn(**arguments) if fn else f"Unknown function: {name}"


def _agent_ref() -> dict:
    return {"type": "agent_reference", "name": AGENT_NAME, "version": AGENT_VERSION}


def main() -> None:
    project = project_client()
    openai = project.get_openai_client()

    conversation = openai.conversations.create()
    print(f"conversation: {conversation.id}")

    first = openai.responses.create(
        conversation=conversation.id,
        input="My VPN keeps disconnecting. What should I do?",
        extra_body={"agent_reference": _agent_ref()},
    )

    tool_outputs = []
    for item in first.output:
        if item.type == "function_call":
            args = json.loads(item.arguments)
            print(f"→ tool: {item.name}({args})")
            tool_outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": _run_local(item.name, args),
                }
            )

    if tool_outputs:
        final = openai.responses.create(
            conversation=conversation.id,
            input=tool_outputs,
            extra_body={"agent_reference": _agent_ref()},
        )
        print("\n=== Final Answer ===")
        print(final.output_text)
    else:
        print(first.output_text)


if __name__ == "__main__":
    main()
