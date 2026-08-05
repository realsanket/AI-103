"""Multi-agent coordination — one router agent delegating to two specialists.

Pattern: the router uses `agent_as_tool` (each specialist is exposed as a
FunctionTool wrapping a Responses API call to the target agent's name). The
model decides which specialist to invoke per turn — no hardcoded routing.
"""
import json

from azure.ai.projects.models import FunctionTool, PromptAgentDefinition
from openai import APIConnectionError, APIStatusError, APITimeoutError

from _shared.config import settings
from _shared.foundry_client import active_agent_reference, project_client

ROUTER = "northwind-router"
BILLING = "northwind-billing-specialist"
TECHNICAL = "northwind-tech-specialist"
MAX_TOOL_ROUNDS = 8


def _ensure_specialists(project) -> dict[str, dict[str, str]]:
    billing = project.agents.create_version(
        agent_name=BILLING,
        definition=PromptAgentDefinition(
            model=settings().default_model,
            instructions="You are a Northwind billing specialist. Answer billing / refund questions only.",
        ),
    )
    technical = project.agents.create_version(
        agent_name=TECHNICAL,
        definition=PromptAgentDefinition(
            model=settings().default_model,
            instructions="You are a Northwind technical specialist. Answer product / troubleshooting questions only.",
        ),
    )
    return {
        "ask_billing_specialist": active_agent_reference(billing),
        "ask_tech_specialist": active_agent_reference(technical),
    }


def _router_tools() -> list[FunctionTool]:
    schema = {
        "type": "object",
        "properties": {"question": {"type": "string"}},
        "required": ["question"],
        "additionalProperties": False,
    }
    return [
        FunctionTool(name="ask_billing_specialist", description="Route billing/refund questions here.",
                     parameters=schema, strict=True),
        FunctionTool(name="ask_tech_specialist", description="Route product/technical questions here.",
                     parameters=schema, strict=True),
    ]


def _delegate(project, target: dict[str, str], question: str) -> str:
    openai = project.get_openai_client()
    try:
        response = openai.responses.create(
            extra_body={"agent_reference": target},
            input=question,
        )
    except (APIConnectionError, APITimeoutError):
        return json.dumps({"error": "Specialist is temporarily unavailable. Try again."})
    except APIStatusError as exc:
        return json.dumps({"error": f"Specialist request failed with status {exc.status_code}."})
    return response.output_text


def _run_router_tool(
    project, name: str, arguments_json: str, targets: dict[str, dict[str, str]]
) -> str:
    target = targets.get(name)
    if target is None:
        return json.dumps({"error": f"Unknown router tool: {name}"})
    try:
        arguments = json.loads(arguments_json)
    except json.JSONDecodeError:
        return json.dumps({"error": "Tool arguments must be valid JSON."})
    if not isinstance(arguments, dict) or set(arguments) != {"question"}:
        return json.dumps({"error": "Tool arguments must contain only question."})
    question = arguments["question"]
    if not isinstance(question, str) or not question.strip():
        return json.dumps({"error": "question must be a non-empty string."})
    return _delegate(project, target, question)


def main() -> None:
    project = project_client()
    specialist_references = _ensure_specialists(project)

    router = project.agents.create_version(
        agent_name=ROUTER,
        definition=PromptAgentDefinition(
            model=settings().default_model,
            instructions=(
                "You are the Northwind support router. Read the customer's message and delegate "
                "to the correct specialist via a tool call. Do not answer directly."
            ),
            tools=_router_tools(),
        ),
    )
    ref = active_agent_reference(router)
    openai = project.get_openai_client()
    conv = openai.conversations.create()

    response = openai.responses.create(
        conversation=conv.id,
        input="I need a refund on my last invoice — it double-charged me.",
        extra_body={"agent_reference": ref},
    )

    for _ in range(MAX_TOOL_ROUNDS):
        tool_outputs = []
        for item in response.output:
            if item.type == "function_call":
                print(f"router → {item.name}({item.arguments})")
                tool_outputs.append(
                    {
                        "type": "function_call_output",
                        "call_id": item.call_id,
                        "output": _run_router_tool(
                            project, item.name, item.arguments, specialist_references
                        ),
                    }
                )
        if not tool_outputs:
            print("\n=== Final ===")
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
