# Run: uv run python 02-generative-ai-and-agents/09_prompt_agent_invoke.py

"""Invoke the IT HelpDesk agent + execute its function-tool requests locally.

The agent decides which tool to call; this app is the executor. Round-trips the
tool outputs back into the same conversation so the final answer is grounded
in what we returned.
"""
import json

from azure.core.exceptions import ResourceNotFoundError

from _shared.foundry_client import active_agent_reference, project_client
from _shared.helpdesk_functions import (
    get_password_reset_steps,
    get_software_install_guide,
    get_vpn_troubleshooting_steps,
)

AGENT_NAME = "IT-HelpDesk-Agent"

_LOCAL_FUNCTIONS = {
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
    fn = _LOCAL_FUNCTIONS.get(name)
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


def _agent_ref(project) -> dict[str, str]:
    try:
        agent = project.agents.get(AGENT_NAME)
    except ResourceNotFoundError as exc:
        raise SystemExit(
            "IT-HelpDesk-Agent was not found. Run lesson 08 before lesson 09:\n"
            "  uv run python 02-generative-ai-and-agents/08_prompt_agent_create.py"
        ) from exc
    return active_agent_reference(agent.versions.latest)


def main() -> None:
    project = project_client()
    openai = project.get_openai_client()
    reference = _agent_ref(project)

    conversation = openai.conversations.create()
    print(f"conversation: {conversation.id}")

    response = openai.responses.create(
        conversation=conversation.id,
        input="My VPN keeps disconnecting. What should I do?",
        extra_body={"agent_reference": reference},
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
            conversation=conversation.id,
            input=tool_outputs,
            extra_body={"agent_reference": reference},
        )
    raise RuntimeError(f"Agent exceeded {MAX_TOOL_ROUNDS} function-call rounds.")


if __name__ == "__main__":
    main()
