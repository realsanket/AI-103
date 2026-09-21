# Run: uv run python 02-generative-ai-and-agents/41_enable_incoming_a2a.py [--apply] [--verify] [--version {1.0,0.3}]

"""Lesson 41 - expose an existing Foundry agent as an incoming A2A endpoint.

Run from repository root:
    uv run python 02-generative-ai-and-agents/41_enable_incoming_a2a.py
    uv run python 02-generative-ai-and-agents/41_enable_incoming_a2a.py --apply
    uv run python 02-generative-ai-and-agents/41_enable_incoming_a2a.py --apply --verify

What. Enabling incoming A2A requires two things in a single PATCH: an
`agent_card` (description, version, skills) and `agent_endpoint.
protocol_configuration` with BOTH `responses: {}` and `a2a: {}`. Incoming
A2A requires the Responses protocol, so Responses must be re-declared in
the same PATCH even if it was already on. Foundry then publishes two card
URLs at `.../endpoint/protocols/a2a/agentCard/v1.0` (GA) and
`.../agentCard/v0.3` (preview) from the same authored card content.

Why. Callers pick the A2A version through card discovery, the `A2A-Version`
header, or the `?a2a-version=` query string. If nothing is set, Foundry
serves preview v0.3 by default - so production integrations MUST pin v1.0
one of those three ways. This lesson defaults the card `version` to `1.0`
and prints both card URLs so you can confirm calling agents will negotiate
v1.0 automatically.

Code path. `patch_body()` builds the doc-verbatim `agent_card` +
`agent_endpoint` JSON. Preflight prints the body, the two card URLs, and
the outbound A2A tool payload another Foundry agent would use to CALL
this one back (audience `https://ai.azure.com`, `AgenticIdentityToken`).
`--apply` calls `project.agents.update_details(...)` from
`azure-ai-projects` with `AgentEndpointConfig`, `ProtocolConfiguration`,
`ResponsesProtocolConfiguration`, `A2AProtocolConfiguration`, `AgentCard`,
and `AgentCardSkill`. `--verify` fetches the v1.0 card through
`az rest --method get` to prove it's live.

What to watch. Preflight: `A2A v1.0 card: ...agentCard/v1.0` and the JSON
body. `--apply`: SDK returns the patched agent; script prints
"Enabled incoming A2A on <name>". `--verify`: printed JSON must include
`protocolVersion: "1.0"` and match the description/skills you sent.
Incoming A2A requires the caller to have `Foundry Agent Consumer` on the
project or agent scope - enabling the protocol does NOT grant access.

Env vars.
  PROJECT_ENDPOINT     - Foundry project HTTPS URL.
  AZURE_AI_AGENT_NAME  - Existing prompt agent to expose (or --agent-name).
  --description        - Agent-card description (default provided).
  --skill-id           - Skill ID (default: general-qa).
  --skill-name         - Skill display name.
  --version            - A2A card version: 1.0 (default, GA) or 0.3 (preview).

Limits. Incoming A2A supports text modality only. Streaming (SSE) is not
supported. v1.0 is JSONRPC-only on the incoming path; HTTP+JSON is v0.3-
only. Tasks and contexts retain for 60 days from the most recent write.

References:
  how-to/enable-agent-to-agent-endpoint.md
  concepts/hosted-agents.md (protocol coexistence)
"""
from __future__ import annotations

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
    ):
        raise ValueError("PROJECT_ENDPOINT must be a Foundry project HTTPS URL.")
    return value.rstrip("/")


def a2a_urls(endpoint: str, agent_name: str) -> dict[str, str]:
    if not agent_name or "/" in agent_name:
        raise ValueError("Agent name must be one path segment.")
    base = f"{project_endpoint(endpoint)}/agents/{quote(agent_name, safe='')}/endpoint/protocols/a2a"
    return {
        "base": base,
        "card_v1_0": f"{base}/agentCard/v1.0",
        "card_v0_3": f"{base}/agentCard/v0.3",
    }


def patch_body(*, version: str, description: str, skill_id: str, skill_name: str) -> dict:
    if version not in {"1.0", "0.3"}:
        raise ValueError("Version must be 1.0 (GA) or 0.3 (preview).")
    if not all((description, skill_id, skill_name)):
        raise ValueError("description, skill_id, skill_name are required.")
    return {
        "agent_card": {
            "description": description,
            "version": version,
            "skills": [
                {"id": skill_id, "name": skill_name, "description": description},
            ],
        },
        "agent_endpoint": {
            "protocol_configuration": {
                # Incoming A2A requires responses; re-declare both.
                "responses": {},
                "a2a": {},
            }
        },
    }


