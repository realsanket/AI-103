# Run: uv run python 05-information-extraction/24_agentic_knowledge_base.py [--apply]
# Practice-question coverage: Q14.
"""Create a knowledge base that references multiple knowledge sources.

A *knowledge base* is the query surface for agentic retrieval: one URL
(/knowledgebases/<name>/retrieve) that fans a single request out to many
knowledge sources in parallel, generates subqueries per source, and merges
the results. Where a knowledge source describes *content*, a knowledge base
describes *routing + defaults*: which sources to query, which LLM to use for
query planning / answer synthesis, and retrieval defaults (reasoning effort,
max runtime, output budget).

This lesson wires together L21 (blob), L22 (search-index), and L23 (web) as
three knowledge sources. `retrievalInstructions` guides which source the
planner picks when a query is ambiguous. `outputMode` = `answerSynthesis`
returns a natural-language answer; the default (`extractiveData`) returns
raw grounding text. `retrievalReasoningEffort.kind` = `auto` lets the
service escalate low→medium if initial results are thin.

Web knowledge sources REQUIRE a `models` entry (web summarization); other
kinds accept it optionally on preview and reject it on GA. The 2026-04-01
API doesn't accept `retrievalInstructions`, `answerInstructions`,
`outputMode`, `models`, or `retrievalReasoningEffort` — this lesson targets
preview.

Code path:
  build_body() assembles the JSON matching the docs' preview body.
  Preflight prints it. With --apply: PUT /knowledgebases/<name>?api-
  version=2026-08-01-preview.

What to watch. `knowledge base '<name>' saved.` A 400 "knowledge source not
found" = run L21-L23 first. A 403 on retrieve later (L25) means Search MI
lacks Cognitive Services User on the Foundry resource for the LLM.

Prerequisites / env vars:
  SEARCH_ENDPOINT           — https://<service>.search.windows.net
  SEARCH_KNOWLEDGE_BASE     — KB name (default northwind-kb)
  SEARCH_KS_BLOB            — blob KS name (from L21; default northwind-blob-ks)
  SEARCH_KS_INDEX           — search-index KS name (from L22; default northwind-index-ks)
  SEARCH_KS_WEB             — web KS name from L23; opt-in. Unset means no web source,
                              because web queries go to Bing outside the Microsoft DPA
  AZURE_OPENAI_ENDPOINT     — AOAI/Foundry resource endpoint
  DEFAULT_MODEL             — chat deployment for query planning + answer synthesis
"""
import argparse
import json

from _search_rest import _PREVIEW_API_VERSION, put_named
from _shared.config import env, settings


def configuration() -> dict[str, str]:
    s = settings()
    return {
        "name": env("SEARCH_KNOWLEDGE_BASE", "northwind-kb"),
        "ks_blob": env("SEARCH_KS_BLOB", "northwind-blob-ks"),
        "ks_index": env("SEARCH_KS_INDEX", "northwind-index-ks"),
        "ks_web": env("SEARCH_KS_WEB"),
        "aoai_endpoint": s.azure_openai_endpoint,
        "chat": s.default_model,
    }


def build_body(cfg: dict[str, str]) -> dict:
    sources = [
        {"name": cfg["ks_blob"]},
        {"name": cfg["ks_index"]},
    ]
    instructions = "Use the blob and search-index knowledge sources for internal Northwind policies."
    if cfg["ks_web"]:
        sources.append({"name": cfg["ks_web"]})
        instructions += " Use the web knowledge source only when the user asks about current external information."
    return {
        "name": cfg["name"],
        "description": "Northwind agentic retrieval knowledge base (blob + index, optional web).",
        "retrievalInstructions": instructions,
        "answerInstructions": "Answer in two concise sentences and cite [ref_id:<n>] for every claim.",
        "outputMode": "answerSynthesis",
        "knowledgeSources": sources,
        "models": [
            {
                "kind": "azureOpenAI",
                "azureOpenAIParameters": {
                    "resourceUri": cfg["aoai_endpoint"],
                    "deploymentId": cfg["chat"],
                    "modelName": cfg["chat"],
                },
            }
        ],
        "encryptionKey": None,
        "retrievalReasoningEffort": {"kind": "auto"},
    }


def preflight(cfg: dict[str, str]) -> None:
    print("Knowledge base preflight. No cloud calls made.")
    for key, value in cfg.items():
        print(f"- {key}: {'configured' if value else 'missing'}")
    print(f"- api-version: {_PREVIEW_API_VERSION}")
    print("Planned request body:")
    print(json.dumps(build_body(cfg), indent=2))


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Create an agentic-retrieval knowledge base.")
    parser.add_argument("--apply", action="store_true", help="Send the PUT request to Search.")
    args = parser.parse_args(argv)
    cfg = configuration()
    if not args.apply:
        preflight(cfg)
        print("- Rerun with --apply to create the knowledge base.")
        return
    if not cfg["aoai_endpoint"]:
        raise SystemExit("Set AZURE_OPENAI_ENDPOINT — required for web summarization / answer synthesis.")
    put_named("knowledgebases", cfg["name"], build_body(cfg), _PREVIEW_API_VERSION)
    print(f"knowledge base '{cfg['name']}' saved.")


if __name__ == "__main__":
    main()
