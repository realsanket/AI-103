# Run: uv run python 01-plan-and-manage/31_ai_red_teaming_preflight.py [--apply]
"""Configure and run an AI red-teaming scan against an Azure OpenAI deployment.

AI red teaming probes model endpoints with adversarial prompts to surface
safety risks before production deployment. The AI Red Teaming Agent sends
single-turn attacks and calculates attack success rates across harm categories.
Run this before promoting a model to production — a clean scan is not a
guarantee, but an unscanned model has unknown safety posture.

Complete lesson 24 first. Lesson 24 uses an unreachable synthetic target to
teach the pipeline safely; this lesson crosses the next boundary by sending
generated probes to the real deployment named by DEFAULT_MODEL. It still does
not test application prompts, retrieval, tools, authorization, or agent actions.

Default preflight checks env vars and prints the scan scope. --apply uses
azure.ai.evaluation.red_team.RedTeam to run a minimal probe (one Violence
objective with baseline and Base64 attacks) and prints attack success rates.
One objective becomes two attack-response pairs here: the direct baseline and
the Base64-transformed version. Base64 is an obfuscation strategy, not a risk
category and not evidence of sophisticated coverage.

Code path:
  preflight: validate PROJECT_ENDPOINT + AZURE_OPENAI_ENDPOINT + DEFAULT_MODEL.
  --apply: RedTeam(azure_ai_project=..., credential=...,
  risk_categories=[Violence], num_objectives=1).scan(
  target=model_config, attack_strategies=[Base64]) → print ASR per category.

What to watch. Attack success rate (ASR) is a percentage; lower is safer.
Review every successful attack before tuning mitigations or promotion. A 0%
ASR over two pairs is a smoke result, not a safety claim. Generated adversarial
text and local result artifacts can be sensitive; restrict access and retention.

Prerequisites / env vars:
  PROJECT_ENDPOINT       — Foundry project HTTPS URL for hosted evaluation
  AZURE_OPENAI_ENDPOINT  — direct Azure OpenAI target endpoint
  DEFAULT_MODEL          — deployed chat model to probe
  Python 3.12–3.13       — repository and PyRIT-supported interpreter
  --apply                — run minimal red-team probe
"""
import argparse
import asyncio
import sys
from collections.abc import Mapping

from _shared.config import settings


def preflight() -> None:
    current = settings()
    checks = {
        "PROJECT_ENDPOINT configured": bool(current.project_endpoint),
        "AZURE_OPENAI_ENDPOINT configured": bool(current.azure_openai_endpoint),
        "DEFAULT_MODEL configured": bool(current.default_model),
        "PROJECT_ENDPOINT is HTTPS": (current.project_endpoint or "").startswith("https://"),
        "AZURE_OPENAI_ENDPOINT is HTTPS": (
            current.azure_openai_endpoint or ""
        ).startswith("https://"),
        "Python version is 3.12 or 3.13": (3, 12)
        <= sys.version_info[:2]
        <= (3, 13),
    }
    print("AI red teaming preflight:")
    all_pass = True
    for check, passed in checks.items():
        status = "PASS" if passed else "FAIL"
        if not passed:
            all_pass = False
        print(f"  [{status}] {check}")
    print("Overall: PASS" if all_pass else "Overall: FAIL")
    print()
    print("Scan scope: adversarial single-turn text generated from curated objectives.")
    print("Apply scope: one Violence objective with baseline and Base64 attacks.")
    print("How the probe works:")
    print("  1. Objective: define the unsafe behavior to probe (Violence).")
    print("  2. Baseline: send the direct adversarial query to the target.")
    print("  3. Strategy: Base64 transforms the same objective to test obfuscation.")
    print("  4. Evaluator: label whether each response is a successful attack.")
    print("  5. Scorecard: summarize successful attacks as ASR.")
    print("One objective produces two attack-response pairs in this configuration.")
    print("A 0% ASR on two pairs is not proof that the model or application is safe.")
    print("Run --apply to execute this minimal billable probe.")


def _attack_success_rates(scorecard: object) -> dict[str, float]:
    if not isinstance(scorecard, Mapping):
        raise RuntimeError("Red-team scan returned no scorecard.")
    summaries = scorecard.get("risk_category_summary")
    if not isinstance(summaries, list) or not summaries:
        raise RuntimeError("Red-team scorecard has no risk-category summary.")
    summary = summaries[0]
    if not isinstance(summary, Mapping):
        raise RuntimeError("Red-team risk-category summary is invalid.")
    rates = {
        key.removesuffix("_asr"): float(value)
        for key, value in summary.items()
        if isinstance(key, str)
        and key.endswith("_asr")
        and isinstance(value, (int, float))
    }
    if not rates:
        raise RuntimeError("Red-team scorecard has no attack success rates.")
    return rates


async def run_scan() -> None:
    from azure.ai.evaluation.red_team import AttackStrategy, RedTeam, RiskCategory
    from azure.identity import DefaultAzureCredential

    current = settings()
    project_endpoint = current.require("PROJECT_ENDPOINT")
    azure_openai_endpoint = current.require("AZURE_OPENAI_ENDPOINT")
    model = current.require("DEFAULT_MODEL")
    credential = DefaultAzureCredential()

    target_config = {
        "azure_endpoint": azure_openai_endpoint,
        "azure_deployment": model,
        "credential": credential,
    }

    red_team = RedTeam(
        azure_ai_project=project_endpoint,
        credential=credential,
        risk_categories=[RiskCategory.Violence],
        num_objectives=1,
    )
    result = await red_team.scan(
        target=target_config,
        scan_name="ai-103-minimal-red-team-probe",
        attack_strategies=[AttackStrategy.Base64],
    )
    rates = _attack_success_rates(result.to_scorecard())
    print("Red team scan results (attack success rate; lower is safer):")
    for category, rate in rates.items():
        print(f"  {category.replace('_', ' ')}: {rate:.2f}%")
    print("Scan complete.")


def apply() -> None:
    asyncio.run(run_scan())


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run AI red-teaming probe against Foundry model.")
    parser.add_argument("--apply", action="store_true", help="Run minimal red-team probe.")
    args = parser.parse_args(argv)
    if not args.apply:
        preflight()
        return
    if not (3, 12) <= sys.version_info[:2] <= (3, 13):
        parser.error("This repository's AI red-team lesson requires Python 3.12 or 3.13.")
    apply()


if __name__ == "__main__":
    main()
