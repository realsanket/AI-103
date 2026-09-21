# Run: uv run python 01-plan-and-manage/34_cloud_evaluation_results.py --eval-id <id> --run-id <id>
"""Poll a cloud evaluation run and summarize per-evaluator pass rates.

WHAT
────
Evaluation runs are asynchronous. This lesson reads a completed run and
prints the summary shape documented at cloud-evaluation-results.md:

  - `result_counts`             passed / failed / total
  - `per_testing_criteria_results`  per-evaluator passed/failed/pass_rate
  - `latency.target`            p50_ms, p95_ms, sample_count  (model targets)
  - `estimated_cost.target`     currency, completeness, model_costs,
                                unpriced_models  (model targets, Global
                                Standard, when priceable)
  - `report_url`                portal link for row inspection

Read-only. The lesson exposes `--apply` for interface symmetry with lessons
32/33 but performs no writes; the flag is a no-op here.

WHY
───
Aggregate scores are the release-gate primitive. Latency and cost are the
run-wide diagnostic surface. Row-level output items live behind pagination
via `openai_client.evals.runs.output_items.list(...)`.

Cost caveat (verbatim from docs): the target cost estimate is based on
reported token usage and published list prices. It excludes evaluator model
usage and evaluation runtime costs, and it does not account for negotiated
pricing, commitments, or discounts. Use Azure billing for actual charges.

CODE PATH
─────────
  1. AIProjectClient(endpoint, DefaultAzureCredential())
  2. openai_client = project.get_openai_client()
  3. Poll: openai_client.evals.runs.retrieve(run_id, eval_id=...)
     Break on completed | failed | canceled.
  4. If completed:
       - print result_counts and per_testing_criteria_results
       - print latency.target if present
       - print estimated_cost.target if present
       - print report_url
  5. Optionally: iterate output_items with --show-items N.

WHAT TO WATCH
─────────────
- `latency.target` is omitted when no row has a usable target latency.
- `estimated_cost.target` is omitted for non-model targets or when no model
  can be priced.
- `completeness = "partial"` means at least one model in `model_costs`
  could not be priced — check `unpriced_models` before comparing runs.
- Long-running "Running" status typically means insufficient model
  capacity; cancel with `openai_client.evals.runs.cancel(run_id, eval_id=...)`
  and increase quota.
- `report_url` opens the row-level portal view for reviewer sign-off.

ENV VARS
────────
  AZURE_AI_PROJECT_ENDPOINT  — Foundry project endpoint URL (required)
  EVAL_ID                    — evaluation ID (or pass --eval-id)
  EVAL_RUN_ID                — run ID (or pass --run-id)
"""
from __future__ import annotations

import argparse
import json
import os
import time
from typing import Any


