"""Pro-mode Content Understanding — create a cross-document review analyzer.

Scenario: mortgage-package review. Compare borrower name/DOB across
application form, pay stub, and bank statement — flag inconsistencies. Pro
mode accepts the comma-separated source URLs as one analyze request.
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
