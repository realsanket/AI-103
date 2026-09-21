# Run: uv run python 02-generative-ai-and-agents/46_work_iq_tool_preflight.py [--apply]
"""Work IQ (preview) tool preflight — Microsoft 365 grounding via A2A.

Work IQ is Microsoft 365's intelligence layer — emails, meetings, files, chats,
and business signals grounded in the signed-in user's tenant and permissions.
Foundry agents connect to Work IQ over the Agent-to-Agent (A2A) protocol using
On-Behalf-Of (OBO) delegated authentication so every request runs in the
context of the signed-in user and honors their Microsoft 365 permissions.

Why it exists as a lesson:
  The doc treats Work IQ as a distinct tool with its own connection type
  (`remote-a2a`), its own Entra app requirement (delegated `WorkIQAgent.Ask`
  scope with tenant-wide admin consent), its own billing model (Copilot
  Credits usage-based billing), and its own compliance boundary (data can
  leave the Foundry service boundary). It is not a generic MCP tool. It is
  not app-only. It is not free. Learn the config surface before invoking.

This lesson is preflight-only by design — even `--apply` does not send data to
Microsoft 365. Instead, `--apply` builds and prints the exact `PromptAgentDefinition`
payload with `WorkIQPreviewTool` you would pass to `agents.create_version` and
the equivalent `WorkIQPreviewToolboxTool` toolbox payload (the recommended path
per the doc). Actually creating either would require a working Work IQ
connection, delegated OBO context, and admin-consented Entra app — none of
which this repo provisions.

Code path:
  Preflight — print scope, prerequisites, RBAC, connection kind, tool payloads.
  --apply   — build the `WorkIQPreviewTool` / `WorkIQPreviewToolboxTool`
              objects and print the JSON payload the SDK would send. No agent
              or toolbox is created.

What to watch:
  `WORK_IQ_PROJECT_CONNECTION_ID` must be the fully qualified ARM resource ID
  of a `remote-a2a` project connection targeting `https://workiq.svc.cloud.microsoft/a2a/`
  and configured with the ingestion app's OAuth2 client credentials. `remote-tool`
  and `remote-mcp` connections do not satisfy Work IQ.

Prerequisites / env vars:
  PROJECT_ENDPOINT             — Foundry project endpoint
  DEFAULT_MODEL                — chat deployment used as PromptAgent model
  WORK_IQ_PROJECT_CONNECTION_ID — /subscriptions/.../connections/<work-iq-conn>
  AZURE_AI_AGENT_NAME          — optional; agent name shown in payload
"""
import argparse
import json
import os

from _shared.config import settings

DEFAULT_AGENT_NAME = "work-iq-preview-lab"
WORK_IQ_A2A_TARGET = "https://workiq.svc.cloud.microsoft/a2a/"
WORK_IQ_SCOPES = "api://workiq.svc.cloud.microsoft/WorkIQAgent.Ask offline_access"


def _work_iq_connection_id() -> str:
    return os.environ.get("WORK_IQ_PROJECT_CONNECTION_ID", "").strip()


def _agent_name() -> str:
    return os.environ.get("AZURE_AI_AGENT_NAME") or DEFAULT_AGENT_NAME


def preflight() -> None:
    s = settings()
    conn = _work_iq_connection_id() or "<WORK_IQ_PROJECT_CONNECTION_ID not set>"
    print("No cloud calls made. Work IQ is preview; connect only with admin approval.")
    print(f"Agent name (planned):   {_agent_name()}")
    print(f"Chat model deployment:  {s.default_model or '<DEFAULT_MODEL not set>'}")
    print(f"Project endpoint:       {s.project_endpoint or '<PROJECT_ENDPOINT not set>'}")
    print(f"Work IQ connection ID:  {conn}")
    print(f"Work IQ A2A target:     {WORK_IQ_A2A_TARGET}")
    print(f"Required OAuth scopes:  {WORK_IQ_SCOPES}")
    print()
    print("Required setup (once per tenant):")
    print("  - Global Admin provisions the Work IQ service principal (application id")
    print("    fdcc1f02-fc51-4226-8753-f668596af7f7) and grants delegated `WorkIQAgent.Ask`.")
    print("  - Register a single-tenant Entra app; add client secret; note tenant + client IDs.")
    print("  - Create a project connection of kind `remote-a2a` targeting the A2A endpoint,")
    print("    auth-type oauth2, with the app's client id/secret and the scopes above.")
    print("  - Add the Foundry-provided OAuth redirect URL back to the app registration.")
    print()
    print("RBAC (per doc):")
    print("  - Foundry User on the project for developer, agent runtime identity, and OAuth users.")
    print("  - Foundry Project Manager on the project to create the Work IQ connection.")
    print("  - Enable Copilot Credits billing; Work IQ API is usage-based, not free.")
    print()
    print("Compliance note: request data can leave the Foundry service boundary; end-to-end")
    print("residency depends on Copilot billing config and Foundry project region.")
    print("Application-only auth is NOT supported — delegated OBO only.")
    print()
    print("Run with --apply to build and print the SDK payloads (no agent is created).")


def apply() -> None:
    from azure.ai.projects.models import (
        PromptAgentDefinition,
        WorkIQPreviewTool,
        WorkIQPreviewToolboxTool,
    )

    s = settings()
    conn = _work_iq_connection_id()
    if not conn:
        raise SystemExit("Set WORK_IQ_PROJECT_CONNECTION_ID to the Work IQ project connection ID.")
    model = s.require("DEFAULT_MODEL")

    prompt_tool = WorkIQPreviewTool(project_connection_id=conn)
    prompt_definition = PromptAgentDefinition(
        model=model,
        instructions="Use the available WorkIQ tools to answer questions and perform tasks.",
        tools=[prompt_tool],
    )
    toolbox_tool = WorkIQPreviewToolboxTool(project_connection_id=conn)

    print("Prompt agent definition (would pass to agents.create_version):")
    print(json.dumps(prompt_definition.as_dict(), indent=2, default=str))
    print()
    print("Toolbox tool payload (would pass in toolboxes.create_version tools=[...]):")
    print(json.dumps(toolbox_tool.as_dict(), indent=2, default=str))
    print()
    print("No cloud call performed. Deleting either the prompt agent or toolbox version later")
    print(f"is the caller's responsibility. Agent name planned: {_agent_name()}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Work IQ tool preflight (preview).")
    parser.add_argument("--apply", action="store_true", help="Build and print SDK payloads.")
    args = parser.parse_args(argv)
    if not args.apply:
        preflight()
        return
    apply()


if __name__ == "__main__":
    main()
