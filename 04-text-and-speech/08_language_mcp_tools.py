"""List tools exposed by the Azure Language MCP server — dynamic discovery."""
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
