# Run: uv run python 08-advanced-agents-other/18_custom_code_interpreter_preflight.py
"""Validate that a custom code interpreter MCP endpoint is reachable and properly configured.

Custom code interpreter gives agents a sandboxed Python runtime with your chosen packages,
backed by Azure Container Apps Dynamic Sessions. The interpreter exposes an MCP server —
agents connect via MCPTool with server_url pointing to the Container Apps session pool endpoint.

This is NOT the built-in code interpreter (lesson 05, domain 02). The built-in runs in an
Azure-managed sandbox with fixed packages. The custom interpreter deploys your own container
and requires infrastructure provisioning (ACA Dynamic Sessions) before agents can use it.

Flows:
  Default  — local preflight: validates env vars and prints MCPTool definition structure.
  --apply  — HTTP probe of MCP_SERVER_URL (GET to confirm reachability); does NOT create agent.

What to watch in the output:
  [OK] MCP_SERVER_URL reachable   → endpoint exists; ACA session pool is running.
  HTTP 200 or 405 on the MCP root → server up (405 = correct endpoint, expects POST for MCP RPC).
  HTTP 4xx                        → auth or endpoint error.
  ConnectionRefusedError          → Container Apps not running or wrong URL.

Prerequisites / env vars:
  MCP_SERVER_URL         — session pool MCP endpoint from Bicep output mcpServerEndpoint
  MCP_CONNECTION_ID      — project connection name pointing to the MCP server (optional)
  PROJECT_ENDPOINT       — Foundry project endpoint
  DEFAULT_MODEL          — model deployment for the agent
  --apply                — probe MCP_SERVER_URL (requires ACA infrastructure deployed)
"""

import argparse
import os
import sys
import urllib.request
import urllib.error

from _shared.config import load_env


def preflight() -> None:
    mcp_url = os.environ.get("MCP_SERVER_URL", "")
    connection_id = os.environ.get("MCP_CONNECTION_ID", "")
    project_endpoint = os.environ.get("PROJECT_ENDPOINT", "")

    print("=== Custom Code Interpreter Preflight ===")
    print()
    _check("MCP_SERVER_URL", mcp_url, required=True)
    _check("MCP_CONNECTION_ID", connection_id, required=False, hint="optional; needed if MCP server requires auth")
    _check("PROJECT_ENDPOINT", project_endpoint, required=True)
    print()
    print("Agent tool definition (Python SDK):")
    print("  from azure.ai.projects.models import MCPTool, MCPToolboxTool, PromptAgentDefinition")
    print()
    print("  # Step 1: add MCP server to a Toolbox")
    print("  toolbox = project.toolboxes.create_version(")
    print("      name='custom-code-interpreter-toolbox',")
    print("      tools=[MCPToolboxTool(")
    print("          server_label='custom-code-interpreter',")
    print(f"          server_url='{mcp_url or '<MCP_SERVER_URL>'}',")
    print(f"          project_connection_id='{connection_id or '<MCP_CONNECTION_ID>'}',")
    print("      )]")
    print("  )")
    print()
    print("  # Step 2: agent references toolbox via MCPTool")
    print("  agent = project.agents.create_version(")
    print("      agent_name='CustomCodeInterpreterAgent',")
    print("      definition=PromptAgentDefinition(")
    print("          model=DEFAULT_MODEL,")
    print("          tools=[MCPTool(")
    print("              server_label='toolbox',")
    print("              server_url=TOOLBOX_MCP_URL,")
    print("              require_approval='never',   # safe: code runs in sandboxed session")
    print("              project_connection_id=TOOLBOX_CONNECTION_NAME,")
    print("          )]")
    print("      )")
    print("  )")
    print()
    print("Infrastructure note: requires ACA Dynamic Sessions pool with MCPServerSettings.")
    print("Register preview feature: az feature register --namespace Microsoft.App --name SessionPoolsSupportMCP")
    print()
    print("Run with --apply to probe MCP_SERVER_URL.")


def apply() -> None:
    mcp_url = os.environ.get("MCP_SERVER_URL", "")
    if not mcp_url:
        print("[FAIL] MCP_SERVER_URL not set — set to session pool mcpServerEndpoint from Bicep output")
        sys.exit(1)

    print(f"Probing MCP endpoint: {mcp_url}")
    try:
        req = urllib.request.Request(mcp_url, method="GET")
        with urllib.request.urlopen(req, timeout=15) as resp:
            code = resp.status
            print(f"[OK] HTTP {code} — MCP server reachable")
    except urllib.error.HTTPError as e:
        if e.code in (405, 400):
            print(f"[OK] HTTP {e.code} — MCP server reachable (expects POST for MCP RPC, GET returns {e.code})")
        elif e.code == 401:
            print(f"[FAIL] HTTP 401 — authentication required; check MCP_CONNECTION_ID credentials")
            sys.exit(1)
        elif e.code == 404:
            print(f"[FAIL] HTTP 404 — endpoint not found; check MCP_SERVER_URL matches mcpServerEndpoint output")
            sys.exit(1)
        else:
            print(f"[WARN] HTTP {e.code} — unexpected response; verify endpoint URL and ACA session pool status")
    except urllib.error.URLError as e:
        print(f"[FAIL] Connection error: {e.reason}")
        print("  → Container Apps session pool may not be running or URL is wrong")
        sys.exit(1)


def _check(name: str, value: str, required: bool, hint: str = "") -> None:
    if value:
        display = value[:60] + "..." if len(value) > 60 else value
        print(f"  [OK]     {name} = {display}")
    elif required:
        print(f"  [FAIL]   {name} — not set{(' — ' + hint) if hint else ''}")
    else:
        print(f"  [WARN]   {name} — not set{(' — ' + hint) if hint else ''}")


def main() -> None:
    load_env()
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if args.apply:
        apply()
    else:
        preflight()


if __name__ == "__main__":
    main()
