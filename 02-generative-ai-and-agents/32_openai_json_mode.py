# Run: uv run python 02-generative-ai-and-agents/32_openai_json_mode.py [--apply]
# Practice-question coverage: Q82.
"""Force strict JSON output via Responses API json_schema response format.

Structured output (json_schema) constrains model output to a validated
schema. Lesson 07 extracts fields with the same mechanism and lesson 38 wraps
it in Pydantic; this lesson shows the raw `text.format` JSON schema on the
Responses API. (`response_format` is the Chat Completions name for the same
idea; the Responses API rejects it.)

Default preflight explains schema. `--apply` sends ONE Responses call
demanding output matching a small support-ticket schema. Prints parsed
result. Failure to match schema is a service-side error, not silent —
enforcement is at the model output layer.

json_schema mode differs from JSON mode (older, `{"type": "json_object"}`):
json_schema enforces STRUCTURE + types; JSON mode only guarantees valid JSON
(any shape).
Use json_schema for downstream parsing that assumes fields exist.

Code path:
  --apply: responses.create(model=DEFAULT_MODEL, input=prompt,
  text={"format": {"type": "json_schema", "name": "TicketRouting",
  "strict": true, "schema": SCHEMA}}) → parse output_text as JSON → print.

What to watch. `{"category": "billing", "priority": "high",
"needs_escalation": true}` — every field from schema present with correct
type. Never truncated or missing fields.

Prerequisites / env vars:
  AZURE_OPENAI_ENDPOINT  — Azure OpenAI resource URL
  DEFAULT_MODEL          — deployment that supports structured outputs (GPT-4.1 and later)
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
    print("- Requires a DEFAULT_MODEL deployment that supports structured outputs (GPT-4.1 and later).")


def request_kwargs(model: str) -> dict:
    """Responses API request: the schema goes in `text.format`, not `response_format`."""
    return {
        "model": model,
        "input": _PROMPT,
        "text": {"format": {"type": "json_schema", "name": "TicketRouting", "strict": True, "schema": _SCHEMA}},
    }


def apply() -> None:
    response = openai_client().responses.create(**request_kwargs(settings().require("DEFAULT_MODEL")))
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
