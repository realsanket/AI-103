# Run: uv run python 05-information-extraction/00_search_index_setup.py
"""Create or replace the chunked vector index used by all Domain 5 search lessons.

The index schema must exist before ingestion starts — it defines vector dimensions,
semantic configuration, and field contracts. This lesson is a prerequisite for all
Search query lessons (01–03) and the indexer (04). Running it again replaces the
schema but does NOT delete indexed documents; a schema incompatible with existing
data may cause query errors until the index is rebuilt.

This lesson makes no query and does not start the indexer. Run lesson 05 (skillset)
and lesson 04 (indexer) after this to ingest documents.

Code path:
  load_definition(index.json) resolves env-var placeholders → PUT /indexes/<name>
  via Entra-authenticated REST (api-version 2026-04-01) → print confirmation.

What to watch. `index '<name>' saved.` A 403 means the calling identity lacks the
Search index-management role. A 409 can mean a dimension or key-field type conflict.

Prerequisites / env vars:
  SEARCH_ENDPOINT    — https://<service>.search.windows.net
  SEARCH_INDEX_VECTOR — index name
  AZURE_OPENAI_ENDPOINT, EMBEDDING_MODEL — referenced in index.json vectorizer config
"""
from pathlib import Path

from _search_rest import load_definition, put

_INDEX_JSON = Path(__file__).parent / "skillset_configs" / "index.json"


def main() -> None:
    index = load_definition(_INDEX_JSON)
    put("indexes", index)
    print(f"index '{index['name']}' saved.")


if __name__ == "__main__":
    main()
