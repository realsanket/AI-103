# Run: uv run python 03-computer-vision/13_content_understanding_image.py
"""Content Understanding image analysis via `prebuilt-imageSearch` — requires `SAMPLE_IMAGE_URL`.

Beginner note:
  CU's `prebuilt-imageSearch` analyzer takes an image URL and returns
  a Markdown representation and a `Summary` field. Contrast with L01
  (multimodal LLM): CU gives a consistent analyzer result, the LLM gives
  free-form prose.

  IMPORTANT: The CU service fetches the URL server-side. `file://` URLs
  won't work — you need a URL CU can reach (Blob SAS is the easiest).
  Set `SAMPLE_IMAGE_URL` in your environment to a public/SAS URL of a
  test image, or upload one of `_shared/sample_data/images/*.png` to Blob
  Storage and paste the SAS URL.
"""
import os

from _shared.config import SAMPLE_DATA
from _shared.cu_client import analyze, result_diagnostic, validate_source_url


def main() -> None:
    image_url = os.environ.get("SAMPLE_IMAGE_URL")
    if not image_url:
        local = SAMPLE_DATA / "images" / "support_ticket_portal.png"
        raise SystemExit(
            "Set SAMPLE_IMAGE_URL to a URL the CU service can fetch (Blob SAS is easiest).\n"
            f"  Example candidate to upload: {local}\n"
            "  See: .context/azure-ai-docs/articles/ai-services/content-understanding/quickstart/"
        )
    try:
        image_url = validate_source_url(image_url)
    except ValueError as error:
        raise SystemExit(f"{error}\nUse a public HTTPS URL or complete Blob SAS URL.") from error

    result = analyze("prebuilt-imageSearch", image_url)
    print("status:", result.get("status"))
    if result.get("status", "").lower() != "succeeded":
        print("diagnostic:", result_diagnostic(result))
        return
    contents = result.get("result", {}).get("contents", [])
    if not contents:
        return

    content = contents[0]
    print("\n--- Image Analysis Result ---")
    print(content.get("markdown", ""))
    summary = content.get("fields", {}).get("Summary", {}).get("valueString")
    if summary:
        print(f"\nSummary: {summary}")


if __name__ == "__main__":
    main()
