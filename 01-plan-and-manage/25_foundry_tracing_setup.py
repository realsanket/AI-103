# Run: uv run python 01-plan-and-manage/25_foundry_tracing_setup.py
# Run: uv run python 01-plan-and-manage/25_foundry_tracing_setup.py --check-connection
"""Foundry tracing setup guide and preflight.

This lesson explains the two tracing modes and checks your configuration.
It makes no Azure calls unless you pass --check-connection.

Modes:

  Server-side tracing (zero code, automatic)
    Connect Application Insights to the Foundry project in the portal.
    Foundry automatically captures hosted/prompt-agent runs — inputs, outputs,
    tool calls, latency, token counts — without changing application code.
    Portal: project → Settings → Tracing → Connect resource.

  Client-side tracing (code instrumentation, lesson 18)
    Set AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING=true.
    Call AIProjectInstrumentor().instrument() before making model calls.
    Add manual spans for custom logic your app owns.
    Complements server-side traces; does not enable or replace them.

Flags:
  (none)             — local preflight only; no Azure calls
  --check-connection — try to fetch App Insights connection string from project API
                       requires PROJECT_ENDPOINT and az login
"""
import sys
from _shared.config import settings


_SERVER_SIDE_STEPS = """\
Portal setup for server-side tracing (zero code required):
  1. Open Foundry portal → your project → Settings → Tracing
  2. Connect an existing Application Insights resource or create a new one
  3. Assign Log Analytics Reader on the resource to anyone who views traces
     (If Log Analytics tables are protected, also assign Privileged Monitoring Data Reader)
  4. Run any hosted or prompt agent — traces appear in Traces tab within 2-5 min
  5. (Optional, preview) Register protectGenAISensitiveData feature flag and set
     AppGenAIContent table as Protected to restrict sensitive content access

Sensitive content in traces:
  gen_ai.input.messages     — prompts and inputs sent to the model
  gen_ai.output.messages    — model responses
  gen_ai.system_instructions — system prompts
  gen_ai.tool.call.arguments — tool call inputs
  gen_ai.tool.call.result    — tool call outputs
  These route to AppGenAIContent (protected table) after Sep 30, 2026.
  Register the flag now to protect them immediately:
    az feature register --namespace Microsoft.Insights --name protectGenAISensitiveData

Cost note:
  Application Insights billing follows Azure Monitor pricing.
  Trace data retention follows your Log Analytics workspace configuration.
  Tracing is off by default — no data collected until you connect the resource.
"""

_CLIENT_SIDE_STEPS = """\
Client-side tracing setup (lesson 26):
  Required env vars:
    PROJECT_ENDPOINT                      — Foundry project URL
    DEFAULT_MODEL                         — deployment name (not model family)
  Optional env vars:
    APPLICATIONINSIGHTS_CONNECTION_STRING — override; else fetched from project API
    CONTENT_SAFETY_ENDPOINT               — add safety severity to custom spans

  Code pattern:
    import os
    os.environ.setdefault("AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING", "true")
    from azure.ai.projects.telemetry import AIProjectInstrumentor
    AIProjectInstrumentor().instrument()   # must run before any openai calls

  What AIProjectInstrumentor does:
    - Instruments openai.responses.create and conversations API calls
    - Creates 'chat <model>' child spans automatically
    - Records latency, token counts, and model name per call
    - Does NOT capture prompt/output text unless content recording is enabled
      (OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=true — dev only)

  Adding custom spans on top:
    tracer = trace.get_tracer("my-app")
    with tracer.start_as_current_span("business-operation") as span:
        span.set_attribute("app.operation", "refund-lookup")
        # SDK auto-span nests inside this parent
        response = oc.responses.create(model=model, input=prompt)
"""


def preflight() -> dict[str, bool]:
    """Check env vars needed for both tracing modes. No Azure calls."""
    current = settings()
    return {
        "PROJECT_ENDPOINT": bool(current.project_endpoint),
        "DEFAULT_MODEL": bool(current.default_model),
        "APPLICATIONINSIGHTS_CONNECTION_STRING": bool(current.app_insights_connection_string),
        "CONTENT_SAFETY_ENDPOINT (optional)": bool(current.content_safety_endpoint),
    }


def check_connection() -> None:
    """Try to fetch App Insights connection string from the project telemetry API.

    Requires PROJECT_ENDPOINT and authenticated credential (az login locally).
    This demonstrates how lesson 18 gets the connection string automatically.
    """
    from _shared.foundry_client import project_client
    from _shared.tracing import resolve_connection_string

    print("Checking App Insights connection via project telemetry API...")
    try:
        client = project_client()
        conn, source = resolve_connection_string(client)
        if conn:
            # Show only the InstrumentationKey portion to avoid logging the full secret
            key_part = conn.split(";")[0] if ";" in conn else conn[:40] + "..."
            print(f"  Connection found ({source})")
            print(f"  Starts with: {key_part}")
            print("  Server-side tracing is enabled for this project.")
        else:
            print(f"  {source}")
            print("  To enable: connect Application Insights in Foundry portal → Settings → Tracing")
    except Exception as exc:
        print(f"  Error: {exc}")
        print("  Verify PROJECT_ENDPOINT is set and 'az login' has run.")


def main() -> None:
    check_conn = "--check-connection" in sys.argv

    print("=" * 60)
    print("Foundry tracing preflight")
    print("=" * 60)

    checks = preflight()
    print("\nEnvironment variable status:")
    for name, configured in checks.items():
        status = "configured" if configured else "missing"
        print(f"  {'✓' if configured else '✗'} {name}: {status}")

    print(f"\n{_SERVER_SIDE_STEPS}")
    print(_CLIENT_SIDE_STEPS)

    if check_conn:
        check_connection()
    else:
        print("Tip: pass --check-connection to verify App Insights is connected to your project.")


if __name__ == "__main__":
    main()
