"""Opt-in Sora 2 remix for one completed Sora 2 video.

Sora 2 remix is supported only from a previously completed video ID, not an
arbitrary local upload. It preserves source structure, motion, and framing
while applying one narrow prompt change. Run without flags for preflight;
`--apply` starts a billable preview job.
"""
import argparse

from _shared.openai_client import openai_client


def preflight() -> None:
    print("Video-remix preflight only. No cloud calls made.")
    print("Remix accepts a previously completed Sora 2 video ID, not a local video file.")
    print("Use one precise change; review source rights, consent, policy, retention, and cost.")
    print("Use --apply --video-id VIDEO_ID only after this review.")


def apply(video_id: str) -> None:
    if not video_id.startswith("video_"):
        raise SystemExit("--video-id must be a previously completed Sora 2 video ID (video_...).")
    video = openai_client().videos.remix(
        video_id=video_id,
        prompt="Change only the lighting to a warm, soft studio look.",
    )
    print(f"Submitted remix job: {video.id} ({video.status})")
    print("Retrieve or delete the job through the documented Sora 2 video API.")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Preflight or submit a supported Sora 2 video remix.")
    parser.add_argument("--apply", action="store_true", help="Submit a billable Sora 2 remix job.")
    parser.add_argument("--video-id", help="Previously completed Sora 2 video ID.")
    args = parser.parse_args(argv)
    if not args.apply:
        preflight()
        return
    if not args.video_id:
        raise SystemExit("--apply requires --video-id.")
    apply(args.video_id)


if __name__ == "__main__":
    main()
