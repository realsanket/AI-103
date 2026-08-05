"""Local Microsoft Agent Framework agent backed by a Foundry model.

This lesson runs on your machine; it is not a hosted-agent deployment. It uses
`Agent` and `FoundryChatClient` to call a Foundry model. A hosted agent needs
its own documented packaging, deployment, and invocation path.
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
        client=chat_client,
        instructions=(
            "You are Northwind operations assistant. Be concise. "
            "If you need current info, ask the user for it — you have no tools yet."
        ),
    )
    result = await agent.run("Give me a one-line summary of Northwind's mission.")
    print(result.text)


def main() -> None:
    asyncio.run(_run())


if __name__ == "__main__":
    main()
