# Run: uv run python 05-information-extraction/01_search_basic_query.py
"""Keyword (BM25) search — exact-token retrieval against a populated AI Search index.

BM25 ranks results by term frequency and inverse document frequency. It is the
right choice for exact policy terms, IDs, SKUs, and rare vocabulary. It misses
paraphrases ("refund" won't find "money back"). Compare with vector search (02)
and hybrid+semantic (03) to see how ranking changes for the same query.

Requires a populated index from lesson 00 (schema) + lesson 05 (skillset) +
lesson 04 (indexer run). Querying an empty index returns zero results silently.

Code path:
  search_client(index_name) → client.search(search_text="refund", select=[chunk,title])
  → print @search.score, title, and 200-char chunk preview per result.

What to watch. BM25 scores (e.g., 2.3, 1.8) and which chunks surface for "refund".
Results that mention the word "refund" score higher than semantically related chunks
that use different wording — that gap is exactly what vector/hybrid (02, 03) closes.

Prerequisites / env vars:
  SEARCH_ENDPOINT     — https://<service>.search.windows.net
  SEARCH_INDEX_VECTOR — populated index name
"""
from _shared.search_client import search_client
from _shared.config import settings


def main() -> None:
    client = search_client(settings().search_index_vector)
    results = client.search(
        search_text="refund",
        select=["chunk", "title"],
    )
    for r in results:
        print(f"score={r['@search.score']:.4f}  title={r.get('title')}")
        print(r.get("chunk", "")[:200])
        print("---")

    print(f"\nindex={settings().search_index_vector}  endpoint={settings().search_endpoint}")


if __name__ == "__main__":
    main()
