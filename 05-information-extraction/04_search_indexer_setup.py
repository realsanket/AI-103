"""Create/update the AI Search indexer that pulls Blob docs + runs the skillset."""
import json
from pathlib import Path

from azure.search.documents.indexes.models import SearchIndexer

from _shared.search_client import indexer_client

_INDEXER_JSON = Path(__file__).parent / "skillset_configs" / "indexer.json"


def main() -> None:
    client = indexer_client()
    body = json.loads(_INDEXER_JSON.read_text())
    indexer = SearchIndexer(**body)
    client.create_or_update_indexer(indexer)
    print(f"indexer '{indexer.name}' saved. Run it in the portal or via .run_indexer()")


if __name__ == "__main__":
    main()