def _dump(obj: Any) -> Any:
    """Best-effort conversion of SDK models to plain dicts for printing."""
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj
    for attr in ("model_dump", "as_dict", "to_dict"):
        fn = getattr(obj, attr, None)
        if callable(fn):
            try:
                return fn()
            except Exception:  # pragma: no cover
                pass
    if isinstance(obj, dict):
        return {k: _dump(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_dump(x) for x in obj]
    return str(obj)


def _get(obj: Any, key: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _print_summary(run: Any) -> None:
    status = _get(run, "status")
    print(f"Run status: {status}")
    if status != "completed":
        error = _get(run, "error")
        if error:
            print(f"Error: {_dump(error)}")
        return

    counts = _get(run, "result_counts")
    if counts:
        counts_d = _dump(counts)
        print("Result counts:")
        print(f"  passed : {_get(counts_d, 'passed')}")
        print(f"  failed : {_get(counts_d, 'failed')}")
        print(f"  total  : {_get(counts_d, 'total')}")

    per_criterion = _get(run, "per_testing_criteria_results") or []
    if per_criterion:
        print("\nPer-evaluator results:")
        print(f"  {'name':<24} {'passed':>7} {'failed':>7} {'pass_rate':>10}")
        for c in per_criterion:
            d = _dump(c)
            name = _get(d, "name", "?")
            passed = _get(d, "passed", 0)
            failed = _get(d, "failed", 0)
            rate = _get(d, "pass_rate")
            rate_s = f"{rate:.3f}" if isinstance(rate, (int, float)) else str(rate)
            print(f"  {str(name):<24} {passed:>7} {failed:>7} {rate_s:>10}")

    latency = _get(run, "latency")
    target_latency = _get(latency, "target") if latency else None
    if target_latency:
        d = _dump(target_latency)
        print("\nModel-target latency:")
        print(f"  p50_ms       : {_get(d, 'p50_ms')}")
        print(f"  p95_ms       : {_get(d, 'p95_ms')}")
        print(f"  sample_count : {_get(d, 'sample_count')}")

    cost = _get(run, "estimated_cost")
    target_cost = _get(cost, "target") if cost else None
    if target_cost:
        d = _dump(target_cost)
        print("\nEstimated target inference cost (list price, excludes evaluators):")
        print(f"  estimated_cost   : {_get(d, 'estimated_cost')} {_get(d, 'currency', '')}")
        print(f"  completeness     : {_get(d, 'completeness')}")
        print(f"  pricing_version  : {_get(d, 'pricing_version')}")
        model_costs = _get(d, "model_costs") or []
        for mc in model_costs:
            mcd = _dump(mc)
            print(f"    - {_get(mcd, 'model_name')}: "
                  f"cost={_get(mcd, 'estimated_cost')} "
                  f"prompt={_get(mcd, 'prompt_tokens')} "
                  f"cached={_get(mcd, 'cached_tokens')} "
                  f"completion={_get(mcd, 'completion_tokens')}")
        unpriced = _get(d, "unpriced_models") or []
        if unpriced:
            print(f"  unpriced_models  : {list(unpriced)}")

    report_url = _get(run, "report_url")
    if report_url:
        print(f"\nReport URL: {report_url}")


def _print_output_items(openai_client, eval_id: str, run_id: str, limit: int) -> None:
    print(f"\nFirst {limit} output items:")
    shown = 0
    for item in openai_client.evals.runs.output_items.list(run_id=run_id, eval_id=eval_id):
        if shown >= limit:
            break
        print(json.dumps(_dump(item), default=str, indent=2))
        shown += 1


def read_run(args: argparse.Namespace) -> None:
    from azure.ai.projects import AIProjectClient
    from azure.identity import DefaultAzureCredential

    endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]
    project = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())
    openai_client = project.get_openai_client()

    while True:
        run = openai_client.evals.runs.retrieve(run_id=args.run_id, eval_id=args.eval_id)
        status = _get(run, "status")
        if status in ("completed", "failed", "canceled"):
            break
        print(f"Waiting for eval run to complete... status={status}")
        time.sleep(args.poll_seconds)

    _print_summary(run)
    if args.show_items > 0 and _get(run, "status") == "completed":
        _print_output_items(openai_client, args.eval_id, args.run_id, args.show_items)


def preflight(args: argparse.Namespace) -> None:
    endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT", "<unset>")
    print("Read-only lesson: no writes even with --apply.")
    print(f"Project endpoint : {endpoint}")
    print(f"Eval ID          : {args.eval_id or '<required>'}")
    print(f"Run ID           : {args.run_id or '<required>'}")
    print(f"Poll interval    : {args.poll_seconds}s")
    print(f"Show output rows : {args.show_items}")
    print()
    print("Would poll openai_client.evals.runs.retrieve(run_id, eval_id=...) until")
    print("status in {completed, failed, canceled}, then print:")
    print("  result_counts, per_testing_criteria_results,")
    print("  latency.target (model targets only, when available),")
    print("  estimated_cost.target (Global Standard model targets, when priceable),")
    print("  report_url.")
    print()
    print("Provide --eval-id and --run-id to fetch the actual summary.")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Summarize a cloud evaluation run.")
    parser.add_argument("--eval-id", default=os.environ.get("EVAL_ID"), help="Evaluation ID.")
    parser.add_argument("--run-id", default=os.environ.get("EVAL_RUN_ID"), help="Evaluation run ID.")
    parser.add_argument("--poll-seconds", type=int, default=5, help="Seconds between status polls.")
    parser.add_argument(
        "--show-items",
        type=int,
        default=0,
        help="Also print the first N output items after summary (0 = skip).",
    )
    parser.add_argument("--apply", action="store_true", help="No-op; kept for symmetry with lessons 32/33.")
    args = parser.parse_args(argv)

    if not args.eval_id or not args.run_id:
        preflight(args)
        if not args.eval_id or not args.run_id:
            return

    if not os.environ.get("AZURE_AI_PROJECT_ENDPOINT"):
        parser.error("AZURE_AI_PROJECT_ENDPOINT is required to read a run.")
    read_run(args)


if __name__ == "__main__":
    main()
