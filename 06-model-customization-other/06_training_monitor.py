# Run: uv run python 06-model-customization-other/06_training_monitor.py --job-id ftjob-... --apply
"""Inspect one fine-tuning job only with explicit opt-in."""
from __future__ import annotations

import argparse

from _shared.openai_client import openai_client
from lab_common import print_preflight


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Read one Foundry fine-tuning job.")
    parser.add_argument("--job-id", required=True)
    parser.add_argument("--apply", action="store_true", help="Read job and last ten events.")
    args = parser.parse_args(argv)
    if not args.apply:
        print_preflight([
            f"Would retrieve job {args.job_id} and its latest ten events.",
            "Would not create, update, deploy, resume, or cancel anything.",
            "Compare validation behavior with baseline before choosing final model or checkpoint.",
        ])
        return
    client = openai_client()
    job = client.fine_tuning.jobs.retrieve(args.job_id)
    events = client.fine_tuning.jobs.list_events(fine_tuning_job_id=args.job_id, limit=10)
    print(f"Job: {job.id}\nStatus: {job.status}\nFine-tuned model: {job.fine_tuned_model}")
    for event in events.data:
        print(f"- {event.created_at}: {event.message}")


if __name__ == "__main__":
    main()
