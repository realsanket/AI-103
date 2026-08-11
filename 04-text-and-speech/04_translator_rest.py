# Run: uv run python 04-text-and-speech/04_translator_rest.py
"""Text Translation via Azure Translator Text v3 REST — multiple target languages.

Azure Translator is a separate REST service from Azure Language. One POST to the
global /translate endpoint returns translations into multiple target languages
simultaneously. It does NOT do document translation (that's the Document Translation
API), glossary, or idiom-aware rendering. Compare with 03_llm_translation.py.

Code path:
  translate() in _shared/translator_client.py sends [{"Text": text}] to global
  /translate?api-version=3.0 with repeated `to` params and Ocp-Apim-ResourceId
  header. result[0]["translations"] is a list; each item has "to" and "text".

What to watch: three lines, one per target language code. The "to" key is the
language code, not "language". If you see 401, check TRANSLATOR_RESOURCE_ID is
the full ARM resource path and that the calling identity has the documented role.

Prerequisites / env vars:
  TRANSLATOR_RESOURCE_ID — full ARM ID of the Translator resource
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
