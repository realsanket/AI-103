# Run: uv run python 06-model-customization-other/02_dpo_dataset.py --dataset preferences.jsonl
"""Validate Direct Preference Optimization JSONL locally."""
from __future__ import annotations

import argparse
from pathlib import Path

from lab_common import jsonl_rows, messages, print_preflight


def validate_dpo(path: Path) -> int:
    rows = jsonl_rows(path)
    for number, row in enumerate(rows, 1):
        input_value = row.get("input")
        if not isinstance(input_value, dict):
            raise ValueError(f"row {number}.input must be an object.")
        messages(input_value.get("messages"), f"row {number}.input.messages")
        for field in ("preferred_output", "non_preferred_output"):
            completion = messages(row.get(field), f"row {number}.{field}")
            if not any(item["role"] == "assistant" for item in completion):
                raise ValueError(f"row {number}.{field} needs an assistant message.")
    return len(rows)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Validate DPO preference-pair JSONL.")
    parser.add_argument("--dataset", type=Path, required=True)
    args = parser.parse_args(argv)
    count = validate_dpo(args.dataset)
    print_preflight([
        f"Validated {count} DPO preference pair(s) in {args.dataset}.",
        "Each row has one input, one preferred output, and one non-preferred output.",
        "No upload or DPO job is created by this lab.",
    ])


if __name__ == "__main__":
    main()
