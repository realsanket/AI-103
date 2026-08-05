"""Lab 05 — configure a current agent's stable endpoint before distribution.

Run from repository root:
    uv run python 08-advanced-agents-other/05_gateway_publishing_preflight.py

`--apply` pins the agent's stable endpoint to one reviewed version. It does not
publish to Microsoft 365 or Teams: current channel publishing is a deliberate
Foundry portal operation after gateway, RBAC, privacy, and channel review.
"""
import argparse
import json
import os
import subprocess
from urllib.parse import quote, urlparse

from dotenv import load_dotenv


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
    load_dotenv()
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
