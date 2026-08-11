# Run: uv run python 06-model-customization-other/06_training_monitor.py --job-id ftjob-... --apply
"""Inspect one fine-tuning job only with explicit opt-in.

Read-only diagnostic. `--apply` retrieves one job by ID and prints its state,
final `fine_tuned_model` (once complete), and the ten most recent events.
This is a snapshot, not continuous polling — re-run to refresh. It does not
select a checkpoint, resume, or cancel.

Compare candidate quality against the held-out set from lesson 08 before
deploying (lesson 07). Choose a checkpoint because it meets predeclared
quality/safety/latency/cost thresholds, not because it's the newest.

Code path:
  --apply: fine_tuning.jobs.retrieve(job_id) → print status + fine_tuned_model.
  fine_tuning.jobs.list_events(fine_tuning_job_id=..., limit=10) → print
  each as `- <created_at>: <message>`.

What to watch. `Status: <succeeded|running|failed|cancelled>`. Event stream
shows checkpoints, validation metrics, warnings. A `succeeded` status with
`fine_tuned_model: ft:...` means the model is ready for lesson 07 deployment.

Prerequisites / env vars:
  --job-id  — ftjob-... from lesson 05 (required)
  --apply   — perform the read
  AZURE_OPENAI_ENDPOINT — control-plane endpoint
"""
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
