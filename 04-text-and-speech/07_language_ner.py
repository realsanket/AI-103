# Run: uv run python 04-text-and-speech/07_language_ner.py
"""NER via Azure AI Language (prebuilt) — fixed categories with confidence scores.

recognize_entities() is the discriminative counterpart to 01_llm_ner.py.
It returns fixed categories (Person, Organization, Location, DateTime, Quantity...)
with subcategories (Person/Employee, Location/City) and a numeric confidence score
per entity. Use when you need a documented fixed schema and auditable confidence
values. Use the LLM path (01) when you need novel categories the prebuilt model
doesn't know, like ticket_id or sla_tier.

Code path:
  language_client() → recognize_entities(_DOCS, language="en") → for each entity:
  print [Category / Subcategory] 'text' (confidence).

What to watch: Sarah Chen → [Person], Acme Logistics → [Organization], hour 6 →
[Quantity/Duration], Northwind Connect → [Product]. Subcategory is optional —
check for None. Confidence is a model signal, not a guarantee.

Prerequisites / env vars:
  LANGUAGE_ENDPOINT — Azure AI Language endpoint
"""
from _shared.language_client import language_client

_DOCS = [
    "Hi, this is Sarah Chen from Acme Logistics writing in again about "
    "ticket TKT-1042. Our Gold-tier SLA promises a 4 hour response time, "
    "and we are now at hour 6 with no update. The VPN client keeps "
    "dropping every 10 minutes on our Windows fleet since the rollout of "
    "Northwind Connect v3.2 last Tuesday. If this isn't resolved by end "
    "of day Friday we will be requesting the $500 SLA breach credit "
    "outlined in our contract.",
]


def main() -> None:
    client = language_client()
    response = client.recognize_entities(_DOCS, language="en")
    for idx, doc in enumerate(response):
        if doc.is_error:
            print(f"--- Document {idx + 1} failed: {doc.error.code} ---")
            continue
        print(f"--- Document {idx + 1} — Prebuilt NER ---")
        for e in doc.entities:
            subcat = f" / {e.subcategory}" if e.subcategory else ""
            print(f"  [{e.category}{subcat}] '{e.text}'  ({e.confidence_score:.2f})")
        print()


if __name__ == "__main__":
    main()
