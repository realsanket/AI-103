"""Baseline keyword search against an AI Search index."""
from _shared.search_client import search_client
from _shared.config import settings


def main() -> None:
    client = search_client()
    results = client.search(
        search_text="refund",
        select=["chunk", "title"],
    )
    for r in results:
        print(f"score={r['@search.score']:.4f}  title={r.get('title')}")
        print(r.get("chunk", "")[:200])
        print("---")

    print(f"\nindex={settings().search_index}  endpoint={settings().search_endpoint}")


if __name__ == "__main__":
    main()
