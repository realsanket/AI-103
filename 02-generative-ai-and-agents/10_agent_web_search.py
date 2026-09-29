# Run: uv run python 02-generative-ai-and-agents/10_agent_web_search.py

"""Prompt Agent with the built-in Web Search tool — real-time grounding.

Beginner note:
  Same tool as L04, but wrapped inside a registered Prompt Agent — the
  agent definition (model + instructions + tools) is stored in Foundry and
  callable by name from anywhere. Contrast with L04 where the tool is
  attached ad-hoc per Responses API call.

What to watch:
  Prints the agent id / name / version. Nothing to invoke here — L09 shows
  how to call a registered agent by name.

Web results are untrusted and public-search queries leave your application's
data boundary. Verify citations; do not include secrets or customer data.
Confirm DPA, retention, residency, RBAC, and query/model costs, then delete
unneeded agent versions.
"""
from azure.ai.projects.models import PromptAgentDefinition, WebSearchTool

from _shared.foundry_client import active_agent_reference, project_client
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

    reference = active_agent_reference(agent)
    openai = client.get_openai_client()
    response = openai.responses.create(
        input="What is the latest news about AI?",
        extra_body={"agent_reference": reference},
    )

    print("Agent invoked:")
    print(response.output_text)



if __name__ == "__main__":
    main()
