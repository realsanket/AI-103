# Run: uv run python 08-advanced-agents-other/23_microsoft_iq_tools_preflight.py
"""Compare Foundry IQ, Fabric IQ preview, and Work IQ preview.

These products all provide enterprise context but have different resources,
identities, networks, and licensing. Foundry IQ retrieves from an Azure AI
Search knowledge base through MCP. Fabric IQ connects Fabric ontology,
semantic-model, or data-agent assets. Work IQ uses delegated Microsoft 365 user
context and does not support app-only authentication.

Flows:
  Default - print a no-cloud decision and prerequisites.
  --kind fabric|work --connection-id ID - build the typed project-agent tool.

What to watch. Fabric IQ network isolation is partial. Work IQ is not supported
in network-isolated projects and requires tenant admin setup, delegated user
authorization, and applicable Microsoft 365 licensing/billing.

Prerequisites / env vars:
  FABRIC_IQ_CONNECTION_ID  - Foundry Fabric IQ project connection
  WORK_IQ_CONNECTION_ID    - Foundry Work IQ OAuth project connection
"""
import argparse
import os

from azure.ai.projects.models import FabricIQPreviewTool, WorkIQPreviewTool

from _shared.config import load_env


def iq_tool(kind: str, connection_id: str):
    if not connection_id:
        raise ValueError("Project connection ID is required.")
    if kind == "fabric":
        return FabricIQPreviewTool(
            project_connection_id=connection_id,
            require_approval="always",
        )
    if kind == "work":
        return WorkIQPreviewTool(project_connection_id=connection_id)
    raise ValueError("kind must be fabric or work.")


def main(argv: list[str] | None = None) -> None:
    load_env()
    parser = argparse.ArgumentParser(description="Build Fabric IQ or Work IQ tool configuration.")
    parser.add_argument("--kind", choices=("fabric", "work"))
    parser.add_argument("--connection-id")
    args = parser.parse_args(argv)
    print("No cloud calls made.")
    print("- Foundry IQ: Azure AI Search knowledge base via project-managed-identity MCP.")
    print("- Fabric IQ preview: Fabric item connection; network support is partial.")
    print("- Work IQ preview: delegated Microsoft 365 user only; no app-only auth.")
    print("- Work IQ is not supported in network-isolated Foundry projects.")
    print("- Foundry IQ permission trimming needs an explicit per-user query token.")
    if not args.kind:
        fabric = os.getenv("FABRIC_IQ_CONNECTION_ID")
        work = os.getenv("WORK_IQ_CONNECTION_ID")
        print(f"- FABRIC_IQ_CONNECTION_ID: {'configured' if fabric else 'missing'}")
        print(f"- WORK_IQ_CONNECTION_ID: {'configured' if work else 'missing'}")
        return
    connection_id = args.connection_id or os.getenv(
        "FABRIC_IQ_CONNECTION_ID" if args.kind == "fabric" else "WORK_IQ_CONNECTION_ID"
    )
    if not connection_id:
        parser.error(f"--kind {args.kind} requires --connection-id or matching env var.")
    print(f"- Tool payload: {iq_tool(args.kind, connection_id).as_dict()}")


if __name__ == "__main__":
    main()
