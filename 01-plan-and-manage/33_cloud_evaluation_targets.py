# Run: uv run python 01-plan-and-manage/33_cloud_evaluation_targets.py [--apply]
"""Configure a cloud evaluation target (model | prompt-agent | hosted-agent).

WHAT
────
A cloud evaluation "target" is the runtime the service calls per row of your
dataset. It lives inside the eval run's `data_source` as:

    data_source = {
      "type": "azure_ai_target_completions",
      "source": {"type": "file_id", "id": <dataset-file-id>},
      "input_messages": {...},   # template OR freeform (invocations protocol)
      "target": {...},            # <-- what this lesson picks
    }

Three target shapes:

  azure_ai_model             — a model deployment
      { "type": "azure_ai_model", "model": "<deployment>",
        "sampling_params": {"top_p": 1.0, "max_completion_tokens": 2048} }
      Model Router is supported only here (not as a query-generator or judge).

  azure_ai_agent (responses)  — Foundry prompt agent or hosted agent that
                                speaks the Responses API
      { "type": "azure_ai_agent", "name": "<agent>", "version": "1" }
      Uses structured `input_messages` template with roles and
      `{{item.query}}` / `{{sample.output_text}}` mapping.

  azure_ai_agent (invocations) — hosted agent that speaks only the invocations
                                 protocol
      Same `target` shape, but `input_messages` is FREEFORM JSON matching the
      hosted agent's /invocations body: e.g. {"message": "{{item.query}}"}.
      If a hosted agent supports both protocols, the service defaults to
      responses — use the structured template.

WHY
───
Same evaluators, same dataset, three ways to plug the system under test in.
The lesson prints the exact JSON body that flows to
`openai_client.evals.runs.create(...)` so a reviewer can eyeball what the
service will call before it runs.

CODE PATH
─────────
  preflight (default): assemble `data_source_config`, `testing_criteria`,
                       `data_source`, and print them. No cloud call.
  --apply: create the eval file (if `EVAL_DATASET_PATH` given), then
           `openai_client.evals.create(...)` + `openai_client.evals.runs.create(...)`.

WHAT TO WATCH
─────────────
- Data mapping: `{{item.query}}` = input row, `{{sample.output_text}}` = plain
  text response, `{{sample.output_items}}` = full structured output (tool
  calls + messages) — required by `builtin.task_adherence`.
- Hosted-agent invocations protocol: `input_messages` becomes a freeform JSON
  object mapping directly to /invocations, not the template shape.
- Model target completed runs may include `latency.target` and
  `estimated_cost.target`; see lesson 34.

ENV VARS
────────
  AZURE_AI_PROJECT_ENDPOINT       — Foundry project endpoint URL (required)
  AZURE_AI_MODEL_DEPLOYMENT_NAME  — deployment name (required)
  AZURE_AI_AGENT_NAME             — agent name (for agent targets)
  AZURE_AI_AGENT_VERSION          — agent version (default: "1")
  EVAL_TARGET_NAME                — display name for the evaluation
                                    (default: "cloud-eval-target-lesson")
  EVAL_TARGET_TYPE                — "model" | "agent" | "hosted_invocations"
                                    (default: "model")
  EVAL_DATASET_PATH               — path to a JSONL eval dataset. Required
                                    with --apply.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from _shared.config import load_env

_DEFAULT_NAME = "cloud-eval-target-lesson"
_DEFAULT_TYPE = "model"
_TARGET_TYPES = ("model", "agent", "hosted_invocations")


def _data_source_config() -> dict:
    return {
        "type": "custom",
        "item_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
        "include_sample_schema": True,
    }


def _testing_criteria(model: str, target_type: str) -> list[dict]:
    criteria: list[dict] = [
        {
            "type": "azure_ai_evaluator",
            "name": "coherence",
            "evaluator_name": "builtin.coherence",
            "initialization_parameters": {"model": model},
            "data_mapping": {
                "query": "{{item.query}}",
                "response": "{{sample.output_text}}",
            },
        },
        {
            "type": "azure_ai_evaluator",
            "name": "violence",
            "evaluator_name": "builtin.violence",
            "data_mapping": {
                "query": "{{item.query}}",
                "response": "{{sample.output_text}}",
            },
        },
    ]
    if target_type in ("agent", "hosted_invocations"):
        criteria.append({
            "type": "azure_ai_evaluator",
            "name": "task_adherence",
            "evaluator_name": "builtin.task_adherence",
            "initialization_parameters": {"model": model},
            "data_mapping": {
                "query": "{{item.query}}",
                "response": "{{sample.output_items}}",
            },
        })
    return criteria


def _input_messages(target_type: str) -> dict:
    if target_type == "hosted_invocations":
        # Freeform JSON that maps to the hosted agent's /invocations body.
        return {"message": "{{item.query}}"}
    if target_type == "agent":
        return {
            "type": "template",
            "template": [
                {
                    "type": "message",
                    "role": "developer",
                    "content": {
                        "type": "input_text",
                        "text": "You are a helpful assistant. Answer clearly and safely.",
                    },
                },
                {
                    "type": "message",
                    "role": "user",
                    "content": {"type": "input_text", "text": "{{item.query}}"},
                },
            ],
        }
    # model
    return {
        "type": "template",
        "template": [
            {
                "type": "message",
                "role": "user",
                "content": {"type": "input_text", "text": "{{item.query}}"},
            }
        ],
    }


def _target(target_type: str, model: str, agent_name: str, agent_version: str) -> dict:
    if target_type == "model":
        return {
            "type": "azure_ai_model",
            "model": model,
            "sampling_params": {"top_p": 1.0, "max_completion_tokens": 2048},
        }
    # agent or hosted_invocations use the same target shape
    return {"type": "azure_ai_agent", "name": agent_name, "version": agent_version}


def _data_source(target_type: str, target: dict, input_messages: dict, file_id_placeholder: str) -> dict:
    return {
        "type": "azure_ai_target_completions",
        "source": {"type": "file_id", "id": file_id_placeholder},
        "input_messages": input_messages,
        "target": target,
    }


def preflight(args: argparse.Namespace) -> None:
    endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT", "<unset>")
    model = os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME", "<unset>")
    agent = os.environ.get("AZURE_AI_AGENT_NAME", "<unset>")
    agent_version = os.environ.get("AZURE_AI_AGENT_VERSION", "1")

    config = _data_source_config()
    criteria = _testing_criteria(model, args.target_type)
    target = _target(args.target_type, model, agent, agent_version)
    input_messages = _input_messages(args.target_type)
    data_source = _data_source(args.target_type, target, input_messages, "<uploaded-at-apply-time>")

    print("PREVIEW: no cloud resources created.")
    print(f"Project endpoint : {endpoint}")
    print(f"Evaluation name  : {args.name}")
    print(f"Target type      : {args.target_type}")
    print()
    print("evals.create(data_source_config=...):")
    print(json.dumps(config, indent=2))
    print()
    print("evals.create(testing_criteria=...):")
    print(json.dumps(criteria, indent=2))
    print()
    print("evals.runs.create(data_source=...):")
    print(json.dumps(data_source, indent=2))
    print()
    print("Run again with --apply --dataset <path.jsonl> to create eval + run.")


def apply(args: argparse.Namespace) -> None:
    from azure.ai.projects import AIProjectClient
    from azure.identity import DefaultAzureCredential

    endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]
    model = os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"]
    agent = os.environ.get("AZURE_AI_AGENT_NAME", "")
    agent_version = os.environ.get("AZURE_AI_AGENT_VERSION", "1")

    project = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())
    openai_client = project.get_openai_client()

    with Path(args.dataset).open("rb") as fh:
        uploaded = openai_client.files.create(
            file=fh,
            purpose="evals",
            expires_after={"anchor": "created_at", "seconds": 2_592_000},
        )
    print(f"Uploaded eval dataset: {uploaded.id}")

    evaluation = openai_client.evals.create(
        name=args.name,
        data_source_config=_data_source_config(),
        testing_criteria=_testing_criteria(model, args.target_type),
    )
    print(f"Evaluation created: {evaluation.id}")

    target = _target(args.target_type, model, agent, agent_version)
    run = openai_client.evals.runs.create(
        eval_id=evaluation.id,
        name=f"{args.name}-run",
        data_source=_data_source(
            args.target_type,
            target,
            _input_messages(args.target_type),
            uploaded.id,
        ),
    )
    print(f"Run started: {run.id}  status={getattr(run, 'status', 'unknown')}")


def main(argv: list[str] | None = None) -> None:
    load_env()
    parser = argparse.ArgumentParser(description="Configure a cloud evaluation target.")
    parser.add_argument(
        "--target-type",
        default=os.environ.get("EVAL_TARGET_TYPE", _DEFAULT_TYPE),
        choices=_TARGET_TYPES,
        help="model | agent (responses) | hosted_invocations (freeform).",
    )
    parser.add_argument(
        "--name",
        default=os.environ.get("EVAL_TARGET_NAME", _DEFAULT_NAME),
        help="Evaluation display name.",
    )
    parser.add_argument(
        "--dataset",
        default=os.environ.get("EVAL_DATASET_PATH"),
        help="JSONL dataset path (required with --apply).",
    )
    parser.add_argument("--apply", action="store_true", help="Create the eval + run.")
    args = parser.parse_args(argv)

    if not args.apply:
        preflight(args)
        return

    required = ["AZURE_AI_PROJECT_ENDPOINT", "AZURE_AI_MODEL_DEPLOYMENT_NAME"]
    if args.target_type in ("agent", "hosted_invocations"):
        required.append("AZURE_AI_AGENT_NAME")
    for var in required:
        if not os.environ.get(var):
            parser.error(f"{var} is required with --apply.")
    if not args.dataset:
        parser.error("--dataset is required with --apply (EVAL_DATASET_PATH env also works).")
    if not Path(args.dataset).is_file():
        parser.error(f"Dataset file not found: {args.dataset}")
    apply(args)


if __name__ == "__main__":
    main()
