"""Language detection via Azure AI Language — primary language + confidence."""
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
    for idx, doc in enumerate(r for r in response if not r.is_error):
        primary = doc.primary_language
        print(f"--- Document {idx + 1}: \"{_DOCS[idx][:40]}...\" ---")
        print(f"  Language:   {primary.name} ({primary.iso6391_name})")
        print(f"  Confidence: {primary.confidence_score:.2f}\n")


if __name__ == "__main__":
    main()
