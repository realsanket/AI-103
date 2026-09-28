# Run: uv run python 02-generative-ai-and-agents/42_register_external_agent.py [--apply] [--list] [--delete]

"""Lesson 42 - register a non-Foundry agent for Foundry tracing / evaluation.

Run from repository root:
    uv run python 02-generative-ai-and-agents/42_register_external_agent.py
    uv run python 02-generative-ai-and-agents/42_register_external_agent.py --apply
    uv run python 02-generative-ai-and-agents/42_register_external_agent.py --list
    uv run python 02-generative-ai-and-agents/42_register_external_agent.py --delete --apply

What. An "external agent" is a Foundry record for an agent whose runtime
lives outside Foundry (any cloud, on-prem, third-party host). Foundry
stores ONLY the registration metadata - it does not host, proxy, or invoke
the runtime. The external agent emits OpenTelemetry spans with attribute
`gen_ai.agent.id` to the Application Insights resource connected to the
Foundry project; Foundry matches spans to the registration by that ID and
displays them in the agent trace view.

Why. This is the Foundry-tracing surface for agents you can't or don't
want to migrate. It is DIFFERENT from Control Plane custom agents, which
route traffic through an AI Gateway. External agents keep their existing
endpoint - no gateway, no proxy, no invocation - and share only telemetry.
Preview surface: creation and update requests require the header
`Foundry-Features: ExternalAgents=V1Preview`, and the SDK opts in through
`AIProjectClient(..., allow_preview=True)`.

Code path.
  1. Preflight prints: the OTel wiring snippet (env vars +
     `use_microsoft_opentelemetry` + `gen_ai.agent.id`), and the
     `ExternalAgentDefinition(otel_agent_id=...)` payload.
  2. `--apply` constructs `AIProjectClient(allow_preview=True)`,
     then calls `project.agents.create_version(agent_name=..., description=...,
     definition=ExternalAgentDefinition(otel_agent_id=...))`. Prints the
     registered name and resolved otel_agent_id.
  3. `--list` prints external registrations via
     `project.agents.list(kind="external")`.
  4. `--delete --apply` calls `project.agents.delete(name=..., force=True)`
     to remove the registration. Does NOT touch the running agent.

What to watch. Preflight: OTel snippet must be run once at agent startup,
before any framework imports you want instrumented; each span must carry
`gen_ai.agent.id == <otel_agent_id>`. `--apply`: printed
"Registered external agent: <name>" and "Resolved otel_agent_id: <id>".
Traces typically appear in the portal 2-5 minutes after the external
agent starts sending spans. If missing: check Application Insights is
connected to THIS project, that the connection string matches, and that
the running agent stamps the exact `otel_agent_id` on every span.

Env vars.
  PROJECT_ENDPOINT              - Foundry project HTTPS URL.
  EXTERNAL_AGENT_NAME           - Foundry-side name (default: travel-planner-agent).
  EXTERNAL_AGENT_DESCRIPTION    - Registration description.
  EXTERNAL_AGENT_OTEL_ID        - Optional; defaults to agent name.
  EXTERNAL_AGENT_ENDPOINT       - Informational; where the agent actually runs.
                                  Foundry does not call it - stored as context only.
  APPLICATIONINSIGHTS_CONNECTION_STRING
                                - Must match the App Insights resource connected
                                  to the project. Used by the running agent, not
                                  by this lesson. Printed for reference.

Not supported for external agents (preview limits): human evaluation,
trace-to-dataset conversion, AI red teaming.

References:
  how-to/register-external-agent.md
"""
from __future__ import annotations

import argparse
import json
import os
from urllib.parse import urlparse

from _shared.config import load_env


OTEL_SNIPPET = '''\
# Run this ONCE at external-agent startup, before any framework imports
# you want instrumented. Foundry matches spans to the registration by the
# `gen_ai.agent.id` attribute stamped on every span.
import os

os.environ.setdefault("AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING", "true")
os.environ.setdefault("OTEL_SEMCONV_STABILITY_OPT_IN", "gen_ai_latest_experimental")
os.environ.setdefault("OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT", "SPAN_AND_EVENT")

from microsoft.opentelemetry import use_microsoft_opentelemetry

AGENT_NAME = os.environ.get("AGENT_NAME", "{name}")
OTEL_AGENT_ID = os.environ.get("OTEL_AGENT_ID", "{otel_id}")

use_microsoft_opentelemetry(
    enable_azure_monitor=True,
    azure_monitor_connection_string=os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"],
    sampling_ratio=1.0,
    instrumentation_options={{
        "fastapi": {{"enabled": False}},
        "langchain": {{
            "enabled": True,
            "agent_id": OTEL_AGENT_ID,
            "agent_name": AGENT_NAME,
        }},
    }},
)

# If your framework does not set the attribute automatically:
from opentelemetry import trace
tracer = trace.get_tracer(__name__)
with tracer.start_as_current_span("agent-run") as span:
    span.set_attribute("gen_ai.agent.id", OTEL_AGENT_ID)
    # ... your agent logic ...
'''


