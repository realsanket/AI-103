# Run: uv run python 09-current-ai-services-other/04_id_document.py [--apply --source-url <https> --show-values]
"""Extract typed ID document fields using Document Intelligence v4.0 prebuilt-idDocument.

`prebuilt-idDocument` supports worldwide passports and documented
government ID coverage. Returns typed fields (FirstName, LastName,
DateOfBirth, DocumentNumber, etc.) with confidence. Extraction ≠ identity
proofing — this alone does not validate an identity claim.

Default preflight validates env + source presence without cloud call.
`--apply` submits ONE billable analysis. Field values are SUPPRESSED
unless `--show-values` — identity data is PII and requires approved data
boundaries + retention policy.

Code path:
  preflight(): validate endpoint + DI_ID_SOURCE_URL. `--apply`:
  analyze("prebuilt-idDocument", url) → result. print_fields() walks
  documents[0].fields; values redacted unless --show-values.

What to watch. Preflight: env status. `--apply`: field list with types +
confidences. Reject low-confidence extractions before onboarding decisions.

Prerequisites / env vars:
  DOCUMENT_INTELLIGENCE_ENDPOINT — custom-subdomain HTTPS URL
  DI_ID_SOURCE_URL               — HTTPS ID URL (or --source-url)
  --apply                        — submit one billable analysis
  --show-values                  — print field values (opt-in for approved data)
"""
import argparse

from document_intelligence_common import analyze, configured, preflight, print_fields

MODEL_ID = "prebuilt-idDocument"
SOURCE_ENV = "DI_ID_SOURCE_URL"


def apply(document_url: str, show_values: bool) -> None:
    print_fields(analyze(MODEL_ID, document_url), show_values=show_values)
    if not show_values:
        print("Identity values suppressed. Re-run with --show-values only for approved data.")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Preflight or run v4.0 ID analysis.")
    parser.add_argument("--source-url", default=configured(SOURCE_ENV))
    parser.add_argument("--show-values", action="store_true")
    parser.add_argument("--apply", action="store_true", help="Submit one billable analysis.")
    args = parser.parse_args(argv)
    if not args.apply:
        preflight(MODEL_ID, SOURCE_ENV)
        return
    if not args.source_url:
        parser.error("--apply requires --source-url or DI_ID_SOURCE_URL.")
    apply(args.source_url, args.show_values)


if __name__ == "__main__":
    main()
