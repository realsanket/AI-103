# Run: uv run python 05-information-extraction/14_cu_markdown_for_rag.py
# Practice-question coverage: Q21, Q84.
"""CU prebuilt-layout → Markdown → inspect chunk boundaries for RAG pipelines.

Structure-aware chunking: Content Understanding extracts document structure as
Markdown (headings, tables, figures), then MarkdownHeaderTextSplitter splits on
headers before a recursive 800-char splitter cuts further. This preserves semantic
boundaries better than character-only splits.

This lesson prints chunks for inspection only — it does NOT upload, embed, or index
them. Directly uploading text-only chunks to this repo's index would skip vector
generation and break vector retrieval. For production: feed original Blob files
through L04/L05 (integrated embedding skillset) or generate client-side embeddings
with source/provenance/ACL fields before uploading.

Code path:
  CU_LAYOUT_SOURCE_URL → analyze("prebuilt-layout") → extract markdown → header split
  on #/##/### → recursive 800/100-char split → print chunk count + first chunk.

What to watch. Chunk count and first chunk content. Check that tables and headers
are not split in the middle. If all chunks are similar length, header splitting
didn't find H1/H2/H3 — try a document with clear heading structure.

Prerequisites / env vars:
  CU_ENDPOINT           — https://<resource>.services.ai.azure.com
  CU_API_VERSION        — 2025-11-01 (GA)
  CU_LAYOUT_SOURCE_URL  — HTTPS URL to a structured document (required)
"""
import os

from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

from _shared.cu_client import analyze


def _cu_markdown(source_url: str) -> str:
    result = analyze("prebuilt-layout", source_url)
    contents = result.get("result", {}).get("contents", [])
    return contents[0].get("markdown", "") if contents else ""


def _chunk(markdown: str) -> list[dict]:
    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[("#", "h1"), ("##", "h2"), ("###", "h3")],
    )
    docs = header_splitter.split_text(markdown)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    chunks = text_splitter.split_documents(docs)
    return [{"chunk": c.page_content, "title": c.metadata.get("h1", "")} for c in chunks]


def main() -> None:
    src = os.environ.get("CU_MARKDOWN_SOURCE_URL")
    if not src:
        raise SystemExit("Set CU_MARKDOWN_SOURCE_URL to a PDF Blob SAS URL to run this lesson.")

    markdown = _cu_markdown(src)
    print(f"CU markdown: {len(markdown)} chars")
    docs = _chunk(markdown)
    print(f"chunked into {len(docs)} pieces")

    if docs:
        print("\n--- First chunk ---")
        print(docs[0]["chunk"][:800])
    print("These chunks are not uploaded: direct uploads need client-generated vectors.")
    print("Upload the source to Blob, then run 05 and 04 --run for this index's integrated vectorization.")


if __name__ == "__main__":
    main()
