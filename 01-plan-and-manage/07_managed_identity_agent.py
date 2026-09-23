# Run: uv run python 01-plan-and-manage/07_managed_identity_agent.py
# Practice-question coverage: Q53, Q71.
"""Keyless project auth smoke test — DefaultAzureCredential end-to-end.

Verifies three things in order:
  1. project_client() authenticates with DefaultAzureCredential
  2. Foundry Agents API is reachable (lists hosted agents)
  3. Responses API works through the project-scoped OpenAI endpoint

DefaultAzureCredential tries configured environment credentials, workload
identity, managed identity, developer-tool credentials such as Azure CLI, and
other supported local credentials. On a developer machine, `az login` commonly
supplies the token; on Azure, managed identity commonly supplies it. This
script doesn't prove which link supplied the token.

Two OpenAI endpoints exist on the same Foundry resource:
  <resource>.openai.azure.com/openai/v1/   → direct Azure OpenAI resource API
  <resource>.services.ai.azure.com/...     → project-scoped Foundry API

This file tests the project-scoped path. It requires access on its Foundry
project/resource; direct resource inference needs a Cognitive Services
inference role instead.
"""
from _shared.config import settings
from _shared.foundry_client import project_client


def main() -> None:
    client = project_client()

    # 1 — Auth check: list hosted agents (Foundry code-based agents, not LLM agents)
    agents = list(client.agents.list())
    print(f"[1] Auth OK — {len(agents)} hosted agent(s) in project")
    for a in agents[:5]:
        print(f"    {getattr(a, 'name', '?')}")

    # 2 — Project-scoped Responses API (same endpoint used by agent turns)
    oc = client.get_openai_client()
    print(f"\n[2] Project OpenAI endpoint: {oc.base_url}")
    r = oc.responses.create(
        model=settings().default_model,
        input="Reply with exactly: auth chain OK",
    )
    print(f"[2] Response: {r.output_text}")

    print("\nSmoke test passed — DefaultAzureCredential + Foundry project endpoint working.")


if __name__ == "__main__":
    main()
