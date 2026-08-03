"""Hosted Agent via Microsoft Agent Framework.

`agent-framework` gives you the `Agent` class + `FoundryChatClient`. Same code
runs locally and inside a Foundry-managed container — you don't rewrite the
loop when moving from dev to prod.
"""
import asyncio

from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from azure.identity import DefaultAzureCredential

from _shared.config import settings


async def _run() -> None:
    chat_client = FoundryChatClient(
        project_endpoint=settings().project_endpoint,
        model=settings().default_model,
        credential=DefaultAzureCredential(),
    )
    agent = Agent(
        chat_client=chat_client,
        instructions=(
            "You are CloudXeus operations assistant. Be concise. "
            "If you need current info, ask the user for it — you have no tools yet."
        ),
    )
    result = await agent.run("Give me a one-line summary of CloudXeus's mission.")
    print(result.messages[-1].content)


def main() -> None:
    asyncio.run(_run())


if __name__ == "__main__":
    main()
