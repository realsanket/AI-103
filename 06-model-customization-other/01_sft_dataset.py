# Run: uv run python 06-model-customization-other/01_sft_dataset.py --dataset training.jsonl
"""Validate supervised fine-tuning JSONL locally.

SFT teaches a model to reproduce reviewed input→output pairs. Each JSONL row
holds a nonempty `messages` array ending in an `assistant` message. This lab
reads the file, validates every row against that contract, and stops at the
first bad row. It never uploads, submits, or contacts Azure.

Fine-tuning changes weights; it does not retrieve current facts or repair a
poor task definition. Confirm a prompt/RAG baseline is genuinely insufficient
before spending on training. Split source data into train/validation/held-out
before training — near duplicates across splits leak answers.

Code path:
  jsonl_rows(path) → for each row, messages() checks nonempty list and role
  strings; assert last role == "assistant". Returns row count for print.

What to watch. `Validated N SFT record(s)` — N matches your file. A ValueError
names the failing row and field (e.g. `row 42 must end with an assistant
message for SFT.`).

Prerequisites / env vars:
  --dataset  — path to SFT JSONL (required)
"""
from __future__ import annotations

import argparse
from pathlib import Path

from lab_common import jsonl_rows, messages, print_preflight


def validate_sft(path: Path) -> int:
    rows = jsonl_rows(path)
    for number, row in enumerate(rows, 1):
        conversation = messages(row.get("messages"), f"row {number}.messages")
        if conversation[-1]["role"] != "assistant":
            raise ValueError(f"row {number} must end with an assistant message for SFT.")
    return len(rows)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Validate SFT JSONL without uploading it.")
    parser.add_argument("--dataset", type=Path, required=True)
    args = parser.parse_args(argv)
    count = validate_sft(args.dataset)
    print_preflight([
        f"Validated {count} SFT record(s) in {args.dataset}.",
        "No upload or training job is created by this lab.",
        "Keep validation and held-out evaluation records separate from training data.",
    ])


if __name__ == "__main__":
    main()
