# Run: uv run python 01-plan-and-manage/22_continuous_evaluation.py
# Practice-question coverage: Q26, Q80.
"""Create a sampled continuous Foundry evaluation rule for an existing agent.

Prerequisites: Python 3.12, `azure-ai-projects`, Foundry project and agent,
connected Application Insights, and `AZURE_AI_PROJECT_ENDPOINT` plus
`AZURE_AI_AGENT_NAME`. The project's managed identity needs Foundry User.
Use a region supported by the chosen evaluator; risk and safety evaluators are
available in East US 2, North Central US, France Central, Sweden Central,
Switzerland West, and Australia East. Continuous evaluation needs traced agent
traffic and writes results to connected Application Insights.

Use this for sampled production monitoring after an offline baseline from
lesson 22. The rule evaluates completed responses, not every request: its
hourly cap controls evaluator volume. Hosted evaluator calls, Application
Insights ingestion, and stored telemetry can incur cost. Add quality rubrics
only after validating them on a labelled dataset.

Safety boundary: no rule or evaluation is created without `--apply`. This
lesson does not create an agent, change its tools, block responses, alter
Application Insights retention, or grant roles. It only targets an existing
agent by name. Treat traces as production data and ensure telemetry redaction
before enabling monitoring.
"""
from __future__ import annotations

import argparse
import os

from _shared.config import load_env

RULE_ID = "northwind-continuous-violence"
MAX_HOURLY_RUNS = 10


def preflight(rule_id: str = RULE_ID, max_hourly_runs: int = MAX_HOURLY_RUNS) -> str:
    """Return exact cloud side effects without contacting Azure."""
    agent = os.environ.get("AZURE_AI_AGENT_NAME", "<unset>")
    return "\n".join(
        [
            "PREVIEW: no cloud resources created or updated.",
            "Would create Foundry evaluation: Northwind continuous violence evaluation",
            f"Would create or update enabled rule: {rule_id}",
            f"Would target completed responses from agent: {agent}",
            f"Would use evaluator: builtin.violence; maximum runs per hour: {max_hourly_runs}",
            "Run again with --apply to perform exactly these actions.",
        ]
    )


def create_rule(rule_id: str, max_hourly_runs: int) -> None:
    """Create evaluation then attach it to response-completed events."""
    from azure.ai.projects import AIProjectClient
    from azure.ai.projects.models import (
        ContinuousEvaluationRuleAction,
        EvaluationRule,
        EvaluationRuleEventType,
        EvaluationRuleFilter,
    )
    from azure.identity import DefaultAzureCredential

    project = AIProjectClient(
        endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
        credential=DefaultAzureCredential(),
    )
    client = project.get_openai_client()
    evaluation = client.evals.create(
        name="Northwind continuous violence evaluation",
        data_source_config={"type": "azure_ai_source", "scenario": "responses"},
        testing_criteria=[
            {
                "type": "azure_ai_evaluator",
                "name": "violence_detection",
                "evaluator_name": "builtin.violence",
            }
        ],
    )
    rule = project.evaluation_rules.create_or_update(
        id=rule_id,
        evaluation_rule=EvaluationRule(
            display_name="Northwind continuous violence evaluation",
            description="Samples completed agent responses for violence evaluation.",
            action=ContinuousEvaluationRuleAction(
                eval_id=evaluation.id, max_hourly_runs=max_hourly_runs
            ),
            event_type=EvaluationRuleEventType.RESPONSE_COMPLETED,
            filter=EvaluationRuleFilter(agent_name=os.environ["AZURE_AI_AGENT_NAME"]),
            enabled=True,
        ),
    )
    print(f"Evaluation created: {evaluation.id}")
    print(f"Continuous rule enabled: {rule.id}")


def main() -> None:
    load_env()
    parser = argparse.ArgumentParser(description="Create sampled continuous evaluation.")
    parser.add_argument("--rule-id", default=RULE_ID)
    parser.add_argument("--max-hourly-runs", type=int, default=MAX_HOURLY_RUNS)
    parser.add_argument("--apply", action="store_true", help="Perform listed cloud writes.")
    args = parser.parse_args()
    if args.max_hourly_runs < 1:
        parser.error("--max-hourly-runs must be at least 1.")
    if not args.apply:
        print(preflight(args.rule_id, args.max_hourly_runs))
        return
    for variable in ("AZURE_AI_PROJECT_ENDPOINT", "AZURE_AI_AGENT_NAME"):
        if not os.environ.get(variable):
            parser.error(f"{variable} is required with --apply.")
    create_rule(args.rule_id, args.max_hourly_runs)


if __name__ == "__main__":
    main()
