"""Tune generation behavior — temperature knob.

Run twice mentally: temperature=0 → deterministic; temperature=2 → wild.
Same prompt, wildly different outputs — that's the parameter doing work.
"""
from _shared.openai_client import openai_client
from _shared.config import settings


def creative_tagline(temperature: float) -> str:
    client = openai_client()
    r = client.responses.create(
        model=settings().default_model,
        instructions="You are a creative copywriter.",
        input="Write a two-sentence tagline for a new AI-powered productivity app.",
        temperature=temperature,
    )
    return r.output_text


def main() -> None:
    for t in (0.0, 1.0, 2.0):
        print(f"\n--- temperature={t} ---")
        print(creative_tagline(t))


if __name__ == "__main__":
    main()
