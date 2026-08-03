"""Multi-agent coordination — one router agent delegating to two specialists.

Pattern: the router uses `agent_as_tool` (each specialist is exposed as a
FunctionTool wrapping a Responses API call to the target agent's name). The
model decides which specialist to invoke per turn — no hardcoded routing.
"""
import json

from azure.ai.projects.models import FunctionTool, PromptAgentDefinition

from _shared.config import settings
from _shared.foundry_client import project_client

ROUTER = "northwind-router"
BILLING = "northwind-billing-specialist"
TECHNICAL = "northwind-tech-specialist"


def _ensure_specialists(project) -> None:
    project.agents.create_version(
        agent_name=BILLING,
        definition=PromptAgentDefinition(
            model=settings().default_model,
            instructions="You are a Northwind billing specialist. Answer billing / refund questions only.",
        ),
    )
    project.agents.create_version(
        agent_name=TECHNICAL,
        definition=PromptAgentDefinition(
            model=settings().default_model,
            instructions="You are a Northwind technical specialist. Answer product / troubleshooting questions only.",
        ),
    )


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


def _delegate(project, target_agent: str, question: str) -> str:
    openai = project.get_openai_client()
    r = openai.responses.create(
        extra_body={"agent_reference": {"type": "agent_reference", "name": target_agent}},
        input=question,
    )
    return r.output_text


def main() -> None:
    project = project_client()
    _ensure_specialists(project)

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
    ref = {"type": "agent_reference", "name": router.name, "version": router.version}
    openai = project.get_openai_client()
    conv = openai.conversations.create()

    first = openai.responses.create(
        conversation=conv.id,
        input="I need a refund on my last invoice — it double-charged me.",
        extra_body={"agent_reference": ref},
    )

    tool_outputs = []
    for item in first.output:
        if item.type == "function_call":
            args = json.loads(item.arguments)
            target = {"ask_billing_specialist": BILLING, "ask_tech_specialist": TECHNICAL}[item.name]
            print(f"router → {item.name}({args})")
            tool_outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": _delegate(project, target, args["question"]),
                }
            )

    if tool_outputs:
        final = openai.responses.create(
            conversation=conv.id,
            input=tool_outputs,
            extra_body={"agent_reference": ref},
        )
        print("\n=== Final ===")
        print(final.output_text)
    else:
        print(first.output_text)


if __name__ == "__main__":
    main()
