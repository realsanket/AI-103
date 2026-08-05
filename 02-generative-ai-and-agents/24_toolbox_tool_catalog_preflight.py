"""Toolbox and tool catalog lab — publish a governed, versioned tool collection.

Run without flags for a no-cloud preflight. `--apply` creates one Toolbox version
containing web search and Toolbox tool search. Tool search reduces tool-definition
tokens for larger catalogs, but it doesn't make a tool safe or authorize access.

Before publishing, confirm target region and model support; grant Foundry User to
the developer and prompt-agent identity; limit every connection to its required
RBAC scope; and review tool owner, DPA, data residency, retention, telemetry,
auth, quotas, and costs. Web search can send prompt content outside your data
boundary. Never add secrets, personal data, or production instructions to it.

`--apply` is persistent. Record printed version, test it, then clean it up with:

    python 24_toolbox_tool_catalog_preflight.py --apply --delete-version <version>

Deleting a version can disrupt consumers. Confirm no agent depends on it first.
"""
import argparse

from azure.ai.projects.models import ToolSearchToolboxTool, WebSearchToolboxTool

from _shared.foundry_client import project_client

TOOLBOX_NAME = "northwind-tool-catalog-lab"


def catalog_tools() -> list:
    return [
        WebSearchToolboxTool(
            name="current-public-web",
            description="Search public web sources for current, non-sensitive information.",
        ),
        ToolSearchToolboxTool(
            description="Discover relevant curated tools without sending every definition to the model.",
        ),
    ]


def preflight() -> None:
    print("No cloud calls made.")
    print("Toolbox is governed catalog and versioned MCP endpoint; it is not an arbitrary MCP server.")
    print("Review each tool's owner, DPA, data boundary, RBAC, auth, region/model support, quotas, and cost.")
    print("Use --apply to publish; use --apply --delete-version <version> only after checking consumers.")


def apply(delete_version: str | None) -> None:
    client = project_client()
    if delete_version:
        client.toolboxes.delete_version(name=TOOLBOX_NAME, version=delete_version)
        print(f"Deleted Toolbox {TOOLBOX_NAME} version {delete_version}.")
        return
    version = client.toolboxes.create_version(
        name=TOOLBOX_NAME,
        description="Northwind lab catalog: public web research and catalog discovery.",
        tools=catalog_tools(),
    )
    print(f"Created Toolbox {version.name} version {version.version}.")
    print(f"Cleanup: --apply --delete-version {version.version}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Preflight or publish the Northwind Toolbox lab.")
    parser.add_argument("--apply", action="store_true", help="Make the requested persistent Toolbox change.")
    parser.add_argument("--delete-version", help="Delete this Toolbox version instead of creating one.")
    args = parser.parse_args(argv)
    if not args.apply:
        preflight()
        return
    apply(args.delete_version)


if __name__ == "__main__":
    main()
