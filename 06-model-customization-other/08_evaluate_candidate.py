# Run: uv run python 06-model-customization-other/08_evaluate_candidate.py --dataset eval.jsonl --candidate ft-deployment --apply
"""Compare a candidate against optional baseline on held-out JSONL.

Small transparent evaluator: exact-match scoring against a held-out set. Row
schema is `{"query": str, "expected": str}`. Default validates rows; `--apply`
sends one Responses call per model per row and prints a single score. This is
NOT a Foundry evaluation object — no dataset, run, portal record, or built-in
evaluator is created.

Exact match is only meaningful when there really is one correct string
(single-token classification, extraction). For open-ended quality use domain
5's Foundry evaluators or lesson 21 in domain 01. Always audit representative
outputs, subgroups, safety failures, latency, tokens, and cost alongside the
aggregate score before promoting a candidate.

Code path:
  validate_eval(path) → rows with nonempty query+expected. With --apply:
  score(model, rows) → per row: responses.create(model, input=query) →
  .output_text.strip().casefold() vs expected.casefold(). Print
  `<label>: matches/total (pct%)` per model.

What to watch. `candidate: 42/50 exact matches (84.0%)`. Baseline optional
but strongly recommended — a candidate that beats no baseline proves nothing.

Prerequisites / env vars:
  --dataset    — held-out JSONL (required)
  --candidate  — deployment name to test (required)
  --baseline   — deployment name to compare against (optional)
  --apply      — send inference requests
  AZURE_OPENAI_ENDPOINT
"""
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
