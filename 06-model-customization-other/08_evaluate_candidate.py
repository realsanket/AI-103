# Run: uv run python 06-model-customization-other/08_evaluate_candidate.py --dataset eval.jsonl --candidate ft-deployment --apply
"""Compare a candidate against optional baseline on held-out JSONL."""
from __future__ import annotations

import argparse
from pathlib import Path

from _shared.openai_client import openai_client
from lab_common import jsonl_rows, print_preflight


def validate_eval(path: Path) -> list[dict]:
    rows = jsonl_rows(path)
    for number, row in enumerate(rows, 1):
        if not isinstance(row.get("query"), str) or not row["query"].strip():
            raise ValueError(f"row {number} needs nonempty query.")
        if not isinstance(row.get("expected"), str) or not row["expected"].strip():
            raise ValueError(f"row {number} needs nonempty expected.")
    return rows


def score(model: str, rows: list[dict]) -> tuple[int, int]:
    client = openai_client()
    matches = 0
    for row in rows:
        output = client.responses.create(model=model, input=row["query"]).output_text.strip()
        matches += output.casefold() == row["expected"].strip().casefold()
    return matches, len(rows)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run exact-match held-out evaluation.")
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--baseline")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    rows = validate_eval(args.dataset)
    if not args.apply:
        print_preflight([
            f"Validated {len(rows)} held-out evaluation row(s).",
            f"Would call candidate {args.candidate}" + (f" and baseline {args.baseline}." if args.baseline else "."),
            "Would print exact-match scores only; no evaluation object, file upload, or deployment is created.",
        ])
        return
    for label, model in (("candidate", args.candidate), ("baseline", args.baseline)):
        if model:
            matches, total = score(model, rows)
            print(f"{label}: {matches}/{total} exact matches ({matches / total:.1%})")


if __name__ == "__main__":
    main()
