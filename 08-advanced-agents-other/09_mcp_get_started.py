# Run: uv run python 08-advanced-agents-other/09_mcp_get_started.py [--apply]
"""Connect a Foundry agent to an MCP server tool and list available tools.

Model Context Protocol (MCP) lets agents discover and call tools hosted on
any MCP-compatible server. Foundry agents support MCP connections through
project connections (lesson 01 pattern) or direct endpoint configuration.

Default preflight explains the MCP connection model. `--apply` uses
`project_client().agents.create_version()` to configure a prompt agent with
an MCP tool connection, lists the tools it discovers, then deletes the agent.
This proves discovery + auth without a persistent agent artifact.

MCP tool authentication flows through project connections (managed identity)
— never embed bearer tokens in agent definitions.

Code path:
  --apply: agents.create_version(agent_name, definition=PromptAgentDefinition(
  model=DEFAULT_MODEL, tools=[McpTool(connection_name=MCP_CONNECTION_NAME)]))
  → agents.list_tools(agent_name, version) → print tool names → agents.delete.

What to watch. Preflight: env status. --apply: list of tool names from the
MCP server. Zero tools = connection name wrong or MCP server empty.
Cleanup: agent deleted before exit.

Prerequisites / env vars:
  PROJECT_ENDPOINT      — Foundry project HTTPS URL
  DEFAULT_MODEL         — deployed chat model
  MCP_CONNECTION_NAME   — Foundry project connection name for MCP server
  --apply               — create ephemeral agent + list tools + delete
"""
import argparse
import os

from _shared.config import settings
from _shared.foundry_client import project_client


def preflight() -> None:
    current = settings()
    print("MCP get-started preflight (no cloud calls).")
    print(f"- project_endpoint: {'configured' if current.project_endpoint else 'missing'}")
    print(f"- default_model: {'configured' if current.default_model else 'missing'}")
    print(f"- MCP_CONNECTION_NAME: {'configured' if os.environ.get('MCP_CONNECTION_NAME') else 'missing'}")
    print("- MCP tools are discovered at agent create time via the connection.")


def apply() -> None:
    from azure.ai.projects.models import PromptAgentDefinition

    connection_name = os.environ.get("MCP_CONNECTION_NAME", "")
    if not connection_name:
        raise SystemExit("Set MCP_CONNECTION_NAME to an existing Foundry project connection.")
    current = settings()
    client = project_client()
    agent_name = "mcp-discovery-probe"
    try:
        # Build tool list using connection — SDK shape varies; use dict for portability
        tools = [{"type": "mcp", "connection_name": connection_name}]
        agent = client.agents.create_version(
            agent_name=agent_name,
            definition=PromptAgentDefinition(
                model=current.require("DEFAULT_MODEL"),
                instructions="You are a tool discovery probe. Do not answer questions.",
                tools=tools,
            ),
        )
        print(f"Agent '{agent.name}' v{agent.version} created for probe.")
        try:
            tool_list = client.agents.list_tools(agent_name, str(agent.version))
            tools_out = getattr(tool_list, "tools", tool_list) or []
            print(f"MCP tools discovered ({len(tools_out)}):")
            for t in tools_out:
                name = getattr(t, "name", str(t))
                print(f"  - {name}")
        finally:
            client.agents.delete(agent_name)
            print("Probe agent deleted.")
    except Exception as exc:
        print(f"Error: {exc}")
        raise


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Connect Foundry agent to MCP; list tools.")
    parser.add_argument("--apply", action="store_true", help="Create probe agent + list MCP tools.")
    args = parser.parse_args(argv)
    if not args.apply:
        preflight()
        return
    apply()


if __name__ == "__main__":
    main()
