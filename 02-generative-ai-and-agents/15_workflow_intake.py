# Run: uv run python 02-generative-ai-and-agents/15_workflow_intake.py

"""Preview workflow prerequisite — intake agent producing structured triage output.

The workflow definition (`workflows/wf_intake_schema.json`) shows the JSON
schema the intake agent must fill in. It supports lesson 16's preview workflow
artifact; workflows retire on December 1, 2026. This script:

1. Creates an intake agent whose Response API call is bound to that schema
   (strict json_schema), and
2. Runs it against a sample ticket, printing the structured triage result
   the workflow uses to route the next step.
"""
import json
from pathlib import Path

from azure.ai.projects.models import PromptAgentDefinition

from _shared.config import settings
from _shared.foundry_client import active_agent_reference, project_client

AGENT_NAME = "wf-IntakeAgent"
SCHEMA_FILE = Path(__file__).parent / "workflows" / "wf_intake_schema.json"

_SAMPLE_TICKET = (
    "Hi Northwind, I signed up for the Pro plan yesterday but I want to cancel "
    "and get my $99 back. The dashboard is much slower than the demo showed."
)


def main() -> None:
    schema_wrapper = json.loads(SCHEMA_FILE.read_text())

    project = project_client()
    agent = project.agents.create_version(
        agent_name=AGENT_NAME,
        definition=PromptAgentDefinition(
            model=settings().default_model,
            instructions=(
                "You are the Northwind support intake agent. Classify the customer's "
                "message into one triage result. Only output the JSON schema requested."
            ),
        ),
    )
    ref = active_agent_reference(agent)
    openai = project.get_openai_client()
    r = openai.responses.create(
        input=_SAMPLE_TICKET,
        extra_body={"agent_reference": ref},
        text={"format": {"type": "json_schema", **schema_wrapper}},
    )
    triage = json.loads(r.output_text)
    print("Triage result:", json.dumps(triage, indent=2))


if __name__ == "__main__":
    main()
