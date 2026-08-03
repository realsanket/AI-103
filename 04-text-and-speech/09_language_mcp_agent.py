"""Use the Azure Language MCP server as a tool inside a Foundry agent.

Attach the MCP server URL as an mcp tool on the agent, then let the model
decide which language tool (PII / NER / language-detect) to invoke per turn.
"""
from azure.ai.projects.models import McpTool, PromptAgentDefinition

from _shared.config import settings
from _shared.foundry_client import project_client

AGENT_NAME = "northwind-language-mcp-agent"


def main() -> None:
    project = project_client()
    tool = McpTool(server_url=settings().language_mcp_url, server_label="azure_language")

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
