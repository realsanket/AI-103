# Run: uv run python 08-advanced-agents-other/22_bing_grounding_preflight.py
"""Build Grounding with Bing tool definitions without calling Bing.

Grounding with Bing is distinct from the Responses Web Search tool. It uses a
Foundry project connection to a Bing resource. Standard Bing grounds on public
web results; Bing Custom Search preview restricts results to a configured
custom instance. Bing traffic uses public egress even for network-secured
Foundry projects.

Flows:
  Default - print prerequisites and missing configuration only.
  --connection-id - build and print the standard BingGroundingTool locally.
  --custom-instance - build BingCustomSearchPreviewTool instead.

What to watch. Python SDK uses the project connection ID in the typed tool.
Creating the Bing resource/connection needs separate reviewed roles and cost.

Prerequisites / env vars:
  BING_PROJECT_CONNECTION_ID  - Foundry project connection ID
  BING_CUSTOM_SEARCH_INSTANCE - optional custom configuration instance
"""
import argparse
import os

from azure.ai.projects.models import (
    BingCustomSearchConfiguration,
    BingCustomSearchPreviewTool,
    BingCustomSearchToolParameters,
    BingGroundingSearchConfiguration,
    BingGroundingSearchToolParameters,
    BingGroundingTool,
)


def bing_tool(connection_id: str, custom_instance: str | None = None):
    if not connection_id:
        raise ValueError("Bing project connection ID is required.")
    if custom_instance:
        return BingCustomSearchPreviewTool(
            bing_custom_search_preview=BingCustomSearchToolParameters(
                search_configurations=[
                    BingCustomSearchConfiguration(
                        project_connection_id=connection_id,
                        instance_name=custom_instance,
                    )
                ]
            )
        )
    return BingGroundingTool(
        bing_grounding=BingGroundingSearchToolParameters(
            search_configurations=[
                BingGroundingSearchConfiguration(
                    project_connection_id=connection_id,
                )
            ]
        )
    )


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Build Grounding with Bing tool configuration.")
    parser.add_argument(
        "--connection-id",
        default=os.getenv("BING_PROJECT_CONNECTION_ID"),
    )
    parser.add_argument(
        "--custom-instance",
        default=os.getenv("BING_CUSTOM_SEARCH_INSTANCE"),
    )
    args = parser.parse_args(argv)
    print("No cloud calls made.")
    print("- Bing grounding is billed and uses public egress.")
    print("- SDK uses connection ID; portal/SDK management can expose connection name.")
    print("- Roles: Foundry Project Manager for connections; Foundry User for agents.")
    print("- Network-secured Foundry does not make Bing traffic private.")
    if not args.connection_id:
        print("- Set BING_PROJECT_CONNECTION_ID to render a typed tool payload.")
        return
    tool = bing_tool(args.connection_id, args.custom_instance)
    print(f"- Tool payload: {tool.as_dict()}")


if __name__ == "__main__":
    main()
