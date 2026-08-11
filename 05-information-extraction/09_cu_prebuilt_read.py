# Run: uv run python 05-information-extraction/09_cu_prebuilt_read.py
"""Content Understanding `prebuilt-read` — basic OCR extraction to Markdown.

`prebuilt-read` extracts words, paragraphs, and formulas into Markdown. It has
no table, figure, or section hierarchy — use `prebuilt-layout` (lesson 10) when
document structure matters for RAG chunking. Good baseline for plain text documents.

CU's async pattern: submit URL → 202 + Operation-Location → poll until succeeded →
consume result.contents[0].markdown. CU fetches the URL server-side; `file://`
paths are not reachable. The default URL is a public Azure sample PDF — replace
with CU_READ_SOURCE_URL for your own document.

Code path:
  analyze("prebuilt-read", src) → poll → print status and first 500 chars of markdown.

What to watch. `status: succeeded` and a Markdown text preview. Tables/figures
absent from output — that's expected for prebuilt-read. Use prebuilt-layout (L10)
to get those.

Prerequisites / env vars:
  CU_ENDPOINT        — https://<resource>.services.ai.azure.com
  CU_API_VERSION     — 2025-11-01 (GA)
  CU_READ_SOURCE_URL — optional; overrides public sample URL
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
