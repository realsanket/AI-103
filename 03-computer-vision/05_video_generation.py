"""Text-to-video via Foundry Sora API.

Beginner note:
  Sora is Foundry's video generation model. Every call is ASYNC — you submit
  a job, poll until it succeeds, then download the MP4. This lesson uses the
  raw REST API via httpx so you can see all three steps clearly. The modern
  OpenAI SDK also exposes `client.videos.create()` if you'd rather use that.

  Correct URL (verified against foundry/openai `new-inference-preview`):
    POST {endpoint}/openai/v1/video/generations/jobs?api-version=preview
    GET  {endpoint}/openai/v1/video/generations/jobs/{job-id}?api-version=preview
    GET  {endpoint}/openai/v1/video/generations/{generation-id}/content/video?api-version=preview

Prereqs:
  - VIDEO_MODEL in .env — deployment name for your Sora model (e.g. `sora-2`).
  - Sora is currently region-limited; check availability in the Foundry portal.

Sora 2 restrictions to know:
  - No copyrighted characters / music, no real people (including public figures).
  - No input images with human faces.
"""
import time
from pathlib import Path

import httpx
from azure.identity import DefaultAzureCredential

from _shared.config import SAMPLE_DATA, settings

_SCOPE = "https://cognitiveservices.azure.com/.default"
_API_VERSION = "preview"


def _token() -> str:
    return DefaultAzureCredential().get_token(_SCOPE).token


def main() -> None:
    s = settings()
    submit_url = f"{s.foundry_endpoint}/openai/v1/video/generations/jobs?api-version={_API_VERSION}"
    body = {
        "model": s.video_model,
        "prompt": (
            "A short cinematic shot of a modern data center — soft blue LEDs on server "
            "racks, camera slowly dollying forward."
        ),
        "seconds": "4",
        "size": "1280x720",
    }
    headers = {"Authorization": f"Bearer {_token()}", "Content-Type": "application/json"}
    r = httpx.post(submit_url, headers=headers, json=body, timeout=60.0)
    r.raise_for_status()
    job = r.json()
    job_id = job["id"]
    print(f"submitted job: {job_id}")

    status_url = f"{s.foundry_endpoint}/openai/v1/video/generations/jobs/{job_id}?api-version={_API_VERSION}"
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
                f"{s.foundry_endpoint}/openai/v1/video/generations/{gen_id}/content/video"
                f"?api-version={_API_VERSION}"
            )
            data = httpx.get(content_url, headers=headers, timeout=120.0).content
            out = SAMPLE_DATA / "generated" / "northwind_video.mp4"
            Path(out).write_bytes(data)
            print(f"saved: {out}")
            return
        if status in ("failed", "canceled"):
            raise SystemExit(f"job failed: {job}")
        time.sleep(5)


if __name__ == "__main__":
    main()
