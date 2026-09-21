# Run: uv run python 05-information-extraction/27_agentic_reasoning_effort_preflight.py
"""Preflight-only walkthrough of the four retrieval reasoning-effort tiers.

`retrievalReasoningEffort.kind` controls how much LLM processing runs
during retrieval. It's set either on a knowledge base (default for every
query) or per retrieve request (override for one call). If neither is set,
the service uses `low`. The trade-off is latency + cost + output-token
budget vs. how many subqueries the planner is willing to run.

+ `minimal` — No LLM planning. Direct text and vector search across every
  knowledge source, no expansion. `alwaysQueryKnowledgeSource` is ignored;
  every source is queried. Requires `outputMode` = `extractiveData`. Answer
  synthesis and web knowledge sources are NOT supported. Fastest, cheapest,
  most predictable. Good for migration from the classic Search API or when
  the app does its own query planning.
+ `low` — One LLM pass of query planning + source selection. Generates
  subqueries and fans out. Enables answer synthesis. 5,000 answer-token
  budget. Max 50 documents for semantic ranking (10 with L3 classifier).
  This is the default.
+ `medium` — Adds a semantic-classifier scoring pass. If initial results are
  weak, the planner rewrites the query and runs a follow-up iteration.
  10,000 answer-token budget. Max 50 documents (20 with L3). Region-limited
  — see the doc's region-support table.
+ `auto` — Lightweight first pass; escalates up to medium only if grounding
  is insufficient. Requires the `2026-08-01-preview` API AND a `models`
  entry on the knowledge base. Best default when you don't know per-query
  depth needs.

This lesson is preflight-only: no cloud call, no --apply. It prints the JSON
request body for each tier so you can drop the shape into lessons 25 / 26
by editing `retrievalReasoningEffort.kind`.

Code path:
  For each tier, build_request(kind) prints the exact `retrievalReasoning
  Effort` object and describes the operational limits. No PUT, no POST.

What to watch. Four labeled JSON snippets, one per tier, with a limit summary
under each. Nothing is sent.

Prerequisites / env vars: none. This is a documentation lesson.
"""
import argparse
import json

_TIERS = {
    "minimal": {
        "output_mode_required": "extractiveData",
        "answer_synthesis": False,
        "web_ks_supported": False,
        "notes": "No LLM planning. Fastest / cheapest. alwaysQueryKnowledgeSource ignored.",
    },
    "low": {
        "output_mode_required": "any",
        "answer_synthesis": True,
        "web_ks_supported": True,
        "notes": "One LLM pass. 5,000 answer-token budget. Default.",
    },
    "medium": {
        "output_mode_required": "any",
        "answer_synthesis": True,
        "web_ks_supported": True,
        "notes": "Semantic classifier + one follow-up iteration. 10,000 answer-token budget. Region-limited.",
    },
    "auto": {
        "output_mode_required": "any",
        "answer_synthesis": True,
        "web_ks_supported": True,
        "notes": "Lightweight first pass, escalates up to medium. Requires KB models entry + preview API.",
    },
}


def build_request(kind: str) -> dict:
    return {
        "messages": [{"role": "user", "content": [{"type": "text", "text": "What is the refund policy?"}]}],
        "outputMode": "extractiveData" if kind == "minimal" else "answerSynthesis",
        "retrievalReasoningEffort": {"kind": kind},
        "includeActivity": True,
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Explain retrieval reasoning-effort tiers.")
    parser.parse_args(argv)
    print("Retrieval reasoning-effort tiers (preflight only — no cloud calls).")
    print("Set retrievalReasoningEffort.kind on either the knowledge base (L24) or the retrieve request (L25/L26).")
    for kind, meta in _TIERS.items():
        print()
        print(f"=== {kind} ===")
        for key, value in meta.items():
            print(f"- {key}: {value}")
        print("Request body:")
        print(json.dumps(build_request(kind), indent=2))
    print()
    print("Guidance:")
    print("- Start with `low` for most workloads (matches the service default).")
    print("- Switch to `minimal` for migrations from the classic /docs/search API or when the app owns planning.")
    print("- Use `medium` when recall matters more than latency and your region supports it.")
    print("- Use `auto` when latency budget varies per query and the KB already has a model configured.")


if __name__ == "__main__":
    main()
