"""Text-to-video via Foundry Video Playground / Sora-family model.

Async: submit → poll → download URL → save. Requires a video model deployment
(`VIDEO_MODEL` in .env). Output size + duration limits vary per model.
"""
import time
from pathlib import Path

import httpx
from azure.identity import DefaultAzureCredential

from _shared.config import SAMPLE_DATA, settings

_SCOPE = "https://cognitiveservices.azure.com/.default"


def _token() -> str:
    return DefaultAzureCredential().get_token(_SCOPE).token


def main() -> None:
    s = settings()
    submit = f"{s.foundry_endpoint}/openai/v1/videos/generations:submit"
    body = {
        "model": s.video_model,
        "prompt": (
            "A short cinematic shot of a modern data center — soft blue LEDs on server "
            "racks, camera slowly dollying forward. 4 seconds. 1080p."
        ),
        "duration_seconds": 4,
        "resolution": "1080p",
    }
    headers = {"Authorization": f"Bearer {_token()}", "Content-Type": "application/json"}
    r = httpx.post(submit, headers=headers, json=body, timeout=60.0)
    r.raise_for_status()
    job_url = r.headers.get("Operation-Location") or r.json().get("id")

    print(f"submitted. polling {job_url} ...")
    while True:
        poll = httpx.get(job_url, headers=headers, timeout=30.0)
        poll.raise_for_status()
        job = poll.json()
        status = job.get("status", "").lower()
        if status in ("succeeded", "completed"):
            download_url = job["result"]["videos"][0]["url"]
            data = httpx.get(download_url, timeout=120.0).content
            out = SAMPLE_DATA / "generated" / "cloudxeus_video.mp4"
            Path(out).write_bytes(data)
            print(f"saved: {out}")
            return
        if status in ("failed", "canceled"):
            print(f"job failed: {job}")
            return
        time.sleep(5)


if __name__ == "__main__":
    main()
