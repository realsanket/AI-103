from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
import json

endpoint = "https://foundry-dev-eus-01.services.ai.azure.com/api/projects/ai-103-project"
deployment_name = "gpt-5.4"

project = AIProjectClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential(),
)

openai = project.get_openai_client()

ticket_text = """
Subject: VPN disconnect issue - escalation needed

Hi team, this is Sarah Chen from Acme Logistics writing in again about
ticket TKT-1042. Our Gold-tier SLA promises a 4 hour response time, and
we are now at hour 6 with no update. The VPN client keeps dropping every
10 minutes on our Windows fleet since the rollout of CloudXeus Connect
v3.2 last Tuesday. If this isn't resolved by end of day Friday we will
be requesting the $500 SLA breach credit outlined in our contract.
"""

system_prompt = """
You are a text analysis engine for CloudXeus support tickets.
Read the ticket text and respond with ONLY a JSON object containing:
- "entities": a list of objects, each with "text" and "category"
  (categories: person, organization, date, product, ticket_id, sla_tier, monetary_amount)
- "topics": a list of short topic labels describing what the ticket is about

Respond with JSON only. Do not include any other text.
"""

extraction_schema = {
    "type": "object",
    "properties": {
        "entities": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The exact substring as it appears in the source text"
                    },
                    "category": {
                        "type": "string",
                        "enum": [
                            "person",
                            "organization",
                            "date",
                            "product",
                            "ticket_id",
                            "sla_tier",
                            "monetary_amount"
                        ]
                    }
                },
                "required": ["text", "category"],
                "additionalProperties": False
            }
        },
        "topics": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Short labels (2-4 words) describing what the text is about"
        }
    },
    "required": ["entities", "topics"],
    "additionalProperties": False
}

response = openai.responses.create(
    model=deployment_name,
    input=[
        {"type": "message", "role": "system", "content": system_prompt},
        {"type": "message", "role": "user", "content": ticket_text}
    ],
    text={
        "format": {
            "type": "json_schema",
            "name": "ticket_extraction",
            "schema": extraction_schema,
            "strict": True
        }
    }
)

result = json.loads(response.output_text)

print("=== Entities ===")
for entity in result["entities"]:
    print(f"  [{entity['category']}] {entity['text']} ")

print("\n=== Topics ===")
for topic in result["topics"]:
    print(f"  - {topic}")