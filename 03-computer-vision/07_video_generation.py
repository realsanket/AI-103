# Run: uv run python 03-computer-vision/07_video_generation.py [--apply] [--seconds 4|8|12] [--delete-remote]
# Practice-question coverage: Q173.
"""Text-to-video with Sora 2 on the v1 API — create, poll, download MP4.

Beginner note:
  Video generation is asynchronous. `videos.create()` starts a job and returns
  a `video_...` ID immediately; `videos.retrieve(id)` reports `queued`,
  `in_progress`, `completed`, or `failed`; `videos.download_content(id,
  variant="video")` returns the MP4 once the job completes.

  Sora 2 uses the Azure OpenAI v1 surface (`{AZURE_OPENAI_ENDPOINT}/openai/v1`,
  `/videos` routes). The original `sora` model and its
  `/video/generations/jobs` request shape (`width`, `height`, `n_seconds`) are
  retired; Sora 2 takes `size` ("1280x720" or "720x1280") and `seconds`
  ("4", "8", or "12").

  Limits worth knowing: two concurrent jobs per resource; finished videos are
  kept for about 24 hours; Sora 2 rejects photorealistic people and IP. Keep a
  completed video ID if you want to remix it (lesson 09); pass
  `--delete-remote` to delete the service copy after download.

Prereqs:
  - VIDEO_MODEL in .env — deployment name of your Sora 2 model (for example `sora-2`).
  - Sora 2 (preview) deployed in a supported region; Cognitive Services User role.
  - Default run is a local preflight; `--apply` starts a billable job.
"""
import argparse
import time

from _shared.config import SAMPLE_DATA, settings

_POLL_INTERVAL_SECONDS = 10.0
_POLL_TIMEOUT_SECONDS = 600.0
_SIZES = ("1280x720", "720x1280")
_SECONDS = ("4", "8", "12")
PROMPT = (
    "A short cinematic shot of a modern data center — soft blue LEDs on server "
    "racks, camera slowly dollying forward."
)
OUTPUT = SAMPLE_DATA / "generated" / "northwind_video.mp4"


def _failure_detail(video) -> str:
    error = getattr(video, "error", None)
    if error is None:
        return "No failure reason returned."
    return str(getattr(error, "message", None) or getattr(error, "code", None) or error)


def wait_for_video(
    client,
    video,
    *,
    timeout: float = _POLL_TIMEOUT_SECONDS,
    interval: float = _POLL_INTERVAL_SECONDS,
    sleep=None,
    clock=None,
):
    """Poll videos.retrieve until completed, failed, or the deadline passes."""
    if timeout <= 0 or interval <= 0:
        raise ValueError("timeout and interval must be greater than zero.")
    sleep = sleep or time.sleep
    clock = clock or time.monotonic
    deadline = clock() + timeout
    while True:
        print(f"  status: {video.status} ({getattr(video, 'progress', 0) or 0}%)")
        if video.status == "completed":
            return video
        if video.status == "failed":
            raise RuntimeError(f"Sora job failed: {_failure_detail(video)}")
        remaining = deadline - clock()
        if remaining <= 0:
            raise TimeoutError(
                f"Sora job {video.id} did not finish within {timeout:g}s; last status: {video.status}. "
                "The job remains active; retrieve it later or delete it."
            )
        sleep(min(interval, remaining))
        video = client.videos.retrieve(video.id)


def generate(client, *, model: str, size: str, seconds: str, delete_remote: bool = False):
    if size not in _SIZES or seconds not in _SECONDS:
        raise ValueError(f"size must be one of {_SIZES} and seconds one of {_SECONDS}.")
    video = client.videos.create(model=model, prompt=PROMPT, size=size, seconds=seconds)
    print(f"submitted video: {video.id}")
    video = wait_for_video(client, video)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    client.videos.download_content(video.id, variant="video").write_to_file(OUTPUT)
    print(f"saved: {OUTPUT}")
    if delete_remote:
        client.videos.delete(video.id)
        print(f"deleted service copy of {video.id}")
    else:
        print(f"keep {video.id} to remix it with lesson 09; it expires after about 24 hours.")
    return video


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--apply", action="store_true", help="Start a billable Sora 2 job.")
    parser.add_argument("--size", choices=_SIZES, default="1280x720")
    parser.add_argument("--seconds", choices=_SECONDS, default="4")
    parser.add_argument("--delete-remote", action="store_true", help="Delete the service copy after download.")
    args = parser.parse_args(argv)

    model = settings().video_model
    if not args.apply:
        print("Video preflight only. No cloud calls made.")
        print(f"Would call videos.create(model={model!r}, size={args.size!r}, seconds={args.seconds!r}).")
        print("Then poll videos.retrieve(id) and save videos.download_content(id, variant='video').")
        print("Re-run with --apply after reviewing prompt, cost (per second), and retention.")
        return

    from _shared.openai_client import openai_client

    generate(openai_client(), model=model, size=args.size, seconds=args.seconds, delete_remote=args.delete_remote)


if __name__ == "__main__":
    main()
