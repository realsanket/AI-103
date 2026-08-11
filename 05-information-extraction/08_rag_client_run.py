# Run: uv run python 05-information-extraction/08_rag_client_run.py
"""App-owned manual RAG — hybrid retrieve → prompt → Foundry agent → grounded answer.

The application owns the full retrieval pipeline: it queries Search with a hybrid
query (BM25 + vector), formats the top-3 chunks as source blocks with title/URL,
and supplies them in the prompt to the L07 agent. The model answers only from the
provided sources and cites the URL. Compare with lesson 20's managed Search tool
where the agent controls retrieval.

This pattern is appropriate when you need custom ranking, ACL filters, deduplication,
or retrieval audit before the model sees anything. NOT a replacement for ACL enforcement
— the Search query here has no security filter and should not be used with
mixed-permission content.

Code path:
  _retrieve(question) → hybrid query with VectorizableTextQuery → format 3 chunks
  as "SOURCE [title]: [chunk]\nURL: [source_url]" blocks → project.get_openai_client()
  → responses.create() with agent_reference (L07 agent) → print output_text.

What to watch. A grounded refund answer or "I don't have that information" refusal.
The agent should cite a source URL. If it hallucinates a policy, the retrieval
didn't return relevant chunks — check index population.

Prerequisites / env vars:
  SEARCH_ENDPOINT     — https://<service>.search.windows.net
  SEARCH_INDEX_VECTOR — populated index
  PROJECT_ENDPOINT    — Foundry project with L07 agent created
  DEFAULT_MODEL       — deployed chat model
"""
from azure.search.documents.models import VectorizableTextQuery

from _shared.config import settings
from _shared.foundry_client import project_client
from _shared.search_client import search_client

AGENT_NAME = "northwind-manual-rag-agent"


def _retrieve(question: str, top: int = 3) -> str:
    client = search_client(settings().search_index_vector)
    results = client.search(
        search_text=question,
        vector_queries=[
            VectorizableTextQuery(
                text=question,
                k_nearest_neighbors=top,
                fields="text_vector",
            )
        ],
        select=["chunk", "title", "parent_id", "source_url"],
        top=top,
    )
    sources = []
    for r in results:
        sources.append(
            f"[Source title: {r.get('title', 'unknown')}]\n"
            f"[Parent ID: {r.get('parent_id', '')}]\n"
            f"[Source URL: {r.get('source_url', '')}]\n"
            f"{r.get('chunk', '')}"
        )
    return "\n\n".join(sources)


def ask(question: str) -> str:
    sources = _retrieve(question)
    prompt = (
        "You are a customer support agent for Northwind Technology Services.\n"
        "Answer using only the sources provided below. If the sources do not contain "
        "enough information, say so.\n\n"
        f"Sources:\n{sources}\n\n"
        f"Customer question:\n{question}\n"
    )
    project = project_client()
    openai = project.get_openai_client()
    r = openai.responses.create(
        extra_body={"agent_reference": {"type": "agent_reference", "name": AGENT_NAME}},
        input=prompt,
    )
    return r.output_text


def main() -> None:
    print(ask("Can I get my money back?"))


if __name__ == "__main__":
    main()
