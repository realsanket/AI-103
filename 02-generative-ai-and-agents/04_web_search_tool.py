# Run: uv run python 02-generative-ai-and-agents/04_web_search_tool.py
# Practice-question coverage: Q6, Q79, Q86.

"""Built-in Web Search tool.

This example demonstrates:
- Enabling the built-in web search tool
- Letting the model decide when to search
- Streaming the response
- Showing when the tool is invoked

The model may decide not to search if it already knows the answer.
Use tool_choice="required" to force a search while learning.
"""

from _shared.openai_client import openai_client
from _shared.config import settings


QUESTION = (
    "What are the latest developments in AI regulation in the European Union?"
)


def main() -> None:
    client = openai_client()

    print(f"Model: {settings().default_model}")
    print(f"Question: {QUESTION}\n")

    stream = client.responses.create(
        model=settings().default_model,
        instructions=(
            "You are a helpful research assistant. "
            "Always use the web search tool and cite sources."
        ),
        input=QUESTION,
        tools=[{"type": "web_search"}],
        tool_choice="required",
        stream=True,
    )

    search_started = False
    answer_started = False

    for event in stream:
        event_type = getattr(event, "type", "")

        # Uncomment this while learning to inspect every event.
        # print(event_type)

        # ------------------------------------------------------------
        # Tool invocation
        # ------------------------------------------------------------
        if (
            event_type == "response.output_item.added"
            and getattr(event, "item", None)
            and getattr(event.item, "type", "") == "web_search_call"
        ):
            if not search_started:
                print("=== Web Search Tool ===")
                print("Searching the web...\n")
                search_started = True

        elif event_type == "response.output_item.done":
            item = getattr(event, "item", None)
            if item and getattr(item, "type", "") == "web_search_call":
                print("✓ Search complete.\n")

        # ------------------------------------------------------------
        # Stream final answer
        # ------------------------------------------------------------
        elif event_type == "response.output_text.delta":
            if not answer_started:
                print("=== Final Answer ===\n")
                answer_started = True

            print(event.delta, end="", flush=True)

    print()


if __name__ == "__main__":
    main()