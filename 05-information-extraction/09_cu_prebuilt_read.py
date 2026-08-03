"""Content Understanding `prebuilt-read` — basic OCR: words + paragraphs.

Lightweight starting point. No tables / figures / sections — use `prebuilt-layout`
for that. Formulas and barcodes come back too when present.
"""
import os

from _shared.cu_client import analyze


def main() -> None:
    src = os.environ.get(
        "CU_READ_SOURCE_URL",
        "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-sample-data-files/master/Language/example.pdf",
    )
    result = analyze("prebuilt-read", src)
    print("status:", result.get("status"))
    contents = result.get("result", {}).get("contents", [])
    if contents:
        print("\n--- Extracted text (first 500 chars) ---")
        print(contents[0].get("markdown", "")[:500])


if __name__ == "__main__":
    main()
