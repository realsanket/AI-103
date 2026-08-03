"""Translation via LLM prompt — preserves tone + register.

Compare with `04_translator_rest.py` — Translator has better language coverage
and glossary support; LLM keeps idiom + tone better.
"""
from _shared.openai_client import openai_client
from _shared.config import settings

_SOURCE = """
Hi team, our VPN keeps dropping every 10 minutes since the last update.
This is affecting our whole sales team and we need this fixed today.
"""


def translate(text: str, target_language: str) -> str:
    client = openai_client()
    system_prompt = f"""
You are a professional translator. Translate the user's text into
{target_language}. Preserve the original line breaks and formatting.
Preserve the tone and register of the original (formal, urgent, casual)
rather than producing a flat literal translation.

Respond in exactly this format, no extra commentary:

SOURCE LANGUAGE: <detected source language>
TRANSLATION: <the translated text>
"""
    r = client.responses.create(
        model=settings().default_model,
        input=[
            {"type": "message", "role": "system", "content": system_prompt},
            {"type": "message", "role": "user", "content": text},
        ],
    )
    return r.output_text


def main() -> None:
    for target in ("French", "Japanese"):
        print(f"--- Translating to {target} ---")
        print(translate(_SOURCE, target))
        print()


if __name__ == "__main__":
    main()
