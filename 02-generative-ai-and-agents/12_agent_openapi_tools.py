# Run: uv run python 02-generative-ai-and-agents/12_agent_openapi_tools.py [--auth anonymous|connection] [--print-tool] [--keep]
# Practice-question coverage: Q7, Q67.

"""Agent with tools defined by an OpenAPI 3.0 spec, with anonymous or connection-key auth.

Beginner note:
  The Foundry Agent Service reads the spec file → auto-wraps each operation
  into a callable tool. No glue code; the operation's `description` field is
  what the model reads to decide when to call which endpoint.

  Backend = `azure_functions_orders/` (Azure Function). `func start` on
  localhost lets you test the function with curl, but Foundry Agent Service
  cannot call your laptop's localhost. Set `ORDERS_FN_ENDPOINT` to a deployed
  backend reachable from Agent Service (without `/api`; this script appends it).

Two auth modes:
  --auth anonymous   (default) Public demo data only. Never for production APIs.
  --auth connection  The API key lives in a Foundry project connection
                     (Custom keys; key name `x-functions-key`). The spec gets an
                     `apiKey` security scheme (`components.securitySchemes` +
                     top-level `security`) and the tool uses
                     `OpenApiProjectConnectionAuthDetails(project_connection_id=...)`.
                     Agent Service then injects the header on every call. Without
                     the security scheme, or without connecting the tool to the
                     connection, the header is never sent (401 from the API).
                     Deploy the Function with app setting ORDERS_REQUIRE_KEY=true
                     so it actually demands the key.
  (Managed identity is the third option: OpenApiManagedAuthDetails(audience=...).)

  Treat OpenAPI descriptions and responses as untrusted. Use least-privilege
  RBAC, validate arguments server-side, and review DPA, data residency,
  retention, observability, region, and model/API costs. The lab agent version
  is deleted after the run unless you pass --keep.

Env vars:
  ORDERS_FN_ENDPOINT      — deployed Function origin without /api
  ORDERS_CONNECTION_NAME  — project connection holding x-functions-key (--auth connection)
  PROJECT_ENDPOINT, DEFAULT_MODEL
"""
import argparse
import copy
import json
from pathlib import Path
from urllib.parse import urlparse

from azure.ai.projects.models import (
    OpenApiAnonymousAuthDetails,
    OpenApiFunctionDefinition,
    OpenApiProjectConnectionAuthDetails,
    OpenApiProjectConnectionSecurityScheme,
    OpenApiTool,
    PromptAgentDefinition,
)

from _shared.config import env, settings
from _shared.foundry_client import active_agent_reference, project_client

AGENT_NAME = "northwind-orders-agent"
SPEC_PATH = Path(__file__).parent / "azure_functions_orders" / "northwind_spec.json"
KEY_HEADER = "x-functions-key"


def _load_spec_with_backend() -> dict:
    """Load the OpenAPI spec and override servers[0].url with ORDERS_FN_ENDPOINT."""
    backend = env("ORDERS_FN_ENDPOINT").rstrip("/")
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


def with_api_key_scheme(spec: dict, header: str = KEY_HEADER) -> dict:
    """Return a copy of the spec that declares one apiKey header scheme for every operation."""
    secured = copy.deepcopy(spec)
    secured.setdefault("components", {}).setdefault("securitySchemes", {})["functionKey"] = {
        "type": "apiKey",
        "name": header,
        "in": "header",
    }
    secured["security"] = [{"functionKey": []}]
    return secured


def build_tool(spec: dict, auth: str, connection_id: str = "") -> OpenApiTool:
    if auth == "connection":
        if not connection_id:
            raise ValueError("--auth connection needs the project connection ID.")
        spec = with_api_key_scheme(spec)
        details = OpenApiProjectConnectionAuthDetails(
            security_scheme=OpenApiProjectConnectionSecurityScheme(project_connection_id=connection_id)
        )
    else:
        details = OpenApiAnonymousAuthDetails()
    return OpenApiTool(
        openapi=OpenApiFunctionDefinition(
            name="northwind_orders",
            spec=spec,
            description="Read Northwind customer orders.",
            auth=details,
        )
    )


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--auth", choices=("anonymous", "connection"), default="anonymous")
    parser.add_argument("--print-tool", action="store_true", help="Print the tool JSON; no Azure call.")
    parser.add_argument("--keep", action="store_true", help="Keep the agent version after the run.")
    args = parser.parse_args(argv)

    spec = _load_spec_with_backend()
    connection_name = env("ORDERS_CONNECTION_NAME")
    if args.auth == "connection" and not connection_name:
        raise SystemExit("Set ORDERS_CONNECTION_NAME to the project connection that stores x-functions-key.")
    if args.print_tool:
        placeholder = f"<connection ID of {connection_name}>" if args.auth == "connection" else ""
        print(json.dumps(build_tool(spec, args.auth, placeholder).as_dict(), indent=2))
        return

    client = project_client()
    connection_id = client.connections.get(connection_name).id if args.auth == "connection" else ""
    agent = client.agents.create_version(
        agent_name=AGENT_NAME,
        definition=PromptAgentDefinition(
            model=settings().default_model,
            instructions=(
                "You are a Northwind operations assistant. Use the northwind_orders "
                "tools to answer questions about order status. If asked about an order "
                "you cannot find, say so — do not invent data."
            ),
            tools=[build_tool(spec, args.auth, connection_id)],
        ),
    )
    print(f"Agent {agent.name} v{agent.version} created ({args.auth} auth) — tools discovered from OpenAPI spec.")
    try:
        response = client.get_openai_client().responses.create(
            input="What is the status of order 1002?",
            extra_body={"agent_reference": active_agent_reference(agent)},
        )
        print(response.output_text)
    finally:
        if not args.keep:
            client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
            print(f"Deleted agent version {agent.version}.")


if __name__ == "__main__":
    main()
