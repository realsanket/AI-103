from azure.identity import AzureCliCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition

PROJECT_ENDPOINT = "https://foundry-dev-eus-01.services.ai.azure.com/api/projects/ai-103-project"

SYSTEM_PROMPT = """
You are a customer support assistant for CloudXeus Technology Services.

Answer the customer's question using ONLY the provided sources.

After your answer, cite the source URL you used.

If the sources do not contain the answer, say:
"I don't have that information in the available knowledge base."

Then suggest contacting support@cloudxeus.com.

Never invent policies, prices, refund rules, or timelines.
"""

project = AIProjectClient(
    endpoint=PROJECT_ENDPOINT,
    credential=AzureCliCredential()
)

agent = project.agents.create_version(
    agent_name="cloudxeus-support-rag-agent",
    definition=PromptAgentDefinition(
        model="gpt-5.4",
        instructions=SYSTEM_PROMPT,
    ),
)