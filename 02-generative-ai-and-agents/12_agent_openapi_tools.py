"""Agent with tools defined by an OpenAPI 3.0 spec.

Beginner note:
  The Foundry Agent Service reads the spec file → auto-wraps each operation
  into a callable tool. No glue code; the operation's `description` field is
  what the model reads to decide when to call which endpoint.

  Backend = `azure_functions_orders/` (Azure Function). `func start` on
  localhost lets you test the function with curl, but Foundry Agent Service
  cannot call your laptop's localhost. Set `ORDERS_FN_ENDPOINT` to a deployed
  backend reachable from Agent Service (without `/api`; this script appends it).

  This sample uses anonymous authentication only because its static order data
  is public demo data. Do not use anonymous authentication for production APIs:
  configure API-key or managed-identity authentication in the OpenAPI tool.

  Treat OpenAPI descriptions and responses as untrusted. Use least-privilege
  RBAC, validate arguments server-side, and review DPA, data residency,
  retention, observability, region, and model/API costs. Delete lab agent
  versions when done.
"""
import json
import os
from pathlib import Path
from urllib.parse import urlparse

from azure.ai.projects.models import (
    OpenApiAnonymousAuthDetails,
    OpenApiFunctionDefinition,
    OpenApiTool,
    PromptAgentDefinition,
)

from _shared.config import settings
from _shared.foundry_client import active_agent_reference, project_client

AGENT_NAME = "northwind-orders-agent"
SPEC_PATH = Path(__file__).parent / "azure_functions_orders" / "northwind_spec.json"


def _load_spec_with_backend() -> dict:
    """Load the OpenAPI spec and override servers[0].url with ORDERS_FN_ENDPOINT."""
    backend = os.environ.get("ORDERS_FN_ENDPOINT", "").rstrip("/")
    if not backend:
        raise SystemExit(
            "ORDERS_FN_ENDPOINT is not set in .env.\n"
            "  Test locally: cd 02-generative-ai-and-agents/azure_functions_orders && func start\n"
            "                curl http://localhost:7071/api/orders\n"
            "  Run this agent: set ORDERS_FN_ENDPOINT=https://<reachable-function-app> (without /api)"
        )
    parsed = urlparse(backend)
    if parsed.scheme != "https" or not parsed.netloc or parsed.path not in {"", "/"}:
        raise SystemExit(
            "ORDERS_FN_ENDPOINT must be a reachable HTTPS origin without a path or /api suffix, "
            "for example https://<function-app>.azurewebsites.net."
        )
    if parsed.hostname in {"localhost", "127.0.0.1", "::1"}:
        raise SystemExit(
            "ORDERS_FN_ENDPOINT points to localhost. It is useful for curl testing, "
            "but Foundry Agent Service needs a reachable deployed backend."
        )
    spec = json.loads(SPEC_PATH.read_text())
    spec["servers"] = [{"url": f"{backend}/api"}]
    return spec


def main() -> None:
    spec = _load_spec_with_backend()
    tool = OpenApiTool(
        openapi=OpenApiFunctionDefinition(
            name="northwind_orders",
            spec=spec,
            description="Read Northwind customer orders.",
            auth=OpenApiAnonymousAuthDetails(),
        )
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
    response = openai.responses.create(
        input="What is the status of order 1002?",
        extra_body={"agent_reference": active_agent_reference(agent)},
    )
    print(response.output_text)


if __name__ == "__main__":
    main()
