# Run: uv run python 03-computer-vision/10_visual_provenance_policy.py
"""Visual-media provenance check via Content Safety Provenance Detect API — preflight + `--run`.

The Content Safety Provenance Detect API checks supported C2PA and Microsoft
watermark signals in an HTTPS Blob or SAS URI. A positive result is an origin
signal, not proof of ownership, truth, safety, or trustworthiness. No result
does not prove media is human-made or non-AI. Run without flags for preflight;
use `--run` to submit and poll a cloud job.
"""
import argparse
import json
import time
from urllib.parse import urlparse

from azure.core.rest import HttpRequest

from _shared.config import settings
from _shared.content_safety_client import content_safety_client

_API_VERSION = "2026-07-01-preview"
_POLL_SECONDS = 2
_MAX_POLLS = 60
_SUPPORTED_MEDIA = (".jpg", ".jpeg", ".png", ".gif", ".webp", ".mp3", ".wav", ".m4a", ".mp4")


def media_uri(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc or not parsed.path.lower().endswith(_SUPPORTED_MEDIA):
        raise SystemExit("Media URI must be an HTTPS Blob or SAS URI for a supported image, audio, or MP4 file.")
    return value


def submit_detection(client, endpoint: str, source_uri: str) -> str:
    operation = client.send_request(
        HttpRequest(
            method="POST",
            url=f"{endpoint.rstrip('/')}/contentsafety/provenance/operations:detect?api-version={_API_VERSION}",
            headers={"Content-Type": "application/json"},
            content=json.dumps({"content": {"uri": source_uri}}).encode(),
        )
    ).json()
    if not operation.get("id"):
        raise RuntimeError(f"Provenance operation did not return an id: {operation}")
    return operation["id"]


def get_detection(client, endpoint: str, operation_id: str) -> dict:
    return client.send_request(
        HttpRequest(
            method="GET",
            url=(
                f"{endpoint.rstrip('/')}/contentsafety/provenance/operations/{operation_id}"
                f"?api-version={_API_VERSION}"
            ),
        )
    ).json()


def preflight() -> None:
    print("Visual-provenance preflight only. No cloud calls made.")
    print("Policy: retain source URI and detector outcome; disclose detected provenance accurately.")
    print("Policy: do not treat detected or absent markers as proof of ownership, truth, safety, or trust.")
    print("Use --run --media-url HTTPS_BLOB_OR_SAS_URI after reviewing retention, access, and cost.")


def run(source_uri: str) -> None:
    endpoint = settings().require("CONTENT_SAFETY_ENDPOINT")
    client = content_safety_client()
    operation_id = submit_detection(client, endpoint, media_uri(source_uri))
    for _ in range(_MAX_POLLS):
        operation = get_detection(client, endpoint, operation_id)
        status = operation.get("status")
        if status not in {"NotStarted", "Running"}:
            break
        time.sleep(_POLL_SECONDS)
    else:
        raise TimeoutError(f"Provenance operation {operation_id} did not complete in {_MAX_POLLS * _POLL_SECONDS} seconds.")

    if operation.get("status") != "Succeeded":
        raise RuntimeError(f"Provenance detection failed: {operation.get('error')}")
    result = operation.get("result", {})
    print("outcome:", result.get("outcome"))
    for marker in result.get("results", []):
        print(
            f"{marker.get('type')}: provider={marker.get('provider')} "
            f"model={marker.get('modelName')}"
        )


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Preflight or run visual-media provenance detection.")
    parser.add_argument("--run", action="store_true", help="Submit and poll a cloud provenance job.")
    parser.add_argument("--media-url", help="HTTPS Blob or SAS URI for supported media.")
    args = parser.parse_args(argv)
    if not args.run:
        preflight()
        return
    if not args.media_url:
        raise SystemExit("--run requires --media-url.")
    run(args.media_url)


if __name__ == "__main__":
    main()
