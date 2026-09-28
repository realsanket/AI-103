# Run: uv run python 05-information-extraction/22_knowledge_source_search_index.py [--apply]
"""Wrap an existing search index as a `searchIndex` knowledge source.

Where lesson 21's `azureBlob` knowledge source generates a whole pipeline,
this kind is a thin pointer: it wraps an index that already exists (e.g., the
one from lessons 00-05) so agentic retrieval can query it. There's no
ingestion, no skillset, no indexer — only a JSON reference and a list of
which fields to include when the retrieval engine composes its response.

`sourceDataFields` lists which fields are surfaced back in the retrieve
response's `references`. `searchFields` lists which fields participate in the
query itself (semantic/vector). Starting with the `2026-05-01-preview` API
version, `semanticConfigurationName` is optional; earlier versions require it.
This lesson targets `2026-08-01-preview` (matches lessons 21, 23-26) but the
same body works on GA `2026-04-01` if you add `semanticConfigurationName`.

Code path:
  build_body() references SEARCH_INDEX_VECTOR (the index created by L00).
  Preflight prints JSON. With --apply: PUT /knowledgesources/<name>?api-
  version=2026-08-01-preview.

What to watch. `knowledge source '<name>' saved.` A 400 with
"searchIndexName not found" means SEARCH_INDEX_VECTOR isn't on this search
service. A 400 about `semanticConfigurationName` means you're on an older
API version — either upgrade or set the field.

Prerequisites / env vars:
  SEARCH_ENDPOINT           — https://<service>.search.windows.net
  SEARCH_KS_INDEX           — knowledge source name (default northwind-index-ks; L24 references it)
  SEARCH_INDEX_VECTOR       — existing index to wrap (from L00)
"""
import argparse
import json

from _search_rest import _PREVIEW_API_VERSION, put_named
from _shared.config import env, settings


def configuration() -> dict[str, str]:
    s = settings()
    return {
        "name": env("SEARCH_KS_INDEX", "northwind-index-ks"),
        "index": s.search_index_vector,
    }


def build_body(cfg: dict[str, str]) -> dict:
    return {
        "name": cfg["name"],
        "kind": "searchIndex",
        "description": "Wraps the existing northwind vector index for agentic retrieval.",
        "encryptionKey": None,
        "searchIndexParameters": {
            "searchIndexName": cfg["index"],
            "sourceDataFields": [
                {"name": "chunk"},
                {"name": "title"},
            ],
            "searchFields": [
                {"name": "chunk"},
            ],
        },
    }


def preflight(cfg: dict[str, str]) -> None:
    print("Search-index knowledge source preflight. No cloud calls made.")
    for key, value in cfg.items():
        print(f"- {key}: {'configured' if value else 'missing'}")
    print(f"- api-version: {_PREVIEW_API_VERSION}")
    print("Planned request body:")
    print(json.dumps(build_body(cfg), indent=2))


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Wrap an existing index as a knowledge source.")
    parser.add_argument("--apply", action="store_true", help="Send the PUT request to Search.")
    args = parser.parse_args(argv)
    cfg = configuration()
    if not args.apply:
        preflight(cfg)
        print("- Rerun with --apply to create the knowledge source.")
        return
    if not cfg["index"]:
        raise SystemExit("Set SEARCH_INDEX_VECTOR to the name of the index to wrap.")
    put_named("knowledgesources", cfg["name"], build_body(cfg), _PREVIEW_API_VERSION)
    print(f"knowledge source '{cfg['name']}' saved.")


if __name__ == "__main__":
    main()
