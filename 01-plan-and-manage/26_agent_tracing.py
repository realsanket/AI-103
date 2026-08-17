# Run: uv run python 01-plan-and-manage/26_agent_tracing.py
"""Client-side tracing with the Microsoft Foundry SDK.

Two flows teach tracing from different angles:

  Flow A — SDK auto-instrumentation (recommended Foundry path)
    AIProjectInstrumentor instruments openai.responses.create automatically.
    Spans for model calls, latency, and token counts appear without extra code.
    App Insights connection string is fetched from the project telemetry API.

  Flow B — Custom parent span (additive to auto-instrumentation)
    A manual span adds business-level context around the auto-instrumented call.
    Records a policy-lookup operation name and safety severity as custom attributes.
    Shows how to layer custom observability on top of SDK-provided spans.

This is client-side tracing only. Server-side Foundry tracing (automatic for
hosted/prompt agents) starts only after connecting Application Insights to the
project in the portal. Lesson 25 explains that setup step.

Prerequisites
  PROJECT_ENDPOINT  — required (uses DefaultAzureCredential / az login locally)
  DEFAULT_MODEL     — required (deployment name, not model family)
  CONTENT_SAFETY_ENDPOINT         — optional (safety attributes on span)
  APPLICATIONINSIGHTS_CONNECTION_STRING — optional (env override; else fetched from project)
"""
import os
from azure.core.exceptions import HttpResponseError, ServiceRequestError, ResourceNotFoundError

from _shared.config import settings, preview_text
from _shared.foundry_client import project_client
from _shared.content_safety_client import content_safety_client
from _shared.tracing import resolve_connection_string, setup_tracing_from_connection_string


_POLICY_CONTEXT = (
    "Northwind refund policy:\n"
    "- Pro plan subscribers can request a refund within 30 days of the charge date.\n"
    "- The window is measured from the invoice charge date, not the usage date.\n"
    "- Refunds after 30 days are reviewed case-by-case by the billing team.\n"
    "- Approved refunds return to the original payment method within 5-10 business days."
)


def _check_safety(text: str) -> dict:
    """Return flat dict of severity scores for span attributes."""
    from azure.ai.contentsafety.models import AnalyzeTextOptions

    client = content_safety_client()
    result = client.analyze_text(AnalyzeTextOptions(text=text[:1000]))

    def _name(category) -> str:
        raw = getattr(category, "value", category)
        return str(raw).lower()

    return {_name(cat.category): cat.severity for cat in result.categories_analysis}


def run_traced_call(client, tracer) -> tuple[str, str, int, int, dict]:
    """
    Flow A: AIProjectInstrumentor auto-creates a 'chat <model>' child span.
    Flow B: Manual parent span adds business-level context around Flow A.
    """
    model = settings().default_model
    safety: dict = {}

    # Flow B: manual parent span for business-level context
    with tracer.start_as_current_span("northwind-support-response") as span:
        span.set_attribute("northwind.operation", "refund-policy-query")
        span.set_attribute("gen_ai.request.model", model)

        # Flow A: AIProjectInstrumentor instruments this call automatically
        # creates a child 'chat <model>' span with latency and token attributes
        with client.get_openai_client() as oc:
            prompt = (
                f"{_POLICY_CONTEXT}\n\n"
                "Summarize Northwind's refund policy in two sentences. Be concise."
            )
            response = oc.responses.create(model=model, input=prompt)

        usage = getattr(response, "usage", None) or {}
        input_tokens = getattr(usage, "input_tokens", 0)
        output_tokens = getattr(usage, "output_tokens", 0)
        # Record tokens on parent span for business-level rollup
        span.set_attribute("gen_ai.usage.input_tokens", input_tokens)
        span.set_attribute("gen_ai.usage.output_tokens", output_tokens)

        output = response.output_text

        if not settings().content_safety_endpoint:
            span.set_attribute("content_safety.skipped", True)
        else:
            try:
                safety = _check_safety(output)
                for category, severity in safety.items():
                    span.set_attribute(f"safety.{category}", severity)
            except (HttpResponseError, ServiceRequestError) as error:
                span.record_exception(error)
                span.set_attribute("content_safety.error.type", type(error).__name__)

        return model, output, input_tokens, output_tokens, safety


def main() -> None:
    current = settings()
    if not current.project_endpoint:
        raise SystemExit("Missing PROJECT_ENDPOINT in .env")
    if not current.default_model:
        raise SystemExit("Missing DEFAULT_MODEL in .env")

    # Step 1: enable GenAI tracing BEFORE calling AIProjectInstrumentor.instrument()
    # Without this env var, instrumentation is a no-op.
    os.environ.setdefault("AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING", "true")

    # Step 2: SDK auto-instrumentation — instruments openai.responses.create calls
    from azure.ai.projects.telemetry import AIProjectInstrumentor
    AIProjectInstrumentor().instrument()

    # Step 3: get App Insights connection string from project API (or env fallback)
    client = project_client()
    conn_string, source = resolve_connection_string(client)

    # Step 4: set up exporter — Azure Monitor if connection string present, else console
    tracer, exporter_name = setup_tracing_from_connection_string(conn_string, "northwind-agent-tracing")

    print("Client-side tracing: Flow A (SDK auto) + Flow B (custom parent span)")
    print(f"  PROJECT_ENDPOINT:       {current.project_endpoint}")
    print(f"  DEFAULT_MODEL:          {current.default_model}")
    print(f"  App Insights source:    {source}")
    print(f"  Exporter:               {exporter_name}")
    print(f"  CONTENT_SAFETY:         {'set' if current.content_safety_endpoint else 'unset (safety attributes skipped)'}")
    print()

    print("Running traced call...")
    model, result, input_tokens, output_tokens, safety = run_traced_call(client, tracer)

    print(f"Model:          {model}")
    print(f"Input tokens:   {input_tokens}")
    print(f"Output tokens:  {output_tokens}")
    print(f"\nOutput:\n{result}")

    print("\nSpan attributes recorded:")
    print("  Parent span (Flow B — business context):")
    print("    northwind.operation = refund-policy-query")
    print(f"    gen_ai.usage.input_tokens = {input_tokens}")
    print(f"    gen_ai.usage.output_tokens = {output_tokens}")
    if safety:
        for category, severity in safety.items():
            print(f"    safety.{category} = {severity}")
    else:
        print("    (no safety attributes — CONTENT_SAFETY_ENDPOINT unset)")
    print("  Child span (Flow A — SDK auto-instrumentation):")
    print("    gen_ai.* attributes added automatically by AIProjectInstrumentor")
    print("    Includes model name, latency, and token counts")

    print(f"\nExporter: {exporter_name}")
    if "console" in exporter_name.lower():
        print("  Spans printed above as JSON. Set APPLICATIONINSIGHTS_CONNECTION_STRING")
        print("  to export to Azure Monitor. Traces appear in 2-5 min.")
    else:
        print("  Check Azure Monitor → Transaction Search for 'northwind-support-response'.")
        print("  Also visible in Foundry portal → your project → Traces tab.")


if __name__ == "__main__":
    main()
