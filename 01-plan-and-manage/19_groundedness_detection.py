# Run: uv run python 01-plan-and-manage/19_groundedness_detection.py [--run]
# Practice-question coverage: Q19, Q26, Q34, Q69, Q103.
"""Detect unsupported claims in generated text with Content Safety Groundedness.

What: preview API that compares generated text with supplied grounding sources.
Why: find claims unsupported by retrieved or policy content. It does not prove
truth outside those sources. Use it after RAG or summarization; do not use it
as a replacement for retrieval authorization, human review, or an evaluator run.

Prerequisites: S0 Content Safety resource in a supported region, Cognitive
Services User, and CONTENT_SAFETY_ENDPOINT. Text and optional QnA query each
allow 7,500 characters; grounding sources allow 55,000 total characters.
Run with --run to make one non-persistent request using synthetic content.
"""
import argparse
import json

from azure.core.rest import HttpRequest

from _shared.content_safety_client import content_safety_client
from _shared.config import settings

_SOURCE = (
    "Northwind Pro subscribers can request a refund within 30 days of the charge "
    "date. Requests after 30 days are reviewed case by case by the billing team."
)
# This is intentionally unsupported relative to the source policy so the groundedness
# API has a clear claim to flag when run against Azure.
_SUPPORTED_TEXT = (
    "Northwind Pro subscribers can request a refund within 30 days of the charge date."
)
_UNSUPPORTED_TEXT = (
    "Northwind Pro subscribers always receive a refund within 60 days, regardless "
    "of the charge date or billing review."
)


def detect_groundedness(
    client, endpoint: str, text: str, grounding_sources: list[str]
) -> dict:
    if not text or len(text) > 7_500:
        raise ValueError("Groundedness text must contain at most 7,500 characters.")
    if not grounding_sources or sum(map(len, grounding_sources)) > 55_000:
        raise ValueError(
            "Groundedness requires sources totaling at most 55,000 characters."
        )

    body = {
        "domain": "Generic",
        "task": "Summarization",
        "text": text,
        "groundingSources": grounding_sources,
        "reasoning": False,
    }
    request = HttpRequest(
        method="POST",
        url=(
            f"{endpoint}/contentsafety/text:detectGroundedness"
            "?api-version=2024-09-15-preview"
        ),
        headers={"Content-Type": "application/json"},
        content=json.dumps(body).encode(),
    )
    return client.send_request(request).json()


def main(run: bool = False) -> None:
    if not run:
        print(
            "Preflight only. Re-run with --run to compare grounded vs unsupported "
            "claims against a synthetic policy source."
        )
        return

    endpoint = settings().require("CONTENT_SAFETY_ENDPOINT")
    for label, sample in {
        "grounded claim": _SUPPORTED_TEXT,
        "unsupported claim": _UNSUPPORTED_TEXT,
    }.items():
        result = detect_groundedness(content_safety_client(), endpoint, sample, [_SOURCE])
        print(f"{label}: ungrounded detected =", result["ungroundedDetected"])
        print(f"{label}: ungrounded percentage =", result["ungroundedPercentage"])
        for detail in result.get("ungroundedDetails", []):
            print(f"{label}: unsupported span =", detail["text"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true", help="Send synthetic text to Azure.")
    main(parser.parse_args().run)
