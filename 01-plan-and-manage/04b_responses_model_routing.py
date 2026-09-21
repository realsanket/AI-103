# Run: uv run python 01-plan-and-manage/04b_responses_model_routing.py [--apply]
"""Responses API as one interface for model-router AND named models.

Lesson 04 already shows a chat-style routing pattern. This lesson lays out the
newer, unified pattern the Foundry docs recommend today: call `responses.create`
through the project-scoped OpenAI client, and change only the `model` string to
switch between automatic routing (`model-router`) and a specific deployment
(for example `gpt-5-mini`, `Deepseek-V3.2`). Same client, same call site, same
response shape — the value you pass to `model` is the sole decision point.

Why it matters:
  Model router optimizes cost/quality per request. Named deployments give
  deterministic behavior for compliance, reproducibility, benchmarking, or
  strict latency SLOs. The Responses API supports both. Every call goes through
  the same `AIProjectClient.get_openai_client()`; auto-failover, prompt caching,
  content filtering, RBAC, model identification, and per-deployment TPM/RPM
  quotas apply uniformly. `response.model` always reports which model
  actually answered — use it for logging, cost attribution, and debug.

Code path (mirrors the Foundry doc `responses-model-routing.md`):
  Preflight — print the decision table, list the router + a named baseline
  deployment, explain trigger conditions ("start with model-router; pin a named
  model only when you need determinism") and cost/latency reporting.
  --apply — send one prompt to the router and one to a named baseline via the
  identical `client.responses.create(model=..., input=...)` call. Print picked
  model, elapsed seconds, and a snippet — the two rows demonstrate that only
  the `model` argument differs.

What to watch:
  `model-router` row shows `responded` as one of the pool's underlying models
  (nano/mini/frontier). Named rows show `responded` equal to the deployment
  requested. If the router picks the same tier as the baseline, run again with
  a harder prompt — routing decisions depend on request content.

Trigger conditions (when to use which):
  - Default: `model-router`. Best fit for mixed traffic; benefits from
    automatic failover (needs at least 2 models in the configured subset).
  - Named model: compliance/jurisdiction requirement, reproducible benchmark
    baseline, deterministic tool/latency/cost budget, or a narrow SLO.
  - Evaluate router against your existing named deployment as the baseline
    before adopting router broadly.

Prerequisites / env vars:
  PROJECT_ENDPOINT          — Foundry project endpoint
  MODEL_ROUTER_DEPLOYMENT   — router deployment alias (default: model-router)
  DEFAULT_MODEL             — named baseline chat deployment
  AZURE_OPENAI_ENDPOINT     — required by shared config; not called directly
"""
import argparse
import time

from _shared.config import settings
from _shared.foundry_client import project_client

_PROMPT = "Explain retrieval-augmented generation in one sentence."


def preflight() -> None:
    s = settings()
    print("No cloud calls made.")
    print("Responses API is one interface; the `model` value is the routing decision.")
    print(f"Router deployment:  {s.model_router_deployment or '<not set>'}  (auto model selection)")
    print(f"Named baseline:     {s.default_model or '<not set>'}  (deterministic pick)")
    print()
    print("Trigger conditions:")
    print("  - Use model-router by default. Configure at least 2 models in the pool for failover.")
    print("  - Use a named deployment for compliance, reproducibility, benchmarking, or strict SLO.")
    print("  - Same code path either way; only the `model` argument changes.")
    print()
    print("Built-in on every call: failover, prompt caching, content filtering, RBAC, TPM/RPM,")
    print("data residency, and `response.model` for cost attribution.")
    print()
    print("Run with --apply to send one router request and one named-deployment request.")


def _run_one(client, deployment: str) -> None:
    start = time.time()
    r = client.responses.create(model=deployment, input=_PROMPT)
    elapsed = time.time() - start
    responded = r.model or "?"
    text = (r.output_text or "").strip().replace("\n", " ")
    print(f"{deployment:<22} {responded:<22} {elapsed:>6.2f}s  {text[:80]}")


def apply() -> None:
    s = settings()
    router = s.require("MODEL_ROUTER_DEPLOYMENT")
    named = s.require("DEFAULT_MODEL")
    client = project_client().get_openai_client()
    print(f"{'Deployment':<22} {'Responded':<22} {'Latency':>7}  Response")
    print("-" * 100)
    _run_one(client, router)
    _run_one(client, named)
    print()
    print("Only the `model=` value changed. `response.model` shows what actually answered.")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Responses API: auto vs direct model routing.")
    parser.add_argument("--apply", action="store_true", help="Send one router + one named request.")
    args = parser.parse_args(argv)
    if not args.apply:
        preflight()
        return
    apply()


if __name__ == "__main__":
    main()
