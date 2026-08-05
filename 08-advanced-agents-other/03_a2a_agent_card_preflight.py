"""Lab 03 — configure incoming A2A v1.0 discovery for a current Foundry agent.

Run from repository root:
    uv run python 08-advanced-agents-other/03_a2a_agent_card_preflight.py

`--apply` PATCHes an existing agent. `--apply --verify` then fetches only its
v1.0 agent card. Both paths use the signed-in Azure identity, never a key.
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


def a2a_urls(endpoint: str, agent_name: str) -> tuple[str, str]:
    if not agent_name or "/" in agent_name:
        raise ValueError("Agent name must be one path segment.")
    base = f"{project_endpoint(endpoint)}/agents/{quote(agent_name, safe='')}/endpoint/protocols/a2a"
    return base, f"{base}/agentCard/v1.0"


def patch_body(description: str, skill_id: str, skill_name: str) -> dict:
    if not all((description, skill_id, skill_name)):
        raise ValueError("Agent-card description, skill ID, and skill name are required.")
    return {
        "agent_card": {
            "description": description,
            "version": "1.0",
            "skills": [
                {
                    "id": skill_id,
                    "name": skill_name,
                    "description": description,
                }
            ],
        },
        "agent_endpoint": {
            "protocol_configuration": {
                "responses": {},
                "a2a": {},
            }
        },
    }


def patch_command(endpoint: str, agent_name: str, body: dict) -> list[str]:
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
        "Content-Type=application/json",
        "--body",
        json.dumps(body),
    ]


def preflight(endpoint: str | None, agent_name: str | None) -> None:
    print("No cloud calls made.")
    if not endpoint or not agent_name:
        print("Set PROJECT_ENDPOINT and FOUNDRY_AGENT_NAME before --apply.")
        return
    base, card = a2a_urls(endpoint, agent_name)
    print(f"A2A v1.0 base endpoint: {base}")
    print(f"A2A v1.0 agent card: {card}")
    print("Use A2A v1.0 for new callers. Assign Foundry Agent Consumer to each calling identity.")


def main(argv: list[str] | None = None) -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Preflight or enable A2A and an agent card.")
    parser.add_argument("--apply", action="store_true", help="PATCH the agent endpoint and card.")
    parser.add_argument("--verify", action="store_true", help="Fetch v1.0 agent card; requires --apply.")
    parser.add_argument("--agent-name", default=os.getenv("FOUNDRY_AGENT_NAME"))
    parser.add_argument("--description", default="Answers approved support-policy questions.")
    parser.add_argument("--skill-id", default="support-policy-qa")
    parser.add_argument("--skill-name", default="Support policy Q&A")
    args = parser.parse_args(argv)
    endpoint = os.getenv("PROJECT_ENDPOINT")
    if not args.apply:
        if args.verify:
            parser.error("--verify requires --apply.")
        preflight(endpoint, args.agent_name)
        return
    if not endpoint or not args.agent_name:
        parser.error("--apply requires PROJECT_ENDPOINT and --agent-name or FOUNDRY_AGENT_NAME.")
    body = patch_body(args.description, args.skill_id, args.skill_name)
    subprocess.run(patch_command(endpoint, args.agent_name, body), check=True)
    _, card = a2a_urls(endpoint, args.agent_name)
    print(f"Enabled current Responses and A2A protocols. v1.0 card: {card}")
    if args.verify:
        subprocess.run(
            ["az", "rest", "--method", "get", "--url", card, "--resource", "https://ai.azure.com"],
            check=True,
        )


if __name__ == "__main__":
    main()
