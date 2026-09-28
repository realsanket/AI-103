# Run: uv run python 02-generative-ai-and-agents/32_openai_json_mode.py [--apply]
# Practice-question coverage: Q82.
"""Force strict JSON output via Responses API json_schema response format.

Structured output (json_schema) constrains model output to a validated
schema. Different from lesson 07's Pydantic wrapper — this is raw
`response_format={"type": "json_schema", ...}` on Responses API.

Default preflight explains schema. `--apply` sends ONE Responses call
demanding output matching a small support-ticket schema. Prints parsed
result. Failure to match schema is a service-side error, not silent —
enforcement is at the model output layer.

json_schema mode differs from json_mode (older): json_schema enforces
STRUCTURE + types; older json_mode only guarantees valid JSON (any shape).
Use json_schema for downstream parsing that assumes fields exist.

Code path:
  --apply: responses.create(model=DEFAULT_MODEL, input=prompt,
  response_format={"type": "json_schema", "json_schema": {"name":
  "TicketRouting", "strict": true, "schema": SCHEMA}}) → parse output_text
  as JSON → print.

What to watch. `{"category": "billing", "priority": "high",
"needs_escalation": true}` — every field from schema present with correct
type. Never truncated or missing fields.

Prerequisites / env vars:
  AZURE_OPENAI_ENDPOINT  — Azure OpenAI resource URL
  DEFAULT_MODEL          — deployment supporting json_schema (o1, gpt-4o+)
  --apply                — send billable request
"""
import argparse
import json

from _shared.config import settings
from _shared.openai_client import openai_client

_SCHEMA = {
    "type": "object",
    "properties": {
        "category": {"type": "string", "enum": ["billing", "technical", "account", "other"]},
        "priority": {"type": "string", "enum": ["low", "medium", "high"]},
        "needs_escalation": {"type": "boolean"},
        "summary": {"type": "string"},
    },
    "required": ["category", "priority", "needs_escalation", "summary"],
    "additionalProperties": False,
}

_PROMPT = (
    "Classify this support ticket: 'My last three invoices were double-charged and "
    "billing support hasn't replied in 48 hours.'"
)


def preflight() -> None:
    print("JSON schema mode preflight (no cloud calls).")
    print(f"- Schema fields: {list(_SCHEMA['properties'].keys())}")
    print("- Requires DEFAULT_MODEL that supports json_schema (o1, gpt-4o+).")


def apply() -> None:
    response = openai_client().responses.create(
        model=settings().require("DEFAULT_MODEL"),
        input=_PROMPT,
        response_format={
            "type": "json_schema",
            "json_schema": {"name": "TicketRouting", "strict": True, "schema": _SCHEMA},
        },
    )
    parsed = json.loads(response.output_text)
    print(f"Model returned: {json.dumps(parsed, indent=2)}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Demo json_schema strict mode.")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    if not args.apply:
        preflight()
        return
    apply()


if __name__ == "__main__":
    main()
