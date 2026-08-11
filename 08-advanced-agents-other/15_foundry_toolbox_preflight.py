# Run: uv run python 08-advanced-agents-other/15_foundry_toolbox_preflight.py [--apply]
"""Discover tools available in the Foundry agent toolbox for this project.

The Foundry toolbox is a curated catalog of pre-built agent tools: Bing web search,
SharePoint, Azure Functions, image generation, reminder, Fabric, custom code
interpreter, and more. Tools are wired to a project as typed connections and declared
in agent definitions by connection name. This lesson enumerates which toolbox
connections are configured in the current project.

Default preflight explains the toolbox structure. --apply calls
project_client().connections.list() filtered to known toolbox connection types
and prints name, type, and endpoint for each.

Code path:
  --apply: project_client().connections.list()
  → filter connection_type in _TOOLBOX_TYPES (case-insensitive)
  → print name, connection_type, target endpoint.

What to watch. Each listed connection is a tool the agent can use. Zero results
= no toolbox tools configured — add via Foundry portal → Project → Connections → Add.

Prerequisites / env vars:
  PROJECT_ENDPOINT  — Foundry project HTTPS URL
  --apply           — list toolbox connections in this project
"""
import argparse

from _shared.config import settings
from _shared.foundry_client import project_client

_TOOLBOX_TYPES = (
    "Bing", "AzureFunction", "SharePoint", "Custom", "MicrosoftFabric",
    "Browser", "AzureAISearch", "ApiKey", "MCP", "Reminder", "ImageGeneration",
)


def preflight() -> None:
    current = settings()
    print("Foundry toolbox preflight (no cloud calls).")
    print(f"- PROJECT_ENDPOINT: {'configured' if current.project_endpoint else 'missing'}")
    print(f"- Toolbox connection types: {', '.join(_TOOLBOX_TYPES)}")
    print("- Each connection becomes an available tool when declared in an agent definition.")
    print("Run --apply to list all toolbox connections in this project.")


def apply() -> None:
    client = project_client()
    all_conns = list(client.connections.list())
    toolbox = [
        c for c in all_conns
        if any(
            t.lower() in str(getattr(c, "connection_type", "")).lower()
            for t in _TOOLBOX_TYPES
        )
    ]
    print(f"Project connections: {len(all_conns)} total, {len(toolbox)} toolbox tools.")
    for c in toolbox:
        name = getattr(c, "name", "?")
        ctype = getattr(c, "connection_type", "?")
        endpoint = str(getattr(c, "target", "") or "")
        print(f"  {name:<40} type={ctype} endpoint={endpoint[:60]}")
    if not toolbox:
        print("  (none — add tools: Foundry portal → Project → Connections → Add)")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="List Foundry toolbox connections in this project.")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    if not args.apply:
        preflight()
        return
    apply()


if __name__ == "__main__":
    main()
