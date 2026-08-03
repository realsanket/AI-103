"""Pro-mode Content Understanding — reason across multiple related documents.

Scenario: mortgage-package review. Compare borrower name/DOB across
application form, pay stub, and bank statement — flag inconsistencies.
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
            "consistency": {
                "type": "object",
                "method": "generate",
                "properties": {
                    "borrower_name_matches": {"type": "boolean"},
                    "borrower_dob_matches": {"type": "boolean"},
                    "income_supports_loan": {"type": "boolean"},
                    "notes": {"type": "string"},
                },
            }
        }
    },
    "referenceData": {"policy": "Underwriting Guide 2026-v4"},
}


def main() -> None:
    create_analyzer(ANALYZER_ID, _DEFINITION)

    package_urls = os.environ.get("CU_PRO_PACKAGE_URLS")
    if not package_urls:
        print(
            "Set CU_PRO_PACKAGE_URLS to a comma-separated list of Blob SAS URLs "
            "(application, pay stub, bank statement) to run it."
        )
        return
    urls = [u.strip() for u in package_urls.split(",")]
    result = analyze(ANALYZER_ID, urls[0] if len(urls) == 1 else urls)
    print(result.get("result", {}).get("contents", [{}])[0].get("fields"))


if __name__ == "__main__":
    main()
