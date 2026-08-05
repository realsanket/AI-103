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

from _shared.config import settings
from _shared.openai_client import openai_client
from _shared.content_safety_client import content_safety_client
from _shared.tracing import setup_tracing


def _check_safety(text: str) -> dict:
    """Return a flat dict of severity scores for span attributes."""
    from azure.ai.contentsafety.models import AnalyzeTextOptions, TextCategory

    client = content_safety_client()
    result = client.analyze_text(AnalyzeTextOptions(text=text[:1000]))
    return {
        cat.category.value.lower(): cat.severity
        for cat in result.categories_analysis
    }


def run_traced_call(prompt: str) -> str:
    tracer = setup_tracing("northwind-agent-tracing")
    oc = openai_client()
    model = settings().default_model

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
            return output

        try:
            safety = _check_safety(output)
            for category, severity in safety.items():
                span.set_attribute(f"safety.{category}", severity)
        except (HttpResponseError, ServiceRequestError) as error:
            span.record_exception(error)
            span.set_attribute("content_safety.error.type", type(error).__name__)

        return output


def main() -> None:
    prompt = (
        "Summarize Northwind's refund policy in two sentences. "
        "Be concise and accurate."
    )
    print("Running traced call...")
    result = run_traced_call(prompt)
    print("\nOutput:", result)
    print("\nSee Application Insights > Transaction Search for the span.")
    print("(If APPLICATIONINSIGHTS_CONNECTION_STRING is unset, spans go to stdout.)")


if __name__ == "__main__":
    main()
