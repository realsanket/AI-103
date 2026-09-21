# Run: uv run python 05-information-extraction/25_agentic_retrieve.py [--apply]
"""Call the retrieve action against the knowledge base created in lesson 24.

The retrieve action (POST /knowledgebases/<name>/retrieve) fans a single user
message out to every knowledge source in the KB, generates subqueries per
source (visible in the `activity` array), and merges results into three
components of the response body:

+ `response`  — extracted grounding text (or synthesized answer, L26)
+ `activity` — per-subquery timing, tokens, and knowledge-source calls
+ `references` — one entry per cited chunk with `activitySource` id linking
  back into `activity`. Indexed sources include a `docKey` for citation URL
  resolution; remote sources (web) omit it.

This lesson uses `outputMode` = `extractiveData` and reasoning `low` — the
default balance between latency and query planning. Set `includeActivity`
and `includeReferences` to `true` so the response contains the diagnostic
arrays. `messages` (preview) accepts an assistant instruction + a user
message; the GA `2026-04-01` API instead uses the older `intents` shape.

Code path:
  build_request(question) assembles the POST body. Preflight prints it.
  With --apply: POST /knowledgebases/<name>/retrieve?api-version=2026-08-01-
  preview → parse response → print synthesized text preview, subqueries from
  `activity`, and up to 5 references with docKey.

What to watch. Preflight: shows configured KB name and printed body. With
--apply: `Response text preview`, then `Subquery` lines from the activity
array, then `Reference` lines. A 400 "outputMode extractiveData not
compatible with minimal effort" means you changed reasoning effort without
matching outputMode — see lesson 27 for the effort matrix.

Prerequisites / env vars:
  SEARCH_ENDPOINT           — https://<service>.search.windows.net
  SEARCH_KNOWLEDGE_BASE     — KB name from L24 (default northwind-kb)
  SEARCH_RETRIEVE_QUESTION  — override the default question (optional)
"""
import argparse
import json
import os

from _search_rest import _PREVIEW_API_VERSION, post

_DEFAULT_QUESTION = "What does Northwind's refund policy say about the trial period?"


def configuration() -> dict[str, str]:
    return {
        "name": os.environ.get("SEARCH_KNOWLEDGE_BASE", "northwind-kb"),
        "question": os.environ.get("SEARCH_RETRIEVE_QUESTION", _DEFAULT_QUESTION),
    }


def build_request(question: str) -> dict:
    return {
        "messages": [
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "You answer only from the retrieved sources. Each source object has a ref_id "
                            "that must be cited as [ref_id:<n>]. If no source supports the answer, say "
                            "'I don't have that information in the knowledge base.'"
                        ),
                    }
                ],
            },
            {"role": "user", "content": [{"type": "text", "text": question}]},
        ],
        "outputMode": "extractiveData",
        "retrievalReasoningEffort": {"kind": "low"},
        "includeActivity": True,
    }


def _first_text(response_body: dict) -> str:
    messages = response_body.get("response") or []
    if not messages:
        return ""
    for content in messages[0].get("content", []) or []:
        if content.get("type") == "text":
            return content.get("text", "")
    return ""


def print_response(body: dict) -> None:
    text = _first_text(body)
    print("Response text preview:")
    print((text[:600] + "...") if len(text) > 600 else text)
    print()
    for activity in body.get("activity", []) or []:
        atype = activity.get("type", "?")
        ks = activity.get("knowledgeSourceName", "-")
        elapsed = activity.get("elapsedMs", "?")
        args = activity.get("searchIndexArguments") or activity.get("webArguments") or {}
        query = args.get("search") or args.get("query") or ""
        print(f"Subquery [{atype} via {ks}] {elapsed}ms: {query}")
    print()
    for ref in (body.get("references") or [])[:5]:
        print(
            f"Reference id={ref.get('id')} source_activity={ref.get('activitySource')} "
            f"docKey={ref.get('docKey', '-')} rerankerScore={ref.get('rerankerScore', '-')}"
        )


def preflight(cfg: dict[str, str]) -> None:
    print("Retrieve preflight. No cloud calls made.")
    for key, value in cfg.items():
        print(f"- {key}: {'configured' if value else 'missing'}")
    print(f"- api-version: {_PREVIEW_API_VERSION}")
    print("Planned POST body:")
    print(json.dumps(build_request(cfg["question"]), indent=2))


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Call the agentic retrieve action.")
    parser.add_argument("--apply", action="store_true", help="Send the retrieve request.")
    args = parser.parse_args(argv)
    cfg = configuration()
    if not args.apply:
        preflight(cfg)
        print("- Rerun with --apply to invoke retrieve.")
        return
    body = post(f"knowledgebases/{cfg['name']}/retrieve", build_request(cfg["question"]), _PREVIEW_API_VERSION)
    print_response(body)


if __name__ == "__main__":
    main()
