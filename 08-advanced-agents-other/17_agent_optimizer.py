# Run: uv run python 08-advanced-agents-other/17_agent_optimizer.py [--apply] [--agent-name <name>]
"""Build an optimizer dataset and submit an agent optimization job to Foundry.

The Agent Optimizer improves a hosted agent's prompts and behavior by running it
against a labeled dataset, evaluating outputs, then suggesting system-prompt edits.
It is a closed-loop feedback cycle: run → evaluate → suggest edits → repeat. This
lesson proves the dataset-creation + job-submission pattern without modifying any
production agent.

Default preflight checks env vars and prints the dataset structure. --apply builds
a 3-sample JSONL dataset, uploads it, and submits an optimization job targeting
the coherence metric. Review results in Foundry portal → Agent → Optimizer.

Code path:
  --apply:
  1. Build JSON-Lines: [{input, expected_output, context}, ...]
  2. agents.optimizer.datasets.create(name, data=BytesIO, filename)
  3. agents.optimizer.jobs.create(agent_name, dataset_id, target_metric="coherence")
  4. Print job_id + status. Poll via agents.optimizer.jobs.get(job_id).

What to watch. job_id returned = optimizer job queued successfully. Poll until
status=="Completed". Check Foundry portal → Agent → Optimizer for suggested prompt.

Prerequisites / env vars:
  PROJECT_ENDPOINT      — Foundry project HTTPS URL
  DEFAULT_MODEL         — deployed chat model
  FOUNDRY_AGENT_NAME    — agent to optimize (or --agent-name)
  --agent-name          — override agent name
  --apply               — create dataset + submit optimizer job
"""
import argparse
import io
import json
import os

from _shared.config import settings
from _shared.foundry_client import project_client

_SAMPLES = [
    {"input": "What is your return policy?",
     "expected_output": "Returns accepted within 30 days with receipt.",
     "context": "retail support agent"},
    {"input": "How do I track my order?",
     "expected_output": "Track at orders.example.com with your order number.",
     "context": "retail support agent"},
    {"input": "Can I exchange a damaged item?",
     "expected_output": "Yes, damaged items exchanged within 14 days. Contact support@example.com.",
     "context": "retail support agent"},
]


def preflight() -> None:
    current = settings()
    agent_name = os.environ.get("FOUNDRY_AGENT_NAME", "")
    print("Agent optimizer preflight (no cloud calls).")
    print(f"- PROJECT_ENDPOINT: {'configured' if current.project_endpoint else 'missing'}")
    print(f"- DEFAULT_MODEL: {'configured' if current.default_model else 'missing'}")
    print(f"- FOUNDRY_AGENT_NAME: {agent_name or 'missing'}")
    print(f"- Dataset: {len(_SAMPLES)} rows (input + expected_output + context)")
    print("- target_metric: coherence (1–5 scale via LLM-as-judge)")
    print("Run --apply to create dataset and submit optimization job.")


def apply(agent_name: str) -> None:
    client = project_client()
    jsonl = "\n".join(json.dumps(s) for s in _SAMPLES)
    buf = io.BytesIO(jsonl.encode())

    try:
        dataset = client.agents.optimizer.datasets.create(
            name="retail-support-optimizer-dataset",
            data=buf,
            filename="dataset.jsonl",
        )
        print(f"Dataset created: {dataset.id}")

        job = client.agents.optimizer.jobs.create(
            agent_name=agent_name,
            dataset_id=dataset.id,
            target_metric="coherence",
        )
        print(f"Optimizer job submitted: {job.id}")
        print(f"Status: {job.status}")
        print("Poll: project_client().agents.optimizer.jobs.get(job_id)")
        print("Results: Foundry portal → Agent → Optimizer → suggested prompt changes.")
    except AttributeError:
        print("[WARN] optimizer API not available in this SDK version.")
        print("Upgrade: uv add --upgrade azure-ai-projects")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Create optimizer dataset and submit agent optimization job.")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--agent-name", default=os.environ.get("FOUNDRY_AGENT_NAME", ""))
    args = parser.parse_args(argv)
    if not args.apply:
        preflight()
        return
    if not args.agent_name:
        parser.error("--apply requires --agent-name or FOUNDRY_AGENT_NAME env var.")
    apply(args.agent_name)


if __name__ == "__main__":
    main()
