# Run: uv run python 02-generative-ai-and-agents/22_cloud_evaluation.py --dataset cases.jsonl
"""Preflight, then optionally create a durable cloud evaluation run.

Unlike L21, this uploads JSONL and persists an evaluation definition and run.
Rows must contain one non-empty ``query`` string: each row is one independent
turn. This sample does not reconstruct a multi-turn conversation; evaluate
multi-turn agents with a reviewed trajectory schema that preserves every
message, tool call, tool result, and final response.

The preview is local and makes no Azure request. ``--apply`` uploads an eval
file (set to expire after 30 days), creates an evaluation, then starts a run.
The run sends every query to the configured deployment and stores inputs,
outputs, and scores. Dataset uploads, evaluator calls, model tokens, and
stored results can incur cost. Validate a labelled local baseline before
enabling continuous production evaluation.

Azure region support varies by model and evaluator. The caller needs Foundry
project access and permission to use the model; restricted telemetry results
also need monitoring-reader access. Private endpoints require working private
DNS and egress from the runner to Foundry, Azure OpenAI, and Azure Monitor.
Never upload credentials, customer secrets, or unredacted personal data.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from _shared.config import load_env

_REQUIRED_ENV = (
    "AZURE_AI_PROJECT_ENDPOINT",
    "AZURE_AI_MODEL_DEPLOYMENT_NAME",
)


def evaluation_criteria(model_deployment: str) -> list[dict]:
    """Return a task-adherence criterion with its complete-turn response mapping."""
    return [
        {
            "type": "azure_ai_evaluator",
            "name": "Task Adherence",
            "evaluator_name": "builtin.task_adherence",
            "initialization_parameters": {"deployment_name": model_deployment},
            "data_mapping": {
                "query": "{{item.query}}",
                "response": "{{sample.output_items}}",
            },
        }
    ]


def validate_dataset(dataset: Path) -> int:
    """Verify local JSONL shape before any persistent cloud call."""
    count = 0
    for line_number, line in enumerate(dataset.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(f"Line {line_number} is not valid JSON.") from error
        if not isinstance(row, dict) or not isinstance(row.get("query"), str) or not row["query"].strip():
            raise ValueError(f"Line {line_number} needs a non-empty string query.")
        count += 1
    if not count:
        raise ValueError("Dataset has no JSONL rows.")
    return count


def preflight(dataset: Path | None) -> str:
    """Describe durable side effects without contacting Azure."""
    model = os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME", "<unset>")
    return "\n".join(
        [
            "PREVIEW: no Azure requests, uploads, evaluations, or runs.",
            f"Would locally validate JSONL dataset: {dataset or '<required with --apply>'}",
            "Would upload an eval dataset file with 30-day expiry.",
            "Would persist evaluation: Northwind agent task-adherence evaluation.",
            f"Would start one durable run using deployment: {model}.",
            "Would retain run inputs, outputs, and scores under project access controls.",
            "Run again with --apply to perform exactly these persistent actions.",
        ]
    )


def run(dataset: Path) -> None:
    """Upload validated JSONL, then create one evaluation and one run."""
    from azure.ai.projects import AIProjectClient
    from azure.identity import DefaultAzureCredential

    model = os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"]
    project = AIProjectClient(
        endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
        credential=DefaultAzureCredential(),
    )
    client = project.get_openai_client()
    with dataset.open("rb") as source:
        uploaded = client.files.create(
            file=source,
            purpose="evals",
            expires_after={"anchor": "created_at", "seconds": 2_592_000},
        )
    evaluation = client.evals.create(
        name="Northwind agent task-adherence evaluation",
        data_source_config={
            "type": "custom",
            "item_schema": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
            "include_sample_schema": True,
        },
        testing_criteria=evaluation_criteria(model),
    )
    evaluation_run = client.evals.runs.create(
        eval_id=evaluation.id,
        name="Northwind agent task-adherence run",
        data_source={
            "type": "responses",
            "source": {"type": "file_id", "id": uploaded.id},
            "input_messages": {
                "type": "template",
                "template": [
                    {
                        "type": "message",
                        "role": "user",
                        "content": {"type": "input_text", "text": "{{item.query}}"},
                    }
                ],
            },
            "model": model,
        },
    )
    print(f"Uploaded dataset file: {uploaded.id}")
    print(f"Evaluation created: {evaluation.id}")
    print(f"Run started: {evaluation_run.id}")


def main() -> None:
    load_env()
    parser = argparse.ArgumentParser(description="Create a reviewed cloud evaluation run.")
    parser.add_argument("--dataset", type=Path, help="JSONL rows with a query field.")
    parser.add_argument("--apply", action="store_true", help="Perform persistent cloud actions.")
    args = parser.parse_args()
    if not args.apply:
        print(preflight(args.dataset))
        return
    if args.dataset is None:
        parser.error("--dataset is required with --apply.")
    if not args.dataset.is_file():
        parser.error(f"Dataset does not exist: {args.dataset}")
    try:
        rows = validate_dataset(args.dataset)
    except ValueError as error:
        parser.error(str(error))
    for variable in _REQUIRED_ENV:
        if not os.environ.get(variable):
            parser.error(f"{variable} is required with --apply.")
    print(f"Validated {rows} local JSONL row(s). Applying persistent cloud actions.")
    run(args.dataset)


if __name__ == "__main__":
    main()
