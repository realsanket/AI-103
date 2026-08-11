# Run: uv run python 02-generative-ai-and-agents/24_production_observability_preflight.py
# Run: uv run python 02-generative-ai-and-agents/24_production_observability_preflight.py --check-connection
"""Production observability guide and configuration preflight for Domain 2.

This lesson explains the three observability layers in a Foundry agentic solution
and checks your local configuration. It makes no Azure calls unless you pass
--check-connection.

Three observability layers:

  1. Server-side tracing (automatic for Foundry-hosted agents)
     Connect Application Insights to your Foundry project in the portal.
     Prompt agents, hosted agents, and workflows emit spans automatically.
     No code changes needed. Traces appear in Foundry portal → Traces tab.

  2. Framework tracing (automatic for Agent Framework and Semantic Kernel)
     When tracing is connected, Agent Framework and Semantic Kernel emit
     spans automatically — no extra packages required (see lesson 17).
     LangChain and LangGraph need explicit instrumentation (lesson 23).

  3. Client-side tracing (code instrumentation for custom spans)
     Use AIProjectInstrumentor() for Foundry SDK agents.
     Use microsoft-opentelemetry package for LangChain/LangGraph (lesson 23).
     Add manual spans for business logic surrounding model calls.

  4. Cloud evaluation (deliberate — lesson 22)
     Uploads reviewed JSONL, creates persisted evaluation run.
     Not automatic. Requires --apply. Review dataset before uploading.

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
     (or: Observability → Traces → Connect resource)
  2. Connect an existing Application Insights resource or create a new one
  3. Run any prompt agent, hosted agent, or Agent Framework agent
  4. Traces appear in Foundry portal → Observability → Traces within 2-5 min
  5. Assign Log Analytics Reader to anyone who views traces in portal
     (If Log Analytics tables are protected, also assign Privileged Monitoring Data Reader)
  6. (Optional, preview) Register protectGenAISensitiveData feature flag to route
     sensitive attributes to AppGenAIContent protected table before Sept 30, 2026:
       az feature register --namespace Microsoft.Insights --name protectGenAISensitiveData

Sensitive attributes protected by AppGenAIContent:
  gen_ai.input.messages         — prompts and inputs sent to the model
  gen_ai.output.messages        — model responses
  gen_ai.system_instructions    — system prompts
  gen_ai.tool.definitions       — tool schemas
  gen_ai.tool.call.arguments    — tool call inputs
  gen_ai.tool.call.result       — tool call outputs
  gen_ai.evaluation.explanation — evaluation reasoning

After Sept 30, 2026, Foundry routes these to AppGenAIContent automatically.
Register the flag now to protect sensitive content immediately.
"""

_FRAMEWORK_TRACING = """\
Framework tracing behavior (lesson 17 vs lesson 23):

  Microsoft Agent Framework (lesson 17):
    - Traces automatically when App Insights is connected to Foundry project
    - No extra packages or code required
    - Spans appear in Foundry portal automatically

  LangChain / LangGraph (lessons 19-20, tracing in lesson 23):
    - Require explicit instrumentation with AzureAIOpenTelemetryTracer
    - Install: pip install langchain-azure-ai
    - Lesson 23 shows the pattern with content recording disabled (safe default)
    - Enable content recording only in dev after privacy/compliance approval:
        OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=true
"""

_CLIENT_SIDE_STEPS = """\
Client-side tracing pattern for Foundry SDK agents:
  Required env vars:
    PROJECT_ENDPOINT    — Foundry project URL (not AZURE_OPENAI_ENDPOINT)
    DEFAULT_MODEL       — deployment name (not model family)
  Optional env vars:
    APPLICATIONINSIGHTS_CONNECTION_STRING — override; else fetched from project API

  Code pattern (set env var FIRST, then instrument):
    import os
    os.environ.setdefault("AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING", "true")
    from azure.ai.projects.telemetry import AIProjectInstrumentor
    AIProjectInstrumentor().instrument()   # must run before any openai calls

  What AIProjectInstrumentor instruments:
    - openai.responses.create and conversations API calls
    - Creates 'chat <model>' child spans automatically
    - Records latency, token counts, and model name per call
    - Does NOT capture prompt/output text unless content recording enabled:
        OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=true  (dev only)

  Adding custom spans on top:
    from opentelemetry import trace
    tracer = trace.get_tracer("my-app")
    with tracer.start_as_current_span("business-operation") as span:
        span.set_attribute("app.operation", "refund-lookup")
        response = oc.responses.create(model=model, input=prompt)
"""

_EVALUATION_LIFECYCLE = """\
Evaluation lifecycle (lessons 21-22):

  Lesson 21 — local SDK evaluation:
    - Calls evaluator classes in process (no cloud state created)
    - Uses AZURE_OPENAI_ENDPOINT for evaluator model calls
    - One synthetic trace proves evaluator input contract only
    - One case is not representative evidence

  Lesson 22 — cloud evaluation (--apply):
    - Uploads reviewed JSONL dataset (30-day expiry)
    - Creates persisted Foundry evaluation definition and run
    - Uses AZURE_AI_PROJECT_ENDPOINT (can differ from PROJECT_ENDPOINT)
    - Stores inputs, outputs, and scores under project access controls
    - Dataset uploads, evaluator calls, model tokens, and results incur cost

  For credible evidence:
    - Version your dataset alongside model/agent/tool versions
    - Include edge, adversarial, and zero-evidence cases
    - Inspect failure distributions, not only average score
    - Gate releases on thresholds with human review
"""


def preflight() -> dict[str, bool]:
    """Check env vars for observability and evaluation. No Azure calls."""
    import os
    current = settings()
    return {
        "PROJECT_ENDPOINT": bool(current.project_endpoint),
        "AZURE_OPENAI_ENDPOINT": bool(current.azure_openai_endpoint),
        "DEFAULT_MODEL": bool(current.default_model),
        "APPLICATIONINSIGHTS_CONNECTION_STRING": bool(current.app_insights_connection_string),
        "SEARCH_ENDPOINT (lesson 27)": bool(current.search_endpoint),
        "AZURE_AI_PROJECT_ENDPOINT (lesson 22 cloud eval)": bool(os.environ.get("AZURE_AI_PROJECT_ENDPOINT")),
    }


def check_connection() -> None:
    """Try to fetch App Insights connection string from the project telemetry API.

    Requires PROJECT_ENDPOINT and authenticated credential (az login locally).
    """
    from _shared.foundry_client import project_client
    from _shared.tracing import resolve_connection_string

    print("Checking App Insights connection via project telemetry API...")
    try:
        client = project_client()
        conn, source = resolve_connection_string(client)
        if conn:
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
    print("Domain 2 production observability preflight")
    print("=" * 60)

    checks = preflight()
    print("\nEnvironment variable status:")
    for name, configured in checks.items():
        status = "configured" if configured else "missing"
        print(f"  {'✓' if configured else '✗'} {name}: {status}")

    print(f"\n{_SERVER_SIDE_STEPS}")
    print(_FRAMEWORK_TRACING)
    print(_CLIENT_SIDE_STEPS)
    print(_EVALUATION_LIFECYCLE)

    if check_conn:
        check_connection()
    else:
        print("Tip: pass --check-connection to verify App Insights is connected to your project.")


if __name__ == "__main__":
    main()
