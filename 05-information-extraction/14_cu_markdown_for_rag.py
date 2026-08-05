"""CU → Markdown → chunks ready for the Search ingestion pipeline.

The clean-representation pattern: let Content Understanding produce faithful
Markdown for each source doc, then use text splitters to inspect chunk
boundaries. For searchable vectors, upload source files to Blob and run the
indexer: its skillset creates vectors before writing the Search index.
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
