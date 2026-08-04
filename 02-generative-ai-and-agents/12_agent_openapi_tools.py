"""Agent with tools defined by an OpenAPI 3.0 spec.

Beginner note:
  The Foundry Agent Service reads the spec file → auto-wraps each operation
  into a callable tool. No glue code; the operation's `description` field is
  what the model reads to decide when to call which endpoint.

  Backend = `azure_functions_orders/` (Azure Function). You must have it
  running somewhere the agent can reach — either locally with `func start`
  or deployed to Azure. Set `ORDERS_FN_ENDPOINT` in `.env` to that URL
  (the URL alone, without `/api` — the spec appends the path). Examples:
    Local:    ORDERS_FN_ENDPOINT=http://localhost:7071
    Deployed: ORDERS_FN_ENDPOINT=https://fn-northwind-<yours>.azurewebsites.net
"""
import json
import os
from pathlib import Path

from azure.ai.projects.models import OpenApiAnonymousAuthDetails, OpenApiTool, PromptAgentDefinition

from _shared.config import settings
from _shared.foundry_client import project_client

AGENT_NAME = "northwind-orders-agent"
SPEC_PATH = Path(__file__).parent / "azure_functions_orders" / "northwind_spec.json"


def _load_spec_with_backend() -> dict:
    """Load the OpenAPI spec and override servers[0].url with ORDERS_FN_ENDPOINT."""
    backend = os.environ.get("ORDERS_FN_ENDPOINT", "").rstrip("/")
    if not backend:
        raise SystemExit(
            "ORDERS_FN_ENDPOINT is not set in .env.\n"
            "  Local:    cd 02-generative-ai-and-agents/azure_functions_orders && func start\n"
            "            then set ORDERS_FN_ENDPOINT=http://localhost:7071 in .env\n"
            "  Deployed: set ORDERS_FN_ENDPOINT=https://<your-func>.azurewebsites.net"
        )
    spec = json.loads(SPEC_PATH.read_text())
    spec["servers"] = [{"url": f"{backend}/api"}]
    return spec


def main() -> None:
    spec = _load_spec_with_backend()
    tool = OpenApiTool(
        name="northwind_orders",
        spec=spec,
        description="Read Northwind customer orders.",
        auth=OpenApiAnonymousAuthDetails(),
    )
    client = project_client()
    agent = client.agents.create_version(
        agent_name=AGENT_NAME,
        definition=PromptAgentDefinition(
            model=settings().default_model,
            instructions=(
                "You are a Northwind operations assistant. Use the northwind_orders "
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
