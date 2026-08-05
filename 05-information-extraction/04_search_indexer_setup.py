"""Create/update Blob data source and indexer from REST JSON definitions."""
import argparse
from pathlib import Path

from _shared.search_client import indexer_client
from _search_rest import load_definition, put

_DATA_SOURCE_JSON = Path(__file__).parent / "skillset_configs" / "data_source.json"
_INDEXER_JSON = Path(__file__).parent / "skillset_configs" / "indexer.json"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true", help="Start indexing after provisioning.")
    args = parser.parse_args()

    data_source = load_definition(_DATA_SOURCE_JSON)
    indexer = load_definition(_INDEXER_JSON)
    put("datasources", data_source)
    put("indexers", indexer)
    print(f"data source '{data_source['name']}' and indexer '{indexer['name']}' saved.")
    if args.run:
        indexer_client().run_indexer(indexer["name"])
        print("indexer run started; check status in the portal or with get_indexer_status().")


if __name__ == "__main__":
    main()
