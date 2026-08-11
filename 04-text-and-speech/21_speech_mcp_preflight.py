# Run: uv run python 04-text-and-speech/21_speech_mcp_preflight.py [--run]
"""Discover trusted Azure Speech MCP tools only after explicit opt-in.

Run with no flags for a local preflight. `--run` connects to the configured
remote server and lists its tools; it does not invoke a tool. Set
`SPEECH_MCP_URL` to the HTTPS Speech MCP endpoint, including its documented
API version. Authentication uses Microsoft Entra through
`DefaultAzureCredential`; never put a bearer token in source or an MCP URL.

Treat an MCP server as an external data boundary: allow-list needed tools,
require human approval before tool calls, and review its retention, region,
network reachability, and logs. See Azure Speech MCP documentation before
using preview endpoints in production.
"""
import argparse
import asyncio
from urllib.parse import parse_qs, urlsplit

import httpx
from azure.identity import DefaultAzureCredential
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

from _shared.config import settings

_SCOPE = "https://cognitiveservices.azure.com/.default"


def speech_mcp_url(url: str) -> str:
    """Validate a remote MCP endpoint without contacting it."""
    parsed = urlsplit(url)
    if parsed.scheme != "https" or not parsed.hostname:
        raise SystemExit("SPEECH_MCP_URL must be a valid HTTPS URL.")
    if parsed.hostname in {"localhost", "127.0.0.1", "::1"}:
        raise SystemExit("Speech MCP endpoint must not use localhost.")
    if not parse_qs(parsed.query).get("api-version"):
        raise SystemExit("SPEECH_MCP_URL must include its documented api-version query parameter.")
    return url


def preflight() -> None:
    configured = bool(settings().speech_mcp_url)
    print("Speech MCP preflight. No cloud calls made.")
    print(f"- speech_mcp_url: {'configured' if configured else 'missing'}")
    print("Use Microsoft Entra (Cognitive Services User), HTTPS, least-privilege tools, and approval.")
    print("Run with --run only after reviewing server ownership, data handling, tool schemas, and cost.")


async def list_tools(url: str) -> None:
    token = DefaultAzureCredential().get_token(_SCOPE).token
    headers = {"Authorization": "Bearer " + token}
    async with httpx.AsyncClient(headers=headers, timeout=httpx.Timeout(30.0, read=300.0)) as http:
        async with streamable_http_client(
            url=url, http_client=http, terminate_on_close=True
        ) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.list_tools()
    print(f"Discovered {len(result.tools)} Speech MCP tool(s); none invoked.")
    for tool in result.tools:
        print(f"- {tool.name}: {tool.description}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Preflight or list Azure Speech MCP tools.")
    parser.add_argument("--run", action="store_true", help="Connect and list tools; no tool is invoked.")
    parser.add_argument("--endpoint", help="Override SPEECH_MCP_URL for this run.")
    args = parser.parse_args(argv)
    if not args.run:
        preflight()
        return
    asyncio.run(list_tools(speech_mcp_url(args.endpoint or settings().speech_mcp_url)))


if __name__ == "__main__":
    main()
