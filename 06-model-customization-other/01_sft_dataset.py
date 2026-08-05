# Run: uv run python 06-model-customization-other/01_sft_dataset.py --dataset training.jsonl
"""Validate supervised fine-tuning JSONL locally."""
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
