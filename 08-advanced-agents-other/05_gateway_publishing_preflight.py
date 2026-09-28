# Run: uv run python 08-advanced-agents-other/05_gateway_publishing_preflight.py [--apply --agent-name <name> --agent-version <int>]
# Practice-question coverage: Q13.
"""Pin an agent's stable endpoint to one reviewed version before distribution.

AI Gateway uses Azure API Management (APIM v2) to apply governance, quotas,
token limits, and observability. Enable it in Foundry portal Operate →
Admin console; confirm both gateway AND target project show `Enabled`.
Existing projects require explicit addition to a configured gateway.

Default preflight prints the pre-distribution checklist without any cloud
call. `--apply` PATCHes the agent's `agent_endpoint.version_selector` to a
`FixedRatio` rule routing 100% of stable-endpoint traffic to the specified
immutable agent version.

Channel publishing (Microsoft 365 Copilot / Teams) is NOT scripted. It's a
deliberate Foundry portal operation after gateway, RBAC, privacy, and
channel review. Do NOT use the deprecated Agent Application publishing
model — this lab targets the current stable-endpoint model.

Code path:
  project_endpoint() → validate URL. endpoint_patch(version) → JSON with
  `version_selection_rules: [{"type": "FixedRatio", "agent_version": ...,
  "traffic_percentage": 100}]`. patch_command() → `az rest --method patch
  --url <endpoint>/agents/<name>?api-version=v1 --headers Content-Type=
  application/merge-patch+json --body <json>`.

What to watch. Preflight: gateway + channel-publishing checklist. `--apply`:
PATCH success + `Stable endpoint pinned. Publish to Microsoft 365 Copilot
or Teams only through reviewed portal flow.`

Prerequisites / env vars:
  PROJECT_ENDPOINT     — Foundry project HTTPS URL
  FOUNDRY_AGENT_NAME   — existing agent (or --agent-name)
  --agent-version INT  — immutable numeric version (required with --apply)
  --apply              — pin stable endpoint via PATCH
"""
import argparse
import json
import os
import subprocess
from urllib.parse import quote, urlparse

from _shared.config import load_env


def project_endpoint(value: str) -> str:
    parsed = urlparse(value)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or not parsed.hostname.endswith(".services.ai.azure.com")
        or "/api/projects/" not in parsed.path
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError("PROJECT_ENDPOINT must be a credential-free Foundry project HTTPS URL.")
    return value.rstrip("/")


def endpoint_patch(agent_version: str) -> dict:
    if not agent_version or not agent_version.isdigit():
        raise ValueError("Agent version must be a numeric immutable version.")
    return {
        "agent_endpoint": {
            "version_selector": {
                "version_selection_rules": [
                    {
                        "type": "FixedRatio",
                        "agent_version": agent_version,
                        "traffic_percentage": 100,
                    }
                ]
            }
        }
    }


def patch_command(endpoint: str, agent_name: str, body: dict) -> list[str]:
    if not agent_name or "/" in agent_name:
        raise ValueError("Agent name must be one path segment.")
    return [
        "az",
        "rest",
        "--method",
        "patch",
        "--url",
        f"{project_endpoint(endpoint)}/agents/{quote(agent_name, safe='')}?api-version=v1",
        "--resource",
        "https://ai.azure.com",
        "--headers",
        "Content-Type=application/merge-patch+json",
        "--body",
        json.dumps(body),
    ]


def preflight() -> None:
    print("No cloud calls made.")
    print("Gateway: portal Admin console must show gateway and project status Enabled.")
    print("Before distribution: test current stable endpoint, pin its version, and grant least privilege to agent identity.")
    print("Channel publish remains Foundry portal only; do not create legacy Agent Applications.")
    print("Review Microsoft 365/Teams data handling, Bot Service permissions, and organization approval before publishing.")


def main(argv: list[str] | None = None) -> None:
    load_env()
    parser = argparse.ArgumentParser(description="Pin a current stable endpoint after gateway preflight.")
    parser.add_argument("--apply", action="store_true", help="Pin stable endpoint to reviewed version.")
    parser.add_argument("--agent-name", default=os.getenv("FOUNDRY_AGENT_NAME"))
    parser.add_argument("--agent-version")
    args = parser.parse_args(argv)
    if not args.apply:
        preflight()
        return
    endpoint = os.getenv("PROJECT_ENDPOINT")
    if not endpoint or not args.agent_name or not args.agent_version:
        parser.error("--apply requires PROJECT_ENDPOINT, --agent-name, and --agent-version.")
    subprocess.run(
        patch_command(endpoint, args.agent_name, endpoint_patch(args.agent_version)),
        check=True,
    )
    print("Stable endpoint pinned. Publish to Microsoft 365 Copilot or Teams only through reviewed portal flow.")


if __name__ == "__main__":
    main()
