"""Structured JSON output — Responses API `text.format` with `json_schema` + `strict=True`.

Plain "respond in JSON" is advisory. `strict=True` constrains the token sampler
so the response is mechanically guaranteed to match the schema — that's what
makes generative extraction production-grade instead of best-effort.
"""
import json

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
Read the ticket text and return the requested structured extraction.
"""

_SCHEMA = {
    "type": "object",
    "properties": {
        "entities": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "category": {
                        "type": "string",
                        "enum": [
                            "person", "organization", "date", "product",
                            "ticket_id", "sla_tier", "monetary_amount",
                        ],
                    },
                },
                "required": ["text", "category"],
                "additionalProperties": False,
            },
        },
        "topics": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["entities", "topics"],
    "additionalProperties": False,
}


def main() -> None:
    client = openai_client()
    r = client.responses.create(
        model=settings().default_model,
        input=[
            {"type": "message", "role": "system", "content": _SYSTEM},
            {"type": "message", "role": "user", "content": _TICKET},
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "ticket_extraction",
                "schema": _SCHEMA,
                "strict": True,
            }
        },
    )
    result = json.loads(r.output_text)
    print("=== Entities ===")
    for e in result["entities"]:
        print(f"  [{e['category']}] {e['text']}")
    print("\n=== Topics ===")
    for t in result["topics"]:
        print(f"  - {t}")


if __name__ == "__main__":
    main()
