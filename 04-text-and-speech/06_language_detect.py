# Run: uv run python 04-text-and-speech/06_language_detect.py
"""Language detection via Azure AI Language — primary language + confidence score.

detect_language() is a routing primitive: detect first, then dispatch to the
right Language model, Translator locale, or summarizer. It returns a primary_language
with iso6391_name (2-letter code) and confidence_score. Short ambiguous text
("OK") gives low confidence — treat that as "unknown" in production rather than
routing on it. This is a read-only language identifier, not a translation service.

Code path:
  language_client() → detect_language(_DOCS) → for each doc: print language name,
  ISO code, and confidence.

What to watch: English ~0.99, French ~0.99, Japanese ~0.99, "OK" → ambiguous with
low confidence. The last doc intentionally shows the low-confidence case.

Prerequisites / env vars:
  LANGUAGE_ENDPOINT — Azure AI Language endpoint
"""
from _shared.language_client import language_client

_DOCS = [
    "Hi, this is Sarah Chen from Acme Logistics regarding ticket TKT-1042.",
    "Bonjour, je vous écris au sujet du ticket TKT-1042 concernant notre VPN.",
    "こんにちは、TKT-1042のチケットについてVPNの問題をご連絡しています。",
    "OK",
]


def main() -> None:
    client = language_client()
    response = client.detect_language(_DOCS)
    for idx, doc in enumerate(response):
        if doc.is_error:
            print(f"--- Document {idx + 1} failed: {doc.error.code} ---")
            continue
        primary = doc.primary_language
        print(f"--- Document {idx + 1}: \"{_DOCS[idx][:40]}...\" ---")
        print(f"  Language:   {primary.name} ({primary.iso6391_name})")
        print(f"  Confidence: {primary.confidence_score:.2f}\n")


if __name__ == "__main__":
    main()
