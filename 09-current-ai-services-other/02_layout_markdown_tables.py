# Run: uv run python 09-current-ai-services-other/02_layout_markdown_tables.py [--apply --source-url <https> --show-markdown]
"""Extract layout + tables as Markdown using Document Intelligence v4.0 prebuilt-layout.

`prebuilt-layout` adds document structure to OCR: tables, selection marks,
paragraph roles, figures, sections. Requesting Markdown output preserves
that structure — complex tables render as HTML inside Markdown so merged
cells and captions remain represented. Default preflight validates env +
source presence with no cloud call.

`--apply` submits ONE billable analysis via v4.0 GA and prints counts for
pages, tables, figures, sections. Markdown content is SUPPRESSED unless
`--show-markdown` is also supplied. Use this over lesson 01 when you need
structure (tables, sections) not just text.

Code path:
  preflight(): validate endpoint + DI_LAYOUT_SOURCE_URL. `--apply`:
  analyze("prebuilt-layout", url, markdown=True) → v4.0 client with
  `output_content_format="markdown"` param → result. Print
  pages/tables/figures/sections counts; markdown only if --show-markdown.

What to watch. Preflight: env var status. `--apply`: `pages: N`,
`tables: M`, `figures: K`, `sections: L`. Markdown body only with
`--show-markdown` (truncated at 4000 chars).

Prerequisites / env vars:
  DOCUMENT_INTELLIGENCE_ENDPOINT — custom-subdomain HTTPS URL
  DI_LAYOUT_SOURCE_URL           — HTTPS document URL (or --source-url)
  --apply                        — submit one billable analysis
  --show-markdown                — print first 4000 chars of Markdown
"""
import argparse

from document_intelligence_common import analyze, configured, preflight

MODEL_ID = "prebuilt-layout"
SOURCE_ENV = "DI_LAYOUT_SOURCE_URL"


def apply(document_url: str, show_markdown: bool) -> None:
    result = analyze(MODEL_ID, document_url, markdown=True)
    print(f"pages: {len(result.pages or [])}")
    print(f"tables: {len(result.tables or [])}")
    print(f"figures: {len(result.figures or [])}")
    print(f"sections: {len(result.sections or [])}")
    if show_markdown:
        print((result.content or "")[:4_000])
    else:
        print("Markdown suppressed. Re-run with --show-markdown only for approved data.")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Preflight or run v4.0 Layout analysis.")
    parser.add_argument("--source-url", default=configured(SOURCE_ENV))
    parser.add_argument("--show-markdown", action="store_true")
    parser.add_argument("--apply", action="store_true", help="Submit one billable analysis.")
    args = parser.parse_args(argv)
    if not args.apply:
        preflight(MODEL_ID, SOURCE_ENV)
        return
    if not args.source_url:
        parser.error("--apply requires --source-url or DI_LAYOUT_SOURCE_URL.")
    apply(args.source_url, args.show_markdown)


if __name__ == "__main__":
    main()
