# Run: uv run python 01-plan-and-manage/35_rag_quality_gate.py [--data <jsonl>] [--apply] [--min-pass-rate 0.8]
# Practice-question coverage: Q19, Q26, Q34, Q66, Q103, Q168.
"""RAG quality gate — built-in RAG evaluators and token analytics that can block a merge.

A RAG answer can fail in different places, and each failure has its own signal:

  Signal (evaluator)            Question it answers                         Symptom it catches
  groundedness                  Is the response supported by the context?   answers not backed by retrieved docs
  relevance                     Does the response address the query?        on-topic docs, off-topic answer
  retrieval                     Is the retrieved context relevant?          weak search results after a content update
  response_completeness         Does the response cover the ground truth?   partial answers
  completion-token analytics    Is the response within its token budget?    long answers raising inference cost

These are the "RAG evaluators" (AI-quality, LLM-judge) from azure-ai-evaluation.
Policy violations and leaked proprietary text are different signals: use the
risk-and-safety evaluators and protected-material detection (lessons 18, 21, 22).

Gate: every evaluator scores 1-5 against `--threshold` and reports pass/fail per
row. The gate fails when an evaluator's pass rate is below `--min-pass-rate` or
too many responses exceed the token budget, and the script exits with code 1.
Wire it as a required status check in GitHub (branch protection → "Require
status checks to pass") so a pull request cannot merge on a failing evaluation.

Code path:
  Default   load_rows() validates query/context/response/ground_truth columns,
            token_report() uses recorded completion_tokens; no model calls.
  --apply   evaluate(data=<jsonl>, evaluators={...}) with an Azure OpenAI judge
            deployment → quality_gate() → exit 1 on failure. `--log-to-project`
            also uploads the run to the Foundry project for review.

Prerequisites / env vars (for --apply):
  AZURE_OPENAI_ENDPOINT — judge endpoint (Entra ID; Cognitive Services OpenAI User)
  DEFAULT_MODEL         — judge deployment (or --judge-model)
  PROJECT_ENDPOINT      — only with --log-to-project (Foundry User)
The sample data is synthetic Northwind FAQ content; rows `off-topic` and
`ungrounded-and-long` are deliberately bad so the gate has something to catch.
"""
import argparse
import json
from pathlib import Path
import sys

from _shared.config import settings

DEFAULT_DATA = Path(__file__).resolve().parent / "data" / "rag_quality_sample.jsonl"
REQUIRED_COLUMNS = ("query", "context", "response", "ground_truth")
EVALUATORS = ("groundedness", "relevance", "retrieval", "response_completeness")


def load_rows(path: Path) -> list[dict]:
    rows = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        row = json.loads(line)
        missing = [column for column in REQUIRED_COLUMNS if not str(row.get(column, "")).strip()]
        if missing:
            raise ValueError(f"{path.name} line {number} is missing {', '.join(missing)}")
        rows.append(row)
    if not rows:
        raise ValueError(f"{path.name} has no rows")
    return rows


def token_report(rows: list[dict], budget: int, max_over_budget_rate: float = 0.2) -> dict:
    """Completion-token analytics from recorded usage (for example exported traces)."""
    tokens = [int(row["completion_tokens"]) for row in rows if "completion_tokens" in row]
    over = [row.get("id", str(index)) for index, row in enumerate(rows) if int(row.get("completion_tokens", 0)) > budget]
    rate = len(over) / len(tokens) if tokens else 0.0
    return {
        "rows_with_usage": len(tokens),
        "mean_completion_tokens": round(sum(tokens) / len(tokens), 1) if tokens else None,
        "budget": budget,
        "over_budget": over,
        "passed": rate <= max_over_budget_rate,
    }


def quality_gate(eval_rows: list[dict], min_pass_rate: float, names: tuple[str, ...] = EVALUATORS) -> dict:
    """Pass rate per evaluator from `outputs.<name>.<name>_result` ("pass"/"fail")."""
    report = {}
    for name in names:
        results = [row.get(f"outputs.{name}.{name}_result") for row in eval_rows]
        scored = [result for result in results if result in ("pass", "fail")]
        rate = sum(result == "pass" for result in scored) / len(scored) if scored else 0.0
        report[name] = {"pass_rate": round(rate, 3), "scored": len(scored), "passed": bool(scored) and rate >= min_pass_rate}
    return report


def run_evaluation(data: Path, judge: str, threshold: float, log_to_project: bool) -> list[dict]:
    from azure.ai.evaluation import (
        GroundednessEvaluator,
        RelevanceEvaluator,
        ResponseCompletenessEvaluator,
        RetrievalEvaluator,
        evaluate,
    )
    from azure.identity import DefaultAzureCredential

    s = settings()
    credential = DefaultAzureCredential()
    model_config = {"azure_endpoint": s.require("AZURE_OPENAI_ENDPOINT"), "azure_deployment": judge}
    evaluators = {
        "groundedness": GroundednessEvaluator(model_config, threshold=threshold, credential=credential),
        "relevance": RelevanceEvaluator(model_config, threshold=threshold, credential=credential),
        "retrieval": RetrievalEvaluator(model_config, threshold=threshold, credential=credential),
        "response_completeness": ResponseCompletenessEvaluator(model_config, threshold=threshold, credential=credential),
    }
    result = evaluate(
        data=str(data),
        evaluators=evaluators,
        evaluation_name="rag-quality-gate",
        azure_ai_project=s.require("PROJECT_ENDPOINT") if log_to_project else None,
    )
    if result.get("studio_url"):
        print(f"Foundry evaluation run: {result['studio_url']}")
    return result.get("rows", [])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--apply", action="store_true", help="Run the LLM-judge evaluators (billable).")
    parser.add_argument("--judge-model", default=None, help="Judge deployment (defaults to DEFAULT_MODEL).")
    parser.add_argument("--threshold", type=float, default=3.0, help="Per-row pass mark on the 1-5 scale.")
    parser.add_argument("--min-pass-rate", type=float, default=0.8)
    parser.add_argument("--token-budget", type=int, default=300)
    parser.add_argument("--max-over-budget-rate", type=float, default=0.2)
    parser.add_argument("--log-to-project", action="store_true", help="Also upload results to PROJECT_ENDPOINT.")
    args = parser.parse_args(argv)

    rows = load_rows(args.data)
    tokens = token_report(rows, args.token_budget, args.max_over_budget_rate)
    print(f"Dataset {args.data.name}: {len(rows)} rows with {', '.join(REQUIRED_COLUMNS)}")
    print(f"Token analytics: {json.dumps(tokens)}")
    if not args.apply:
        print(f"Evaluators planned: {', '.join(EVALUATORS)} (threshold {args.threshold}, min pass rate {args.min_pass_rate}).")
        print("Preflight only: no judge-model calls. Re-run with --apply to evaluate and enforce the gate.")
        return 0

    judge = args.judge_model or settings().default_model
    report = quality_gate(run_evaluation(args.data, judge, args.threshold, args.log_to_project), args.min_pass_rate)
    for name, outcome in report.items():
        print(f"  {'PASS' if outcome['passed'] else 'FAIL'}  {name:<22} pass rate {outcome['pass_rate']:.0%} ({outcome['scored']} scored)")
    print(f"  {'PASS' if tokens['passed'] else 'FAIL'}  completion tokens      over budget: {tokens['over_budget'] or 'none'}")
    passed = tokens["passed"] and all(outcome["passed"] for outcome in report.values())
    print("Quality gate:", "PASSED" if passed else "FAILED — block the merge and inspect failing rows.")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
