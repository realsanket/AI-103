"""Create prompt agent used by this domain's manual RAG lesson.

This agent has no Azure AI Search tool. `08_rag_client_run.py` retrieves
chunks itself and supplies them in the prompt.
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
