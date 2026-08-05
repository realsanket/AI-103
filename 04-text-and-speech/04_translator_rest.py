"""Translation via Azure Translator Text v3 REST.

Compare with `03_llm_translation.py` — Translator gives predictable
per-character pricing and huge language coverage; LLM gives better tone.
"""
from _shared.translator_client import translate


def main() -> None:
    text = (
        "Our VPN keeps dropping every 10 minutes since the last update. "
        "This is affecting our whole sales team."
    )
    result = translate(text, targets=["fr", "ja", "es"], source_language="en")
    for translation in result[0]["translations"]:
        print(f"[{translation['to']}] {translation['text']}")


if __name__ == "__main__":
    main()
