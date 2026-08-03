"""Sentiment + tone via LLM prompt — per-topic + overall."""
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

That said, I do want to say thank you to Marcus on your team who called
me yesterday and was incredibly helpful in walking through workarounds.
"""

_SYSTEM = """
You are a sentiment and tone analysis engine for Northwind support tickets.
Identify each distinct concern or topic raised in the text, and for each one
report the sentiment, an intensity score, and a short rationale.
Separately, assess the overall tone of the message as a whole.
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
