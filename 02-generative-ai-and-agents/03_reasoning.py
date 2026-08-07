# Run:
# uv run python 02-generative-ai-and-agents/03_reasoning.py

"""Reasoning example with streaming."""

from _shared.openai_client import openai_client
from _shared.config import settings

_PROBLEM = """
A distributed e-commerce system is experiencing intermittent checkout failures
during peak traffic. The failures appear random, affect roughly 3 percent of the
transactions, and only occur when inventory checks and payment processing run
concurrently. Identify the most likely root cause and propose a solution.
"""


def main() -> None:
    client = openai_client()

    print(f"Model: {settings().reasoning_model}")
    print("\nStreaming...\n")

    stream = client.responses.create(
        model=settings().reasoning_model,
        instructions="You are a senior software architect.",
        input=_PROBLEM,
        reasoning={
            "effort": "high",
            "summary": "detailed",  # try "auto" if "detailed" isn't supported
        },
        stream=True,
    )

    saw_summary = False

    for event in stream:
        # Uncomment while debugging
        # print(event.type)

        if event.type == "response.reasoning_summary_text.delta":
            if not saw_summary:
                print("\n=== Reasoning Summary ===\n")
                saw_summary = True
            print(event.delta, end="", flush=True)

        elif event.type == "response.output_text.delta":
            if saw_summary:
                # transition to answer once
                print("\n\n=== Final Answer ===\n")
                saw_summary = False
            print(event.delta, end="", flush=True)

    print()


if __name__ == "__main__":
    main()