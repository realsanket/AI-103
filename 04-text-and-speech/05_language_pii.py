"""PII detection + redaction via Azure AI Language."""
from _shared.language_client import language_client


_DOCS = [
    "Hi, this is Sarah Chen from Acme Logistics. You can reach me at "
    "sarah.chen@acmelogistics.com or call 312-555-1234 regarding ticket TKT-1042.",
]


def main() -> None:
    client = language_client()
    response = client.recognize_pii_entities(_DOCS, language="en")
    for idx, doc in enumerate(r for r in response if not r.is_error):
        print(f"--- Document {idx + 1} ---")
        print(f"Redacted: {doc.redacted_text}")
        print("Entities:")
        for e in doc.entities:
            print(f"  [{e.category}] '{e.text}'  ({e.confidence_score:.2f})")
        print()


if __name__ == "__main__":
    main()
