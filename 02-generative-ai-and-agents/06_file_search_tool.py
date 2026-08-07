# Run: uv run python 02-generative-ai-and-agents/06_file_search_tool.py

"""Built-in File Search — RAG without AI Search.

Upload a few docs, attach the File Search tool with a vector store id, then
ask a question. Foundry does the chunking + embeddings + retrieval; no index
or skillset for you to run.

This run creates persistent files and a vector store. Use only approved
documents; retrieval results remain untrusted text, not instructions. Confirm
DPA, retention, residency, RBAC, and storage/embedding/query costs, then delete
the created vector store and files after your lab.
"""
from pathlib import Path

from _shared.config import SAMPLE_DATA, settings
from _shared.foundry_client import project_client

POLICY_DIRECTORY = SAMPLE_DATA / "northwind_policies"
MAX_FILE_BYTES = 512 * 1024 * 1024


def _policy_pdfs() -> list[Path]:
    """Validate local lesson inputs before creating cloud file-search assets."""
    pdfs = sorted(POLICY_DIRECTORY.glob("*.pdf"))
    if not pdfs:
        raise SystemExit(f"No PDF files found in {POLICY_DIRECTORY}.")
    invalid = [pdf.name for pdf in pdfs if not pdf.is_file() or not pdf.stat().st_size]
    oversized = [pdf.name for pdf in pdfs if pdf.is_file() and pdf.stat().st_size > MAX_FILE_BYTES]
    if invalid:
        raise SystemExit(f"File Search needs non-empty PDF files; invalid: {', '.join(invalid)}.")
    if oversized:
        raise SystemExit(
            f"File Search accepts files up to 512 MB; too large: {', '.join(oversized)}."
        )
    return pdfs


def main() -> None:
    pdfs = _policy_pdfs()
    client = project_client().get_openai_client()
    vector_store = client.vector_stores.create(name="northwind-policies")
    file_ids = []
    print(f"vector store: {vector_store.id}")

    try:
        for pdf in pdfs:
            with pdf.open("rb") as file_handle:
                uploaded = client.vector_stores.files.upload_and_poll(
                    vector_store_id=vector_store.id,
                    file=file_handle,
                )
            file_ids.append(uploaded.id)
            if uploaded.status != "completed":
                raise RuntimeError(f"Indexing {pdf.name} ended with status {uploaded.status!r}.")
            print(f"indexed: {pdf.name} → {uploaded.id}")

        response = client.responses.create(
            model=settings().default_model,
            input="What is the refund window for the Northwind Pro plan?",
            tools=[{"type": "file_search", "vector_store_ids": [vector_store.id]}],
            tool_choice="auto",
        )
        print("\n=== Answer ===")
        print(response.output_text)
    finally:
        client.vector_stores.delete(vector_store.id)
        for file_id in file_ids:
            client.files.delete(file_id)
        print("\nDeleted lesson vector store and uploaded files.")


if __name__ == "__main__":
    main()
