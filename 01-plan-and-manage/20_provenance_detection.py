# Run: uv run python 01-plan-and-manage/20_provenance_detection.py [--run]
# Practice-question coverage: Q59, Q63.
"""Detect C2PA or watermark provenance in media stored in Azure Blob Storage.

What: preview asynchronous Content Safety operation that checks a media URI for
provenance markers. Why: establish content-origin signals before a workflow
trusts generated media. It does not establish ownership, authenticity, or a
complete moderation decision.

Prerequisites: Content Safety resource, Cognitive Services User for caller,
and Storage Blob Data Reader for the Content Safety resource's managed
identity on the Blob account. Set PROVENANCE_SOURCE_URL to an HTTPS Blob or
SAS URI. Run with --run; this creates no resource but sends the URI to Azure.
"""
import argparse
import json
import time

from azure.core.rest import HttpRequest

from _shared.content_safety_client import content_safety_client
from _shared.config import settings

_API_VERSION = "2026-07-01-preview"


def submit_detection(client, endpoint: str, source_uri: str) -> str:
    if not source_uri.startswith("https://"):
        raise ValueError("PROVENANCE_SOURCE_URL must be an HTTPS Blob or SAS URI.")
    request = HttpRequest(
        method="POST",
        url=f"{endpoint}/contentsafety/provenance/operations:detect?api-version={_API_VERSION}",
        headers={"Content-Type": "application/json"},
        content=json.dumps({"content": {"uri": source_uri}}).encode(),
    )
    operation = client.send_request(request).json()
    if not operation.get("id"):
        raise RuntimeError(f"Provenance operation did not return an id: {operation}")
    return operation["id"]


def get_detection(client, endpoint: str, operation_id: str) -> dict:
    request = HttpRequest(
        method="GET",
        url=(
            f"{endpoint}/contentsafety/provenance/operations/{operation_id}"
            f"?api-version={_API_VERSION}"
        ),
    )
    return client.send_request(request).json()


def main(run: bool = False) -> None:
    if not run:
        print(
            "Preflight only. Set PROVENANCE_SOURCE_URL and re-run with --run to "
            "submit an asynchronous provenance detection job."
        )
        return

    endpoint = settings().require("CONTENT_SAFETY_ENDPOINT")
    client = content_safety_client()
    operation_id = submit_detection(
        client, endpoint, settings().require("PROVENANCE_SOURCE_URL")
    )
    while True:
        operation = get_detection(client, endpoint, operation_id)
        if operation["status"] not in {"NotStarted", "Running"}:
            break
        time.sleep(2)

    if operation["status"] != "Succeeded":
        raise RuntimeError(f"Provenance detection failed: {operation.get('error')}")
    print("outcome:", operation["result"]["outcome"])
    for marker in operation["result"].get("results", []):
        print(
            f"{marker['type']}: provider={marker.get('provider')} "
            f"model={marker.get('modelName')}"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true", help="Submit and poll a live job.")
    main(parser.parse_args().run)
