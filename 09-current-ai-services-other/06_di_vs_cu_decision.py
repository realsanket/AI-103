"""Local current-GA Document Intelligence versus Content Understanding chooser."""
from __future__ import annotations

import argparse


def choose_tool(
    scenario: str,
    *,
    needs_reasoning: bool = False,
    multiple_files: bool = False,
    air_gapped: bool = False,
) -> tuple[str, str]:
    """Return current documented default, without checking Azure."""
    if air_gapped:
        return (
            "Document Intelligence containers",
            "Document Intelligence is option for on-premises or air-gapped deployment.",
        )
    if needs_reasoning or multiple_files or scenario == "unstructured":
        return (
            "Content Understanding",
            "Use LLM-powered analyzers for unstructured, inferred, or multi-file work.",
        )
    if scenario == "ocr-layout":
        return (
            "Content Understanding",
            "Use prebuilt-read or prebuilt-layout for OCR or layout-only processing.",
        )
    if scenario == "custom-labeled":
        return (
            "Document Intelligence custom neural",
            "Use labeled, structured documents for deterministic custom extraction.",
        )
    return (
        "Document Intelligence prebuilt model",
        "Use deterministic extraction for standard structured forms such as invoices and IDs.",
    )


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Choose DI or CU locally; no Azure calls.")
    parser.add_argument(
        "--scenario",
        choices=("ocr-layout", "standard-form", "unstructured", "custom-labeled"),
        required=True,
    )
    parser.add_argument("--needs-reasoning", action="store_true")
    parser.add_argument("--multiple-files", action="store_true")
    parser.add_argument("--air-gapped", action="store_true")
    args = parser.parse_args(argv)
    tool, reason = choose_tool(
        args.scenario,
        needs_reasoning=args.needs_reasoning,
        multiple_files=args.multiple_files,
        air_gapped=args.air_gapped,
    )
    print("No cloud calls made.")
    print(f"Choose: {tool}")
    print(f"Why: {reason}")


if __name__ == "__main__":
    main()
