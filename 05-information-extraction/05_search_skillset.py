"""Create/update the chunking and embedding skillset from REST JSON."""
from pathlib import Path

from _search_rest import load_definition, put

_SKILLSET_JSON = Path(__file__).parent / "skillset_configs" / "skillset.json"


def main() -> None:
    skillset = load_definition(_SKILLSET_JSON)
    put("skillsets", skillset)
    print(f"skillset '{skillset['name']}' saved.")


if __name__ == "__main__":
    main()
