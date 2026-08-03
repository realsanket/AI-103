"""Built-in File Search — RAG without AI Search.

Upload a few docs, attach the File Search tool with a vector store id, then
ask a question. Foundry does the chunking + embeddings + retrieval; no index
or skillset for you to run.
"""
from pathlib import Path

from _shared.config import SAMPLE_DATA, settings
from _shared.openai_client import openai_client


def main() -> None:
    client = openai_client()

    # Upload the Northwind policy PDFs
    files = []
    for pdf in sorted((SAMPLE_DATA / "northwind_policies").glob("*.pdf")):
        f = client.files.create(file=Path(pdf).open("rb"), purpose="assistants")
        files.append(f.id)
        print(f"uploaded: {pdf.name} → {f.id}")

    vs = client.vector_stores.create(name="northwind-policies", file_ids=files)
    print(f"vector store: {vs.id}")

    r = client.responses.create(
        model=settings().default_model,
        input="What is the refund window for the Northwind Pro plan?",
        tools=[{"type": "file_search", "vector_store_ids": [vs.id]}],
        tool_choice="auto",
    )
    print("\n=== Answer ===")
    print(r.output_text)


if __name__ == "__main__":
    main()
