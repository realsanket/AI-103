"""Foundry Memory (preview) with a memory store and memory search tool.

This lesson creates a store with the configured chat and embedding deployments,
then attaches `MemorySearchPreviewTool` to a prompt agent. The store partitions
records by the `x-memory-user-id` header through the `{{$userId}}` scope.

Memory writes are asynchronous and debounced. The second conversation shows a
possible recall after about one minute; it does not guarantee that a specific
fact has already been extracted or retrieved.
"""
import time

from azure.ai.projects.models import (
    MemorySearchPreviewTool,
    MemoryStoreDefaultDefinition,
    MemoryStoreDefaultOptions,
    PromptAgentDefinition,
)

from _shared.config import settings
from _shared.foundry_client import project_client

AGENT_NAME = "northwind-support-with-memory"
MEMORY_STORE_NAME = "northwind-support-memory"
USER_ID = "user-sarah-chen"


def _ensure_memory_store(project):
    for store in project.beta.memory_stores.list():
        if store.name == MEMORY_STORE_NAME:
            return store

    s = settings()
    definition = MemoryStoreDefaultDefinition(
        chat_model=s.default_model,
        embedding_model=s.embedding_model,
        options=MemoryStoreDefaultOptions(
            user_profile_details=(
                "Store customer support preferences only. Do not store credentials, "
                "financial information, or precise location."
            )
        ),
    )
    return project.beta.memory_stores.create(
        name=MEMORY_STORE_NAME,
        definition=definition,
        description="Preview memory store for the Northwind support lesson.",
    )


def main() -> None:
    project = project_client()
    store = _ensure_memory_store(project)
    agent = project.agents.create_version(
        agent_name=AGENT_NAME,
        definition=PromptAgentDefinition(
            model=settings().default_model,
            instructions=(
                "You are Northwind customer support. Use relevant customer preferences "
                "from memory, but never claim a preference you cannot retrieve."
            ),
            tools=[
                MemorySearchPreviewTool(
                    memory_store_name=store.name,
                    scope="{{$userId}}",
                    update_delay=1,
                )
            ],
        ),
    )
    openai = project.get_openai_client()
    headers = {"x-memory-user-id": USER_ID}
    reference = {"type": "agent_reference", "name": agent.name, "version": agent.version}

    first = openai.responses.create(
        conversation=openai.conversations.create().id,
        input="For future visits, I prefer email updates and dairy-free catering.",
        extra_body={"agent_reference": reference},
        extra_headers=headers,
    )
    print("[first conversation]", first.output_text)

    print("Waiting about one minute for the preview memory update...")
    time.sleep(65)
    second = openai.responses.create(
        conversation=openai.conversations.create().id,
        input="What catering preference do you have for me?",
        extra_body={"agent_reference": reference},
        extra_headers=headers,
    )
    print("[second conversation]", second.output_text)


if __name__ == "__main__":
    main()
