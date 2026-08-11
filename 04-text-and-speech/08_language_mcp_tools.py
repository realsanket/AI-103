# Run: uv run python 04-text-and-speech/08_language_mcp_tools.py
"""Discover tools exposed by the Azure Language MCP server (preview).

The Language MCP server exposes Language SDK capabilities (NER, PII, sentiment,
language detection, key phrases, summarization) as MCP tools that any
MCP-compatible agent or client can call. This lesson performs discovery only —
it lists tool names and descriptions without invoking a tool. See 09_language_mcp_agent.py
for attaching the MCP server to a Foundry Prompt Agent.

Code path:
  DefaultAzureCredential → Cognitive Services token → httpx.AsyncClient with Bearer header
  → streamable_http_client(language_mcp_url) → ClientSession.initialize() →
  list_tools() → print tool name + description.

What to watch: a list of MCP tools — NER, PII detection, sentiment analysis,
language detection. Tool names returned at runtime are authoritative; preview
contracts can change.

Prerequisites / env vars:
  LANGUAGE_MCP_URL — https://<resource>.cognitiveservices.azure.com/language/mcp?api-version=...
"""
import asyncio

import httpx
from azure.identity import DefaultAzureCredential
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

from _shared.config import settings

_SCOPE = "https://cognitiveservices.azure.com/.default"


async def _list_tools() -> None:
    token = DefaultAzureCredential().get_token(_SCOPE).token
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(headers=headers, timeout=httpx.Timeout(30.0, read=300.0)) as http:
        async with streamable_http_client(
            url=settings().language_mcp_url,
            http_client=http,
            terminate_on_close=True,
        ) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.list_tools()
                print(f"Found {len(result.tools)} tool(s) on the Azure Language MCP server:\n")
                for t in result.tools:
                    print(f"• {t.name}")
                    print(f"  {t.description}\n")


def main() -> None:
    asyncio.run(_list_tools())


if __name__ == "__main__":
    main()
