# Run: uv run python 05-information-extraction/26_agentic_answer_synthesis.py [--apply]
"""Toggle `answerSynthesis` on the retrieve call: get a formulated answer + citations.

Lesson 25 returned `extractiveData` — a JSON string of the top chunks. This
lesson sets `outputMode` to `answerSynthesis` on the same retrieve call.
Instead of raw chunks, the KB's LLM (configured in L24's `models` array)
writes a natural-language answer and inlines citations as `[ref_id:<n>]`
tokens that map to the `references` array in the same response.

Answer synthesis requires:
+ `2026-08-01-preview` API (GA `2026-04-01` doesn't support it)
+ A `models` entry on the knowledge base (L24 has it)
+ Reasoning effort must be `low`, `medium`, or `auto` (not `minimal`)

Setting `outputMode` on the retrieve request overrides the knowledge base
default per-call. L24 already defaults to `answerSynthesis`; this lesson
sets it explicitly so it works even if a user rebuilt the KB with
`extractiveData` as the default.

Code path:
  build_request(question) assembles the POST body with `outputMode` =
  `answerSynthesis`, `answerInstructions`, and `includeActivity`. Preflight
  prints it. With --apply: POST /knowledgebases/<name>/retrieve → print
  synthesized answer, then references with docKey.

What to watch. With --apply: a bulleted or paragraph answer with `[ref_id:1]`
style citations. If the answer is empty and `activity` shows zero results,
the KB has no matching documents — verify L21's indexer completed. A 400
about "answerSynthesis requires a model" means L24's `models` array is
empty; recreate the KB with a chat deployment configured.

Prerequisites / env vars:
  SEARCH_ENDPOINT           — https://<service>.search.windows.net
  SEARCH_KNOWLEDGE_BASE     — KB name from L24 (default northwind-kb)
  SEARCH_RETRIEVE_QUESTION  — override the default question (optional)
"""
import argparse
import json
import os

from _search_rest import _PREVIEW_API_VERSION, post

_DEFAULT_QUESTION = "How does the refund window interact with the trial period, and who do I contact if there is a dispute?"


def configuration() -> dict[str, str]:
    return {
        "name": os.environ.get("SEARCH_KNOWLEDGE_BASE", "northwind-kb"),
        "question": os.environ.get("SEARCH_RETRIEVE_QUESTION", _DEFAULT_QUESTION),
    }


def build_request(question: str) -> dict:
    return {
        "messages": [
            {"role": "user", "content": [{"type": "text", "text": question}]},
        ],
        "outputMode": "answerSynthesis",
        "answerInstructions": (
            "Answer in short bullet points and cite [ref_id:<n>] after every claim. "
            "If sources conflict, note the conflict."
        ),
        "retrievalReasoningEffort": {"kind": "low"},
        "includeActivity": True,
    }


def _first_text(body: dict) -> str:
    messages = body.get("response") or []
    if not messages:
        return ""
    for content in messages[0].get("content", []) or []:
        if content.get("type") == "text":
            return content.get("text", "")
    return ""


def print_answer(body: dict) -> None:
    print("Synthesized answer:")
    print(_first_text(body) or "(empty response — check activity below)")
    print()
    for ref in (body.get("references") or [])[:8]:
        print(
            f"ref_id={ref.get('id')} activity_source={ref.get('activitySource')} "
            f"docKey={ref.get('docKey', '-')}"
        )
    print()
    total_input = 0
    total_output = 0
    for activity in body.get("activity", []) or []:
        total_input += activity.get("inputTokens") or 0
        total_output += activity.get("outputTokens") or 0
    print(f"Total LLM tokens across activity: input={total_input} output={total_output}")


def preflight(cfg: dict[str, str]) -> None:
    print("Answer-synthesis preflight. No cloud calls made.")
    for key, value in cfg.items():
        print(f"- {key}: {'configured' if value else 'missing'}")
    print(f"- api-version: {_PREVIEW_API_VERSION}")
    print("Planned POST body:")
    print(json.dumps(build_request(cfg["question"]), indent=2))


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Retrieve with answer synthesis.")
    parser.add_argument("--apply", action="store_true", help="Send the retrieve request.")
    args = parser.parse_args(argv)
    cfg = configuration()
    if not args.apply:
        preflight(cfg)
        print("- Rerun with --apply to invoke retrieve with answer synthesis.")
        return
    body = post(f"knowledgebases/{cfg['name']}/retrieve", build_request(cfg["question"]), _PREVIEW_API_VERSION)
    print_answer(body)


if __name__ == "__main__":
    main()
