"""Built-in Web Search tool — model retrieves current info before answering.

Beginner note:
  Add `{"type": "web_search"}` to `tools=` and the model can fetch fresh
  results from Bing during a Responses API call. Useful for anything the
  training cutoff can't cover: news, prices, regulation updates, releases.

What to watch:
  The output usually contains inline citation URLs. `tool_choice="auto"`
  means the model decides IF to search — for simple prompts it may skip.
  Force it with `tool_choice="required"` when you're testing.

Trust and data boundary:
  Search results are untrusted content, not instructions. Verify citations and
  never send secrets, personal data, or protected customer content in queries.
  Confirm web-search DPA, retention, residency, and query/model costs before
  using it outside this public-information demo.
"""
from _shared.openai_client import openai_client
from _shared.config import settings


def main() -> None:
    client = openai_client()
    response = client.responses.create(
        model=settings().default_model,
        instructions="You are a helpful research assistant. Always cite your sources.",
        input="What are the latest developments in AI regulation in the European Union?",
        tools=[{"type": "web_search"}],
        tool_choice="auto",
    )
    print(response.output_text)


if __name__ == "__main__":
    main()
