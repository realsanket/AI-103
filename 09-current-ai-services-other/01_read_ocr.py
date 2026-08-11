# Run: uv run python 09-current-ai-services-other/01_read_ocr.py [--apply --source-url <https> --show-text]
"""Extract OCR text from one document using Document Intelligence v4.0 prebuilt-read.

`prebuilt-read` returns OCR words, lines, paragraphs, language, and page
locations. Use for pure text extraction; use `prebuilt-layout` (lesson 02)
when you also need tables + structure. Default preflight validates env +
source presence without a cloud call.

`--apply` submits ONE billable analysis via v4.0 API `2024-11-30 GA` and
prints page + language counts. OCR text is SUPPRESSED unless `--show-text`
is also supplied — printing raw content is opt-in for approved data only.

Requires a Document Intelligence resource with custom subdomain endpoint
(regional endpoints don't support Entra auth). Caller needs `Cognitive
Services User` at resource scope. Source URL must be reachable HTTPS
(SAS-bearing Blob URL common) — treat it as a secret; never commit.

Code path:
  preflight(): validate DOCUMENT_INTELLIGENCE_ENDPOINT + DI_READ_SOURCE_URL
  presence + shape. `--apply`: analyze("prebuilt-read", url) →
  DocumentIntelligenceClient.begin_analyze_document → poll → result. Print
  page/language counts; text only if --show-text.

What to watch. Preflight: `configured`/`missing` status. `--apply`:
`pages: N`, `languages: M`. Raw text visible only when `--show-text` used.

Prerequisites / env vars:
  DOCUMENT_INTELLIGENCE_ENDPOINT — custom-subdomain HTTPS URL
  DI_READ_SOURCE_URL             — HTTPS document URL (or --source-url)
  --apply                        — submit one billable analysis
  --show-text                    — print first 2000 chars of OCR text
"""
import argparse

from document_intelligence_common import analyze, configured, preflight

MODEL_ID = "prebuilt-read"
SOURCE_ENV = "DI_READ_SOURCE_URL"


def apply(document_url: str, show_text: bool) -> None:
    result = analyze(MODEL_ID, document_url)
    print(f"pages: {len(result.pages or [])}")
    print(f"languages: {len(result.languages or [])}")
    if show_text:
        print((result.content or "")[:2_000])
    else:
        print("OCR text suppressed. Re-run with --show-text only for approved data.")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Preflight or run v4.0 Read OCR.")
    parser.add_argument("--source-url", default=configured(SOURCE_ENV))
    parser.add_argument("--show-text", action="store_true")
    parser.add_argument("--apply", action="store_true", help="Submit one billable analysis.")
    args = parser.parse_args(argv)
    if not args.apply:
        preflight(MODEL_ID, SOURCE_ENV)
        return
    if not args.source_url:
        parser.error("--apply requires --source-url or DI_READ_SOURCE_URL.")
    apply(args.source_url, args.show_text)


if __name__ == "__main__":
    main()
