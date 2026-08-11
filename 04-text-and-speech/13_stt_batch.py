# Run: uv run python 04-text-and-speech/13_stt_batch.py
"""Batch Transcription — async REST for many audio files in a Blob container.

POST a container SAS URL to /speechtotext/transcriptions and the service processes
all files asynchronously. Best for call-center archives, weekly processing batches,
and any scenario where no user is waiting. Unlike Fast Transcription, this runs
in the background with an explicit submit→poll→fetch→cleanup lifecycle. Jobs can
queue; spread submissions across hours. The finally block deletes the service job —
copy results to governed storage before that happens.

Code path:
  _submit(container_sas_url) → POST to transcriptions API → returns job self-URL.
  _wait(job_url) → GET job URL until status in {Succeeded, Failed, Cancelled},
  honoring Retry-After or bounded 60-600s backoff.
  _print_transcripts(files_url) → GET links.files → filter kind=Transcription →
  GET each contentUrl → print combinedRecognizedPhrases.
  finally: DELETE job URL.

What to watch: status=Running polls, then transcript phrases per file. The job
self-URL is printed on submit — save it externally for reconciliation if the client
is interrupted before the finally block runs.

Prerequisites / env vars:
  SPEECH_REGION             — must match the Speech resource location
  BATCH_STT_CONTAINER_SAS  — Blob container SAS with read + list permissions (runtime-only, not in .env)
"""
import time

import httpx
from azure.identity import DefaultAzureCredential

from _shared.config import settings
from _shared.speech_config import speech_region

_SCOPE = "https://cognitiveservices.azure.com/.default"
_API_VERSION = "2024-11-15"


def _base_url() -> str:
    s = settings()
    return s.speech_endpoint.rstrip("/") or f"https://{speech_region()}.api.cognitive.microsoft.com"


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
        f"{_base_url()}/speechtotext/transcriptions?api-version={_API_VERSION}",
        headers=_headers(),
        json=body,
        timeout=60.0,
    )
    r.raise_for_status()
    return r.json()["self"]


def _poll_delay(headers: dict[str, str], attempt: int) -> int:
    try:
        return max(60, min(600, int(headers.get("Retry-After", ""))))
    except ValueError:
        return min(600, 60 * 2**min(attempt, 3))


def _wait(job_url: str) -> dict:
    attempt = 0
    while True:
        r = httpx.get(job_url, headers=_headers(), timeout=30.0)
        r.raise_for_status()
        body = r.json()
        if body["status"] in ("Succeeded", "Failed", "Cancelled"):
            return body
        delay = _poll_delay(r.headers, attempt)
        print(f"  status={body['status']} — waiting {delay}s")
        time.sleep(delay)
        attempt += 1


def _delete(job_url: str) -> None:
    r = httpx.delete(job_url, headers=_headers(), timeout=30.0)
    r.raise_for_status()


def _print_transcripts(files_url: str) -> None:
    files = httpx.get(files_url, headers=_headers(), timeout=30.0)
    files.raise_for_status()
    transcription_files = [
        item for item in files.json().get("values", []) if item.get("kind") == "Transcription"
    ]
    if not transcription_files:
        print("No transcription result files were returned.")
        return
    for item in transcription_files:
        content_url = item.get("links", {}).get("contentUrl")
        if not content_url:
            print(f"{item.get('name', 'unnamed result')}: no result URL")
            continue
        result = httpx.get(content_url, timeout=30.0)
        result.raise_for_status()
        phrases = result.json().get("combinedRecognizedPhrases", [])
        text = " ".join(phrase.get("display", "") for phrase in phrases).strip()
        print(f"{item.get('name', 'unnamed result')}: {text or '(no recognized speech)'}")


def main() -> None:
    import os
    container = os.environ.get("BATCH_STT_CONTAINER_SAS")
    if not container:
        raise SystemExit("Set BATCH_STT_CONTAINER_SAS to a Blob container SAS URL of WAV files.")
    job_url = _submit(container)
    print(f"submitted: {job_url}")
    try:
        done = _wait(job_url)
        if done["status"] != "Succeeded":
            raise SystemExit(f"batch transcription failed: {done}")
        print("done: Succeeded. Downloading transcription result files...")
        _print_transcripts(done["links"]["files"])
    finally:
        _delete(job_url)
        print("deleted batch transcription and service-managed results.")


if __name__ == "__main__":
    main()
