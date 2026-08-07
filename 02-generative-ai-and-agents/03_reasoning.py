# Run: uv run python 02-generative-ai-and-agents/03_reasoning.py

"""Multi-step reasoning via `reasoning.effort=high` on a reasoning-tier model."""
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
    response = client.responses.create(
        model=settings().reasoning_model,
        instructions="You are a senior software architect.",
        input=_PROBLEM,
        reasoning={"effort": "high"},
    )
    print(response.output_text)


if __name__ == "__main__":
    main()
