"""Content Understanding `prebuilt-layout` — tables + figures + sections + reading order.

Preserves document structure so downstream RAG chunks stay semantically clean.
"""
import os

from _shared.cu_client import analyze


def main() -> None:
    src = os.environ.get("CU_LAYOUT_SOURCE_URL")
    if not src:
        raise SystemExit(
            "Set CU_LAYOUT_SOURCE_URL to a PDF URL (Blob SAS is easiest). "
            "Use a document with tables/figures to see the layout output."
        )
    result = analyze("prebuilt-layout", src)
    contents = result.get("result", {}).get("contents", [])
    if not contents:
        print("no contents")
        return
    doc = contents[0]
    print(f"pages: {len(doc.get('pages', []))}")
    print(f"tables: {len(doc.get('tables', []))}")
    print(f"figures: {len(doc.get('figures', []))}")
    print(f"sections: {len(doc.get('sections', []))}")
    print("\n--- Markdown preview ---")
    print(doc.get("markdown", "")[:800])


if __name__ == "__main__":
    main()
