# Run: uv run python 05-information-extraction/13_cu_cross_document_validation.py [--apply] [--delete]
"""Cross-document validation with Content Understanding GA (successor to retired Pro mode).

Standard versus Pro, then and now:
  - Standard mode analyzes one file per request. That is the only mode in GA
    `2025-11-01`, whose analyze `inputs` array accepts a single item.
  - Pro mode (`2025-05-01-preview`) accepted several related files in one
    request and reasoned across them, optionally against reference data. That
    preview API was retired on July 15, 2026 and now returns HTTP 410.
  - Agentic mode (`2026-06-01-preview`, `config.workflow: "agentic"`) reasons
    over ONE document for calculations and validation; it is not multi-file.

Current pattern for a mortgage package (application, pay stub, bank statement):
  1. One custom analyzer extracts the values to compare, with confidence and
     grounding (`estimateSourceAndConfidence` is required for `extract`).
  2. Analyze each document separately — one input per request.
  3. Compare in application code: flag mismatched values and low-confidence
     fields for a reviewer, with the source location of each value.

Code path:
  Default   validate + print analyzer JSON and the comparison rules; no Azure call.
  --apply   create_analyzer() (persistent) → analyze() once per URL →
            consistency_report() prints matches, mismatches, and review items.
  --delete  delete_analyzer() — cleanup.

Prerequisites / env vars:
  CU_ENDPOINT             — https://<resource>.services.ai.azure.com
  CU_API_VERSION          — 2025-11-01 (GA)
  CU_PACKAGE_SOURCE_URLS  — runtime-only, comma-separated HTTPS Blob SAS URLs
                            (secrets; never commit or add to .env.example)
  Roles: Cognitive Services Content Understanding Contributor (create/analyze)
  and Owner (delete) on the Foundry resource.
"""
import argparse
import json
import re

from _shared.config import env

ANALYZER_ID = "northwind-mortgage-identity"
REVIEW_THRESHOLD = 0.80
COMPARED_FIELDS = ("borrower_name", "date_of_birth")

_DEFINITION = {
    "description": "Extract borrower identity fields from one mortgage-package document.",
    "baseAnalyzerId": "prebuilt-document",
    "config": {"returnDetails": True, "estimateFieldSourceAndConfidence": True},
    "fieldSchema": {
        "name": "MortgageIdentity",
        "fields": {
            "document_type": {
                "type": "string",
                "method": "classify",
                "enum": ["loan_application", "pay_stub", "bank_statement", "other"],
                "description": "Kind of mortgage-package document.",
            },
            "borrower_name": {
                "type": "string",
                "method": "extract",
                "estimateSourceAndConfidence": True,
                "description": "Full legal name of the borrower or account holder.",
            },
            "date_of_birth": {
                "type": "date",
                "method": "extract",
                "estimateSourceAndConfidence": True,
                "description": "Borrower date of birth, if the document shows one.",
            },
        },
    },
}


def _value(field: dict | None):
    if not field:
        return None
    for key in ("valueString", "valueDate", "valueNumber"):
        if key in field:
            return field[key]
    return None


def _normalize(value) -> str:
    return re.sub(r"\s+", " ", str(value)).strip().casefold()


def consistency_report(documents: dict[str, dict], threshold: float = REVIEW_THRESHOLD) -> dict:
    """Compare the same fields across per-document CU results.

    `documents` maps a label (for example the file name) to that document's
    `contents[0].fields`. A field is consistent when every document that
    returned it agrees after whitespace/case normalization.
    """
    report: dict = {"consistent": [], "mismatched": {}, "review": []}
    for name in COMPARED_FIELDS:
        seen = {}
        for label, fields in documents.items():
            field = fields.get(name)
            value = _value(field)
            if value is None:
                continue
            seen[label] = value
            confidence = field.get("confidence")
            if confidence is None or confidence < threshold:
                report["review"].append(
                    {"document": label, "field": name, "confidence": confidence, "source": field.get("source")}
                )
        if len({_normalize(value) for value in seen.values()}) > 1:
            report["mismatched"][name] = seen
        elif seen:
            report["consistent"].append(name)
    return report


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--apply", action="store_true", help="Create the analyzer and analyze each document.")
    parser.add_argument("--delete", action="store_true", help="Delete the custom analyzer.")
    args = parser.parse_args(argv)

    if args.delete:
        from _shared.cu_client import delete_analyzer

        print("deleted." if delete_analyzer(ANALYZER_ID) else "analyzer not found.")
        return

    urls = [url.strip() for url in env("CU_PACKAGE_SOURCE_URLS").split(",") if url.strip()]
    if not args.apply:
        print(f"Analyzer '{ANALYZER_ID}' (no Azure call):")
        print(json.dumps(_DEFINITION, indent=2))
        print(f"Compared fields: {', '.join(COMPARED_FIELDS)}; review below confidence {REVIEW_THRESHOLD}.")
        print(f"CU_PACKAGE_SOURCE_URLS: {len(urls)} document(s) configured.")
        print("Re-run with --apply to analyze each document (one request per file).")
        return
    if len(urls) < 2:
        raise SystemExit("Set CU_PACKAGE_SOURCE_URLS to two or more comma-separated Blob SAS URLs.")

    from _shared.cu_client import analyze, create_analyzer

    create_analyzer(ANALYZER_ID, _DEFINITION)
    documents = {}
    for index, url in enumerate(urls, start=1):
        result = analyze(ANALYZER_ID, url)
        contents = result.get("result", {}).get("contents") or [{}]
        fields = contents[0].get("fields", {})
        documents[f"doc{index}:{_value(fields.get('document_type')) or 'unknown'}"] = fields
    print(json.dumps(consistency_report(documents), indent=2, default=str))
    print("Delete when finished: uv run python 05-information-extraction/13_cu_cross_document_validation.py --delete")


if __name__ == "__main__":
    main()
