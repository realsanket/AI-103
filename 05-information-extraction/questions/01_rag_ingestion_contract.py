# Run: uv run python 05-information-extraction/questions/01_rag_ingestion_contract.py
# Practice-question coverage: Q21.
"""Question supplement: preserve RAG chunk provenance during document ingestion.

Maps PDF question 21. This application-level contract keeps
page, source, structure, and ACL metadata attached to every chunk. It is not a
replacement for the Search index, data source, skillset, and indexer assets;
those four assets must still be changed and validated as one unit.
"""
from __future__ import annotations


def rag_chunk(*, document_id: str, page_number: int, markdown: str,
              source_path: str, acl_ids: list[str]) -> dict[str, object]:
    if not document_id or not source_path:
        raise ValueError("document_id and source_path are required.")
    if page_number < 1:
        raise ValueError("page_number must be one-based.")
    if not markdown.strip():
        raise ValueError("markdown must not be blank.")
    if not acl_ids or any(not value.strip() for value in acl_ids):
        raise ValueError("acl_ids must contain at least one nonblank principal or group ID.")
    return {
        "id": f"{document_id}-p{page_number}",
        "parent_document_id": document_id,
        "page_number": page_number,
        "content_markdown": markdown,
        "source_path": source_path,
        "allowed_principals": acl_ids,
        "provenance": {"layout_preserved": True, "ocr_required_for_scans": True},
    }


def main() -> None:
    print("No cloud calls made. Example chunk contract:")
    print(rag_chunk(
        document_id="maintenance-guide-2026", page_number=3,
        markdown="## Reset procedure\n| Step | Action |\n|---|---|\n| 1 | Disconnect power |",
        source_path="guides/maintenance.pdf", acl_ids=["group:field-engineers"],
    ))


if __name__ == "__main__":
    main()
