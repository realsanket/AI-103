"""Document Intelligence v4.0 prebuilt ID document lesson."""
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
