# Run: uv run python 02-generative-ai-and-agents/26_toolbox_tool_catalog_preflight.py

"""Create, inspect, and call a governed, versioned Foundry Toolbox.

Run without flags for a no-cloud preflight. `--apply` creates one Toolbox version
containing web search and Toolbox tool search. Tool search reduces tool-definition
tokens for larger catalogs, but it doesn't make a tool safe or authorize access.
This two-tool lab includes Tool Search only to demonstrate its contract; small
production catalogs normally expose their few tools directly.

`--invoke --toolbox-version VERSION` connects a local Agent Framework agent to
that exact version's MCP developer endpoint. `--use-default-version` explicitly
chooses the mutable consumer endpoint instead. The MCP client gets a fresh Entra
token for the `https://ai.azure.com/.default` scope on each HTTP request. The
model can discover and invoke toolbox tools, so prompts must contain only data
approved for every tool the catalog exposes.

Before publishing, confirm target region and model support; grant Foundry User to
the developer and prompt-agent identity; limit every connection to its required
RBAC scope; and review tool owner, DPA, data residency, retention, telemetry,
auth, quotas, and costs. Web search can send prompt content outside your data
boundary. Never add secrets, personal data, or production instructions to it.

`--apply` is persistent. Record printed version, test it, then clean it up with:

    uv run python 02-generative-ai-and-agents/26_toolbox_tool_catalog_preflight.py \
      --apply --delete-version <version>

Deleting a version can disrupt consumers. Confirm no agent depends on it first.

Code paths:
  Preflight — explain build, version, endpoint, authentication, and cleanup.
  --apply — create an immutable Toolbox version and print consumer/developer URLs.
  --invoke --toolbox-version — attach the versioned MCP endpoint to an ephemeral
  local Agent Framework agent, run one model request, then close all clients.
  --invoke --use-default-version — call the current default via consumer endpoint.
  --apply --delete-version — delete an exact version after consumer review.

Prerequisites / env vars:
  PROJECT_ENDPOINT      — Foundry project endpoint containing /api/projects/
  DEFAULT_MODEL         — chat-capable deployment alias for FoundryChatClient
  FOUNDRY_TOOLBOX_NAME  — optional override; defaults to the Northwind lab name
  --toolbox-version     — exact immutable version to test before promotion
  --use-default-version — explicitly follow the Toolbox default version
  --invoke              — perform the billable model/tool call
"""
import argparse
import asyncio
import os

import httpx
from agent_framework import MCPStreamableHTTPTool
from agent_framework.foundry import FoundryChatClient
from azure.ai.projects.models import ToolSearchToolboxTool, WebSearchToolboxTool
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

from _shared.config import settings
from _shared.foundry_client import project_client

DEFAULT_TOOLBOX_NAME = "northwind-tool-catalog-lab"
TOKEN_SCOPE = "https://ai.azure.com/.default"


class _ToolboxAuth(httpx.Auth):
    """Add a freshly acquired Foundry bearer token to each MCP request."""

    def __init__(self, token_provider):
        self._token_provider = token_provider

    def auth_flow(self, request):
        request.headers["Authorization"] = f"Bearer {self._token_provider()}"
        yield request


def toolbox_name() -> str:
    return os.getenv("FOUNDRY_TOOLBOX_NAME") or DEFAULT_TOOLBOX_NAME


def toolbox_mcp_url(
    project_endpoint: str,
    name: str,
    version: str | None = None,
) -> str:
    base = f"{project_endpoint.rstrip('/')}/toolboxes/{name}"
    if version:
        return f"{base}/versions/{version}/mcp?api-version=v1"
    return f"{base}/mcp?api-version=v1"


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
    print(f"Toolbox name: {toolbox_name()}")
    print("Build: --apply creates an immutable version; the first version becomes default.")
    print("Test: --invoke --toolbox-version VERSION uses the exact developer endpoint.")
    print("Consume: --invoke --use-default-version explicitly follows the mutable default.")
    print(f"Authentication: fresh Entra bearer token per MCP request; scope={TOKEN_SCOPE}")
    print("Runtime: local Agent Framework agent; no prompt/hosted agent resource is persisted.")
    print("Review each tool's owner, DPA, data boundary, RBAC, auth, region/model support, quotas, and cost.")
    print("Use --apply to publish; invoke only with approved non-sensitive prompts.")
    print("Use --apply --delete-version VERSION only after checking all consumers.")


