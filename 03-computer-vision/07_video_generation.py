# Run: uv run python 03-computer-vision/07_video_generation.py
"""Text-to-video via Sora 2 direct API — submit job, poll, download MP4.

Beginner note:
  This lesson submits a job, polls until it succeeds, then downloads the MP4.
  It uses the raw REST API via httpx so all three steps are visible.

  Sora 2 direct API:
    POST {endpoint}/openai/v1/video/generations/jobs?api-version=preview
    GET  {endpoint}/openai/v1/video/generations/jobs/{job-id}?api-version=preview
    GET  {endpoint}/openai/v1/video/generations/{generation-id}/content/video?api-version=preview

Prereqs:
  - VIDEO_MODEL in .env — deployment name for your Sora model (e.g. `sora-2`).
  - Sora 2 preview access in a supported Azure OpenAI region.
"""
import time
from pathlib import Path

import httpx
from azure.identity import DefaultAzureCredential

from _shared.config import SAMPLE_DATA, settings

# Sora 2's direct Azure OpenAI API uses this documented Entra ID token scope.
_SCOPE = "https://ai.azure.com/.default"
_API_VERSION = "preview"
_POLL_INTERVAL_SECONDS = 5.0
_POLL_TIMEOUT_SECONDS = 300.0
_SUCCESS_STATUSES = {"succeeded", "completed"}
_FAILURE_STATUSES = {"failed", "cancelled", "canceled"}


def _token() -> str:
    return DefaultAzureCredential().get_token(_SCOPE).token


def _failure_detail(job: dict) -> str:
    reason = job.get("failure_reason") or job.get("error")
    if isinstance(reason, dict):
        reason = reason.get("message") or reason.get("code") or reason
    return str(reason or "No failure reason returned.")


def _wait_for_job(
    status_url: str,
    headers: dict[str, str],
    *,
    timeout: float = _POLL_TIMEOUT_SECONDS,
    interval: float = _POLL_INTERVAL_SECONDS,
) -> dict:
    if timeout <= 0 or interval <= 0:
        raise ValueError("timeout and interval must be greater than zero.")
    deadline = time.monotonic() + timeout
    last_status = "unknown"
    while True:
        poll = httpx.get(status_url, headers=headers, timeout=30.0)
        poll.raise_for_status()
        job = poll.json()
        status = str(job.get("status", "")).lower()
        last_status = status or last_status
        print(f"  status: {last_status}")
        if status in _SUCCESS_STATUSES:
            return job
        if status in _FAILURE_STATUSES:
            raise RuntimeError(f"Sora job {status}: {_failure_detail(job)}")
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError(
                f"Sora job did not finish within {timeout:g}s; last status: {last_status}. "
                "The job remains active; no cancellation request was sent."
            )
        time.sleep(min(interval, remaining))


def main() -> None:
    s = settings()
    endpoint = s.require("AZURE_OPENAI_ENDPOINT")
    submit_url = (
        f"{endpoint}/openai/v1/video/generations/jobs"
        f"?api-version={_API_VERSION}"
    )
    body = {
        "model": s.video_model,
        "prompt": (
            "A short cinematic shot of a modern data center — soft blue LEDs on server "
            "racks, camera slowly dollying forward."
        ),
        "width": 1280,
        "height": 720,
        "n_seconds": 5,
    }
    headers = {"Authorization": f"Bearer {_token()}", "Content-Type": "application/json"}
    r = httpx.post(submit_url, headers=headers, json=body, timeout=60.0)
    r.raise_for_status()
    job = r.json()
    job_id = job.get("id")
    if not isinstance(job_id, str) or not job_id:
        raise RuntimeError(f"Sora job submission did not return an id: {job}")
    print(f"submitted job: {job_id}")

    status_url = (
        f"{endpoint}/openai/v1/video/generations/jobs/{job_id}"
        f"?api-version={_API_VERSION}"
    )
    job = _wait_for_job(status_url, headers)
    generations = job.get("generations", [])
    if (
        not generations
        or not isinstance(generations[0], dict)
        or not isinstance(generations[0].get("id"), str)
    ):
        raise RuntimeError(f"Sora job succeeded but returned no generation id: {job}")
    gen_id = generations[0]["id"]
    content_url = (
        f"{endpoint}/openai/v1/video/generations/{gen_id}/content/video"
        f"?api-version={_API_VERSION}"
    )
    video = httpx.get(content_url, headers=headers, timeout=120.0)
    video.raise_for_status()
    out = SAMPLE_DATA / "generated" / "northwind_video.mp4"
    Path(out).write_bytes(video.content)
    print(f"saved: {out}")


if __name__ == "__main__":
    main()
