# Run: uv run python 04-text-and-speech/questions/01_mixed_language_translation_routing.py
"""Question supplement: route single-language transcript segments to Translator.

Maps PDF question 57. Speech recognition or Language detection must establish
the language label before this local routing step. The module intentionally
does not guess language from text and never sends transcript content remotely.
"""
from __future__ import annotations

from collections import defaultdict


def translator_batches(segments: list[dict[str, str]]) -> dict[str, list[str]]:
    batches: dict[str, list[str]] = defaultdict(list)
    for segment in segments:
        language = segment.get("language", "").strip().lower()
        text = segment.get("text", "").strip()
        if not language or language == "mixed":
            raise ValueError("Each segment needs one resolved language before translation.")
        if not text:
            raise ValueError("Transcript segments must not be blank.")
        batches[language].append(text)
    return dict(batches)


def main() -> None:
    print("No cloud calls made. Translator batches:")
    print(translator_batches([
        {"language": "en", "text": "Your case is open."},
        {"language": "es", "text": "El caso sigue abierto."},
    ]))


if __name__ == "__main__":
    main()
