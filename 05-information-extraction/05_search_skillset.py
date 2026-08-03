"""Create/update the built-in skillset — OCR + Merge + LangDetect + KeyPhrases."""
import json
from pathlib import Path

from azure.search.documents.indexes.models import SearchIndexerSkillset

from _shared.search_client import indexer_client

_SKILLSET_JSON = Path(__file__).parent / "skillset_configs" / "skillset.json"


def main() -> None:
    client = indexer_client()
    body = json.loads(_SKILLSET_JSON.read_text())
    skillset = SearchIndexerSkillset(**body)
    client.create_or_update_skillset(skillset)
    print(f"skillset '{skillset.name}' saved. Attach it to your indexer to run enrichment.")


if __name__ == "__main__":
    main()
