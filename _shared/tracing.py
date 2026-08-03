"""OpenTelemetry setup — exports traces to Azure Monitor when APPINSIGHTS is set.

Usage:
    from _shared.tracing import setup_tracing
    setup_tracing("my-agent-lesson")
"""
from opentelemetry import trace
from .config import settings


def setup_tracing(service_name: str) -> trace.Tracer:
    conn = settings().app_insights_connection_string
    if conn:
        # Auto-instrument if Azure Monitor is configured
        from azure.monitor.opentelemetry import configure_azure_monitor

        configure_azure_monitor(connection_string=conn, resource_attributes={"service.name": service_name})
    else:
        # Console fallback for local dev — no cred needed
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

        provider = TracerProvider()
        provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
        trace.set_tracer_provider(provider)
    return trace.get_tracer(service_name)
