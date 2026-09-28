# Run: uv run python 08-advanced-agents-other/13_agent_365_preflight.py [--apply]
"""Validate Microsoft 365 (Agent 365) integration prerequisites for a Foundry agent.

Agent 365 lets Foundry hosted agents access Microsoft 365 data — emails, calendar,
Teams messages, SharePoint — through delegated or application permissions. This
requires: (1) an Entra app registration with M365 Graph API permissions, (2) admin
consent granted in the tenant, (3) AGENT_365_CLIENT_ID configured in the hosted
agent's runtime environment.

Default preflight checks env vars and prints what admin consent is needed. --apply
calls the Microsoft Graph to verify the service principal exists and which
Graph permissions have been granted.

Code path:
  preflight: check AGENT_365_CLIENT_ID + AZURE_TENANT_ID, print consent instructions.
  --apply: az rest GET graph.microsoft.com/v1.0/servicePrincipals?$filter=appId eq {id}
  → check oauth2PermissionGrants scopes vs _REQUIRED_PERMISSIONS
  → print PASS/FAIL per permission.

What to watch. All required permissions show PASS before wiring agent to M365.
Missing consent = agent cannot access M365 data at runtime, even with correct credentials.

Prerequisites / env vars:
  AGENT_365_CLIENT_ID  — Entra app registration client ID for M365 access
  AZURE_TENANT_ID      — Entra tenant ID
  --apply              — verify Graph API permissions via az rest
"""
import argparse
import json
import os
import subprocess

from _shared.config import load_env

_REQUIRED_PERMISSIONS = ("Mail.Read", "Calendars.Read", "Sites.ReadWrite.All", "Chat.Read")


def preflight() -> None:
    client_id = os.environ.get("AGENT_365_CLIENT_ID", "")
    tenant_id = os.environ.get("AZURE_TENANT_ID", "")
    print("Agent 365 (M365 integration) preflight (no cloud calls).")
    print(f"- AGENT_365_CLIENT_ID: {'configured' if client_id else 'MISSING'}")
    print(f"- AZURE_TENANT_ID: {'configured' if tenant_id else 'MISSING'}")
    print()
    print("Required Microsoft Graph API permissions (admin consent):")
    for perm in _REQUIRED_PERMISSIONS:
        print(f"  - {perm}")
    print()
    print("Grant consent: Azure Portal → Entra ID → App registrations")
    print("  → {app} → API permissions → Grant admin consent for tenant.")
    print("Set in hosted agent: AGENT_365_CLIENT_ID env var (see lesson 08 pattern).")
    print("Run --apply to verify Graph permissions are granted.")


def apply() -> None:
    client_id = os.environ.get("AGENT_365_CLIENT_ID", "")
    if not client_id:
        raise SystemExit("Set AGENT_365_CLIENT_ID env var.")
    url = (
        f"https://graph.microsoft.com/v1.0/servicePrincipals"
        f"?$filter=appId eq '{client_id}'"
        f"&$select=id,displayName,oauth2PermissionGrants"
    )
    result = subprocess.run(
        ["az", "rest", "--method", "get", "--url", url,
         "--resource", "https://graph.microsoft.com"],
        capture_output=True, text=True, check=True,
    )
    data = json.loads(result.stdout)
    spns = data.get("value", [])
    if not spns:
        print(f"[FAIL] No service principal found for client_id={client_id!r}")
        return
    spn = spns[0]
    print(f"Service principal: {spn.get('displayName')} (id={spn.get('id')})")
    grants = spn.get("oauth2PermissionGrants", [])
    granted: set[str] = set()
    for grant in grants:
        for scope in (grant.get("scope") or "").split():
            granted.add(scope)
    for perm in _REQUIRED_PERMISSIONS:
        status = "PASS" if perm in granted else "FAIL"
        print(f"  [{status}] {perm}")


def main(argv: list[str] | None = None) -> None:
    load_env()
    parser = argparse.ArgumentParser(description="Validate Agent 365 M365 integration prerequisites.")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    if not args.apply:
        preflight()
        return
    apply()


if __name__ == "__main__":
    main()
