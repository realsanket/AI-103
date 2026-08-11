# Run: uv run python 04-text-and-speech/01_llm_ner.py
"""Entity extraction via LLM prompt (generative path).

Azure Language NER covers fixed categories (Person, Organization, Location...).
When a ticket contains domain-specific concepts like ticket_id, sla_tier, or
monetary_amount, those categories don't exist in the prebuilt model. This lesson
shows the generative alternative: describe the categories you need in a system
prompt and let the LLM extract them. Compare with 07_language_ner.py which uses
the prebuilt discriminative path on the same ticket — exam expects you to know both.

Code path:
  openai_client() → responses.create() with system + user messages → output_text printed.
  output_text is intended to be JSON; parse it only after schema-validating.

What to watch: entities list should include Sarah Chen (person), Acme Logistics
(organization), TKT-1042 (ticket_id), Gold (sla_tier), $500 (monetary_amount).
If the model adds extra commentary, the system prompt's "JSON only" isn't working
— tighten it or add a response schema.

Prerequisites / env vars:
  DEFAULT_MODEL — deployed chat model (e.g., gpt-4o)
"""
from _shared.openai_client import openai_client
from _shared.config import settings

_TICKET = """
Subject: VPN disconnect issue - escalation needed

Hi team, this is Sarah Chen from Acme Logistics writing in again about
ticket TKT-1042. Our Gold-tier SLA promises a 4 hour response time, and
we are now at hour 6 with no update. The VPN client keeps dropping every
10 minutes on our Windows fleet since the rollout of Northwind Connect
v3.2 last Tuesday. If this isn't resolved by end of day Friday we will
be requesting the $500 SLA breach credit outlined in our contract.
"""

_SYSTEM = """
You are a text analysis engine for Northwind support tickets.
Read the ticket text and respond with ONLY a JSON object containing:
- "entities": list of objects with "text" and "category"
  (categories: person, organization, date, product, ticket_id, sla_tier, monetary_amount)
- "topics": list of short topic labels

Respond with JSON only. No other text.
"""


def main() -> None:
    client = openai_client()
    r = client.responses.create(
        model=settings().default_model,
        input=[
            {"type": "message", "role": "system", "content": _SYSTEM},
            {"type": "message", "role": "user", "content": _TICKET},
        ],
    )
    print(r.output_text)


if __name__ == "__main__":
    main()
