# Run: uv run python 05-information-extraction/12_cu_custom_analyzer.py
# Practice-question coverage: Q41, Q92.
"""Custom Content Understanding analyzer — domain-specific field schema on prebuilt-document.

A custom analyzer combines a `baseAnalyzerId` (prebuilt-document) with a `fieldSchema`
you define: extract strings/numbers, classify into an enum (sla_tier), or generate a
summary. This lesson creates the `northwind-support-notice` analyzer and optionally
analyzes a document. The analyzer persists in the CU resource — creating it requires
Cognitive Services Content Understanding Contributor.

Three field methods: `extract` (pull value from doc), `classify` (map to enum),
`generate` (LLM produces a value). `generate` is model output, not source truth.

Code path:
  create_analyzer(ANALYZER_ID, _DEFINITION) → PUT analyzer. If URL env var set:
  analyze(ANALYZER_ID, src) → poll → print contents[0].fields.

What to watch. Analyzer creation: `analyzer '<id>' ready.` Field output: ticket_id,
customer_name, sla_tier (classified into enum), breach_penalty_usd (extracted number),
summary (generated). A missing field means CU couldn't extract it — inspect source doc.

Prerequisites / env vars:
  CU_ENDPOINT            — https://<resource>.services.ai.azure.com
  CU_API_VERSION         — 2025-11-01 (GA)
  CU_CUSTOM_SOURCE_URL   — optional HTTPS URL to a support notice PDF to analyze
"""
import os

from _shared.cu_client import analyze, create_analyzer

ANALYZER_ID = "northwind-support-notice"

_DEFINITION = {
    "description": "Extract Northwind support-notice fields.",
    "baseAnalyzerId": "prebuilt-document",
    "fieldSchema": {
        "fields": {
            "ticket_id": {"type": "string", "method": "extract"},
            "customer_name": {"type": "string", "method": "extract"},
            "sla_tier": {
                "type": "string",
                "method": "classify",
                "enum": ["Bronze", "Silver", "Gold", "Platinum"],
            },
            "breach_penalty_usd": {"type": "number", "method": "extract"},
            "summary": {"type": "string", "method": "generate"},
        }
    },
}


def main() -> None:
    print(f"creating analyzer '{ANALYZER_ID}'...")
    create_analyzer(ANALYZER_ID, _DEFINITION)
    print("done.")

    src = os.environ.get("CU_SUPPORT_NOTICE_URL")
    if not src:
        print("\nSet CU_SUPPORT_NOTICE_URL to a Blob SAS URL of a support notice PDF to run it.")
        return
    result = analyze(ANALYZER_ID, src)
    print(result.get("result", {}).get("contents", [{}])[0].get("fields"))


if __name__ == "__main__":
    main()
