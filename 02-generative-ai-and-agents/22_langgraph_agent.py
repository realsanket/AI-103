"""LangGraph stateful agent — Northwind policy Q&A backed by FAISS + PDFs.

Shows LangGraph's core primitives: `StateGraph`, `MessagesState`, nodes,
conditional edges. RAG uses a local FAISS index over the Northwind policy
PDFs in `_shared/sample_data/northwind_policies/`.

Not production RAG — FAISS is local, in-memory, rebuilt from sample PDFs on
each run, and has no service RBAC, network boundary, or operational index
lifecycle. For production, use Azure AI Search (see Domain 5), with managed
indexing, RBAC, private networking, and retention controls. This lesson is
about the *graph orchestration* pattern.
"""
from langchain.tools import tool
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import END, MessagesState, START, StateGraph
from langgraph.prebuilt import ToolNode

from _shared.config import SAMPLE_DATA, settings
from _shared.openai_client import azure_openai_token_provider


def _clients() -> tuple[ChatOpenAI, OpenAIEmbeddings]:
    s = settings()
    api_key = azure_openai_token_provider()
    base_url = f"{s.require('AZURE_OPENAI_ENDPOINT')}/openai/v1"
    return (
        ChatOpenAI(base_url=base_url, api_key=api_key, model=s.default_model),
        OpenAIEmbeddings(base_url=base_url, api_key=api_key, model=s.embedding_model),
    )


def _build_vector_store(embeddings: OpenAIEmbeddings) -> FAISS:
    docs = []
    for pdf in sorted((SAMPLE_DATA / "northwind_policies").glob("*.pdf")):
        docs.extend(PyPDFLoader(str(pdf)).load())
    print(f"Loaded {len(docs)} pages across Northwind policies.")
    chunks = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50).split_documents(docs)
    print(f"Split into {len(chunks)} chunks. Building vector store...")
    return FAISS.from_documents(chunks, embeddings)


def main() -> None:
    model, embeddings = _clients()
    vector_store = _build_vector_store(embeddings)

    @tool
    def search_northwind_policies(query: str) -> str:
        """Search Northwind policy documents (AUP, refund, SLA)."""
        hits = vector_store.similarity_search(query, k=3)
        if not hits:
            return "No relevant policy information found."
        return "\n\n".join(
            f"[Excerpt {i} from {d.metadata.get('source', 'policy')}]\n{d.page_content}"
            for i, d in enumerate(hits, 1)
        )

    tools = [search_northwind_policies]
    model_with_tools = model.bind_tools(tools)

    def call_model(state: MessagesState) -> dict:
        system = {
            "role": "system",
            "content": (
                "You are the Northwind policy assistant. Answer using search_northwind_policies. "
                "Ground answers in retrieved excerpts. Say so if you cannot find the answer."
            ),
        }
        return {"messages": [model_with_tools.invoke([system] + state["messages"])]}

    def should_continue(state: MessagesState) -> str:
        return "tools" if state["messages"][-1].tool_calls else END

    graph = (
        StateGraph(MessagesState)
        .add_node("call_model", call_model)
        .add_node("tools", ToolNode(tools))
        .add_edge(START, "call_model")
        .add_conditional_edges("call_model", should_continue)
        .add_edge("tools", "call_model")
        .compile()
    )
    print("Agent ready.\n")

    for question in [
        "What is the refund window for a Northwind Pro subscription?",
        "What uptime does Northwind guarantee for Enterprise customers?",
        "Can I mine cryptocurrency on Northwind compute resources?",
    ]:
        print(f"Q: {question}")
        result = graph.invoke({"messages": [{"role": "user", "content": question}]})
        print(f"A: {result['messages'][-1].content}\n{'-' * 60}")


if __name__ == "__main__":
    main()