def project_endpoint(value: str) -> str:
    parsed = urlparse(value)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or not parsed.hostname.endswith(".services.ai.azure.com")
        or "/api/projects/" not in parsed.path
    ):
        raise ValueError("PROJECT_ENDPOINT must be a Foundry project HTTPS URL.")
    return value.rstrip("/")


def registration_payload(*, name: str, description: str, otel_agent_id: str) -> dict:
    """The logical shape of the ExternalAgentDefinition passed to create_version."""
    return {
        "agent_name": name,
        "description": description,
        "definition": {
            "kind": "external",
            "otel_agent_id": otel_agent_id,
        },
        # SDK auto-adds this via allow_preview=True; shown here for parity with
        # the REST/C#/TypeScript paths documented in register-external-agent.md.
        "foundry_features": "ExternalAgents=V1Preview",
    }


def apply_create(endpoint: str, name: str, description: str, otel_agent_id: str) -> None:
    from azure.identity import DefaultAzureCredential
    from azure.ai.projects import AIProjectClient
    from azure.ai.projects.models import ExternalAgentDefinition

    project = AIProjectClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(),
        allow_preview=True,
    )
    agent = project.agents.create_version(
        agent_name=name,
        description=description,
        definition=ExternalAgentDefinition(otel_agent_id=otel_agent_id),
    )
    print(f"Registered external agent: {agent.name}")
    try:
        resolved = agent.versions.latest.definition.otel_agent_id
    except AttributeError:
        resolved = otel_agent_id
    print(f"Resolved otel_agent_id: {resolved}")


def apply_list(endpoint: str) -> None:
    from azure.identity import DefaultAzureCredential
    from azure.ai.projects import AIProjectClient

    project = AIProjectClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(),
        allow_preview=True,
    )
    found = False
    for agent in project.agents.list(kind="external"):
        found = True
        print(f"- {agent.name}")
    if not found:
        print("(no external agents registered)")


def apply_delete(endpoint: str, name: str) -> None:
    from azure.identity import DefaultAzureCredential
    from azure.ai.projects import AIProjectClient

    project = AIProjectClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(),
        allow_preview=True,
    )
    # force=True removes all internal revisions atomically. Running agent is untouched.
    project.agents.delete(agent_name=name, force=True)
    print(f"Deleted external agent registration: {name}")
    print("The external runtime is NOT affected. Spans remain in Application Insights.")


def main(argv: list[str] | None = None) -> None:
    load_env()
    parser = argparse.ArgumentParser(
        description="Preflight or register an external agent for Foundry tracing / evaluation.",
    )
    parser.add_argument("--apply", action="store_true", help="Call the SDK (create by default).")
    parser.add_argument("--list", action="store_true", help="List external agent registrations.")
    parser.add_argument("--delete", action="store_true", help="Delete the registration (needs --apply).")
    parser.add_argument("--name", default=os.getenv("EXTERNAL_AGENT_NAME", "travel-planner-agent"))
    parser.add_argument(
        "--description",
        default=os.getenv("EXTERNAL_AGENT_DESCRIPTION", "Travel planning agent hosted externally."),
    )
    parser.add_argument(
        "--otel-agent-id",
        default=os.getenv("EXTERNAL_AGENT_OTEL_ID"),
        help="Defaults to --name if omitted (matches SDK default).",
    )
    args = parser.parse_args(argv)

    otel_id = args.otel_agent_id or args.name
    endpoint = os.getenv("PROJECT_ENDPOINT")
    external_endpoint = os.getenv("EXTERNAL_AGENT_ENDPOINT")
    app_insights = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")

    print("External agent registration - preview surface")
    print("  Foundry-Features header: ExternalAgents=V1Preview (SDK: allow_preview=True)")
    print(f"  Foundry agent name:      {args.name}")
    print(f"  otel_agent_id:           {otel_id}")
    print(f"  Description:             {args.description}")
    print(f"  External runtime URL:    {external_endpoint or '(unset - informational only)'}")
    print(f"  App Insights connected:  {'yes' if app_insights else 'no (running agent needs it)'}")
    print()
    print("SDK payload for create_version (ExternalAgentDefinition):")
    print(json.dumps(registration_payload(
        name=args.name, description=args.description, otel_agent_id=otel_id,
    ), indent=2))
    print()
    print("Startup snippet the external agent runs (paste into its own codebase):")
    print(OTEL_SNIPPET.format(name=args.name, otel_id=otel_id))

    if not (args.apply or args.list):
        print("Preflight only. Use --apply to create/delete, --list to enumerate.")
        return

    if not endpoint:
        parser.error("--apply/--list require PROJECT_ENDPOINT.")
    try:
        endpoint = project_endpoint(endpoint)
    except ValueError as exc:
        parser.error(str(exc))

    if args.list:
        apply_list(endpoint)
        return
    if args.delete:
        if not args.apply:
            parser.error("--delete requires --apply.")
        apply_delete(endpoint, args.name)
        return
    apply_create(endpoint, args.name, args.description, otel_id)
    print("Note: traces typically appear 2-5 minutes after the external agent emits spans.")


if __name__ == "__main__":
    main()
