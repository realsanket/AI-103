# Run: uv run python 04-text-and-speech/02_llm_sentiment.py
"""Sentiment + tone via LLM prompt — per-topic breakdown with rationale.

Azure Language Sentiment returns structured labels (positive/negative/mixed) and,
with opinion mining, target+assessment pairs. The LLM path costs more but adds
free-form rationale and custom topic grouping in a single call. This lesson
shows when the generative path wins over the structured service. Compare with
20_language_sentiment.py for the structured alternative.

Code path:
  openai_client() → responses.create() with system instruction asking for per-topic
  sentiment + intensity + rationale + overall tone → output_text printed as prose.

What to watch: two or more concern blocks (SLA breach → frustrated; Marcus's help →
grateful) plus an overall tone assessment. If the model merges them, adjust the
system prompt to be more explicit about per-topic separation.

Prerequisites / env vars:
  DEFAULT_MODEL — deployed chat model
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
