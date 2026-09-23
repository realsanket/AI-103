# Run: uv run python 02-generative-ai-and-agents/01_first_api_call.py
# Practice-question coverage: Q53, Q155.

"""First Responses API call — keyless auth via DefaultAzureCredential.

The Responses API is the unified Azure OpenAI-compatible endpoint for generating
completions. This lesson calls it directly: no agent definition, no tools, no
conversation state — the simplest possible path to confirm your endpoint and
credential chain work. DefaultAzureCredential picks up `az login` tokens on a
workstation and managed identity in Azure.

What this proves: `AZURE_OPENAI_ENDPOINT` + deployment name + credential chain.
What it does NOT prove: project endpoint access, tool use, throughput, or
production authorization (successful credential ≠ correct RBAC scope).

What to watch:
  Printed answer confirms the direct client, credential, and deployment are wired
  correctly. 401/403 → check endpoint URL and data-plane role assignment.

Prerequisites / env vars:
  AZURE_OPENAI_ENDPOINT — Azure OpenAI-compatible base URL
  DEFAULT_MODEL         — deployment name (not model family)
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
