# Run: uv run python 06-model-customization-other/09_batch_inference.py --input batch.jsonl --apply
"""Validate and submit a Global Batch Responses job only with --apply."""
from __future__ import annotations

import argparse
from pathlib import Path

from _shared.openai_client import openai_client
from lab_common import jsonl_rows, print_preflight


def validate_batch(path: Path) -> tuple[int, str]:
    rows = jsonl_rows(path)
    ids: set[str] = set()
    models: set[str] = set()
    for number, row in enumerate(rows, 1):
        if row.get("method") != "POST" or row.get("url") != "/v1/responses":
            raise ValueError(f"row {number} must POST to /v1/responses.")
        custom_id = row.get("custom_id")
        body = row.get("body")
        if not isinstance(custom_id, str) or not custom_id or custom_id in ids:
            raise ValueError(f"row {number} needs a unique custom_id.")
        if not isinstance(body, dict) or not isinstance(body.get("model"), str):
            raise ValueError(f"row {number}.body needs deployment model.")
        ids.add(custom_id)
        models.add(body["model"])
    if len(models) != 1:
        raise ValueError("All Batch rows must target one Global Batch deployment.")
    return len(rows), models.pop()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Submit a validated Global Batch Responses job.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    count, model = validate_batch(args.input)
    if not args.apply:
        print_preflight([
            f"Validated {count} Global Batch request(s) for deployment {model}.",
            "Would upload input with purpose batch and submit one asynchronous 24h batch job.",
            "Global Batch doesn't support fine-tuned models; completed work remains billable after cancellation.",
        ])
        return
    client = openai_client()
    with args.input.open("rb") as source:
        uploaded = client.files.create(file=source, purpose="batch")
    batch = client.batches.create(input_file_id=uploaded.id, endpoint="/v1/responses", completion_window="24h")
    print(f"Uploaded batch file: {uploaded.id}\nBatch: {batch.id} ({batch.status})")


if __name__ == "__main__":
    main()
