# Run: uv run python 01-plan-and-manage/18_protected_material.py [--run]
# Practice-question coverage: Q40, Q103, Q107.
"""Detect protected material in model output with Azure AI Content Safety.

What: a GA Content Safety API that detects matching protected text in an LLM
completion. Why: an output safety control, not a copyright decision engine.
Use it on English output after generation; do not use it on user prompts or
short snippets. It requires a Content Safety resource and Cognitive Services
User role. The API accepts 110-10,000 characters.

Run with --run only after setting CONTENT_SAFETY_ENDPOINT. This sends synthetic
text to Azure and does not create persistent resource state.
"""
import argparse
import json

from azure.core.rest import HttpRequest

from _shared.content_safety_client import content_safety_client
from _shared.config import settings

_ORIGINAL_TEXT = (
    "Northwind support guidance is original training text. It explains that refund "
    "requests are reviewed against the charge date, subscription plan, and account "
    "history. Support staff should confirm the invoice, state the available options, "
    "and escalate exceptions without reproducing third-party source material."
)

# A longer, well-known copyrighted excerpt used as an intentionally detection-friendly
# example for the protected-material API. Keep it realistic and avoid shipping a
# production copy of a proprietary source in a lesson.
_PROTECTED_TEXT_EXAMPLE = (
    "Hey Jude, don't make it bad. Take a sad song and make it better. Remember to "
    "let her into your heart, then you can start to make it better. Hey Jude, don't "
    "be afraid. You were made to go out and get her. The minute you let her under "
    "your skin, then you begin to make it better."
)


def detect_protected_material(client, endpoint: str, text: str) -> dict:
    if not 110 <= len(text) <= 10_000:
        raise ValueError("Protected Material text must contain 110 to 10,000 characters.")
    request = HttpRequest(
        method="POST",
        url=f"{endpoint}/contentsafety/text:detectProtectedMaterial?api-version=2024-09-01",
        headers={"Content-Type": "application/json"},
        content=json.dumps({"text": text}).encode(),
    )
    return client.send_request(request).json()


def main(run: bool = False) -> None:
    if not run:
        print(
            "Preflight only. Re-run with --run to compare a safe synthetic completion "
            "against a known protected-material example."
        )
        return

    endpoint = settings().require("CONTENT_SAFETY_ENDPOINT")
    for label, sample in {
        "safe synthetic output": _ORIGINAL_TEXT,
        "known protected example": _PROTECTED_TEXT_EXAMPLE,
    }.items():
        result = detect_protected_material(content_safety_client(), endpoint, sample)
        print(f"{label}:", result["protectedMaterialAnalysis"]["detected"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true", help="Send synthetic output to Azure.")
    main(parser.parse_args().run)
