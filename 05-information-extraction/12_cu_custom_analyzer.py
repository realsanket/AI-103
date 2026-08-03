"""Custom Content Understanding analyzer via `baseAnalyzerId: prebuilt-document`.

Defines a Northwind-specific schema (ticket_id, sla_tier, breach_penalty)
and applies it to a scanned support notice.
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
