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

from _shared.config import settings
from _shared.foundry_client import project_client

SCHEMA_FILE = Path(__file__).parent / "workflows" / "wf_intake_schema.json"

_SAMPLE_TICKET = (
    "Hi Northwind, I signed up for the Pro plan yesterday but I want to cancel "
    "and get my $99 back. The dashboard is much slower than the demo showed."
)

_INSTRUCTIONS = (
    "You are the Northwind support intake agent. Classify the customer's "
    "message into one triage result. Only output the JSON schema requested."
)


def main() -> None:
    schema_wrapper = json.loads(SCHEMA_FILE.read_text())

    project = project_client()
    openai = project.get_openai_client()
    # structured output (text.format) is not allowed with agent_reference —
    # use model directly so the response is schema-bound
    r = openai.responses.create(
        model=settings().default_model,
        instructions=_INSTRUCTIONS,
        input=_SAMPLE_TICKET,
        text={"format": {"type": "json_schema", **schema_wrapper}},
    )
    triage = json.loads(r.output_text)
    print("Triage result:", json.dumps(triage, indent=2))


if __name__ == "__main__":
    main()