def apply(delete_version: str | None) -> str | None:
    client = project_client()
    name = toolbox_name()
    if delete_version:
        client.toolboxes.delete_version(name=name, version=delete_version)
        print(f"Deleted Toolbox {name} version {delete_version}.")
        return None
    version = client.toolboxes.create_version(
        name=name,
        description="Northwind lab catalog: public web research and catalog discovery.",
        tools=catalog_tools(),
    )
    print(f"Created Toolbox {version.name} version {version.version}.")
    current = settings()
    if current.project_endpoint:
        print(
            "Developer endpoint: "
            f"{toolbox_mcp_url(current.project_endpoint, version.name, version.version)}"
        )
        print(
            "Consumer endpoint: "
            f"{toolbox_mcp_url(current.project_endpoint, version.name)}"
        )
    print(f"Cleanup: --apply --delete-version {version.version}")
    return str(version.version)


async def invoke_toolbox(version: str | None, prompt: str) -> None:
    """Run one local Agent Framework request through a Toolbox MCP endpoint."""
    current = settings()
    endpoint = current.require("PROJECT_ENDPOINT")
    model = current.require("DEFAULT_MODEL")
    name = toolbox_name()
    url = toolbox_mcp_url(endpoint, name, version)

    credential = DefaultAzureCredential()
    token_provider = get_bearer_token_provider(credential, TOKEN_SCOPE)
    http_client: httpx.AsyncClient | None = None
    toolbox: MCPStreamableHTTPTool | None = None
    try:
        http_client = httpx.AsyncClient(
            auth=_ToolboxAuth(token_provider),
            timeout=120.0,
        )
        toolbox = MCPStreamableHTTPTool(
            name=name,
            url=url,
            http_client=http_client,
            load_prompts=False,
        )
        chat_client = FoundryChatClient(
            project_endpoint=endpoint,
            model=model,
            credential=credential,
        )
        agent = chat_client.as_agent(
            name="toolbox-agent",
            instructions=(
                "You are a concise assistant connected to a governed Foundry Toolbox. "
                "Use only tools needed for the request. Never claim a tool ran unless "
                "you received its result."
            ),
            tools=[toolbox],
        )
        endpoint_type = "developer (pinned version)" if version else "consumer (default version)"
        print(f"Toolbox {endpoint_type} endpoint: {url}")
        print(f"Model deployment: {model}")
        response = await agent.run(prompt)
        print("Agent response:")
        print(response.text)
    finally:
        try:
            if toolbox is not None:
                await toolbox.close()
        finally:
            try:
                if http_client is not None:
                    await http_client.aclose()
            finally:
                credential.close()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Preflight or publish the Northwind Toolbox lab.")
    parser.add_argument("--apply", action="store_true", help="Make the requested persistent Toolbox change.")
    parser.add_argument("--delete-version", help="Delete this Toolbox version instead of creating one.")
    parser.add_argument(
        "--invoke",
        action="store_true",
        help="Run one local Agent Framework request through a Toolbox version.",
    )
    endpoint_group = parser.add_mutually_exclusive_group()
    endpoint_group.add_argument(
        "--toolbox-version",
        help="Exact Toolbox version for --invoke; tests the developer endpoint.",
    )
    endpoint_group.add_argument(
        "--use-default-version",
        action="store_true",
        help="Use the consumer endpoint and follow the current default version.",
    )
    parser.add_argument(
        "--prompt",
        default="What tools are available? Explain what each one is for.",
        help="Approved non-sensitive prompt passed to the local agent.",
    )
    args = parser.parse_args(argv)
    if args.delete_version and not args.apply:
        parser.error("--delete-version requires --apply.")
    if args.delete_version and args.invoke:
        parser.error("--delete-version cannot be combined with --invoke.")
    if args.apply and args.use_default_version:
        parser.error(
            "--apply --invoke must test the created version; "
            "do not combine --apply with --use-default-version."
        )
    if not args.apply and not args.invoke:
        preflight()
        return

    created_version = apply(args.delete_version) if args.apply else None
    if args.invoke:
        version = None if args.use_default_version else args.toolbox_version or created_version
        if not version and not args.use_default_version:
            parser.error(
                "--invoke requires --toolbox-version, --use-default-version, "
                "or --apply."
            )
        asyncio.run(invoke_toolbox(version, args.prompt))


if __name__ == "__main__":
    main()
