"""Document Intelligence v4.0 Read OCR lesson."""
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
