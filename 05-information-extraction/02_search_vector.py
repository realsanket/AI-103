# Run: uv run python 05-information-extraction/02_search_vector.py
"""Vector search — semantic similarity retrieval via server-side embedding.

`VectorizableTextQuery` sends the query text to the index's configured vectorizer
(which calls the embedding model), then performs HNSW approximate nearest-neighbor
search over `text_vector`. It finds paraphrases and intent matches that BM25 misses,
but loses exact-term recall. Use when meaning matters more than exact tokens.

Compare with lesson 01 (BM25) and lesson 03 (hybrid + semantic). The same phrase
"how do I get my money back" finds refund-related chunks even if they never use
the word "refund" — that's the semantic gap BM25 cannot close.

Code path:
  VectorizableTextQuery(text, k_nearest_neighbors=5, fields="text_vector") →
  client.search(search_text=None, vector_queries=[...], top=5) →
  print @search.score and chunk preview.

What to watch. Scores are cosine-distance based (0–1 range typical). Compare
them to BM25 scores from lesson 01 — they are NOT comparable across modes.
`search_text=None` disables BM25; lesson 03 combines both.

Prerequisites / env vars:
  SEARCH_ENDPOINT     — https://<service>.search.windows.net
  SEARCH_INDEX_VECTOR — index with populated text_vector field and vectorizer configured
"""
from azure.search.documents.models import VectorizableTextQuery

from _shared.config import settings
from _shared.search_client import search_client


def main() -> None:
    client = search_client(settings().search_index_vector)
    results = client.search(
        search_text=None,  # vector-only
        vector_queries=[
            VectorizableTextQuery(
                text="how do I get my money back",
                k_nearest_neighbors=5,
                fields="text_vector",
            )
        ],
        select=["chunk", "title"],
        top=5,
    )
    for r in results:
        print(f"score={r['@search.score']:.4f}  title={r.get('title')}")
        print(r.get("chunk", "")[:200], "\n---")


if __name__ == "__main__":
    main()
