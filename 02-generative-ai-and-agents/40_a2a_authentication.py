# Run: uv run python 02-generative-ai-and-agents/40_a2a_authentication.py [--mode {key,entra,oauth,project-mi,agentic-id,none}] [--apply]

"""Lesson 40 - walk the five A2A outbound-connection auth modes.

Run from repository root:
    uv run python 02-generative-ai-and-agents/40_a2a_authentication.py
    uv run python 02-generative-ai-and-agents/40_a2a_authentication.py --mode entra
    uv run python 02-generative-ai-and-agents/40_a2a_authentication.py --mode key --apply

What. The Foundry A2A tool talks to a remote agent through a project
connection. The connection carries the authentication method. Five methods
are supported: key-based ("CustomKeys"), Microsoft Entra ID via the agent
identity ("AgenticIdentityToken"), Microsoft Entra ID via the project
managed identity ("ProjectManagedIdentity"), OAuth 2.0 identity passthrough
("OAuth2"), and unauthenticated access ("None"). Each maps to a different
`authType` on the ARM `Microsoft.CognitiveServices/.../connections` PUT body.

Why. The auth method is chosen once at connection creation time and cannot
be updated for OAuth. Picking the wrong mode either leaks a shared secret
(key when OAuth passthrough was needed), locks out per-user permissions
(agent identity when the endpoint expects OAuth), or fails outright
(unauthenticated against a protected endpoint). This lesson prints the
comparison table, the mode you pick, and the exact JSON body Foundry
expects, so you can compare before you commit.

Code path.
  1. `AUTH_MODES` dict encodes each mode's authType, extra properties, and
     "user context persists" flag from the concept doc.
  2. `comparison_table()` prints the doc's summary table verbatim.
  3. `build_body(mode, target, ...)` returns the ARM connection PUT body
     with the correct `authType`, `category=RemoteA2A`, and mode-specific
     properties (Credentials.Keys, audience, TokenUrl, etc.). Mirrors the
     REST examples in `how-to/tools/agent-to-agent.md`.
  4. Preflight prints the body only. No cloud calls.
  5. `--apply` writes the connection through `az rest --method put` on
     the ARM connections endpoint. Requires ARM_TOKEN (fetched inline via
     `az account get-access-token --scope https://management.azure.com/.default`).

What to watch. Preflight: printed body must contain `RemoteA2A`, correct
`authType`, and either `Credentials.Keys`, `audience`, or OAuth URLs -
never both a shared key AND an OAuth block. `--apply`: `az rest` prints
the created connection resource ID; save the connection *name* for the
A2A tool (`project_connection_id` in the tool definition).

Env vars.
  PROJECT_ENDPOINT       - Foundry project URL (validated shape).
  A2A_TARGET_AGENT_URL   - Remote A2A base URL (HTTPS).
  A2A_AUTH_MODE          - Default mode; override with --mode.
  A2A_CONNECTION_NAME    - Connection name (default: my-a2a-conn).
  A2A_KEY_NAME / A2A_KEY_VALUE - Required for --mode key.
  A2A_ENTRA_AUDIENCE     - Required for entra/project-mi/agentic-id
                           (typically https://ai.azure.com for Foundry).
  A2A_OAUTH_CLIENT_ID / A2A_OAUTH_CLIENT_SECRET / A2A_OAUTH_AUTHORIZATION_URL /
  A2A_OAUTH_TOKEN_URL / A2A_OAUTH_REFRESH_URL / A2A_OAUTH_SCOPES
                         - Required for --mode oauth (custom OAuth).
  AZURE_SUBSCRIPTION_ID / AZURE_RESOURCE_GROUP / FOUNDRY_ACCOUNT_NAME /
  FOUNDRY_PROJECT_NAME   - Required for --apply (ARM path parts).

References:
  concepts/agent-to-agent-authentication.md
  how-to/tools/agent-to-agent.md#create-an-a2a-connection-by-using-the-rest-api
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
from urllib.parse import urlparse

from dotenv import load_dotenv


# ponytail: verbatim from doc's "Supported authentication methods" table.
AUTH_MODES: dict[str, dict] = {
    "key": {
        "authType": "CustomKeys",
        "description": "API key / PAT / bearer token in an HTTP header.",
        "user_context_persists": False,
    },
    "entra": {
        "authType": "AgenticIdentityToken",
        "description": "Microsoft Entra ID - agent managed identity.",
        "user_context_persists": False,
    },
    "project-mi": {
        "authType": "ProjectManagedIdentity",
        "description": "Microsoft Entra ID - project managed identity.",
        "user_context_persists": False,
    },
    "agentic-id": {
        "authType": "AgenticIdentityToken",
        "description": "Alias of `entra`; agent-identity token (Foundry target audience https://ai.azure.com).",
        "user_context_persists": False,
    },
    "oauth": {
        "authType": "OAuth2",
        "description": "OAuth 2.0 identity passthrough. Custom app registration.",
        "user_context_persists": True,
    },
    "none": {
        "authType": "None",
        "description": "Unauthenticated. Only for public / network-protected endpoints.",
        "user_context_persists": False,
    },
}


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


def target_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.hostname:
        raise ValueError("A2A_TARGET_AGENT_URL must be HTTPS.")
    return value.rstrip("/")


def comparison_table() -> None:
    print()
    print("A2A outbound authentication - method comparison")
    print("-" * 78)
    print(f"{'mode':<12}{'authType':<26}{'user ctx':<10}description")
    print("-" * 78)
    for mode, cfg in AUTH_MODES.items():
        yn = "yes" if cfg["user_context_persists"] else "no"
        print(f"{mode:<12}{cfg['authType']:<26}{yn:<10}{cfg['description']}")
    print("-" * 78)
    print("Shared identity for all users: key / entra / project-mi / agentic-id.")
    print("Per-user identity passthrough: oauth.")
    print("Card-fetch credentials: set send_credentials_for_agent_card=true on the A2A tool")
    print("only when the endpoint publisher confirms the card path is protected.")


def build_body(
    mode: str,
    target: str,
    *,
    key_name: str | None,
    key_value: str | None,
    audience: str | None,
    oauth: dict | None,
) -> dict:
    """Return the ARM connection PUT body for `mode`.

    Mirrors the JSON in how-to/tools/agent-to-agent.md verbatim.
    """
    cfg = AUTH_MODES[mode]
    props: dict = {
        "authType": cfg["authType"],
        "group": "ServicesAndApps",
        "category": "RemoteA2A",
        "expiryTime": None,
        "target": target,
        "isSharedToAll": True,
        "sharedUserList": [],
        "Credentials": {},
        "metadata": {"ApiType": "Azure"},
    }
    if mode == "key":
        if not key_name or not key_value:
            raise ValueError("--mode key needs A2A_KEY_NAME and A2A_KEY_VALUE.")
        props["Credentials"] = {"Keys": {key_name: key_value}}
    elif mode in {"entra", "agentic-id", "project-mi"}:
        if not audience:
            raise ValueError(f"--mode {mode} needs A2A_ENTRA_AUDIENCE (e.g. https://ai.azure.com).")
        props["audience"] = audience
    elif mode == "oauth":
        required = ("client_id", "authorization_url", "token_url", "scopes")
        if not oauth or not all(oauth.get(k) for k in required):
            raise ValueError(
                "--mode oauth needs A2A_OAUTH_CLIENT_ID, A2A_OAUTH_AUTHORIZATION_URL, "
                "A2A_OAUTH_TOKEN_URL, A2A_OAUTH_SCOPES. Optional: CLIENT_SECRET, REFRESH_URL."
            )
        props["TokenUrl"] = oauth["token_url"]
        props["AuthorizationUrl"] = oauth["authorization_url"]
        if oauth.get("refresh_url"):
            props["RefreshUrl"] = oauth["refresh_url"]
        props["Scopes"] = oauth["scopes"]
        creds: dict = {"ClientId": oauth["client_id"]}
        if oauth.get("client_secret"):
            creds["ClientSecret"] = oauth["client_secret"]
        props["Credentials"] = creds
    elif mode == "none":
        pass
    else:
        raise ValueError(f"Unknown mode: {mode}")
    return {"properties": props}


def a2a_tool_body(project_connection_id: str, base_url: str) -> dict:
    """The `a2a` tool definition body that references the connection.

    Verbatim shape from concepts/agent-to-agent-authentication.md.
    """
    return {
        "type": "a2a",
        "a2a_version": "1.0",
        "base_url": base_url,
        "project_connection_id": project_connection_id,
        # Only true when the endpoint publisher confirmed the card path
        # requires auth. Keep default false in the printed sample.
        "send_credentials_for_agent_card": False,
    }


def arm_connection_url(sub: str, rg: str, account: str, project: str, conn: str) -> str:
    return (
        "https://management.azure.com"
        f"/subscriptions/{sub}/resourceGroups/{rg}"
        f"/providers/Microsoft.CognitiveServices/accounts/{account}"
        f"/projects/{project}/connections/{conn}"
        "?api-version=2025-04-01-preview"
    )


def apply_connection(url: str, body: dict) -> None:
    subprocess.run(
        [
            "az", "rest",
            "--method", "put",
            "--url", url,
            "--resource", "https://management.azure.com",
            "--headers", "Content-Type=application/json",
            "--body", json.dumps(body),
        ],
        check=True,
    )


def main(argv: list[str] | None = None) -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Preflight or create an A2A project connection.")
    parser.add_argument(
        "--mode",
        choices=sorted(AUTH_MODES),
        default=os.getenv("A2A_AUTH_MODE", "").lower() or None,
        help="Which auth mode to print / apply.",
    )
    parser.add_argument("--apply", action="store_true", help="PUT the connection through ARM.")
    parser.add_argument("--connection-name", default=os.getenv("A2A_CONNECTION_NAME", "my-a2a-conn"))
    args = parser.parse_args(argv)

    comparison_table()

    if args.mode is None:
        print()
        print("Pick a mode with --mode {key,entra,project-mi,agentic-id,oauth,none} to see the JSON body.")
        return

    endpoint = os.getenv("PROJECT_ENDPOINT")
    target = os.getenv("A2A_TARGET_AGENT_URL")
    if endpoint:
        try:
            project_endpoint(endpoint)
        except ValueError as exc:
            parser.error(str(exc))
    if not target:
        parser.error("A2A_TARGET_AGENT_URL is required (HTTPS URL of the remote A2A base).")
    target = target_url(target)

    try:
        body = build_body(
            args.mode,
            target,
            key_name=os.getenv("A2A_KEY_NAME"),
            key_value=os.getenv("A2A_KEY_VALUE"),
            audience=os.getenv("A2A_ENTRA_AUDIENCE"),
            oauth={
                "client_id": os.getenv("A2A_OAUTH_CLIENT_ID"),
                "client_secret": os.getenv("A2A_OAUTH_CLIENT_SECRET"),
                "authorization_url": os.getenv("A2A_OAUTH_AUTHORIZATION_URL"),
                "token_url": os.getenv("A2A_OAUTH_TOKEN_URL"),
                "refresh_url": os.getenv("A2A_OAUTH_REFRESH_URL"),
                "scopes": [s for s in (os.getenv("A2A_OAUTH_SCOPES") or "").split() if s] or None,
            } if args.mode == "oauth" else None,
        )
    except ValueError as exc:
        parser.error(str(exc))

    print()
    print(f"Mode: {args.mode} ({AUTH_MODES[args.mode]['authType']})")
    print(f"Connection name: {args.connection_name}")
    print(f"Target: {target}")
    print("Connection PUT body:")
    # Redact secrets when printing.
    redacted = json.loads(json.dumps(body))
    creds = redacted["properties"].get("Credentials") or {}
    if "Keys" in creds:
        creds["Keys"] = {k: "***REDACTED***" for k in creds["Keys"]}
    if "ClientSecret" in creds:
        creds["ClientSecret"] = "***REDACTED***"
    print(json.dumps(redacted, indent=2))

    print()
    print("A2A tool payload that references this connection (once created):")
    print(json.dumps(a2a_tool_body("<connection-id-from-project.connections.get>", target), indent=2))

    if not args.apply:
        print()
        print("Preflight only. Re-run with --apply to create the connection through ARM.")
        return

    sub = os.getenv("AZURE_SUBSCRIPTION_ID")
    rg = os.getenv("AZURE_RESOURCE_GROUP")
    account = os.getenv("FOUNDRY_ACCOUNT_NAME")
    project = os.getenv("FOUNDRY_PROJECT_NAME")
    if not all((sub, rg, account, project)):
        parser.error(
            "--apply requires AZURE_SUBSCRIPTION_ID, AZURE_RESOURCE_GROUP, "
            "FOUNDRY_ACCOUNT_NAME, FOUNDRY_PROJECT_NAME."
        )
    url = arm_connection_url(sub, rg, account, project, args.connection_name)
    print(f"PUT {url}")
    apply_connection(url, body)
    print(f"Created connection: {args.connection_name} (mode={args.mode}).")


if __name__ == "__main__":
    main()
