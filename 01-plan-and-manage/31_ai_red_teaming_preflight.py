# Run: uv run python 01-plan-and-manage/31_ai_red_teaming_preflight.py [--apply]
"""Configure and run an AI red-teaming scan against a Foundry-hosted model.

AI red teaming probes model endpoints with adversarial prompts to surface
safety risks before production deployment. Foundry's red-teaming orchestrator
sends multi-turn attacks and scores responses across harm categories. Run this
before promoting a model to production — a clean scan is not a guarantee, but
an unscanned model has unknown safety posture.

Default preflight checks env vars and prints the scan scope. --apply uses
azure.ai.evaluation.red_team.RedTeamingOrchestrator to run a minimal probe
(1 attack, violence category) and prints the risk scores.

Code path:
  preflight: validate PROJECT_ENDPOINT + DEFAULT_MODEL + AZURE_SUBSCRIPTION_ID.
  --apply: RedTeamingOrchestrator(azure_ai_project=..., credential=...,
  target=model_config, attack_strategies=[BASE64], risk_categories=[VIOLENCE],
  num_objectives=1).orchestrate() → print risk_scores per category.

What to watch. risk_score per category: 0.0 = no harm detected, 1.0 = harm.
High scores = content filter tuning needed before promotion.

Prerequisites / env vars:
  PROJECT_ENDPOINT          — Foundry project HTTPS URL
  DEFAULT_MODEL             — deployed chat model to probe
  AZURE_SUBSCRIPTION_ID     — subscription for scan resource
  AZURE_RESOURCE_GROUP      — resource group (optional)
  AZURE_PROJECT_NAME        — project name (optional)
  --apply                   — run minimal red-team probe
"""
import argparse
import os

from _shared.config import settings


def preflight() -> None:
    current = settings()
    checks = {
        "PROJECT_ENDPOINT configured": bool(current.project_endpoint),
        "DEFAULT_MODEL configured": bool(current.default_model),
        "AZURE_SUBSCRIPTION_ID set": bool(os.environ.get("AZURE_SUBSCRIPTION_ID")),
        "PROJECT_ENDPOINT is HTTPS": (current.project_endpoint or "").startswith("https://"),
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
    print("Scan scope: adversarial multi-turn conversations (not real harmful content).")
    print("Categories: violence, sexual, self-harm, hate/fairness.")
    print("Attack strategies: direct, indirect, BASE64, role-play, and more.")
    print("Run --apply to execute a minimal 1-attack probe.")


def apply() -> None:
    from azure.ai.evaluation.red_team import AttackStrategy, RedTeamingOrchestrator, RiskCategory
    from azure.identity import DefaultAzureCredential

    current = settings()
    endpoint = current.require("PROJECT_ENDPOINT")
    model = current.require("DEFAULT_MODEL")

    target_config = {
        "azure_endpoint": endpoint,
        "azure_deployment": model,
        "api_version": "2024-10-21",
    }
    azure_ai_project = {
        "subscription_id": os.environ.get("AZURE_SUBSCRIPTION_ID", ""),
        "resource_group_name": os.environ.get("AZURE_RESOURCE_GROUP", ""),
        "project_name": os.environ.get("AZURE_PROJECT_NAME", ""),
    }

    orchestrator = RedTeamingOrchestrator(
        azure_ai_project=azure_ai_project,
        credential=DefaultAzureCredential(),
        target=target_config,
        attack_strategies=[AttackStrategy.BASE64],
        risk_categories=[RiskCategory.VIOLENCE],
        num_objectives=1,
    )
    result = orchestrator.orchestrate()
    print("Red team scan results:")
    for category, score in (result.get("risk_scores") or {}).items():
        print(f"  {category}: {score:.3f}")
    print("Scan complete.")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run AI red-teaming probe against Foundry model.")
    parser.add_argument("--apply", action="store_true", help="Run minimal red-team probe.")
    args = parser.parse_args(argv)
    if not args.apply:
        preflight()
        return
    apply()


if __name__ == "__main__":
    main()
