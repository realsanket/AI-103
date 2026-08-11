# Run: uv run python 01-plan-and-manage/24_red_teaming.py
"""Run one bounded AI Red Teaming Agent smoke scan against synthetic output.

Prerequisites: Python 3.10–3.13, `azure-ai-evaluation[redteam]`, a Foundry
project referenced by `AZURE_AI_PROJECT`, and Azure identity. Evaluation
guidance requires Foundry User for the project managed identity. AI red
teaming currently supports East US 2 and North Central US according to
evaluation region and limits guidance. Each scan generates attack prompts and
runs hosted evaluation, so it can consume model and evaluation capacity and
incur cost.

Use this only to verify local SDK wiring and result flow before a reviewed
red-team exercise. Real testing belongs in a purple environment: nonproduction
with production-like resources. AI Red Teaming Agent supports single-turn,
text-only scenarios. Agentic risks need cloud red teaming's minimally
sandboxed environment; this small callback scan does not test them.

Safety boundary: this lesson accepts no endpoint, model configuration, or
application callback. It sends all generated prompts only to the explicit
safe synthetic callback below, which returns a fixed refusal. No customer
data, real tools, secrets, production traffic, or destructive actions are
reachable. No scan starts without `--apply`.
"""
from __future__ import annotations

import argparse
import asyncio
import os
import sys


def safe_synthetic_callback(_: str) -> str:
    """Return fixed safe text; never call an application, model, or tool."""
    return "I can't help with harmful content or unsafe actions."


def preflight() -> str:
    """Return exact scan side effect without creating a red-team client."""
    return "\n".join(
        [
            "PREVIEW: no red-team scan started and no prompts generated.",
            "Would create one RedTeam client for configured Foundry project.",
            "Would scan only safe_synthetic_callback.",
            "Would use one Violence objective and baseline direct prompts only.",
            "Would send no prompt to a real model, endpoint, tool, or application.",
            "Run again with --apply to perform exactly these actions.",
        ]
    )


async def run_safe_scan() -> None:
    """Start the deliberately bounded, synthetic-only scan."""
    from azure.ai.evaluation.red_team import RedTeam, RiskCategory
    from azure.identity import DefaultAzureCredential

    project = os.environ["AZURE_AI_PROJECT"]
    red_team = RedTeam(
        azure_ai_project=project,
        credential=DefaultAzureCredential(),
        risk_categories=[RiskCategory.Violence],
        num_objectives=1,
    )
    result = await red_team.scan(
        target=safe_synthetic_callback,
        scan_name="northwind-safe-synthetic-smoke-scan",
    )
    print(result)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run safe synthetic red-team smoke scan.")
    parser.add_argument("--apply", action="store_true", help="Start listed scan.")
    args = parser.parse_args()
    if not args.apply:
        print(preflight())
        return
    if sys.version_info[:2] not in {(3, 10), (3, 11), (3, 12), (3, 13)}:
        parser.error("AI Red Teaming Agent requires Python 3.10 through 3.13.")
    if not os.environ.get("AZURE_AI_PROJECT"):
        parser.error("AZURE_AI_PROJECT is required with --apply.")
    asyncio.run(run_safe_scan())


if __name__ == "__main__":
    main()
