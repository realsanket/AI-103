# Run: uv run python 01-plan-and-manage/18_protected_material.py [--run]
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

_TEXT = (
    "Northwind support guidance is original training text. It explains that refund "
    "requests are reviewed against the charge date, subscription plan, and account "
    "history. Support staff should confirm the invoice, state the available options, "
    "and escalate exceptions without reproducing third-party source material."
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
        print("Preflight only. Re-run with --run to analyze synthetic English model output.")
        return

    result = detect_protected_material(
        content_safety_client(),
        settings().require("CONTENT_SAFETY_ENDPOINT"),
        _TEXT,
    )
    print(
        "protected material detected:",
        result["protectedMaterialAnalysis"]["detected"],
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true", help="Send synthetic output to Azure.")
    main(parser.parse_args().run)
