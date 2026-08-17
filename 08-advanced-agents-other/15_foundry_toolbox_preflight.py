# Run: uv run python 08-advanced-agents-other/15_foundry_toolbox_preflight.py [--apply]
"""Discover project connections that can support agent and Toolbox tools.

Project connections store downstream endpoints and authentication configuration.
They can support direct agent tools or tools included in a Toolbox, but a connection
is not itself a Toolbox version and does not prove a tool is published or usable.
Connectionless tools such as Reminder also will not appear here.

Default preflight explains the toolbox structure. --apply calls
project_client().connections.list() filtered to known toolbox connection types
and prints candidate name, type, and endpoint for each.

Code path:
  --apply: project_client().connections.list()
  → filter connection_type in _TOOLBOX_TYPES (case-insensitive)
  → print name, connection_type, target endpoint.

What to watch. Each listed row is only connection inventory. Inspect actual agent
and Toolbox version definitions to prove which tools consume it.

Prerequisites / env vars:
  PROJECT_ENDPOINT  — Foundry project HTTPS URL
  --apply           — list toolbox connections in this project
"""
import argparse

from _shared.config import settings
from _shared.foundry_client import project_client

_TOOL_CONNECTION_MARKERS = (
    "Bing", "AzureFunction", "SharePoint", "Custom", "MicrosoftFabric",
    "Browser", "AzureAISearch", "ApiKey", "MCP", "Reminder", "ImageGeneration",
)


def preflight() -> None:
    current = settings()
    print("Agent tool connection preflight (no cloud calls).")
    print(f"- PROJECT_ENDPOINT: {'configured' if current.project_endpoint else 'missing'}")
    print(f"- Connection markers: {', '.join(_TOOL_CONNECTION_MARKERS)}")
    print("- A connection is not proof of Toolbox membership or runtime authorization.")
    print("Run --apply to list candidate tool connections in this project.")


def apply() -> None:
    client = project_client()
    all_conns = list(client.connections.list())
    toolbox = [
        c for c in all_conns
        if any(
            t.lower() in str(getattr(c, "connection_type", "")).lower()
            for t in _TOOL_CONNECTION_MARKERS
        )
    ]
    print(f"Project connections: {len(all_conns)} total, {len(toolbox)} tool candidates.")
    for c in toolbox:
        name = getattr(c, "name", "?")
        ctype = getattr(c, "connection_type", "?")
        endpoint = str(getattr(c, "target", "") or "")
        print(f"  {name:<40} type={ctype} endpoint={endpoint[:60]}")
    if not toolbox:
        print("  (none — create reviewed project connections before connection-backed tools)")


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
