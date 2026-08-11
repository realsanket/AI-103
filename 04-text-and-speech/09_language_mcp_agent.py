# Run: uv run python 04-text-and-speech/09_language_mcp_agent.py
"""Attach the Language MCP server to a Foundry Prompt Agent and run a query.

Builds on 08_language_mcp_tools.py: instead of listing tools directly, this lesson
wraps the Language MCP server as an MCPTool on a Foundry agent. The model decides
which Language capability to invoke (NER, language detect, PII...) based on the
user's question — no hardcoded routing. Requires a Foundry project connection that
authorizes Language MCP for agent authentication; the lesson does not create that
connection.

Code path:
  project_client() → MCPTool(server_url, server_label) → agents.create_version()
  with PromptAgentDefinition → project.get_openai_client() → responses.create()
  with agent_reference → output_text printed.

What to watch: the response should identify Japanese as the language and Sarah Chen
as a mentioned person, with the agent having called the appropriate MCP tools
under the hood (check Foundry trace if available).

Prerequisites / env vars:
  LANGUAGE_MCP_URL — Language MCP endpoint URL
  PROJECT_ENDPOINT — Foundry project endpoint
  DEFAULT_MODEL    — deployed chat model
"""
from azure.ai.projects.models import MCPTool, PromptAgentDefinition

from _shared.config import settings
from _shared.foundry_client import project_client

AGENT_NAME = "northwind-language-mcp-agent"


def main() -> None:
    project = project_client()
    tool = MCPTool(server_url=settings().language_mcp_url, server_label="azure_language")

    agent = project.agents.create_version(
        agent_name=AGENT_NAME,
        definition=PromptAgentDefinition(
            model=settings().default_model,
            instructions=(
                "You analyze customer support text using the Azure Language MCP tools. "
                "Pick the right tool per user question — do not answer from memory."
            ),
            tools=[tool],
        ),
    )
    ref = {"type": "agent_reference", "name": agent.name, "version": agent.version}
    openai = project.get_openai_client()
    r = openai.responses.create(
        input=(
            "Analyze this message. What language is it in, and who is mentioned?\n\n"
            "こんにちは、Sarah Chenです。TKT-1042の件でVPNの問題を報告しています。"
        ),
        extra_body={"agent_reference": ref},
    )
    print(r.output_text)


if __name__ == "__main__":
    main()
