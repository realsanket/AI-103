"""Agent with tools defined by an OpenAPI 3.0 spec.

The Foundry Agent Service reads the spec file → auto-wraps each operation into
a callable tool. No glue code; the operation's `description` field is what the
model reads to decide when to call which endpoint.

Backend is `azure_functions_orders/` (deploy it, then update the spec's
`servers.url` before running this).
"""
import json
from pathlib import Path

from azure.ai.projects.models import OpenApiAnonymousAuthDetails, OpenApiTool, PromptAgentDefinition

from _shared.config import settings
from _shared.foundry_client import project_client

AGENT_NAME = "cloudxeus-orders-agent"
SPEC_PATH = Path(__file__).parent / "azure_functions_orders" / "cloudxeus_spec.json"


def main() -> None:
    spec = json.loads(SPEC_PATH.read_text())
    tool = OpenApiTool(
        name="cloudxeus_orders",
        spec=spec,
        description="Read CloudXeus customer orders.",
        auth=OpenApiAnonymousAuthDetails(),
    )
    client = project_client()
    agent = client.agents.create_version(
        agent_name=AGENT_NAME,
        definition=PromptAgentDefinition(
            model=settings().default_model,
            instructions=(
                "You are a CloudXeus operations assistant. Use the cloudxeus_orders "
                "tools to answer questions about order status. If asked about an order "
                "you cannot find, say so — do not invent data."
            ),
            tools=[tool],
        ),
    )
    print(f"Agent {agent.name} v{agent.version} created — tools discovered from OpenAPI spec.")

    openai = client.get_openai_client()
    r = openai.responses.create(
        input="What is the status of order 1002?",
        extra_body={
            "agent_reference": {
                "type": "agent_reference",
                "name": agent.name,
                "version": agent.version,
            }
        },
    )
    print(r.output_text)


if __name__ == "__main__":
    main()
