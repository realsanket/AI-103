"""Text-to-video via Sora 2 direct API.

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


def _token() -> str:
    return DefaultAzureCredential().get_token(_SCOPE).token


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
    job_id = job["id"]
    print(f"submitted job: {job_id}")

    status_url = (
        f"{endpoint}/openai/v1/video/generations/jobs/{job_id}"
        f"?api-version={_API_VERSION}"
    )
    while True:
        poll = httpx.get(status_url, headers=headers, timeout=30.0)
        poll.raise_for_status()
        job = poll.json()
        status = job.get("status", "").lower()
        print(f"  status: {status}")
        if status in ("succeeded", "completed"):
            generations = job.get("generations", [])
            if not generations:
                raise SystemExit(f"job completed but no generations returned: {job}")
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
            return
        if status in ("failed", "cancelled"):
            raise SystemExit(f"job failed: {job}")
        time.sleep(5)


if __name__ == "__main__":
    main()
