"""Create/update the chunked vector index used by Domain 5 search lessons."""
from pathlib import Path

from _search_rest import load_definition, put

_INDEX_JSON = Path(__file__).parent / "skillset_configs" / "index.json"


def main() -> None:
    index = load_definition(_INDEX_JSON)
    put("indexes", index)
    print(f"index '{index['name']}' saved.")


if __name__ == "__main__":
    main()
