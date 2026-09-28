# Run: uv run python 08-advanced-agents-other/26_enterprise_data_tools_preflight.py
"""Build preview Fabric data-agent and SharePoint agent-tool definitions.

Both tools retrieve enterprise data with delegated user context, but their
resources and constraints differ. Fabric data agent requires the same tenant
and region, READ permission on the agent and its sources, and does not support a
service principal. SharePoint requires delegated user access, permission
trimming, applicable Microsoft 365 licensing/billing, and only one SharePoint
tool per agent.

Flows:
  Default - print identity, tenant, data, and permission-trimming checklist.
  --kind fabric|sharepoint --connection-id ID - build typed SDK payload locally.

What to watch. A successful connection does not prove security trimming. Test
with one document the user can read and one the user cannot read.

Prerequisites / env vars:
  FABRIC_DATA_AGENT_CONNECTION_ID  - Foundry connection to Fabric data agent
  SHAREPOINT_CONNECTION_ID         - Foundry SharePoint delegated-user connection
"""
import argparse
import os

from azure.ai.projects.models import (
    FabricDataAgentToolParameters,
    MicrosoftFabricPreviewTool,
    SharepointGroundingToolParameters,
    SharepointPreviewTool,
    ToolProjectConnection,
)

from _shared.config import load_env


def enterprise_tool(kind: str, connection_id: str):
    if not connection_id:
        raise ValueError("Project connection ID is required.")
    connection = ToolProjectConnection(project_connection_id=connection_id)
    if kind == "fabric":
        return MicrosoftFabricPreviewTool(
            fabric_dataagent_preview=FabricDataAgentToolParameters(
                project_connections=[connection]
            )
        )
    if kind == "sharepoint":
        return SharepointPreviewTool(
            sharepoint_grounding_preview=SharepointGroundingToolParameters(
                project_connections=[connection]
            )
        )
    raise ValueError("kind must be fabric or sharepoint.")


def main(argv: list[str] | None = None) -> None:
    load_env()
    parser = argparse.ArgumentParser(description="Build enterprise-data tool definitions.")
    parser.add_argument("--kind", choices=("fabric", "sharepoint"))
    parser.add_argument("--connection-id")
    args = parser.parse_args(argv)
    print("No cloud calls made.")
    print("- Both tools are preview and require delegated user context.")
    print("- Fabric: same tenant/region; READ on data agent and underlying sources.")
    print("- Fabric data agent does not support service-principal authentication.")
    print("- SharePoint: one tool per agent; not supported in Teams in current docs.")
    print("- Test permission trimming with readable and unreadable content.")
    if not args.kind:
        print(
            "- FABRIC_DATA_AGENT_CONNECTION_ID: "
            f"{'configured' if os.getenv('FABRIC_DATA_AGENT_CONNECTION_ID') else 'missing'}"
        )
        print(
            "- SHAREPOINT_CONNECTION_ID: "
            f"{'configured' if os.getenv('SHAREPOINT_CONNECTION_ID') else 'missing'}"
        )
        return
    variable = (
        "FABRIC_DATA_AGENT_CONNECTION_ID"
        if args.kind == "fabric"
        else "SHAREPOINT_CONNECTION_ID"
    )
    connection_id = args.connection_id or os.getenv(variable)
    if not connection_id:
        parser.error(f"--kind {args.kind} requires --connection-id or {variable}.")
    print(f"- Tool payload: {enterprise_tool(args.kind, connection_id).as_dict()}")


if __name__ == "__main__":
    main()
