"""Foundry workflow preview — deploy the conditional-routing YAML.

Microsoft Foundry retires workflows on December 1, 2026. Use this lesson to
study the existing preview artifact, then move new orchestration to Microsoft
Agent Framework and deploy it as a hosted agent.

Beginner note:
  `workflows/wf_triage.yml` defines a three-agent triage flow:

      OnConversationStart
          → InvokeAzureAgent(wf-IntakeAgent) → Local.Triage
          → ConditionGroup:
                Local.Triage.category == "policy_question" → wf-KnowledgeAgent
                else                                        → wf-TicketAgent
          → EndConversation

  This script:
    1. Creates the two "leaf" agents (Knowledge + Ticket) inline so the
       workflow deploy doesn't reference missing agents.
    2. Verifies wf-IntakeAgent exists (created by L15 — you must run L15 first).
    3. Uploads/updates the workflow itself.

  While the preview remains available, test it in the Foundry portal → Agents
  playground → wf-Triage.
"""
from pathlib import Path

from azure.ai.projects.models import PromptAgentDefinition

from _shared.config import settings
from _shared.foundry_client import project_client

WORKFLOW_NAME = "wf-Triage"
WORKFLOW_FILE = Path(__file__).parent / "workflows" / "wf_triage.yml"

INTAKE = "wf-IntakeAgent"   # created by L15
KNOWLEDGE = "wf-KnowledgeAgent"
TICKET = "wf-TicketAgent"


def _ensure_leaf_agents(project) -> None:
    """Create Knowledge + Ticket agents referenced by the workflow YAML."""
    project.agents.create_version(
        agent_name=KNOWLEDGE,
        definition=PromptAgentDefinition(
            model=settings().default_model,
            instructions=(
                "You are the Northwind Knowledge Base agent. Answer product/policy "
                "questions concisely. If the answer isn't in the general knowledge "
                "base, say so and suggest opening a ticket."
            ),
        ),
    )
    project.agents.create_version(
        agent_name=TICKET,
        definition=PromptAgentDefinition(
            model=settings().default_model,
            instructions=(
                "You are the Northwind Ticket Intake agent. Acknowledge the issue, "
                "collect any missing details you need (order id, product, tier), "
                "then confirm that a ticket has been created."
            ),
        ),
    )


def _verify_intake_exists(project) -> None:
    """wf-IntakeAgent must exist — it's created by L15."""
    names = [a.name for a in project.agents.list()]
    if INTAKE not in names:
        raise SystemExit(
            f"{INTAKE} not found. Run L15 first:\n"
            "  uv run python 02-generative-ai-and-agents/15_workflow_intake.py"
        )


def main() -> None:
    client = project_client()
    _verify_intake_exists(client)
    _ensure_leaf_agents(client)

    yaml_text = WORKFLOW_FILE.read_text()

    # Preview surface varies by SDK version.
    workflow = client.agents.create_version(
        agent_name=WORKFLOW_NAME,
        definition={"kind": "workflow", "definition": yaml_text},
    )
    print(f"Workflow {workflow.name} v{workflow.version} deployed.")
    print("Preview only: test in the Foundry portal → Agents playground → wf-Triage.")


if __name__ == "__main__":
    main()
