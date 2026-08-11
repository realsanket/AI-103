# Run: uv run python 09-current-ai-services-other/06_di_vs_cu_decision.py --scenario <ocr-layout|standard-form|unstructured|custom-labeled> [--needs-reasoning] [--multiple-files] [--air-gapped]
"""Local decision-tree chooser: Document Intelligence vs Content Understanding.

Zero cloud calls. Given a scenario + capability flags, prints current
default tool + rationale. Encodes current Foundry guidance:
- `air-gapped` → DI containers (only on-prem option)
- `unstructured` / `needs-reasoning` / `multiple-files` → CU analyzers
- `ocr-layout` → CU prebuilt-read/prebuilt-layout
- `custom-labeled` → DI custom neural
- `standard-form` (default) → DI prebuilt models

Result is a starting default — validate with representative documents +
production requirements before commitment. This encodes guidance, not a
performance or cost guarantee.

Code path:
  choose_tool(scenario, needs_reasoning, multiple_files, air_gapped) →
  early return for air-gapped; then LLM triggers; then scenario switch.
  Prints tool + why.

What to watch. `Choose: <tool>` + `Why: <reason>`. Repeat with different
flag combinations to see routing logic.

Prerequisites / env vars:
  --scenario           — ocr-layout | standard-form | unstructured | custom-labeled (required)
  --needs-reasoning    — LLM-inferred output required
  --multiple-files     — multi-file cross-referencing required
  --air-gapped         — on-premises / disconnected deployment
"""
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
