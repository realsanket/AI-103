# Run: uv run python 01-plan-and-manage/30_evaluation_cicd_preflight.py [--apply]
# Practice-question coverage: Q9, Q19, Q49, Q101, Q130.
"""Validate environment for running AI evaluations from CI/CD pipelines.

Foundry evaluations run in GitHub Actions and Azure DevOps. Two patterns:

  1. Microsoft's `microsoft/ai-agent-evals` GitHub Action (preview) invokes
     Foundry agents with test queries and runs catalog evaluators. Inputs:
     `azure-ai-project-endpoint`, `deployment-name`, `agent-ids`
     (`name:version`), and `data-path` — a JSON file that lists the
     `evaluators` and the `data` rows. Authenticate with `azure/login` using
     OpenID Connect (`permissions: id-token: write`), never a stored secret.
  2. Your own gate script with the azure-ai-evaluation SDK (lesson 35) that
     exits non-zero when thresholds fail.

  Either way, make the workflow a required status check in branch protection
  so a pull request cannot merge while the evaluation fails.

Default preflight checks configuration and prints both workflow patterns.
--apply runs a one-sample CoherenceEvaluator locally (judge = DEFAULT_MODEL on
AZURE_OPENAI_ENDPOINT) and, when PROJECT_ENDPOINT is set, logs the run to the
Foundry project.

Code path:
  preflight: check env vars + print CI pipeline snippets.
  --apply: write one sample row to a temporary JSONL (evaluate() takes a file
  path) → CoherenceEvaluator(model_config={azure_endpoint, azure_deployment},
  credential=DefaultAzureCredential()) → evaluate(...) → print score + metrics.

What to watch. --apply: coherence score in 1–5 range. 401/403 = the CI
identity lacks Cognitive Services OpenAI User on the judge resource.

Prerequisites / env vars:
  AZURE_OPENAI_ENDPOINT     — judge endpoint (https://<resource>.openai.azure.com)
  DEFAULT_MODEL             — judge deployment name
  PROJECT_ENDPOINT          — optional; logs the run to the Foundry project
  --apply                   — run the one-sample evaluation
"""
import argparse
import json
import tempfile
from pathlib import Path

from _shared.config import settings

AGENT_EVALS_WORKFLOW = """\
permissions:
  id-token: write        # OIDC token for azure/login; no stored secret
  contents: read
jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: azure/login@v2
        with:
          client-id: ${{ vars.AZURE_CLIENT_ID }}
          tenant-id: ${{ vars.AZURE_TENANT_ID }}
          subscription-id: ${{ vars.AZURE_SUBSCRIPTION_ID }}
      - uses: microsoft/ai-agent-evals@v3-beta
        with:
          azure-ai-project-endpoint: ${{ vars.PROJECT_ENDPOINT }}
          deployment-name: ${{ vars.JUDGE_DEPLOYMENT }}
          agent-ids: "support-agent:3"
          data-path: ${{ github.workspace }}/evals/agent-evals.json"""


def preflight() -> None:
    current = settings()
    checks = {
        "AZURE_OPENAI_ENDPOINT configured (judge)": bool(current.azure_openai_endpoint),
        "DEFAULT_MODEL configured (judge deployment)": bool(current.default_model),
        "PROJECT_ENDPOINT configured (optional logging)": bool(current.project_endpoint),
    }
    print("CI/CD evaluation preflight:")
    for check, passed in checks.items():
        print(f"  [{'PASS' if passed else 'MISSING'}] {check}")
    print()
    print("GitHub Actions — Foundry agent evaluation action (pull_request trigger):")
    print(AGENT_EVALS_WORKFLOW)
    print()
    print("GitHub Actions — self-hosted RAG gate (exits 1 on failure):")
    print("  - run: uv run python 01-plan-and-manage/35_rag_quality_gate.py --apply")
    print("Make the job a required status check so a failing evaluation blocks the merge.")
    print()
    print("Azure DevOps pattern:")
    print("  - task: AzureCLI@2   # workload identity federation service connection")
    print("    inputs:")
    print("      scriptType: bash")
    print("      inlineScript: uv run python 01-plan-and-manage/35_rag_quality_gate.py --apply")


def apply() -> None:
    from azure.ai.evaluation import CoherenceEvaluator, evaluate
    from azure.identity import DefaultAzureCredential

    current = settings()
    evaluator = CoherenceEvaluator(
        model_config={
            "azure_endpoint": current.require("AZURE_OPENAI_ENDPOINT"),
            "azure_deployment": current.require("DEFAULT_MODEL"),
        },
        credential=DefaultAzureCredential(),
    )
    row = {
        "query": "What is Microsoft Foundry?",
        "response": "Microsoft Foundry is a unified platform for building, evaluating, and deploying AI apps and agents.",
    }
    with tempfile.TemporaryDirectory() as folder:
        data = Path(folder) / "ci_sample.jsonl"
        data.write_text(json.dumps(row) + "\n", encoding="utf-8")
        result = evaluate(
            data=str(data),
            evaluators={"coherence": evaluator},
            evaluation_name="ci-coherence-smoke",
            azure_ai_project=current.project_endpoint or None,
        )
    print("Evaluation result:")
    for result_row in result.get("rows", []):
        print(f"  coherence: {result_row.get('outputs.coherence.coherence', 'n/a')}")
    for k, v in result.get("metrics", {}).items():
        print(f"  {k}: {v:.3f}" if isinstance(v, float) else f"  {k}: {v}")
    if result.get("studio_url"):
        print(f"Foundry run: {result['studio_url']}")
    print("CI evaluation complete.")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Validate CI/CD evaluation setup.")
    parser.add_argument("--apply", action="store_true", help="Run a one-sample evaluation (judge model call).")
    args = parser.parse_args(argv)
    if not args.apply:
        preflight()
        return
    apply()


if __name__ == "__main__":
    main()
