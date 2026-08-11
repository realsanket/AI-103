"""OpenTelemetry helpers for Foundry lessons.

Two entry points:

  setup_tracing(service_name)
    Legacy helper used by older lessons. Reads APPLICATIONINSIGHTS_CONNECTION_STRING
    from env and configures Azure Monitor or console exporter.

  resolve_connection_string(client) -> (str | None, str)
    Tries to get the App Insights connection string from the project telemetry API
    first, then falls back to the APPLICATIONINSIGHTS_CONNECTION_STRING env var.
    Returns (connection_string_or_None, source_description).

  setup_tracing_from_connection_string(conn, service_name) -> (Tracer, exporter_name)
    Configures Azure Monitor exporter when conn is present, console exporter otherwise.
    Returns a tracer and a human-readable exporter description for logging.
"""
from opentelemetry import trace
from .config import settings


def resolve_connection_string(client) -> tuple[str | None, str]:
    """Return (connection_string, source) for the configured App Insights resource.

    Priority:
      1. APPLICATIONINSIGHTS_CONNECTION_STRING env var (explicit override)
      2. Project telemetry API (client.telemetry.get_application_insights_connection_string)
      3. None — no App Insights configured; caller should fall back to console export
    """
    env_cs = settings().app_insights_connection_string
    if env_cs:
        return env_cs, "APPLICATIONINSIGHTS_CONNECTION_STRING env var"

    try:
        cs = client.telemetry.get_application_insights_connection_string()
        return cs, "project telemetry API"
    except Exception:
        return None, "not found (no App Insights connected to project)"


def setup_tracing_from_connection_string(
    connection_string: str | None,
    service_name: str,
) -> tuple[trace.Tracer, str]:
    """Configure exporter and return (tracer, exporter_description).

    Uses Azure Monitor when connection_string is present; console otherwise.
    Console export is useful for local development — no credentials needed.
    """
    if connection_string:
        from azure.monitor.opentelemetry import configure_azure_monitor

        configure_azure_monitor(
            connection_string=connection_string,
            resource_attributes={"service.name": service_name},
        )
        exporter_name = "Azure Monitor Application Insights"
    else:
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

        provider = TracerProvider()
        provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
        trace.set_tracer_provider(provider)
        exporter_name = "console (no App Insights configured)"

    return trace.get_tracer(service_name), exporter_name


def setup_tracing(service_name: str) -> trace.Tracer:
    """Legacy helper — reads connection string from env only.

    Prefer setup_tracing_from_connection_string() for new lessons so you can
    also pass a connection string fetched from the project telemetry API.
    """
    conn = settings().app_insights_connection_string
    tracer, _ = setup_tracing_from_connection_string(conn, service_name)
    return tracer
