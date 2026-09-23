# Run: uv run python 05-information-extraction/07_rag_prompt_agent.py
# Practice-question coverage: Q88.
"""Create the constrained Prompt Agent used by lesson 08's manual RAG orchestration.

This agent has NO Azure AI Search tool attached — the application (lesson 08) owns
retrieval. The agent's system prompt tells it to answer ONLY from supplied sources
and never invent policies, prices, or timelines. This is the "app owns retrieval"
pattern: explicit control of what the model sees vs lesson 20's managed Search tool.

Agents created here are versioned. Each run creates a new version. Clean up agent
versions in production to avoid accumulating stale versions.

Code path:
  project_client() → agents.create_version(agent_name, PromptAgentDefinition(model,
  instructions)) → print name and version.

What to watch. `Agent northwind-manual-rag-agent v<version> created.` If the agent
name already exists, a new version is added. Run lesson 08 after this to use it.

Prerequisites / env vars:
  PROJECT_ENDPOINT — Foundry project endpoint
  DEFAULT_MODEL    — deployed chat model (must exist in the project)
"""
from azure.ai.projects.models import PromptAgentDefinition

from _shared.config import settings
from _shared.foundry_client import project_client

AGENT_NAME = "northwind-manual-rag-agent"

_SYSTEM_PROMPT = """
You are a customer support assistant for Northwind Technology Services.

Answer the customer's question using ONLY the provided sources.
After your answer, cite the source URL you used.
If the sources do not contain the answer, say:
"I don't have that information in the available knowledge base."
Then suggest contacting support@northwind.com.

Never invent policies, prices, refund rules, or timelines.
"""


def main() -> None:
    client = project_client()
    agent = client.agents.create_version(
        agent_name=AGENT_NAME,
        definition=PromptAgentDefinition(
            model=settings().default_model,
            instructions=_SYSTEM_PROMPT,
        ),
    )
    print(f"Agent {agent.name} v{agent.version} created.")


if __name__ == "__main__":
    main()
