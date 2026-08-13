# Run: uv run python 01-plan-and-manage/21_foundry_evaluation.py --dataset path/to/agent-tests.jsonl
"""Create a Foundry agent evaluation from a reviewed JSONL dataset.

Prerequisites: Python 3.12, `azure-ai-projects`, an existing Foundry project,
agent, and Azure OpenAI chat-model deployment. Set
`AZURE_AI_PROJECT_ENDPOINT`, `AZURE_AI_AGENT_NAME`, and
`AZURE_AI_MODEL_DEPLOYMENT_NAME`; this lesson never reads keys. Create or
confirm the Foundry project and agent first, verify the signed-in principal has
the Foundry User role, and choose a supported region for the evaluators you
plan to enable. Batch evaluation supports many regions, but evaluator
availability is narrower: risk and safety evaluators support East US 2, North
Central US, France Central, Sweden Central, Switzerland West, and Australia
East. Confirm current limits and region support before a run.

Use this after curating representative, edge-case, and safety test queries.
It creates a dataset version, evaluation, and evaluation run. Agent calls and
LLM-judge evaluators consume tokens; hosted safety evaluators and storage can
also incur charges. The default criteria cover task adherence and violence;
pass `--rubric` only after reviewing that rubric's dimensions and threshold.

Safety boundary: no cloud write or agent query occurs without `--apply`.
Preflight prints every intended write. Never put production secrets, customer
data, or destructive tool instructions in the dataset. Evaluation observes and
scores behavior; it does not block a live request or authorize a tool call.

Lesson 17 is an application self-critique loop: one model call critiques
another and can regenerate an answer. This lesson creates durable Foundry
evaluation records and applies independent evaluator criteria across a
dataset. They are complementary, not interchangeable.

Task Adherence has three distinct surfaces:
* Lesson 14 calls Content Safety's Task Adherence REST endpoint to detect
  risky planned tool actions.
* A Foundry Task Adherence guardrail annotates and can filter an agent
  workflow at runtime.
* `builtin.task_adherence` below is an offline/continuous evaluation
  criterion that scores adherence; it is not the REST API or a guardrail.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path

_SAMPLE_DATASET = Path("01-plan-and-manage/data/foundry_evaluation_sample.jsonl")


def _setting(name: str) -> str:
    """Read documented evaluation variables without exposing values."""
    return os.environ.get(name, "<unset>")


def testing_criteria(model_deployment: str, rubric_name: str | None = None) -> list[dict]:
    """Return criteria using structured agent output where evaluator needs it."""
    criteria = [
        {
            "type": "azure_ai_evaluator",
            "name": "Task Adherence",
            "evaluator_name": "builtin.task_adherence",
            "initialization_parameters": {"deployment_name": model_deployment},
            "data_mapping": {
                "query": "{{item.query}}",
                "response": "{{sample.output_items}}",
            },
        },
        {
            "type": "azure_ai_evaluator",
            "name": "Violence",
            "evaluator_name": "builtin.violence",
            "data_mapping": {
                "query": "{{item.query}}",
                "response": "{{sample.output_text}}",
            },
        },
    ]
    if rubric_name:
        criteria.insert(
            0,
            {
                "type": "azure_ai_evaluator",
                "name": "Reviewed rubric",
                "evaluator_name": rubric_name,
                "initialization_parameters": {"deployment_name": model_deployment},
                "data_mapping": {
                    "query": "{{item.query}}",
                    "response": "{{sample.output_items}}",
                },
            },
        )
    return criteria


def preflight(dataset: Path | None, rubric_name: str | None = None) -> str:
    """Return exact cloud side effects for a reviewable dry run."""
    criteria = ["builtin.task_adherence", "builtin.violence"]
    if rubric_name:
        criteria.insert(0, rubric_name)
    dataset_path = dataset or _SAMPLE_DATASET
    return "\n".join(
        [
            "PREVIEW: no cloud resources created and no agent queries sent.",
            "Prerequisites checklist:",
            "- Create or confirm a Foundry project and agent before any evaluation run.",
            "- Configure AZURE_AI_PROJECT_ENDPOINT, AZURE_AI_AGENT_NAME, and AZURE_AI_MODEL_DEPLOYMENT_NAME.",
            "- Verify the signed-in principal has the Foundry User role.",
            "- Use a supported region for the evaluators you plan to enable.",
            "- Prepare a JSONL dataset with a query field and keep it under the documented size limits.",
            "- Sample dataset: 01-plan-and-manage/data/foundry_evaluation_sample.jsonl (copy and edit it for your scenario).",
            f"Would upload dataset version from: {dataset_path}",
            "Would create Foundry evaluation: Northwind agent quality evaluation",
            f"Would create one run against agent: {_setting('AZURE_AI_AGENT_NAME')}",
            f"Would use model deployment: {_setting('AZURE_AI_MODEL_DEPLOYMENT_NAME')}",
            f"Would apply criteria: {', '.join(criteria)}",
            "Run again with --apply only after the prerequisites above are in place.",
        ]
    )


def run(dataset: Path, rubric_name: str | None = None) -> None:
    """Perform preflighted dataset upload, evaluation creation, and one run."""
    from azure.ai.projects import AIProjectClient
    from azure.identity import DefaultAzureCredential
    from openai.types.eval_create_params import DataSourceConfigCustom

    endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]
    agent_name = os.environ["AZURE_AI_AGENT_NAME"]
    model = os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"]
    project = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())
    dataset_asset = project.datasets.upload_file(
        name="northwind-agent-evaluation-inputs",
        version="1",
        file_path=str(dataset),
    )
    client = project.get_openai_client()
    evaluation = client.evals.create(
        name="Northwind agent quality evaluation",
        data_source_config=DataSourceConfigCustom(
            type="custom",
            item_schema={
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
            include_sample_schema=True,
        ),
        testing_criteria=testing_criteria(model, rubric_name),  # type: ignore[arg-type]
    )
    evaluation_run = client.evals.runs.create(
        eval_id=evaluation.id,
        name="Northwind agent quality run",
        data_source={
            "type": "azure_ai_target_completions",
            "source": {"type": "file_id", "id": dataset_asset.id},
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
            "target": {"type": "azure_ai_agent", "name": agent_name},
        },
    )
    print(f"Evaluation created: {evaluation.id}")
    print(f"Run started: {evaluation_run.id}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Create a reviewed Foundry evaluation run after setting up a Foundry "
            "project, agent, deployment, evaluator prerequisites, and a JSONL dataset."
        )
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        help=(
            "JSONL rows with a query field. Defaults to the sample dataset at "
            "01-plan-and-manage/data/foundry_evaluation_sample.jsonl."
        ),
    )
    parser.add_argument("--rubric", help="Existing, reviewed Foundry rubric evaluator name.")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Perform listed cloud writes after prerequisites are confirmed.",
    )
    args = parser.parse_args()
    if not args.apply:
        print(preflight(args.dataset, args.rubric))
        return
    if args.dataset is None:
        parser.error("--dataset is required with --apply.")
    if not args.dataset.is_file():
        parser.error(f"Dataset does not exist: {args.dataset}")
    for variable in (
        "AZURE_AI_PROJECT_ENDPOINT",
        "AZURE_AI_AGENT_NAME",
        "AZURE_AI_MODEL_DEPLOYMENT_NAME",
    ):
        if not os.environ.get(variable):
            parser.error(f"{variable} is required with --apply.")
    run(args.dataset, args.rubric)


if __name__ == "__main__":
    main()