def outbound_tool_payload(base_url: str) -> dict:
    """The `a2a` tool payload another Foundry agent would use to call this one."""
    return {
        "type": "a2a",
        "a2a_version": "1.0",
        "base_url": base_url,
        "project_connection_id": "<AgenticIdentityToken connection to this agent>",
        "send_credentials_for_agent_card": False,
    }


def apply_via_sdk(endpoint: str, agent_name: str, body: dict) -> None:
    from azure.identity import DefaultAzureCredential
    from azure.ai.projects import AIProjectClient
    from azure.ai.projects.models import (
        A2AProtocolConfiguration,
        AgentCard,
        AgentCardSkill,
        AgentEndpointConfig,
        ProtocolConfiguration,
        ResponsesProtocolConfiguration,
    )

    project = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())
    card_dict = body["agent_card"]
    patched = project.agents.update_details(
        agent_name=agent_name,
        agent_endpoint=AgentEndpointConfig(
            protocol_configuration=ProtocolConfiguration(
                responses=ResponsesProtocolConfiguration(),
                a2a=A2AProtocolConfiguration(),
            ),
        ),
        agent_card=AgentCard(
            version=card_dict["version"],
            description=card_dict["description"],
            skills=[
                AgentCardSkill(
                    id=s["id"], name=s["name"], description=s.get("description", ""),
                )
                for s in card_dict["skills"]
            ],
        ),
    )
    print(f"Enabled incoming A2A on {patched.name}.")


def verify_card(card_url: str) -> None:
    subprocess.run(
        ["az", "rest", "--method", "get", "--url", card_url,
         "--resource", "https://ai.azure.com"],
        check=True,
    )


def main(argv: list[str] | None = None) -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Preflight or enable incoming A2A on a Foundry agent.")
    parser.add_argument("--apply", action="store_true", help="PATCH the agent through the SDK.")
    parser.add_argument("--verify", action="store_true", help="After apply, GET the v1.0 card.")
    parser.add_argument("--agent-name", default=os.getenv("AZURE_AI_AGENT_NAME"))
    parser.add_argument("--version", choices=("1.0", "0.3"), default="1.0",
                        help="A2A card version: 1.0 GA (default) or 0.3 preview.")
    parser.add_argument("--description", default="A helpful assistant that answers questions.")
    parser.add_argument("--skill-id", default="general-qa")
    parser.add_argument("--skill-name", default="General Q&A")
    args = parser.parse_args(argv)

    endpoint = os.getenv("PROJECT_ENDPOINT")
    if not endpoint or not args.agent_name:
        if args.apply or args.verify:
            parser.error("--apply/--verify require PROJECT_ENDPOINT and --agent-name / AZURE_AI_AGENT_NAME.")
        print("Set PROJECT_ENDPOINT and AZURE_AI_AGENT_NAME to see the URLs and body.")
        return

    try:
        endpoint = project_endpoint(endpoint)
    except ValueError as exc:
        parser.error(str(exc))
    urls = a2a_urls(endpoint, args.agent_name)
    body = patch_body(
        version=args.version,
        description=args.description,
        skill_id=args.skill_id,
        skill_name=args.skill_name,
    )

    print(f"Agent: {args.agent_name}")
    print(f"A2A base:        {urls['base']}")
    print(f"A2A v1.0 card:   {urls['card_v1_0']}  (GA - recommended)")
    print(f"A2A v0.3 card:   {urls['card_v0_3']}  (preview)")
    print()
    print("PATCH body (update_details maps this into AgentCard + protocol_configuration):")
    print(json.dumps(body, indent=2))
    print()
    print("Outbound `a2a` tool payload a caller Foundry agent would use to reach this one:")
    print(json.dumps(outbound_tool_payload(urls["base"]), indent=2))
    print()
    print("Reminder: incoming A2A requires Microsoft Entra ID. Assign Foundry Agent")
    print("Consumer to each calling identity at project or agent scope.")
    print("v1.0 is JSONRPC-only. Text modality only. Streaming is not supported.")

    if args.verify and not args.apply:
        parser.error("--verify requires --apply.")
    if not args.apply:
        print("\nPreflight only. Re-run with --apply to enable A2A on the agent.")
        return

    apply_via_sdk(endpoint, args.agent_name, body)
    if args.verify:
        print(f"\nGET {urls['card_v1_0']}")
        verify_card(urls["card_v1_0"])


if __name__ == "__main__":
    main()
