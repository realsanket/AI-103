# Run: uv run python 01-plan-and-manage/12_agent_tracing.py
"""OpenTelemetry observability for agent calls: tracing, token analytics,
safety signals, and latency breakdowns.

The exam covers all four under "Set up observability":
  - Tracing   → manual spans sent to Application Insights (or stdout)
  - Tokens    → input_tokens, output_tokens, total tracked per call
  - Safety    → content-filter result attached to span attributes
  - Latency   → wall-clock duration captured via span timing

When APPLICATIONINSIGHTS_CONNECTION_STRING is set the spans reach Azure Monitor
automatically. Otherwise they print to the console via the stdlib exporter.
"""
import time

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

    with tracer.start_as_current_span("agent.responses_create") as span:
        span.set_attribute("model", model)
        span.set_attribute("input.preview", prompt[:200])

        t0 = time.perf_counter()
        response = oc.responses.create(model=model, input=prompt)
        latency_ms = (time.perf_counter() - t0) * 1000

        # Token analytics
        usage = response.usage or {}
        input_tokens = getattr(usage, "input_tokens", 0)
        output_tokens = getattr(usage, "output_tokens", 0)
        span.set_attribute("tokens.input", input_tokens)
        span.set_attribute("tokens.output", output_tokens)
        span.set_attribute("tokens.total", input_tokens + output_tokens)

        # Latency
        span.set_attribute("latency_ms", round(latency_ms, 1))

        output = response.output_text
        # Safety signals — check the model output before returning
        try:
            safety = _check_safety(output)
            for category, severity in safety.items():
                span.set_attribute(f"safety.{category}", severity)
        except Exception:
            span.set_attribute("safety.error", "content_safety_unavailable")

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
