"""Built-in Web Search tool — model retrieves current info before answering."""
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
