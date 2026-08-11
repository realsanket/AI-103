# Run: uv run python 05-information-extraction/03_search_hybrid_semantic.py
"""Hybrid + semantic ranking — keyword vs vector vs hybrid+semantic, side-by-side.

Hybrid search combines BM25 (keyword) and HNSW (vector) candidates via reciprocal
rank fusion (RRF), then semantic ranker reranks the top RRF results using a
language model. This is the production RAG baseline: exact matches AND meaning,
semantically boosted. The semantic ranker does NOT scan the full corpus — it only
reranks candidates already surfaced by BM25+vector.

Compare the three modes on the same query to see how ranking changes. Semantic
reranker score (`@search.reranker_score`) is NOT comparable to BM25/vector scores.
Requires semantic ranker enabled on the Search service (region/SKU dependent).

Code path:
  Three client.search() calls on the same _QUERY:
  1. keyword-only: search_text only
  2. vector-only: VectorizableTextQuery, search_text=None
  3. hybrid+semantic: both + QueryType.SEMANTIC + semantic_configuration_name="default"
  _print_top() prints rank, score, title, chunk preview for top-3.

What to watch. Compare which chunks appear and where across three columns. Hybrid
usually surfaces more relevant results. Semantic score range differs from BM25/vector.

Prerequisites / env vars:
  SEARCH_ENDPOINT     — https://<service>.search.windows.net
  SEARCH_INDEX_VECTOR — populated index with semantic config "default" enabled
"""
from azure.search.documents.models import QueryType, VectorizableTextQuery

from _shared.config import settings
from _shared.search_client import search_client

_QUERY = "does the refund window include the trial period?"


def _print_top(mode: str, results) -> None:
    print(f"\n=== {mode} ===")
    for i, r in enumerate(list(results)[:3], 1):
        score = r.get("@search.reranker_score") or r.get("@search.score")
        print(f"  {i}. score={score:.4f}  {r.get('title')}")
        print(f"     {r.get('chunk', '')[:140]}")


def main() -> None:
    idx = settings().search_index_vector
    client = search_client(idx)

    # Keyword-only
    _print_top("KEYWORD", client.search(search_text=_QUERY, select=["chunk", "title"], top=3))

    # Vector-only
    _print_top(
        "VECTOR",
        client.search(
            search_text=None,
            vector_queries=[VectorizableTextQuery(text=_QUERY, k_nearest_neighbors=10, fields="text_vector")],
            select=["chunk", "title"],
            top=3,
        ),
    )

    # Hybrid + semantic ranker
    _print_top(
        "HYBRID + SEMANTIC",
        client.search(
            search_text=_QUERY,
            vector_queries=[VectorizableTextQuery(text=_QUERY, k_nearest_neighbors=10, fields="text_vector")],
            query_type=QueryType.SEMANTIC,
            semantic_configuration_name="default",
            select=["chunk", "title"],
            top=3,
        ),
    )


if __name__ == "__main__":
    main()
