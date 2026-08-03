"""OpenTelemetry tracing on an agent call.

Wraps a Responses API call in a manual span so you can see the trace in
Application Insights (when APPLICATIONINSIGHTS_CONNECTION_STRING is set) or
in the console otherwise. Combine with the auto-instrumentation the Foundry
SDKs enable when Azure Monitor is configured.
"""
from _shared.openai_client import openai_client
from _shared.config import settings
from _shared.tracing import setup_tracing


def main() -> None:
    tracer = setup_tracing("northwind-tracing-demo")
    client = openai_client()

    with tracer.start_as_current_span("demo.responses_create") as span:
        span.set_attribute("model", settings().default_model)
        r = client.responses.create(
            model=settings().default_model,
            input="Give me one sentence about OpenTelemetry.",
        )
        span.set_attribute("output.tokens", getattr(r.usage, "output_tokens", 0))
        print(r.output_text)


if __name__ == "__main__":
    main()
