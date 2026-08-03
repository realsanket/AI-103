"""CU → Markdown → chunk → index into AI Search.

The clean-representation pattern: let Content Understanding produce faithful
Markdown for each source doc, then use LangChain's text splitters (or the
native Search text-split skill) to chunk before indexing.
"""
import os

from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

from _shared.cu_client import analyze
from _shared.config import settings
from _shared.search_client import search_client


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
    return [{"id": f"chunk-{i}", "chunk": c.page_content, "title": c.metadata.get("h1", "")} for i, c in enumerate(chunks)]


def main() -> None:
    src = os.environ.get("CU_MARKDOWN_SOURCE_URL")
    if not src:
        raise SystemExit("Set CU_MARKDOWN_SOURCE_URL to a PDF Blob SAS URL to run this lesson.")

    markdown = _cu_markdown(src)
    print(f"CU markdown: {len(markdown)} chars")
    docs = _chunk(markdown)
    print(f"chunked into {len(docs)} pieces")

    client = search_client(settings().search_index)
    client.merge_or_upload_documents(documents=docs)
    print(f"uploaded to index {settings().search_index}")


if __name__ == "__main__":
    main()
