# Run: uv run python 06-model-customization-other/04_distillation_dataset.py --source prompts.jsonl --output distilled.jsonl
"""Generate reviewed SFT candidates from a teacher model only with --apply.

Distillation uses a stronger teacher to produce training data for a smaller
student. Default run validates source `messages` rows without any Azure call.
`--apply` calls the teacher deployment once per prompt and writes a new SFT
JSONL to `--output`. Output path must not exist — prevents overwriting a
reviewed dataset.

Teacher output is a candidate, never approved training data. Sample and
grade every row, remove duplicates and hallucinated claims, red-team safety
behavior, and split from the seed prompts used to generate it. Track lineage
(seed, teacher, model version, timestamp, reviewer).

Code path:
  validate_source() → jsonl_rows + messages check. With --apply:
  openai_client().responses.create(model=teacher, input=messages) per row →
  append assistant response → write SFT-shaped JSONL line.

What to watch. Preflight: `Validated N distillation prompt(s)`. With --apply:
`Created <output> from N teacher response(s).` Errors: pre-existing output
file, missing --teacher.

Prerequisites / env vars:
  --source   — JSONL of message arrays (required)
  --output   — new file path, must not exist (required)
  --teacher  — teacher deployment/model name (required with --apply)
  --apply    — call teacher and write output
  AZURE_OPENAI_ENDPOINT — teacher endpoint (via openai_client)
"""
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
