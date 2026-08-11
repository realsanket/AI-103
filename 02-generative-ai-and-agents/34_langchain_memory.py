# Run: uv run python 02-generative-ai-and-agents/34_langchain_memory.py [--apply]
"""LangChain memory pattern: multi-turn conversation with server-side thread state.

Beyond lesson 19 (single-turn LangChain call), production agents need
conversation state across turns. This lab uses LangChain's memory
primitive backed by Azure OpenAI Responses API — server maintains state via
`previous_response_id`, LangChain wraps it as a `Memory` object.

Default preflight explains pattern. `--apply` sends THREE turns to prove
memory: turn 1 introduces context, turn 2 asks follow-up (should reference
turn 1), turn 3 confirms retention. Uses AzureChatOpenAI + a simple in-memory
`ChatMessageHistory` — production would use Redis, Cosmos, or Foundry-managed
memory (see lesson 14).

Alternative: use Foundry `previous_response_id` directly (lesson 13).
LangChain adds middleware/tool wrapping but same underlying state model.

Code path:
  --apply: AzureChatOpenAI + ChatMessageHistory + RunnableWithMessageHistory.
  Call 3 times with same session_id → each turn appends to history. Print
  each response.

What to watch. Turn 2 response references "Northwind Pro" from turn 1
without re-mentioning it. Turn 3 correctly identifies the last topic. If
memory not working, turn 2 will ask "what plan?"

Prerequisites / env vars:
  AZURE_OPENAI_ENDPOINT  — Azure OpenAI resource URL
  DEFAULT_MODEL          — deployment name
  --apply                — send 3 billable requests
"""
import argparse

from _shared.config import settings


def preflight() -> None:
    print("LangChain memory preflight (no cloud calls).")
    print("- Uses AzureChatOpenAI + ChatMessageHistory + RunnableWithMessageHistory.")
    print("- Production: replace ChatMessageHistory with Redis / Cosmos / Foundry Memory.")
    print("- Compare with lesson 13 (server-side thread) + lesson 14 (Foundry Memory preview).")


def apply() -> None:
    from langchain_core.chat_history import InMemoryChatMessageHistory
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain_core.runnables.history import RunnableWithMessageHistory
    from langchain_openai import AzureChatOpenAI

    llm = AzureChatOpenAI(
        azure_deployment=settings().require("DEFAULT_MODEL"),
        api_version="2024-10-21",
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are Northwind support. Keep answers under 20 words."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ])
    store: dict[str, InMemoryChatMessageHistory] = {}
    chain = RunnableWithMessageHistory(
        prompt | llm,
        lambda session_id: store.setdefault(session_id, InMemoryChatMessageHistory()),
        input_messages_key="input",
        history_messages_key="history",
    )
    session = {"configurable": {"session_id": "demo-session"}}
    turns = [
        "I subscribe to Northwind Pro. What's the refund window?",
        "And what if I cancel after that period?",
        "OK, what was my subscription plan again?",
    ]
    for i, turn in enumerate(turns, 1):
        print(f"\nTurn {i}: {turn}")
        response = chain.invoke({"input": turn}, config=session)
        print(f"  → {response.content}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="LangChain memory pattern demo.")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    if not args.apply:
        preflight()
        return
    apply()


if __name__ == "__main__":
    main()
