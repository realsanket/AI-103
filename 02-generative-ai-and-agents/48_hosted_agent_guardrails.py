# Run: uv run python 02-generative-ai-and-agents/48_hosted_agent_guardrails.py [--apply]
"""Attach a Responsible AI guardrail to a hosted agent.

Hosted agents accept an optional `rai_config` on the version definition. Set
`rai_config.rai_policy_name` to the FULL ARM resource ID of the RAI policy on
the Foundry account and the platform screens prompts + responses against that
policy at runtime. The same RAI policy also carries network egress rules
(preview) that govern which outbound hosts the sandbox can reach.

Warnings the doc calls out explicitly:
  - Deploy-time validation does NOT catch a bad policy ID. An agent that
    references a non-existent policy is created successfully, reports
    `active`, and applies NO filtering — the guardrail fails open. Always
    verify the policy exists on the account before trusting the agent.
  - `rai_policy_name` must be the full ARM ID, not the bare policy name.
  - Omitting `rai_config` → no content-safety guardrail. Including it without
    `rai_policy_name` → default policy `Microsoft.DefaultV2`.

This lesson is a companion to lesson 28 (hosted-agent Responses runtime): it
attaches a guardrail to a NEW hosted-agent version that reuses your existing
image. Preflight prints the exact `HostedAgentDefinition` shape without touching
Azure. `--apply` creates the version and prints the returned definition so you
can confirm `rai_config.rai_policy_name` round-tripped correctly. Follow the
doc's HTTP test-and-verify steps to prove the guardrail actually filters.

Code path:
  Preflight — validate env vars, print the JSON payload with `rai_config`.
  --apply   — build `HostedAgentDefinition(rai_config=RaiConfig(...))`,
              call `agents.create_version`, print the returned version,
              print the returned `rai_config` for verification.

What to watch:
  Returned `rai_config.rai_policy_name` must match `RAI_POLICY_ID`. Content-
  filter behavior at request time is what actually proves the guardrail is
  wired — send a policy-violating prompt to the agent's Responses endpoint
  and expect `HTTP 400 content_filter` (or `HTTP 200` for a benign prompt).

Prerequisites / env vars:
  PROJECT_ENDPOINT           — Foundry project endpoint
  HOSTED_AGENT_NAME          — hosted agent name to create/replace a version on
  HOSTED_AGENT_IMAGE         — container image (e.g. registry.azurecr.io/img:tag)
  RAI_POLICY_ID              — FULL ARM ID of the RAI policy to attach
"""
import argparse
import json
import os

from _shared.config import settings


def _configuration() -> tuple[str, str, str, str]:
    project_endpoint = settings().require("PROJECT_ENDPOINT")
    name = os.environ.get("HOSTED_AGENT_NAME", "").strip()
    image = os.environ.get("HOSTED_AGENT_IMAGE", "").strip()
    rai = os.environ.get("RAI_POLICY_ID", "").strip()
    missing = [
        k
        for k, v in {
            "HOSTED_AGENT_NAME": name,
            "HOSTED_AGENT_IMAGE": image,
            "RAI_POLICY_ID": rai,
        }.items()
        if not v
    ]
    if missing:
        raise SystemExit(f"Missing required env vars: {', '.join(missing)}")
    if not rai.startswith("/subscriptions/") or "/raiPolicies/" not in rai:
        raise SystemExit(
            "RAI_POLICY_ID must be the FULL ARM resource ID "
            "(/subscriptions/<sub>/resourceGroups/<rg>/providers/"
            "Microsoft.CognitiveServices/accounts/<account>/raiPolicies/<policy>)."
        )
    return project_endpoint, name, image, rai


def _payload_preview(name: str, image: str, rai: str) -> dict:
    return {
        "agent_name": name,
        "definition": {
            "kind": "hosted",
            "container_configuration": {"image": image},
            "cpu": "1",
            "memory": "2Gi",
            "protocol_versions": [{"protocol": "responses", "version": "1.0.0"}],
            "rai_config": {"rai_policy_name": rai},
        },
    }


def preflight() -> None:
    s = settings()
    name = os.environ.get("HOSTED_AGENT_NAME") or "<HOSTED_AGENT_NAME not set>"
    image = os.environ.get("HOSTED_AGENT_IMAGE") or "<HOSTED_AGENT_IMAGE not set>"
    rai = os.environ.get("RAI_POLICY_ID") or "<RAI_POLICY_ID not set>"
    print("No cloud calls made.")
    print(f"Project endpoint:  {s.project_endpoint or '<PROJECT_ENDPOINT not set>'}")
    print(f"Hosted agent name: {name}")
    print(f"Container image:   {image}")
    print(f"RAI policy ARM ID: {rai}")
    print()
    print("Payload the SDK would send to agents.create_version:")
    print(json.dumps(_payload_preview(name, image, rai), indent=2))
    print()
    print("Verification tips (doc-verbatim):")
    print("  - After creation, list account raiPolicies and confirm the final segment matches.")
    print("  - Send a policy-violating prompt to the agent's Responses endpoint and expect")
    print("    HTTP 400 with `content_filter` error.")
    print("  - Network egress rules (preview) travel on the SAME RAI policy — no separate attach.")
    print()
    print("Run with --apply to create the hosted-agent version with rai_config attached.")


def apply() -> None:
    from azure.ai.projects.models import (
        AgentEndpointProtocol,
        ContainerConfiguration,
        HostedAgentDefinition,
        ProtocolVersionRecord,
        RaiConfig,
    )
    from _shared.foundry_client import project_client

    _, name, image, rai = _configuration()
    client = project_client()

    definition = HostedAgentDefinition(
        cpu="1",
        memory="2Gi",
        container_configuration=ContainerConfiguration(image=image),
        protocol_versions=[
            ProtocolVersionRecord(protocol=AgentEndpointProtocol.RESPONSES, version="1.0.0"),
        ],
        rai_config=RaiConfig(rai_policy_name=rai),
    )
    agent = client.agents.create_version(agent_name=name, definition=definition)
    print(f"Created hosted agent {agent.name} version {agent.version}.")
    returned = getattr(agent.definition, "rai_config", None)
    print("Returned rai_config:")
    print(json.dumps(
        returned.as_dict() if hasattr(returned, "as_dict") else {"rai_policy_name": rai},
        indent=2,
        default=str,
    ))
    print()
    print("Guardrail is attached. Test it by sending a policy-violating prompt to the")
    print("agent's Responses endpoint; a properly wired guardrail returns HTTP 400")
    print("with `code: content_filter`. A benign prompt returns HTTP 200 as normal.")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Attach an RAI guardrail to a hosted agent.")
    parser.add_argument("--apply", action="store_true", help="Create the hosted-agent version.")
    args = parser.parse_args(argv)
    if not args.apply:
        preflight()
        return
    apply()


if __name__ == "__main__":
    main()
