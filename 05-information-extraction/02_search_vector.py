"""Vector-only search — retrieve by semantic similarity, not exact match.

Uses `VectorizableTextQuery` (server-side embedding via a vectorizer on the
index) — see `03_search_hybrid_semantic.py` for how vector combines with text.
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
