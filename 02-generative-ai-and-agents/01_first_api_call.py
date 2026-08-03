"""First Responses API call — keyless auth via DefaultAzureCredential.

Prints a short answer from the default model. Zero infra prereqs beyond
`.env` + `az login`.
"""
from _shared.openai_client import openai_client
from _shared.config import settings


def main() -> None:
    client = openai_client()
    response = client.responses.create(
        model=settings().default_model,
        input="What are the three main benefits of using managed AI endpoints in the cloud?",
    )
    print("answer:", response.output_text)


if __name__ == "__main__":
    main()
