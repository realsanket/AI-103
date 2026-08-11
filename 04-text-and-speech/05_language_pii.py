# Run: uv run python 04-text-and-speech/05_language_pii.py
"""PII detection + redaction via Azure AI Language — prebuilt categories only.

recognize_pii_entities() returns two things: (1) entity spans with category
(Person, Email, PhoneNumber...) and confidence score, and (2) redacted_text
with detected spans masked. This is a privacy signal, not a compliance
certification — missed detections and application-level handling remain your
responsibility. Does NOT cover conversation PII or document (native) PII.

Code path:
  language_client() → recognize_pii_entities(_DOCS, language="en") →
  for each doc: print redacted_text and each entity with category + confidence.

What to watch: Sarah Chen masked, email masked, phone number masked. The raw
redacted_text still contains the ticket ID — TKT-1042 is not a PII category.
That's expected: prebuilt categories are fixed and cannot be extended here.

Prerequisites / env vars:
  LANGUAGE_ENDPOINT — Azure AI Language endpoint (cognitiveservices.azure.com)
"""
from _shared.language_client import language_client


_DOCS = [
    "Hi, this is Sarah Chen from Acme Logistics. You can reach me at "
    "sarah.chen@acmelogistics.com or call 312-555-1234 regarding ticket TKT-1042.",
]


def main() -> None:
    client = language_client()
    response = client.recognize_pii_entities(_DOCS, language="en")
    for idx, doc in enumerate(response):
        if doc.is_error:
            print(f"--- Document {idx + 1} failed: {doc.error.code} ---")
            continue
        print(f"--- Document {idx + 1} ---")
        print(f"Redacted: {doc.redacted_text}")
        print("Entities:")
        for e in doc.entities:
            print(f"  [{e.category}] '{e.text}'  ({e.confidence_score:.2f})")
        print()


if __name__ == "__main__":
    main()
