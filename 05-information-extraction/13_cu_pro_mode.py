# Run: CU_API_VERSION=2025-05-01-preview uv run python 05-information-extraction/13_cu_pro_mode.py
# Practice-question coverage: Q36, Q46, Q122.
"""Pro-mode Content Understanding — cross-document reasoning over related files.

CU Pro mode accepts multiple related document URLs in one analyze request and
generates a cross-document summary. The scenario here is mortgage-package review:
compare borrower name/DOB across application form, pay stub, and bank statement —
flag inconsistencies. Pro mode supports ONLY `generate` and `classify` field methods;
`extract` is not supported. No grounding/confidence metadata is returned.

Pro mode is NOT a better single-document OCR switch. Use it only when a decision
genuinely needs cross-document reasoning. It requires a separate preview API version
(`2025-05-01-preview`) — restore `CU_API_VERSION` to the GA value after this lesson.

Code path:
  Set CU_API_VERSION=2025-05-01-preview externally. create_analyzer(ANALYZER_ID,
  _DEFINITION with mode="pro") → analyze() with comma-separated URL list → poll →
  print fields.consistency_summary.

What to watch. A generated consistency summary comparing document fields. If the
URLs contain documents with conflicting names, the summary should flag that.

Prerequisites / env vars:
  CU_ENDPOINT       — https://<resource>.services.ai.azure.com
  CU_API_VERSION    — must be 2025-05-01-preview for Pro mode
  PRO_DOC_URLS      — comma-separated HTTPS URLs (application, pay stub, bank statement)
"""
import os

from _shared.cu_client import analyze, create_analyzer

ANALYZER_ID = "mortgage-package-review"

_DEFINITION = {
    "description": "Cross-document review of a mortgage application package.",
    "baseAnalyzerId": "prebuilt-document",
    "mode": "pro",
    "fieldSchema": {
        "fields": {
            "consistency_summary": {
                "type": "string",
                "method": "generate",
            }
        }
    },
}


def main() -> None:
    source_urls = [
        url.strip()
        for url in os.environ.get("CU_PRO_SOURCE_URLS", "").split(",")
        if url.strip()
    ]
    if not source_urls:
        print(
            "Set CU_PRO_SOURCE_URLS to comma-separated document Blob SAS URLs to analyze."
        )
        return
    create_analyzer(ANALYZER_ID, _DEFINITION)
    result = analyze(ANALYZER_ID, source_urls)
    print(result.get("result", {}).get("contents", [{}])[0].get("fields"))


if __name__ == "__main__":
    main()
