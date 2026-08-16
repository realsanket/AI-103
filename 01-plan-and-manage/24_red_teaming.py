# Run: uv run python 01-plan-and-manage/24_red_teaming.py
"""Learn the red-team workflow with one bounded scan against synthetic output.

Red teaming is authorized adversarial testing: define a risk, generate probes,
send them to a target, evaluate each response, and review the failures. It
finds weaknesses to investigate; it is not a runtime guardrail, a compliance
certificate, or proof that an application is safe.

This is the beginner lab before lesson 31. Its target is a fixed callback that
always refuses, so learners can inspect the objective -> target -> evaluator ->
scorecard flow without exposing a real model, agent, tool, or customer system.

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

Code paths:
  Preflight — define the red-team pipeline and print every side effect.
  --apply   — generate one Violence objective, send the baseline probe only
              to safe_synthetic_callback, evaluate the refusal, and report ASR.

What to watch. The expected ASR is 0%, but that proves only that the fixed
callback refused this tiny sample. Generated adversarial text and result
artifacts still require controlled access, retention, and human review.

Prerequisites / env vars:
  PROJECT_ENDPOINT  — Foundry project used by hosted safety evaluation
  --apply           — run the one-objective billable synthetic scan
  Python 3.12–3.13  — repository and PyRIT-supported interpreter
"""
from __future__ import annotations

import argparse
import asyncio
import sys

from _shared.config import settings


def safe_synthetic_callback(_: str) -> str:
    """Return fixed safe text; never call an application, model, or tool."""
    return "I can't help with harmful content or unsafe actions."


def preflight() -> str:
    """Return exact scan side effect without creating a red-team client."""
    project_status = "configured" if settings().project_endpoint else "missing"
    return "\n".join(
        [
            "PREVIEW: no red-team scan started and no prompts generated.",
            f"PROJECT_ENDPOINT: {project_status}.",
            "Learning map: objective -> strategy -> target -> evaluator -> scorecard.",
            "- Objective: the unsafe behavior the probe tries to surface.",
            "- Target: the system receiving the probe; here it is a fixed refusal callback.",
            "- Evaluator: labels whether the response represents a successful attack.",
            "- ASR: successful attacks / total attacks; lower is safer, not proof of safety.",
            "Would create one RedTeam client for configured Foundry project.",
            "Would scan only safe_synthetic_callback.",
            "Would use one Violence objective and baseline direct prompts only.",
            "Would send no generated attack to a real target model, tool, or application.",
            "Foundry-hosted generation and evaluation still process the synthetic pair.",
            "Expected ASR: 0%; this validates wiring, not a real system's safety.",
            "Run again with --apply to perform exactly these actions.",
        ]
    )


async def run_safe_scan() -> None:
    """Start the deliberately bounded, synthetic-only scan."""
    from azure.ai.evaluation.red_team import RedTeam, RiskCategory
    from azure.identity import DefaultAzureCredential

    project = settings().require("PROJECT_ENDPOINT")
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
    if sys.version_info[:2] not in {(3, 12), (3, 13)}:
        parser.error("This repository's AI red-team lesson requires Python 3.12 or 3.13.")
    if not settings().project_endpoint:
        parser.error("PROJECT_ENDPOINT is required with --apply.")
    asyncio.run(run_safe_scan())


if __name__ == "__main__":
    main()
