# Run: uv run python 08-advanced-agents-other/11_agent_memory.py [--apply]
"""Attach a vector-store memory to a Foundry agent and verify recall.

Agent memory lets hosted agents persist information across sessions by storing
embeddings in a Foundry vector store. The agent retrieves relevant memories
automatically via file_search tool. This lesson proves the create→attach→query
→cleanup pattern: create a vector store, write a fact, attach it to an agent,
query the fact, then delete both artifacts.

Default preflight checks env. --apply creates a vector store, uploads one text
document, creates a prompt agent with file_search pointing at the vector store,
runs a query, then deletes agent and vector store.

Code path:
  --apply:
  1. agents.vector_stores.create(name=...) → vs.id
  2. agents.vector_stores.files.upload_and_poll(vector_store_id, file, filename)
  3. agents.create_version(tools=[{"type":"file_search","file_search":{"vector_store_ids":[vs.id]}}])
  4. agents.threads.create() → messages.create(user query) → runs.create_and_process()
  5. agents.messages.list() → print assistant reply
  6. agents.delete() + agents.vector_stores.delete()

What to watch. Assistant answer references the uploaded fact. No recall =
vector store not yet indexed (indexing async; the upload_and_poll call waits).

Prerequisites / env vars:
  PROJECT_ENDPOINT  — Foundry project HTTPS URL
  DEFAULT_MODEL     — deployed chat model
  --apply           — create vector store + ephemeral agent + query + cleanup
"""
import argparse
import io

from _shared.config import settings
from _shared.foundry_client import project_client

_FACT = "The Northwind Seattle warehouse holds 42,000 units of SKU-7829 (Blue Widget Pro)."
_QUERY = "How many Blue Widget Pro units are in the Seattle warehouse?"


def preflight() -> None:
    current = settings()
    print("Agent memory (vector store) preflight (no cloud calls).")
    print(f"- project_endpoint: {'configured' if current.project_endpoint else 'missing'}")
    print(f"- default_model: {'configured' if current.default_model else 'missing'}")
    print("- Pattern: vector store → upload doc → file_search tool → agent query → cleanup.")
    print("Run --apply to create an ephemeral memory-enabled agent and verify recall.")


def apply() -> None:
    from azure.ai.projects.models import PromptAgentDefinition

    current = settings()
    client = project_client()
    agent_name = "memory-probe-agent"
    vs = None
    try:
        vs = client.agents.vector_stores.create(name="memory-probe-vs")
        print(f"Vector store created: {vs.id}")

        buf = io.BytesIO(_FACT.encode())
        client.agents.vector_stores.files.upload_and_poll(
            vector_store_id=vs.id,
            file=buf,
            filename="fact.txt",
        )
        print("Fact uploaded and indexed.")

        tools = [{"type": "file_search", "file_search": {"vector_store_ids": [vs.id]}}]
        agent = client.agents.create_version(
            agent_name=agent_name,
            definition=PromptAgentDefinition(
                model=current.require("DEFAULT_MODEL"),
                instructions="Answer questions using the provided knowledge base.",
                tools=tools,
            ),
        )
        print(f"Agent '{agent.name}' v{agent.version} created.")

        thread = client.agents.threads.create()
        client.agents.messages.create(thread_id=thread.id, role="user", content=_QUERY)
        client.agents.runs.create_and_process(thread_id=thread.id, agent_name=agent_name)
        for msg in client.agents.messages.list(thread_id=thread.id):
            if msg.role == "assistant":
                for block in (msg.content or []):
                    if hasattr(block, "text"):
                        print(f"Answer: {block.text.value}")
                break
    finally:
        if vs:
            try:
                client.agents.delete(agent_name)
            except Exception:
                pass
            client.agents.vector_stores.delete(vs.id)
            print("Cleanup complete.")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Attach vector-store memory to agent; verify recall.")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    if not args.apply:
        preflight()
        return
    apply()


if __name__ == "__main__":
    main()
