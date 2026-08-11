# Run: uv run python 04-text-and-speech/25_text_speech_governance_preflight.py
"""Local monitoring and governance preflight for text and speech workloads.

This lesson intentionally makes no Azure request or configuration change.
Enable Azure Monitor diagnostic settings and alerts through reviewed IaC or
portal change control, then use this preflight in release checks. Do not
export prompts, translations, transcripts, audio, SAS URLs, tokens, or keys
as telemetry dimensions.

Monitor availability, latency, throttling, errors, authentication failures,
and batch terminal states. Govern data residency, private networking, RBAC,
retention/deletion, human review for sensitive translations, and approved
voice/MCP tool boundaries. See Azure Translator secure deployment guidance and
Azure Speech data/privacy documentation before production use.
"""
from _shared.config import settings


def preflight() -> dict[str, bool]:
    current = settings()
    return {
        "application_insights_configured": bool(current.app_insights_connection_string),
        "speech_endpoint_configured": bool(current.speech_endpoint),
        "voice_live_endpoint_configured": bool(current.voice_live_endpoint),
        "speech_mcp_endpoint_configured": bool(current.speech_mcp_url),
    }


def main(argv: list[str] | None = None) -> None:
    if argv:
        raise SystemExit("This local-only preflight accepts no arguments.")
    checks = preflight()
    print("Text and speech monitoring/governance preflight. No cloud calls made.")
    for name, configured in checks.items():
        print(f"- {name}: {'configured' if configured else 'missing'}")
    print("Monitor: availability, latency, throttling, errors, auth failures, and Document Translation terminal status.")
    print("Telemetry: redact content and identifiers; alert on anomalous rate, failure, and access changes.")
    print("Govern: least-privilege RBAC, private DNS/egress, residency, retention/deletion, human review, approved voices/MCP.")
    print("Apply diagnostic settings, alert rules, Policy, and retention only through reviewed IaC/change control.")


if __name__ == "__main__":
    main()
