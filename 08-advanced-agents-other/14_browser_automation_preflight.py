# Run: uv run python 08-advanced-agents-other/14_browser_automation_preflight.py [--apply]
"""Validate browser automation (computer use) tool configuration for a Foundry agent.

Browser automation lets hosted agents drive a headless Chromium browser to fill forms,
scrape dynamic pages, and click UI elements — tasks that REST APIs cannot handle. It is
exposed as a tool in the agent definition under type "browser". The hosted agent
container must have Playwright/Chromium installed, and the Foundry project needs a
browser-type connection configured.

Default preflight checks env vars and lists what the hosted container needs. --apply
creates an ephemeral probe agent with the browser tool declared, calls list_tools to
verify discovery, then deletes. Actual navigation requires a target URL and a live
browser-enabled hosted agent.

Code path:
  preflight: check PROJECT_ENDPOINT, DEFAULT_MODEL, BROWSER_CONNECTION_NAME.
  --apply: agents.create_version(tools=[{"type":"browser","connection_name":...}])
  → agents.list_tools(agent_name, version) → check browser in tool list → agents.delete.

What to watch. "browser" in discovered tool list = connection valid and tool provisioned.
Not found = BROWSER_CONNECTION_NAME wrong or browser tool not enabled for this project.

Prerequisites / env vars:
  PROJECT_ENDPOINT         — Foundry project HTTPS URL
  DEFAULT_MODEL            — deployed chat model
  BROWSER_CONNECTION_NAME  — Foundry project connection name for browser tool
  --apply                  — create probe agent + verify browser tool discovery
"""
import argparse
import os

from _shared.config import settings
from _shared.foundry_client import project_client


def preflight() -> None:
    current = settings()
    print("Browser automation preflight (no cloud calls).")
    print(f"- PROJECT_ENDPOINT: {'configured' if current.project_endpoint else 'missing'}")
    print(f"- DEFAULT_MODEL: {'configured' if current.default_model else 'missing'}")
    print(f"- BROWSER_CONNECTION_NAME: {'configured' if os.environ.get('BROWSER_CONNECTION_NAME') else 'missing'}")
    print()
    print("Container requirements for browser tool:")
    print("  - Playwright + Chromium installed in hosted agent container.")
    print("  - Foundry project connection type: browser.")
    print("  - Tool declared: {\"type\": \"browser\", \"connection_name\": BROWSER_CONNECTION_NAME}")
    print("Run --apply to probe browser tool discovery on an ephemeral agent.")


def apply() -> None:
    from azure.ai.projects.models import PromptAgentDefinition

    connection_name = os.environ.get("BROWSER_CONNECTION_NAME", "")
    if not connection_name:
        raise SystemExit("Set BROWSER_CONNECTION_NAME.")
    current = settings()
    client = project_client()
    agent_name = "browser-probe-agent"
    try:
        tools = [{"type": "browser", "connection_name": connection_name}]
        agent = client.agents.create_version(
            agent_name=agent_name,
            definition=PromptAgentDefinition(
                model=current.require("DEFAULT_MODEL"),
                instructions="Browser automation probe — do not respond to any input.",
                tools=tools,
            ),
        )
        print(f"Agent '{agent.name}' v{agent.version} created.")
        tool_list = client.agents.list_tools(agent_name, str(agent.version))
        tools_out = getattr(tool_list, "tools", tool_list) or []
        print(f"Discovered tools ({len(tools_out)}):")
        for t in tools_out:
            print(f"  - {getattr(t, 'name', str(t))}")
        has_browser = any(
            "browser" in str(getattr(t, "type", "")).lower()
            for t in tools_out
        )
        print(f"Browser tool: {'[PASS] found' if has_browser else '[FAIL] not found'}")
    finally:
        try:
            client.agents.delete(agent_name)
        except Exception:
            pass
        print("Probe agent deleted.")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Validate browser automation tool for Foundry agent.")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    if not args.apply:
        preflight()
        return
    apply()


if __name__ == "__main__":
    main()
