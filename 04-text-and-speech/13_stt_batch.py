"""Batch transcription — async REST. Submit files, poll, then fetch results.

Use for backlog / archives / anything with no user waiting. Region processes
serially — spread submissions across hours, not minutes.
"""
import time

import httpx
from azure.identity import DefaultAzureCredential

from _shared.config import settings

_SCOPE = "https://cognitiveservices.azure.com/.default"


def _base_url() -> str:
    s = settings()
    return f"https://{s.speech_region}.api.cognitive.microsoft.com"


def _headers() -> dict:
    token = DefaultAzureCredential().get_token(_SCOPE).token
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def _submit(container_sas_url: str) -> str:
    body = {
        "displayName": "northwind-support-calls-batch",
        "description": "Weekly call archive transcription",
        "locale": "en-US",
        "contentContainerUrl": container_sas_url,
        "properties": {
            "diarizationEnabled": True,
            "wordLevelTimestampsEnabled": True,
            "timeToLiveHours": 48,
        },
    }
    r = httpx.post(
        f"{_base_url()}/speechtotext/v3.2/transcriptions",
        headers=_headers(),
        json=body,
        timeout=60.0,
    )
    r.raise_for_status()
    return r.json()["self"]


def _wait(job_url: str) -> dict:
    while True:
        r = httpx.get(job_url, headers=_headers(), timeout=30.0)
        r.raise_for_status()
        body = r.json()
        if body["status"] in ("Succeeded", "Failed"):
            return body
        print(f"  status={body['status']} — waiting 30s")
        time.sleep(30)


def _print_transcripts(files_url: str) -> None:
    files = httpx.get(files_url, headers=_headers(), timeout=30.0)
    files.raise_for_status()
    for item in files.json().get("values", []):
        if item.get("kind") != "Transcription":
            continue
        content_url = item["links"]["contentUrl"]
        result = httpx.get(content_url, timeout=30.0)
        result.raise_for_status()
        phrases = result.json().get("combinedRecognizedPhrases", [])
        text = " ".join(phrase.get("display", "") for phrase in phrases)
        print(f"{item['name']}: {text}")


def main() -> None:
    import os
    container = os.environ.get("BATCH_STT_CONTAINER_SAS")
    if not container:
        raise SystemExit("Set BATCH_STT_CONTAINER_SAS to a Blob container SAS URL of WAV files.")
    job_url = _submit(container)
    print(f"submitted: {job_url}")
    done = _wait(job_url)
    if done["status"] == "Failed":
        raise SystemExit(f"batch transcription failed: {done}")
    print("done: Succeeded. Downloading transcription result files...")
    _print_transcripts(done["links"]["files"])


if __name__ == "__main__":
    main()
