"""Content Understanding — video analyzer producing transcript + segments + key frames.

Async: submit → poll → read `contents` for segment list. Requires the video URL
to be accessible to the CU service (Blob SAS is easiest).
"""
import os

from _shared.cu_client import analyze


def main() -> None:
    video_url = os.environ.get("SAMPLE_VIDEO_URL")
    if not video_url:
        raise SystemExit(
            "Set SAMPLE_VIDEO_URL to a Blob SAS URL of an MP4 to run this lesson. "
            "See .context/azure-ai-docs/articles/ai-services/content-understanding/video/"
        )
    result = analyze("prebuilt-video", video_url)
    print("status:", result.get("status"))
    for seg in result.get("result", {}).get("contents", []):
        print(f"\n[{seg.get('startTime')} – {seg.get('endTime')}] {seg.get('summary', '')[:200]}")


if __name__ == "__main__":
    main()
