# Run: uv run python 02-generative-ai-and-agents/08_prompt_agent_create.py
# Practice-question coverage: Q154, Q169.

"""Create a versioned Prompt Agent definition — instructions and function tool schemas.

A Foundry Prompt Agent is a stored, versioned definition: model + instructions + tools.
Unlike a direct Responses call (lesson 01), the definition lives in Foundry and can be
invoked by name from any client. Each `create_version()` call increments the version;
the agent does NOT run until invoked (lesson 09 or 11).

This file shows exactly what a Prompt Agent definition contains:
  - `PromptAgentDefinition`: model, instructions, list of FunctionTool schemas
  - `FunctionTool`: name, description, JSON Schema parameters, strict=True
  - `strict=True`: constrains token sampler to schema — it does NOT authorize execution

Code path:
  1. `project_client()` → `AIProjectClient` via PROJECT_ENDPOINT
  2. `client.agents.create_version()` → registers new version in Foundry
  3. Prints agent id, name, version — save these for lesson 09

What to watch:
  Printed version number. Run twice → version increments. Re-run after changing
  instructions to see versioning in action.

Prerequisites / env vars:
  PROJECT_ENDPOINT — Foundry project URL
  DEFAULT_MODEL    — deployment name for the agent's model
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
