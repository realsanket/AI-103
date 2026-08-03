"""Foundry Workflow — deploy the conditional-routing workflow (YAML).

`workflows/wf_triage.yml` defines:

    OnConversationStart
        → InvokeAgent(wf-IntakeAgent) → Local.Triage
        → ConditionGroup:
              Local.Triage.category == "policy_question" → wf-KnowledgeAgent
              else                                      → wf-TicketAgent
        → EndConversation

This script uploads/updates that workflow so the portal designer + code view
stay in sync. Prereq: `wf-IntakeAgent`, `wf-KnowledgeAgent`, `wf-TicketAgent`
already exist in the project.
"""
from pathlib import Path

from _shared.foundry_client import project_client

WORKFLOW_NAME = "wf-Triage"
WORKFLOW_FILE = Path(__file__).parent / "workflows" / "wf_triage.yml"


def main() -> None:
    yaml_text = WORKFLOW_FILE.read_text()
    client = project_client()

    # Workflow deploy surface is preview and varies by SDK version — the shape
    # below matches azure-ai-projects >= 1.0.0b10. Update if your SDK differs.
    workflow = client.agents.create_version(
        agent_name=WORKFLOW_NAME,
        definition={"kind": "workflow", "definition": yaml_text},
    )
    print(f"Workflow {workflow.name} v{workflow.version} deployed.")
    print("Test in the portal → Agents playground → wf-Triage.")


if __name__ == "__main__":
    main()
