"""Prompt Shields — indirect (document) prompt injection via OCR text.

The user's message is harmless. The attached "OCR extract" contains hidden
instructions the model must NOT follow — that's the textbook case for Prompt
Shields for Documents (+ Spotlighting).

Set `content_filters.prompt_shields.mode = "block"` on your project to see
the shield fire; otherwise you'll see the model's own refusal.
"""
from pathlib import Path

from _shared.foundry_client import project_client

AGENT_NAME = "cloudxeus-support"

_OCR_TEXT = Path(__file__).parent / "data" / "malicious_ocr_sample.txt"

_USER_PROMPT = (
    "I attached an OCR extract of an error screenshot. What does the error mean "
    "and what should I do?"
)


def main() -> None:
    project = project_client()
    openai = project.get_openai_client()
    r = openai.responses.create(
        extra_body={"agent_reference": {"type": "agent_reference", "name": AGENT_NAME}},
        input=(
            f"{_USER_PROMPT}\n\n--- OCR extract ---\n{_OCR_TEXT.read_text()}"
        ),
    )
    print("=== Model output ===")
    print(r.output_text)
    filters = getattr(r, "model_extra", {}).get("content_filters") if hasattr(r, "model_extra") else None
    if filters:
        print("\n=== Prompt Shield filters (document attack channel) ===")
        print(filters)


if __name__ == "__main__":
    main()
