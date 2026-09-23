# Run: uv run python 05-information-extraction/05_search_skillset.py
# Practice-question coverage: Q171, Q172.
"""Create or update the chunking and embedding skillset.

The skillset defines what happens at ingestion time — NOT at query time. It uses
SplitSkill (character-based, 2000-char chunks with 500-char overlap) to break
Blob document content into pages, then AzureOpenAIEmbeddingSkill to embed each
chunk using the configured deployment. Index projections write one child Search
document per chunk, repeating title/source_url and mapping parent_id automatically.

The skillset must be created before the indexer runs. The Search service's
managed identity must have Cognitive Services OpenAI User on the embedding resource.
Never manually map `parent_id` in index projections — it breaks change tracking.

Code path:
  load_definition(skillset.json) resolves AZURE_OPENAI_ENDPOINT + EMBEDDING_MODEL
  placeholders → PUT /skillsets/<name> → print confirmation.

What to watch. `skillset '<name>' saved.` A 403 means the identity lacks Search
management role. A 400 usually means a JSON structure or endpoint mismatch.

Prerequisites / env vars:
  SEARCH_ENDPOINT       — https://<service>.search.windows.net
  SEARCH_SKILLSET       — skillset name
  AZURE_OPENAI_ENDPOINT — used by AzureOpenAIEmbeddingSkill
  EMBEDDING_MODEL       — deployment name for embedding (e.g., text-embedding-3-large)
"""
from pathlib import Path

from _search_rest import load_definition, put

_SKILLSET_JSON = Path(__file__).parent / "skillset_configs" / "skillset.json"


def main() -> None:
    skillset = load_definition(_SKILLSET_JSON)
    put("skillsets", skillset)
    print(f"skillset '{skillset['name']}' saved.")


if __name__ == "__main__":
    main()
