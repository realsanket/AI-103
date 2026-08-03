"""Create a Prompt Agent that answers strictly from AI Search results.

Companion `08_rag_client_run.py` runs the retrieval + calls the agent with
retrieved chunks stuffed into the prompt. (For the fully-managed alternative
where the agent has AI Search attached as a *tool* — see the Foundry portal.)
"""
from azure.ai.projects.models import PromptAgentDefinition

from _shared.config import settings
from _shared.foundry_client import project_client

AGENT_NAME = "cloudxeus-support-rag-agent"

_SYSTEM_PROMPT = """
You are a customer support assistant for CloudXeus Technology Services.

Answer the customer's question using ONLY the provided sources.
After your answer, cite the source URL you used.
If the sources do not contain the answer, say:
"I don't have that information in the available knowledge base."
Then suggest contacting support@cloudxeus.com.

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
