# Run: uv run python 06-model-customization-other/03_rft_dataset_grader.py --dataset rft.jsonl --grader grader.py
"""Validate reinforcement fine-tuning prompts and Python grader source locally.

RFT improves reasoning by rewarding correct answers. Each JSONL row ends in a
`user` message (not assistant — the model produces the answer during training)
plus fields your grader consumes. The grader defines `grade(sample, item) →
numeric score`; the service runs it in a sandbox, this lab compiles it
locally to check syntax but never executes.

Only use RFT for tasks with a verifiable outcome (math, extraction, code). A
rising train reward with a flat validation reward is reward hacking, not
progress. Current RFT service has a $5,000 safety stop for training + grading
— that is a stop, not a budget.

Code path:
  jsonl_rows(path) → assert last message role == "user"; grader.read_text()
  → assert `def grade(sample, item):` present → compile() checks syntax
  without running.

What to watch. `Validated N RFT prompt(s) and compiled <grader>`. Errors name
missing `grade` signature or Python compile errors in grader.

Prerequisites / env vars:
  --dataset  — RFT JSONL path (required)
  --grader   — Python grader file path (required)
"""
from __future__ import annotations

import argparse
from pathlib import Path

from lab_common import jsonl_rows, messages, print_preflight


def validate_rft(path: Path, grader: Path) -> int:
    rows = jsonl_rows(path)
    for number, row in enumerate(rows, 1):
        conversation = messages(row.get("messages"), f"row {number}.messages")
        if conversation[-1]["role"] != "user":
            raise ValueError(f"row {number} must end with a user message for RFT.")
    source = grader.read_text(encoding="utf-8")
    if "def grade(sample, item):" not in source:
        raise ValueError("RFT Python grader must define def grade(sample, item):")
    compile(source, str(grader), "exec")
    return len(rows)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Validate RFT JSONL and a grader without executing it.")
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--grader", type=Path, required=True)
    args = parser.parse_args(argv)
    count = validate_rft(args.dataset, args.grader)
    print_preflight([
        f"Validated {count} RFT prompt(s) and compiled {args.grader}.",
        "The grader is not executed locally or uploaded.",
        "Calibrate reward behavior on held-out data; watch train/validation reward divergence.",
    ])


if __name__ == "__main__":
    main()
