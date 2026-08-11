# Run: uv run python 04-text-and-speech/03_llm_translation.py
"""Translation via LLM prompt — preserves tone + register.

Azure Translator Text gives predictable per-character pricing and wide language
coverage, but produces flat literal output. This lesson demonstrates the LLM
alternative: instruct the model to preserve the urgency and register of the
original rather than word-for-word rendering. Compare with 04_translator_rest.py.

Code path:
  translate() builds a system prompt asking for tone-preserving translation into
  the target language. responses.create() returns SOURCE LANGUAGE + TRANSLATION
  formatted text. main() runs French and Japanese.

What to watch: the translated text should feel urgent, not bureaucratic. If it
sounds flat, the system prompt's "preserve tone" instruction isn't landing —
add a few-shot example or strengthen the register instruction.

Prerequisites / env vars:
  DEFAULT_MODEL — deployed chat model
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
