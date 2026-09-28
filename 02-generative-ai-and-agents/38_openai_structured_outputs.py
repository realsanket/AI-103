# Run: uv run python 02-generative-ai-and-agents/38_openai_structured_outputs.py
"""Extract a typed Python object from model output using Pydantic structured outputs.

Structured outputs (chat.completions.parse) let you define a Pydantic schema and
receive a typed Python object directly — no JSON parsing, no field validation. The
difference from json_schema mode (lesson 32, Responses API): this uses the Chat
Completions API endpoint with response_format=<PydanticModel>, returns
completion.choices[0].message.parsed, and requires pydantic.

This is NOT lesson 07 (Responses API json_schema + strict=True) and NOT lesson 32
(json_schema mode via responses.create). All three enforce schema but at different
API layers and return different result shapes.

Flows:
  Default / --apply  Extract a CalendarEvent from a natural-language sentence.

What to watch in the output:
  parsed.name, parsed.date, parsed.participants — all populated as Python objects.
  refusal: if model refuses extraction, message.refusal is set instead of parsed.

Prerequisites / env vars:
  AZURE_OPENAI_ENDPOINT  — https://<resource>.openai.azure.com
  DEFAULT_MODEL          — deployment that supports structured outputs (GPT-4.1 or newer)
  --apply                — call the live API (default: dry-run prints schema only)
"""

import argparse
import sys

from _shared.config import settings
from _shared.openai_client import openai_client


def preflight() -> None:
    try:
        from pydantic import BaseModel  # noqa: F401
        print("[OK] pydantic available")
    except ImportError:
        print("[WARN] pydantic not installed — run: uv add pydantic")
    try:
        from openai import OpenAI  # noqa: F401
        print("[OK] openai SDK available")
    except ImportError:
        print("[FAIL] openai not installed")
        sys.exit(1)
    print()
    print("Schema that would be sent:")
    print("  class CalendarEvent(BaseModel):")
    print("      name: str")
    print("      date: str")
    print("      participants: list[str]")
    print()
    print("API: client.chat.completions.parse(model=DEFAULT_MODEL, messages=..., response_format=CalendarEvent)")
    print("Result: completion.choices[0].message.parsed  →  CalendarEvent instance")
    print()
    print("Key difference from lesson 07 / lesson 32:")
    print("  Lesson 07 — Responses API, json_schema + strict=True, returns dict via json.loads()")
    print("  Lesson 32 — Responses API, json_schema mode, returns dict via json.loads()")
    print("  Lesson 38 — Chat Completions API, parse(), returns typed Pydantic object")


def apply() -> None:
    from pydantic import BaseModel

    class CalendarEvent(BaseModel):
        name: str
        date: str
        participants: list[str]

    client = openai_client()
    deployment = settings().default_model

    sentence = "Alice and Bob are going to a science fair on Friday."
    print(f"Input: {sentence!r}")

    completion = client.chat.completions.parse(
        model=deployment,
        messages=[
            {"role": "system", "content": "Extract the event information."},
            {"role": "user", "content": sentence},
        ],
        response_format=CalendarEvent,
    )

    msg = completion.choices[0].message
    if msg.refusal:
        print(f"[REFUSAL] model refused: {msg.refusal}")
        return

    event = msg.parsed
    print(f"name:         {event.name}")
    print(f"date:         {event.date}")
    print(f"participants: {event.participants}")
    print()
    print("finish_reason:", completion.choices[0].finish_reason)
    print("usage:", completion.usage)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if args.apply:
        apply()
    else:
        preflight()


if __name__ == "__main__":
    main()
