# Run: uv run python 05-information-extraction/10_cu_prebuilt_layout.py
# Practice-question coverage: Q2, Q84.
"""Content Understanding `prebuilt-layout` — structure-preserving extraction to Markdown.

`prebuilt-layout` extracts pages, tables, figures, sections, and reading order into
Markdown. Use it when document structure matters for RAG chunks — tables become
Markdown tables, headings become header markers, figures are referenced. This is
better evidence than flattened OCR (prebuilt-read, L09) for documents with tables.
Does NOT extract domain-specific fields like invoice totals — use prebuilt-invoice (L11).

Requires CU_LAYOUT_SOURCE_URL set to an HTTPS URL. Upload your document to Blob
and generate a short-lived read-only SAS URL. A document with tables and figures
best demonstrates the layout output.

Code path:
  analyze("prebuilt-layout", CU_LAYOUT_SOURCE_URL) → poll → print pages, tables,
  figures, sections counts and first 800 chars of markdown.

What to watch. Table count > 0 and Markdown includes `| col | col |` table syntax.
If counts are all 0, the document has no detectable structure. Compare with L09.

Prerequisites / env vars:
  CU_ENDPOINT           — https://<resource>.services.ai.azure.com
  CU_API_VERSION        — 2025-11-01 (GA)
  CU_LAYOUT_SOURCE_URL  — HTTPS URL to a document with tables/figures (required)
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
