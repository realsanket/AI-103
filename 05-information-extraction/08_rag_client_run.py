"""Manual RAG orchestration — retrieve → build prompt → call agent.

Contrast with an agent that has AI Search attached as a first-class tool: this
file shows the "app owns the retrieval" pattern. Useful when you need custom
ranking, filtering, or hybrid strategies before the model sees anything.
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
