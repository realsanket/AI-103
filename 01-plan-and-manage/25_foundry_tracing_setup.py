# Run: uv run python 01-plan-and-manage/26_foundry_tracing_setup.py
"""Read-only Microsoft Foundry tracing preflight.

This lesson makes no Azure calls and changes no project, role, feature flag, or
retention setting. Connect Application Insights to a Foundry project only after
reviewing what trace content is collected and who can read it.

Server-side tracing is recommended first: connecting Application Insights makes
Foundry capture supported hosted-agent traces without application changes.
Manual/client-side tracing, as in lesson 18, adds spans for application code
around an agent call. It complements, but does not enable, server-side tracing.
"""
from _shared.config import settings


def preflight() -> dict[str, bool]:
    """Return local configuration checks without contacting Azure."""
    current = settings()
    return {
        "project_endpoint_configured": bool(current.project_endpoint),
        "application_insights_connection_string_configured": bool(
            current.app_insights_connection_string
        ),
    }


def main() -> None:
    checks = preflight()
    print("Foundry tracing preflight (read-only; no Azure calls or changes)")
    for name, configured in checks.items():
        print(f"- {name}: {'configured' if configured else 'missing'}")
    print("\nSetup after approval: connect Application Insights to Foundry project.")
    print("Server-side: Foundry captures supported hosted-agent traces without app code.")
    print("Manual/client-side: lesson 18 adds application spans; it does not enable server-side tracing.")
    print("Trace data lives in Application Insights; Log Analytics retention and billing apply.")
    print("Readers need project access plus telemetry read access (for example, Log Analytics Reader).")
    print("Protected tables also require Privileged Monitoring Data Reader.")
    print("Do not log prompts, outputs, credentials, tokens, or unredacted personal data.")
    print("Sensitive GenAI content can be routed to AppGenAIContent and protected by RBAC.")


if __name__ == "__main__":
    main()
