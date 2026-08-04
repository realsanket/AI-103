"""Prompt Agent with the built-in Web Search tool — real-time grounding.

Beginner note:
  Same tool as L04, but wrapped inside a registered Prompt Agent — the
  agent definition (model + instructions + tools) is stored in Foundry and
  callable by name from anywhere. Contrast with L04 where the tool is
  attached ad-hoc per Responses API call.

What to watch:
  Prints the agent id / name / version. Nothing to invoke here — L18 and
  the multi-agent lessons show how to consume the created agent.
"""
from azure.ai.projects.models import PromptAgentDefinition, WebSearchTool

from _shared.foundry_client import project_client
from _shared.config import settings

AGENT_NAME = "web-search-lab-agent"


def main() -> None:
    client = project_client()
    agent = client.agents.create_version(
        agent_name=AGENT_NAME,
        definition=PromptAgentDefinition(
            model=settings().default_model,
            instructions=(
                "You are a helpful assistant. Use web search to answer questions "
                "that require current information. Always cite sources."
            ),
            tools=[WebSearchTool()],
        ),
    )
    print("Agent created:")
    print(f"  ID      : {agent.id}")
    print(f"  Name    : {agent.name}")
    print(f"  Version : {agent.version}")


if __name__ == "__main__":
    main()
