"""Hybrid + semantic ranking — same query, three modes, side-by-side.

Keyword vs vector vs hybrid+semantic. Prints top-3 for each. Real RAG usually
uses the last one — exact matches AND meaning-based, semantically re-ranked.
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
