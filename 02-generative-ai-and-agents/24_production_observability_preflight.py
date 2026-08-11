# Run: uv run python 02-generative-ai-and-agents/30_production_observability_preflight.py
"""Read-only production tracing and evaluation data-lifecycle preflight.

No Azure request is made. This checks local configuration only; it does not
connect telemetry, change retention, grant RBAC, create an evaluation, or
upload data. L21 exports metadata-only LangChain spans. L29 is the separate,
explicit ``--apply`` path for durable dataset/evaluation/run records.
"""
from _shared.config import settings


def preflight() -> dict[str, bool]:
    """Report local prerequisites without exposing connection-string values."""
    current = settings()
    return {
        "application_insights_configured": bool(current.app_insights_connection_string),
        "foundry_project_configured": bool(current.project_endpoint),
        "azure_openai_configured": bool(current.azure_openai_endpoint),
        "production_search_configured": bool(current.search_endpoint),
    }


def main() -> None:
    checks = preflight()
    print("Production observability preflight (read-only; no Azure requests or changes)")
    for name, configured in checks.items():
        print(f"- {name}: {'configured' if configured else 'missing'}")
    print("\nLifecycle: redact before export; L21 records metadata, not prompts, outputs, or tool arguments.")
    print("Application Insights / Log Analytics ingestion, retention, export, and queries incur cost.")
    print("L29 uploads evaluation data for 30 days; evaluation definitions and runs remain until deleted.")
    print("RBAC: least-privilege project/model access; Monitoring Reader for telemetry; protected tables need Privileged Monitoring Data Reader.")
    print("Network: verify private DNS and runner egress to Foundry, Azure OpenAI, Azure Monitor, and Search private endpoints.")
    print("Region: verify selected model, evaluator, and telemetry availability before creating a run.")
    print("Local FAISS is ephemeral demo storage; production Azure AI Search supplies managed index, RBAC, network, and retention controls.")


if __name__ == "__main__":
    main()
