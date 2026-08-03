"""End-to-end IT HelpDesk agent demo — create + invoke + execute functions in one run.

Lesson 08 shows just the create; 09 shows just the invoke. This file runs the
whole loop so you can see the agentic cycle:

    user message → model picks tool → app executes → tool output → final answer
"""
import json

from azure.ai.projects.models import FunctionTool, PromptAgentDefinition

from _shared.config import settings
from _shared.foundry_client import project_client
from _shared.helpdesk_functions import (
    get_password_reset_steps,
    get_software_install_guide,
    get_vpn_troubleshooting_steps,
)

AGENT_NAME = "IT-HelpDesk-Agent-Demo"

_TOOLS = [
    FunctionTool(
        name="get_password_reset_steps",
        description="Company password reset steps.",
        parameters={"type": "object", "properties": {}, "required": [], "additionalProperties": False},
        strict=True,
    ),
    FunctionTool(
        name="get_vpn_troubleshooting_steps",
        description="VPN troubleshooting steps.",
        parameters={"type": "object", "properties": {}, "required": [], "additionalProperties": False},
        strict=True,
    ),
    FunctionTool(
        name="get_software_install_guide",
        description="Install guide for a supported software package.",
        parameters={
            "type": "object",
            "properties": {"software_name": {"type": "string"}},
            "required": ["software_name"],
            "additionalProperties": False,
        },
        strict=True,
    ),
]

_LOCAL = {
    "get_password_reset_steps": lambda **_: get_password_reset_steps(),
    "get_vpn_troubleshooting_steps": lambda **_: get_vpn_troubleshooting_steps(),
    "get_software_install_guide": lambda software_name: get_software_install_guide(software_name),
}


def main() -> None:
    project = project_client()
    agent = project.agents.create_version(
        agent_name=AGENT_NAME,
        definition=PromptAgentDefinition(
            model=settings().default_model,
            instructions=(
                "You are the CloudXeus IT support assistant. "
                "Call tools when you need company-specific information. "
                "Otherwise answer in your own words."
            ),
            tools=_TOOLS,
        ),
    )
    ref = {"type": "agent_reference", "name": agent.name, "version": agent.version}
    openai = project.get_openai_client()
    conv = openai.conversations.create()

    first = openai.responses.create(
        conversation=conv.id,
        input="I need to install Slack and I forgot my password.",
        extra_body={"agent_reference": ref},
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
                    "output": _LOCAL[item.name](**args),
                }
            )

    if tool_outputs:
        final = openai.responses.create(
            conversation=conv.id,
            input=tool_outputs,
            extra_body={"agent_reference": ref},
        )
        print("\n=== Final Answer ===")
        print(final.output_text)
    else:
        print(first.output_text)


if __name__ == "__main__":
    main()
