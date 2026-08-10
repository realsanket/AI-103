# Run: uv run python 01-plan-and-manage/18_agent_tracing.py
"""Manual OpenTelemetry span around a model call.

This is application instrumentation, not complete Foundry tracing:
  - Tracing   → one manual span sent to Application Insights (or stdout)
  - Tokens    → input_tokens and output_tokens tracked per call
  - Safety    → content-filter result attached to span attributes
  - Latency   → span start and end times

Server-side tracing starts when Application Insights is connected to a Foundry
project and captures supported Foundry-hosted agent activity without app code.
This manual, client-side span supplements that view with this application's
model call; it does not connect a project or enable server-side tracing.

Prompts and outputs are deliberately not span attributes. They can contain
sensitive data. When APPLICATIONINSIGHTS_CONNECTION_STRING is set, this manual
span reaches Azure Monitor; otherwise it prints to the console.
"""
from azure.core.exceptions import HttpResponseError, ServiceRequestError

from _shared.config import settings, preview_text
from _shared.openai_client import openai_client
from _shared.content_safety_client import content_safety_client
from _shared.tracing import setup_tracing


_POLICY_CONTEXT = (
    "Northwind refund policy:\n"
    "- Pro plan subscribers can request a refund within 30 days of the charge date.\n"
    "- The window is measured from the invoice charge date, not the usage date.\n"
    "- Refunds after 30 days are reviewed case-by-case by the billing team.\n"
    "- Approved refunds return to the original payment method within 5-10 business days."
)


def _print_preflight() -> None:
    current = settings()
    print("Preflight checks:")
    print(f"  AZURE_OPENAI_ENDPOINT set: {bool(current.azure_openai_endpoint)}")
    print(f"  DEFAULT_MODEL set: {bool(current.default_model)} ({current.default_model or 'missing'})")
    print(f"  CONTENT_SAFETY_ENDPOINT set: {bool(current.content_safety_endpoint)}")
    print(
        "  APPLICATIONINSIGHTS_CONNECTION_STRING set: "
        f"{bool(current.app_insights_connection_string)}"
    )
    print("  Note: if Application Insights is unset, spans are printed locally instead.")


def _build_prompt() -> str:
    return (
        f"{_POLICY_CONTEXT}\n\n"
        "Summarize Northwind's refund policy in two sentences. "
        "Be concise and accurate."
    )


def _check_safety(text: str) -> dict:
    """Return a flat dict of severity scores for span attributes."""
    from azure.ai.contentsafety.models import AnalyzeTextOptions

    client = content_safety_client()
    result = client.analyze_text(AnalyzeTextOptions(text=text[:1000]))

    def _category_name(category) -> str:
        raw = getattr(category, "value", category)
        return str(raw).lower()

    return {
        _category_name(cat.category): cat.severity
        for cat in result.categories_analysis
    }


def run_traced_call(prompt: str) -> tuple[str, str, int, int, dict]:
    tracer = setup_tracing("northwind-agent-tracing")
    oc = openai_client()
    model = settings().default_model
    safety: dict = {}

    with tracer.start_as_current_span(f"chat {model}") as span:
        span.set_attribute("gen_ai.operation.name", "chat")
        span.set_attribute("gen_ai.system", "openai")
        span.set_attribute("gen_ai.request.model", model)

        response = oc.responses.create(model=model, input=prompt)

        usage = response.usage or {}
        input_tokens = getattr(usage, "input_tokens", 0)
        output_tokens = getattr(usage, "output_tokens", 0)
        span.set_attribute("gen_ai.response.model", model)
        span.set_attribute("gen_ai.usage.input_tokens", input_tokens)
        span.set_attribute("gen_ai.usage.output_tokens", output_tokens)

        output = response.output_text
        if not settings().content_safety_endpoint:
            span.set_attribute("content_safety.error.type", "ConfigurationMissing")
            return model, output, input_tokens, output_tokens, safety

        try:
            safety = _check_safety(output)
            for category, severity in safety.items():
                span.set_attribute(f"safety.{category}", severity)
        except (HttpResponseError, ServiceRequestError) as error:
            span.record_exception(error)
            span.set_attribute("content_safety.error.type", type(error).__name__)

        return model, output, input_tokens, output_tokens, safety


def main() -> None:
    prompt = _build_prompt()
    print("Manual tracing example: one model call wrapped in one OpenTelemetry span")
    _print_preflight()
    if not settings().azure_openai_endpoint:
        raise SystemExit("Missing AZURE_OPENAI_ENDPOINT in .env")
    if not settings().default_model:
        raise SystemExit("Missing DEFAULT_MODEL in .env")
    print("\nInput prompt:")
    print(f"  {preview_text(prompt, max_len=500)}")
    print("\nRunning traced call...")
    model, result, input_tokens, output_tokens, safety = run_traced_call(prompt)
    print(f"\nModel: {model}")
    print(f"Input tokens: {input_tokens}")
    print(f"Output tokens: {output_tokens}")
    print("\nModel output:")
    print(f"{result}")
    print("\nSafety summary attached to the span:")
    if safety:
        for category, severity in safety.items():
            print(f"  {category}: severity={severity}")
    else:
        print("  No safety scores attached (Content Safety endpoint unset or call failed).")
    print("\nWhat to look for in tracing:")
    print("  - one span named with the model deployment")
    print("  - token counts on span attributes")
    print("  - safety.* attributes for each analyzed category")
    print("(If APPLICATIONINSIGHTS_CONNECTION_STRING is unset, spans go to stdout.)")
    print("See Application Insights > Transaction Search for the span.")


if __name__ == "__main__":
    main()
