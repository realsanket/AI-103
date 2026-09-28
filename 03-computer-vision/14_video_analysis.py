# Run: uv run python 03-computer-vision/14_video_analysis.py
# Practice-question coverage: Q105.
"""Content Understanding video analysis via `prebuilt-videoSearch` — requires `SAMPLE_VIDEO_URL`.

Beginner note:
  `prebuilt-videoSearch` returns analyzer contents for video segments. This
  lesson prints each segment's time range and Summary field. `prebuilt-video`
  is only a base analyzer for custom analyzers.

  Async: submit → poll → read `contents` for the segment list. The video
  URL must be reachable by the CU service (Blob SAS is easiest — you can't
  hand it a local path).
"""
import os

from _shared.cu_client import analyze, result_diagnostic, validate_source_url


def main() -> None:
    video_url = os.environ.get("SAMPLE_VIDEO_URL")
    if not video_url:
        raise SystemExit(
            "Set SAMPLE_VIDEO_URL to a Blob SAS URL of an MP4 to run this lesson.\n"
            "See: .context/azure-ai-docs/articles/ai-services/content-understanding/video/"
        )
    try:
        video_url = validate_source_url(video_url)
    except ValueError as error:
        raise SystemExit(f"{error}\nUse a public HTTPS URL or complete Blob SAS URL.") from error

    result = analyze("prebuilt-videoSearch", video_url)
    print("status:", result.get("status"))
    if result.get("status", "").lower() != "succeeded":
        print("diagnostic:", result_diagnostic(result))
        return
    for content in result.get("result", {}).get("contents", []):
        summary = content.get("fields", {}).get("Summary", {}).get("valueString", "")
        start = content.get("startTimeMs")
        end = content.get("endTimeMs")
        print(f"\n[{start}–{end} ms] {summary}")


if __name__ == "__main__":
    main()
