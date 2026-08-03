"""Visual characteristic extraction via Content Understanding `prebuilt-imageSearch`.

Turns a screenshot into structured description text useful for search + agent
reasoning. Contrast with `01_multimodal_understanding.py` — CU gives
schematized output, the LLM gives free-form prose.
"""
from _shared.config import SAMPLE_DATA
from _shared.cu_client import analyze

_IMAGE_LOCAL = SAMPLE_DATA / "images" / "support_ticket_portal.png"


def main() -> None:
    # CU async REST wants a URL. For local dev, upload to Blob w/ SAS and pass here.
    url = f"file://{_IMAGE_LOCAL}"
    result = analyze("prebuilt-imageSearch", url)
    print("status:", result.get("status"))
    contents = result.get("result", {}).get("contents", [])
    if contents:
        print("\n--- Image Analysis Result ---")
        print(contents[0])


if __name__ == "__main__":
    main()
