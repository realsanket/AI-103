# Run: uv run python 08-advanced-agents-other/14_browser_automation_preflight.py [--apply]
"""Validate the preview Browser Automation tool for a Foundry agent.

Browser Automation uses an Azure Playwright workspace connection so an agent
can navigate and interact with websites. It is not the direct Computer Use
model loop in lesson 25. Browser authority is high risk: use isolated test
sites, least privilege, bounded domains/actions, approval, and tracing.

Default preflight checks env vars and lists what the hosted container needs. --apply
creates an ephemeral probe agent with the browser tool declared, calls list_tools to
verify discovery, then deletes. Actual navigation requires a target URL and a live
browser-enabled hosted agent.

Code path:
  browser_tool() builds BrowserAutomationPreviewTool with the Playwright
  project_connection_id. --apply creates one probe agent, calls list_tools,
  checks browser_automation_preview, then deletes the probe agent.

What to watch. "browser" in discovered tool list = connection valid and tool provisioned.
Not found = BROWSER_PROJECT_CONNECTION_ID wrong or browser tool not enabled for this project.

Prerequisites / env vars:
  PROJECT_ENDPOINT         — Foundry project HTTPS URL
  DEFAULT_MODEL            — deployed chat model
  BROWSER_PROJECT_CONNECTION_ID  — Foundry Playwright project connection ID
  --apply                  — create probe agent + verify browser tool discovery
"""
import argparse
import os

from _shared.config import settings
from _shared.foundry_client import project_client


def browser_tool(connection_id: str):
    from azure.ai.projects.models import (
        BrowserAutomationPreviewTool,
        BrowserAutomationToolConnectionParameters,
        BrowserAutomationToolParameters,
    )

    if not connection_id:
        raise ValueError("Browser project connection ID is required.")
    return BrowserAutomationPreviewTool(
        browser_automation_preview=BrowserAutomationToolParameters(
            connection=BrowserAutomationToolConnectionParameters(
                project_connection_id=connection_id
            )
        )
    )


def preflight() -> None:
    current = settings()
    print("Browser automation preflight (no cloud calls).")
    print(f"- PROJECT_ENDPOINT: {'configured' if current.project_endpoint else 'missing'}")
    print(f"- DEFAULT_MODEL: {'configured' if current.default_model else 'missing'}")
    print(
        "- BROWSER_PROJECT_CONNECTION_ID: "
        f"{'configured' if os.environ.get('BROWSER_PROJECT_CONNECTION_ID') else 'missing'}"
    )
    print()
    print("Current preview requirements:")
    print("  - Azure Playwright workspace and Foundry project connection.")
    print("  - Foundry Project Manager to create connection.")
    print("  - Contributor only while provisioning the Playwright workspace.")
    print("  - Private website access remains private preview.")
    print("  - Trace browser_automation_preview_call events; bound domains and actions.")
    connection_id = os.environ.get("BROWSER_PROJECT_CONNECTION_ID")
    if connection_id:
        print(f"  - Tool payload: {browser_tool(connection_id).as_dict()}")
    print("Run --apply to probe typed tool discovery on an ephemeral agent.")


def apply() -> None:
    from azure.ai.projects.models import PromptAgentDefinition

    connection_id = os.environ.get("BROWSER_PROJECT_CONNECTION_ID", "")
    if not connection_id:
        raise SystemExit("Set BROWSER_PROJECT_CONNECTION_ID.")
    current = settings()
    client = project_client()
    agent_name = "browser-probe-agent"
    created = False
    try:
        agent = client.agents.create_version(
            agent_name=agent_name,
            definition=PromptAgentDefinition(
                model=current.require("DEFAULT_MODEL"),
                instructions="Browser automation probe — do not respond to any input.",
                tools=[browser_tool(connection_id)],
            ),
        )
        created = True
        print(f"Agent '{agent.name}' v{agent.version} created.")
        tool_list = client.agents.list_tools(agent_name, str(agent.version))
        tools_out = getattr(tool_list, "tools", tool_list) or []
        print(f"Discovered tools ({len(tools_out)}):")
        for t in tools_out:
            print(f"  - {getattr(t, 'name', str(t))}")
        has_browser = any(
            "browser_automation_preview" in str(getattr(t, "type", "")).lower()
            for t in tools_out
        )
        print(f"Browser tool: {'[PASS] found' if has_browser else '[FAIL] not found'}")
    finally:
        if created:
            client.agents.delete(agent_name)
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
