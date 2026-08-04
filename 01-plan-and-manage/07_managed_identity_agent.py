# Run: uv run python 01-plan-and-manage/07_managed_identity_agent.py
"""Keyless auth smoke test — DefaultAzureCredential end-to-end.

Verifies three things in order:
  1. project_client() authenticates via az login (DefaultAzureCredential)
  2. Foundry Agents API is reachable (lists hosted agents)
  3. Responses API works through the project-scoped OpenAI endpoint

If all three pass, every other lesson's auth will work the same way.

Two OpenAI endpoints exist on the same Foundry resource:
  openai.azure.com/openai/v1/             → direct Azure OpenAI (openai_client())
  services.ai.azure.com/.../openai/v1/   → project-scoped Foundry (project_client().get_openai_client())

This file tests the project-scoped path.
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
