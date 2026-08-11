# Run: uv run python 08-advanced-agents-other/03_a2a_agent_card_preflight.py [--apply [--verify] --agent-name <name>]
"""Configure incoming A2A v1.0 discovery for a Foundry agent.

Agent-to-Agent (A2A) is the standard for one agent to call another. New
callers should target A2A v1.0. The agent card is protected by Entra ID —
NOT anonymously discoverable. Default preflight prints the two A2A URLs
without contacting Azure.

`--apply` runs `az rest --method patch` to write the agent card metadata
(description, skill id + name) and enable both `responses` and `a2a`
protocols in the agent's endpoint. `--apply --verify` then fetches the v1.0
card via `az rest --method get` to confirm it's live.

Enabling A2A does NOT grant caller access. Assign `Foundry Agent Consumer`
to each calling identity on the project or agent scope. Decide on-behalf-of
vs service-identity authentication deliberately. Test with A2A v1.0 clients
only for new integrations.

Code path:
  project_endpoint() → validate URL. a2a_urls() → build base +
  `/agentCard/v1.0`. patch_body() → JSON with agent_card + agent_endpoint
  protocol_configuration. patch_command() → `az rest --method patch --url
  <endpoint>/agents/<name>?api-version=v1 --resource https://ai.azure.com
  --body <json>`. `--verify`: same URL, GET.

What to watch. Preflight: `A2A v1.0 base endpoint: <url>` + `A2A v1.0 agent
card: <url>`. `--apply`: PATCH success + `Enabled current Responses and A2A
protocols. v1.0 card: <url>`. `--verify`: fetched card JSON printed.

Prerequisites / env vars:
  PROJECT_ENDPOINT      — Foundry project HTTPS URL
  FOUNDRY_AGENT_NAME    — existing agent name (or --agent-name)
  --description         — agent-card description (default provided)
  --skill-id            — skill identifier (default: support-policy-qa)
  --skill-name          — skill display name (default provided)
  --apply               — PATCH agent card + protocols
  --verify              — GET v1.0 card after apply (requires --apply)
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
