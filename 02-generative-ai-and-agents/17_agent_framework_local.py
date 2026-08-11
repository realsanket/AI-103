# Run: uv run python 02-generative-ai-and-agents/17_agent_framework_local.py

"""Local Microsoft Agent Framework agent backed by a Foundry model.

Microsoft Agent Framework is a Python library for building agents that call
Foundry models. This lesson runs entirely on your machine — it is not deployed,
packaged, or hosted anywhere. The framework handles the async run loop; your
application supplies instructions and tools.

Agent Framework vs prompt agent vs hosted agent:
  This file   — local Python process, no cloud agent definition.
  Lesson 08   — prompt agent: stored versioned Foundry definition, project API.
  Lessons 28–30 — hosted agent: packaged runtime with deployment lifecycle.

Agent Framework natively integrates with Foundry tracing: when Application
Insights is connected to the project, traces appear in the Foundry portal
automatically — no additional instrumentation code is needed. Lesson 23
covers explicit tracing for LangChain/LangGraph, which do not have this
automatic integration.
"""
import asyncio

from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from azure.identity import DefaultAzureCredential

from _shared.config import settings


async def _run() -> None:
    chat_client = FoundryChatClient(
        project_endpoint=settings().require("PROJECT_ENDPOINT"),
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
