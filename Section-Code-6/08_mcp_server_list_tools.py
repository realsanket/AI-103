# pip install mcp
import asyncio
import httpx

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


FOUNDRY_RESOURCE_NAME = "foundry-dev-eus-01"

LANGUAGE_MCP_URL = (
    f"https://{FOUNDRY_RESOURCE_NAME}.cognitiveservices.azure.com"
    f"/language/mcp?api-version=2025-11-15-preview"
)

SUBSCRIPTION_KEY = ""


async def list_language_mcp_tools():
    headers = {
        "Ocp-Apim-Subscription-Key": SUBSCRIPTION_KEY
    }

    timeout = httpx.Timeout(
        timeout=30.0,
        read=300.0
    )

    async with httpx.AsyncClient(headers=headers, timeout=timeout) as http_client:
        async with streamable_http_client(
            url=LANGUAGE_MCP_URL,
            http_client=http_client,
            terminate_on_close=True,
        ) as (read_stream, write_stream, _):

            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()

                result = await session.list_tools()

                print(f"Found {len(result.tools)} tool(s) on the Azure Language MCP server:\n")

                for tool in result.tools:
                    print(f"• {tool.name}")
                    print(f"  {tool.description}")
                    print()


if __name__ == "__main__":
    asyncio.run(list_language_mcp_tools())