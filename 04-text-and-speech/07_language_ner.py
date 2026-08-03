"""NER via Azure AI Language (prebuilt) — discriminative path.

Discriminative advantage: benchmarked confidence scores you can defend.
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
    for idx, doc in enumerate(r for r in response if not r.is_error):
        print(f"--- Document {idx + 1} — Prebuilt NER ---")
        for e in doc.entities:
            subcat = f" / {e.subcategory}" if e.subcategory else ""
            print(f"  [{e.category}{subcat}] '{e.text}'  ({e.confidence_score:.2f})")
        print()


if __name__ == "__main__":
    main()
