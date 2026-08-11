# Run: uv run python 08-advanced-agents-other/08_hosted_agent_env_preflight.py [--apply --agent-name <name> --env-name <KEY> --env-value <value>]
"""Set or read runtime environment variables on a deployed Foundry hosted agent.

Hosted-agent runtime env vars (APPSETTING-like entries) are set after deploy,
not baked into the container. Foundry exposes them via PATCH on the agent
resource. This lesson proves the pattern: preflight shows what variables would
be set; --apply PATCHes the named env var onto the agent.

NEVER pass secrets as plain env vars — use Key Vault reference syntax:
`@Microsoft.KeyVault(SecretUri=...)`. This lesson validates that syntax when
value starts with `@Microsoft.KeyVault`.

Code path:
  preflight(): validate PROJECT_ENDPOINT + FOUNDRY_AGENT_NAME + args shape.
  --apply: `az rest --method patch --url <endpoint>/agents/<name>?api-version=v1
  --body {"runtime": {"env_vars": [{"name": KEY, "value": VALUE}]}}`.

What to watch. Preflight: env validation. --apply: PATCH success. Confirm
value in portal: Foundry → agent → Settings → Environment variables.
Key Vault refs are resolved at runtime — value in portal shows the ref string.

Prerequisites / env vars:
  PROJECT_ENDPOINT      — Foundry project HTTPS URL
  FOUNDRY_AGENT_NAME    — existing hosted agent (or --agent-name)
  --env-name KEY        — env var name (required with --apply)
  --env-value VALUE     — env var value or @Microsoft.KeyVault(...) ref
  --apply               — PATCH env var onto agent
"""
import argparse
import json
import os
import subprocess
from urllib.parse import quote

from _shared.config import settings


def preflight(agent_name: str | None, env_name: str | None, env_value: str | None) -> None:
    print("Hosted agent env var preflight (no cloud calls).")
    current = settings()
    print(f"- project_endpoint: {'configured' if current.project_endpoint else 'missing'}")
    print(f"- agent_name: {agent_name or 'missing'}")
    if env_name and env_value and env_value.startswith("@Microsoft.KeyVault"):
        print(f"- value syntax: Key Vault reference (secure)")
    elif env_name and env_value:
        print(f"- value syntax: plain text (use KV ref for secrets)")


def apply(endpoint: str, agent_name: str, env_name: str, env_value: str) -> None:
    body = {"runtime": {"env_vars": [{"name": env_name, "value": env_value}]}}
    url = f"{endpoint}/agents/{quote(agent_name, safe='')}?api-version=v1"
    subprocess.run(
        ["az", "rest", "--method", "patch", "--url", url,
         "--resource", "https://ai.azure.com",
         "--headers", "Content-Type=application/json",
         "--body", json.dumps(body)],
        check=True,
    )
    print(f"Env var '{env_name}' set on agent '{agent_name}'.")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Set a runtime env var on a hosted agent.")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--agent-name", default=os.environ.get("FOUNDRY_AGENT_NAME"))
    parser.add_argument("--env-name")
    parser.add_argument("--env-value")
    args = parser.parse_args(argv)
    if not args.apply:
        preflight(args.agent_name, args.env_name, args.env_value)
        return
    endpoint = settings().require("PROJECT_ENDPOINT")
    if not args.agent_name or not args.env_name or args.env_value is None:
        parser.error("--apply requires --agent-name, --env-name, --env-value.")
    apply(endpoint, args.agent_name, args.env_name, args.env_value)


if __name__ == "__main__":
    main()
