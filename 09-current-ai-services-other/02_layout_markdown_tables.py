"""Document Intelligence v4.0 Layout Markdown and tables lesson."""
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
