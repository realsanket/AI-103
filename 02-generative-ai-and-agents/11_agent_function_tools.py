# Run: uv run python 02-generative-ai-and-agents/11_agent_function_tools.py

"""End-to-end IT HelpDesk agent demo — create + invoke + execute functions in one run.

Lesson 08 shows just the create; 09 shows just the invoke. This file runs the
whole loop so you can see the agentic cycle:

    user message → model picks tool → app executes → tool output → final answer

Tool schemas constrain model input but don't replace authorization. Keep
functions least-privilege, validate every argument, treat tool output as
untrusted, and confirm DPA, data boundaries, RBAC, and model/tool costs before
replacing these local demo functions. Delete unneeded agent versions.
"""
import json

from azure.ai.projects.models import FunctionTool, PromptAgentDefinition

from _shared.config import settings
from _shared.foundry_client import active_agent_reference, project_client
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
_FUNCTION_PARAMETERS = {
    "get_password_reset_steps": set(),
    "get_vpn_troubleshooting_steps": set(),
    "get_software_install_guide": {"software_name"},
}
_REQUIRED_PARAMETERS = {"get_software_install_guide": {"software_name"}}
MAX_TOOL_ROUNDS = 8


def _run_local(name: str, arguments_json: str) -> str:
    fn = _LOCAL.get(name)
    if fn is None:
        return json.dumps({"error": f"Unknown function: {name}"})
    try:
        arguments = json.loads(arguments_json)
    except json.JSONDecodeError:
        return json.dumps({"error": "Function arguments must be valid JSON."})
    if not isinstance(arguments, dict):
        return json.dumps({"error": "Function arguments must be a JSON object."})

    allowed = _FUNCTION_PARAMETERS[name]
    missing = _REQUIRED_PARAMETERS.get(name, set()) - arguments.keys()
    unexpected = arguments.keys() - allowed
    if missing or unexpected:
        return json.dumps(
            {"error": f"Invalid arguments; missing={sorted(missing)}, unexpected={sorted(unexpected)}."}
        )
    if name == "get_software_install_guide" and not isinstance(arguments["software_name"], str):
        return json.dumps({"error": "software_name must be a string."})
    try:
        return fn(**arguments)
    except (TypeError, ValueError) as exc:
        return json.dumps({"error": f"Function rejected arguments: {exc}"})


def main() -> None:
    project = project_client()
    agent = project.agents.create_version(
        agent_name=AGENT_NAME,
        definition=PromptAgentDefinition(
            model=settings().default_model,
            instructions=(
                "You are the Northwind IT support assistant. "
                "Call tools when you need company-specific information. "
                "Otherwise answer in your own words."
            ),
            tools=_TOOLS,
        ),
    )
    ref = active_agent_reference(agent)
    openai = project.get_openai_client()
    conv = openai.conversations.create()

    response = openai.responses.create(
        conversation=conv.id,
        input="I need to install Slack and I forgot my password.",
        extra_body={"agent_reference": ref},
    )

    for _ in range(MAX_TOOL_ROUNDS):
        tool_outputs = []
        for item in response.output:
            if item.type == "function_call":
                print(f"→ tool: {item.name}({item.arguments})")
                tool_outputs.append(
                    {
                        "type": "function_call_output",
                        "call_id": item.call_id,
                        "output": _run_local(item.name, item.arguments),
                    }
                )
        if not tool_outputs:
            print("\n=== Final Answer ===")
            print(response.output_text)
            return
        response = openai.responses.create(
            conversation=conv.id,
            input=tool_outputs,
            extra_body={"agent_reference": ref},
        )
    raise RuntimeError(f"Agent exceeded {MAX_TOOL_ROUNDS} function-call rounds.")


if __name__ == "__main__":
    main()
