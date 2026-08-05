"""Visual characteristic extraction via Content Understanding `prebuilt-imageSearch`.

Beginner note:
  CU's `prebuilt-imageSearch` analyzer takes an image URL and returns
  structured description/tags/objects — perfect for building a searchable
  index over screenshots or product photos. Contrast with L01
  (multimodal LLM): CU gives schematized output, the LLM gives free-form prose.

  IMPORTANT: The CU service fetches the URL server-side. `file://` URLs
  won't work — you need a URL CU can reach (Blob SAS is the easiest).
  Set `SAMPLE_IMAGE_URL` in your environment to a public/SAS URL of a
  test image, or upload one of `_shared/sample_data/images/*.png` to Blob
  Storage and paste the SAS URL.
"""
import os

from _shared.config import SAMPLE_DATA
from _shared.cu_client import analyze


def main() -> None:
    image_url = os.environ.get("SAMPLE_IMAGE_URL")
    if not image_url:
        local = SAMPLE_DATA / "images" / "support_ticket_portal.png"
        raise SystemExit(
            "Set SAMPLE_IMAGE_URL to a URL the CU service can fetch (Blob SAS is easiest).\n"
            f"  Example candidate to upload: {local}\n"
            "  See: .context/azure-ai-docs/articles/ai-services/content-understanding/quickstart/"
        )
    if image_url.startswith("file://"):
        raise SystemExit(
            "CU cannot fetch file:// URLs — the service fetches server-side.\n"
            "Upload the image to Blob Storage and use a SAS URL instead."
        )

    result = analyze("prebuilt-imageSearch", image_url)
    print("status:", result.get("status"))
    contents = result.get("result", {}).get("contents", [])
    if contents:
        print("\n--- Image Analysis Result ---")
        print(contents[0])


if __name__ == "__main__":
    main()
