# Run: uv run python 01-plan-and-manage/30_evaluation_cicd_preflight.py [--apply]
# Practice-question coverage: Q9, Q19, Q49, Q101, Q130.
"""Validate environment for running AI evaluations from CI/CD pipelines.

Azure AI Foundry evaluations can run in GitHub Actions and Azure DevOps via
the azure-ai-evaluation SDK. CI evaluation catches regression between model
versions before production promotion. This lesson validates the env and
optionally runs a minimal cloud evaluation using the Foundry eval endpoint.

Default preflight checks PROJECT_ENDPOINT and DEFAULT_MODEL and prints the
GitHub Actions and Azure DevOps pipeline patterns. --apply submits a single-
sample coherence evaluation and prints the result score.

Code path:
  preflight: check env vars + print CI pipeline snippets.
  --apply: CoherenceEvaluator(model_config={azure_endpoint, azure_deployment})
  + evaluate(data=[one sample], evaluators={"coherence": evaluator})
  → print per-sample score and aggregate metric.

What to watch. --apply: coherence score in 1–5 range. AuthenticationError
= missing AZURE_CLIENT_ID or no logged-in CLI session.

Prerequisites / env vars:
  PROJECT_ENDPOINT          — Foundry project HTTPS URL
  DEFAULT_MODEL             — deployed chat model name
  AZURE_SUBSCRIPTION_ID     — subscription (optional for cloud logging)
  AZURE_RESOURCE_GROUP      — resource group (optional for cloud logging)
  AZURE_PROJECT_NAME        — project name (optional for cloud logging)
  --apply                   — run one-sample cloud evaluation
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
    print("CI/CD evaluation preflight:")
    all_pass = True
    for check, passed in checks.items():
        status = "PASS" if passed else "FAIL"
        if not passed:
            all_pass = False
        print(f"  [{status}] {check}")
    print("Overall: PASS" if all_pass else "Overall: FAIL — resolve before wiring to CI pipeline.")
    print()
    print("GitHub Actions pattern:")
    print("  - uses: azure/login@v2")
    print("  - run: uv run python 01-plan-and-manage/30_evaluation_cicd_preflight.py --apply")
    print()
    print("Azure DevOps pattern:")
    print("  - task: AzureCLI@2")
    print("    inputs:")
    print("      scriptType: bash")
    print("      inlineScript: uv run python 01-plan-and-manage/30_evaluation_cicd_preflight.py --apply")


def apply() -> None:
    from azure.ai.evaluation import CoherenceEvaluator, evaluate

    current = settings()
    endpoint = current.require("PROJECT_ENDPOINT")
    model = current.require("DEFAULT_MODEL")

    azure_ai_project = {
        "subscription_id": os.environ.get("AZURE_SUBSCRIPTION_ID", ""),
        "resource_group_name": os.environ.get("AZURE_RESOURCE_GROUP", ""),
        "project_name": os.environ.get("AZURE_PROJECT_NAME", ""),
    }

    evaluator = CoherenceEvaluator(model_config={
        "azure_endpoint": endpoint,
        "azure_deployment": model,
        "api_version": "2024-10-21",
    })

    data = [{"query": "What is Azure AI Foundry?",
              "response": "Azure AI Foundry is a unified platform for building and deploying AI applications."}]

    use_cloud = all(azure_ai_project.values())
    result = evaluate(
        data=data,
        evaluators={"coherence": evaluator},
        azure_ai_project=azure_ai_project if use_cloud else None,
    )
    print("Evaluation result:")
    for row in result.get("rows", []):
        print(f"  coherence: {row.get('outputs.coherence.coherence', 'n/a')}")
    for k, v in result.get("metrics", {}).items():
        print(f"  {k}: {v:.3f}" if isinstance(v, float) else f"  {k}: {v}")
    print("CI evaluation complete.")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Validate CI/CD evaluation setup.")
    parser.add_argument("--apply", action="store_true", help="Submit one-sample cloud evaluation.")
    args = parser.parse_args(argv)
    if not args.apply:
        preflight()
        return
    apply()


if __name__ == "__main__":
    main()
