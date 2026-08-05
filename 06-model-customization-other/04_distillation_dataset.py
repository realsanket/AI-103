# Run: uv run python 06-model-customization-other/04_distillation_dataset.py --source prompts.jsonl --output distilled.jsonl
"""Generate reviewed SFT candidates from a teacher model only with --apply."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from _shared.openai_client import openai_client
from lab_common import jsonl_rows, messages, print_preflight


def validate_source(path: Path) -> list[dict]:
    rows = jsonl_rows(path)
    for number, row in enumerate(rows, 1):
        messages(row.get("messages"), f"row {number}.messages")
    return rows


def generate(rows: list[dict], teacher: str, output: Path) -> None:
    client = openai_client()
    with output.open("x", encoding="utf-8") as destination:
        for row in rows:
            response = client.responses.create(model=teacher, input=row["messages"])
            record = {"messages": [*row["messages"], {"role": "assistant", "content": response.output_text}]}
            destination.write(json.dumps(record, ensure_ascii=False) + "\n")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Create teacher-generated SFT candidates.")
    parser.add_argument("--source", type=Path, required=True, help="JSONL rows containing messages.")
    parser.add_argument("--output", type=Path, required=True, help="New output path; must not exist.")
    parser.add_argument("--teacher", help="Teacher deployment or supported model name.")
    parser.add_argument("--apply", action="store_true", help="Call teacher and write output JSONL.")
    args = parser.parse_args(argv)
    rows = validate_source(args.source)
    if not args.apply:
        print_preflight([
            f"Validated {len(rows)} distillation prompt(s) in {args.source}.",
            f"Would create {args.output} only if it does not already exist.",
            "Would call the selected teacher once per prompt; review, filter, and split output before training.",
        ])
        return
    if not args.teacher:
        parser.error("--teacher is required with --apply.")
    if args.output.exists():
        parser.error(f"--output already exists: {args.output}")
    generate(rows, args.teacher, args.output)
    print(f"Created {args.output} from {len(rows)} teacher response(s). Review before any fine-tuning upload.")


if __name__ == "__main__":
    main()
