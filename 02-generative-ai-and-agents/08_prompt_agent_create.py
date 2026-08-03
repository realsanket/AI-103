"""Create the IT HelpDesk Prompt Agent — instructions + function tool schemas.

Registers a new version of the agent. Run this once (or after editing the
instructions/tools) — the agent's version increments each save.
"""
from azure.ai.projects.models import FunctionTool, PromptAgentDefinition

from _shared.foundry_client import project_client
from _shared.config import settings

AGENT_NAME = "IT-HelpDesk-Agent"

_TOOLS = [
    FunctionTool(
        name="get_password_reset_steps",
        description="Get the company password reset steps.",
        parameters={
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
        strict=True,
    ),
    FunctionTool(
        name="get_vpn_troubleshooting_steps",
        description="Get troubleshooting steps for VPN connection issues.",
        parameters={
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
        strict=True,
    ),
    FunctionTool(
        name="get_software_install_guide",
        description="Get installation instructions for a supported software package.",
        parameters={
            "type": "object",
            "properties": {
                "software_name": {
                    "type": "string",
                    "description": "The software name, for example Slack, Zoom, or VS Code.",
                }
            },
            "required": ["software_name"],
            "additionalProperties": False,
        },
        strict=True,
    ),
]


def main() -> None:
    client = project_client()
    agent = client.agents.create_version(
        agent_name=AGENT_NAME,
        definition=PromptAgentDefinition(
            model=settings().default_model,
            instructions=(
                "You are an IT support assistant for Northwind. "
                "Help users with password resets, VPN issues, and software installation. "
                "Give clear, step-by-step answers. Call your tools when you need company-specific "
                "information. If the question is outside IT support, politely say so."
            ),
            tools=_TOOLS,
        ),
    )
    print("Agent created:")
    print(f"  ID      : {agent.id}")
    print(f"  Name    : {agent.name}")
    print(f"  Version : {agent.version}")


if __name__ == "__main__":
    main()
