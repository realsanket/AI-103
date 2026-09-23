# Run: uv run python 01-plan-and-manage/questions/01_access_and_metrics_preflight.py
# Practice-question coverage: Q23, Q113, Q175.
"""Question supplement: keyless agent access and operational metrics.

Maps PDF questions 23, 113, and 175. This is deliberately a local preflight:
it builds a reviewable access and telemetry plan but never reads a secret,
changes RBAC, or calls Azure.
"""
from __future__ import annotations


def keyless_agent_access_plan(agent_name: str) -> dict[str, object]:
    """Return the minimum plan for reading an existing project agent."""
    if not agent_name or "/" in agent_name:
        raise ValueError("agent_name must be one nonempty path segment")
    return {
        "credential": "DefaultAzureCredential()",
        "operation": f"project_client.agents.get(agent_name={agent_name!r})",
        "does_not_do": ["use an API key", "create a new agent version"],
        "review_before_run": [
            "Foundry project RBAC for the calling principal",
            "separate Key Vault role and network access when a Key Vault connection is used",
        ],
    }


def operational_metrics() -> dict[str, str]:
    """Name the signals needed to distinguish capacity from run-level latency."""
    return {
        "availability": "successful requests / total requests",
        "utilization": "deployment quota and throughput consumption",
        "latency": "end-to-end and child LLM/tool/retrieval span durations",
        "failures": "HTTP status and exception category without prompt or tool-result content",
        "tokens": "input, output, and cached-token counts",
    }


def main() -> None:
    print("No cloud calls made. Review this plan before configuring access or telemetry.")
    print("Agent access:")
    for key, value in keyless_agent_access_plan("Agent1").items():
        print(f"  {key}: {value}")
    print("Metrics:")
    for key, value in operational_metrics().items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
