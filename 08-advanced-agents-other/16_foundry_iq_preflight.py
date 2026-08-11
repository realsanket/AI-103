# Run: uv run python 08-advanced-agents-other/16_foundry_iq_preflight.py [--apply]
"""Validate Foundry IQ (enterprise knowledge) connection for a hosted agent.

Foundry IQ connects Foundry agents to enterprise data sources — SharePoint,
OneDrive, Teams, ServiceNow — through a curated knowledge index. The agent
uses the IQ connection to answer questions grounded in live organizational
data without the user uploading files. Access is governed by existing M365
permissions: the agent sees only what the requesting user can see.

Default preflight checks required env vars and explains the IQ data flow.
--apply verifies the named IQ connection is present in the project and readable.

Code path:
  preflight: check PROJECT_ENDPOINT + FOUNDRY_IQ_CONNECTION_NAME.
  --apply: project_client().connections.get(FOUNDRY_IQ_CONNECTION_NAME)
  → print connection_type, target endpoint, PASS/FAIL.

What to watch. connection_type contains "FoundryIQ" or "AzureAISearch".
Status reachable = IQ index live and credentials valid. Not found = wrong
connection name or IQ not provisioned for this project.

Prerequisites / env vars:
  PROJECT_ENDPOINT              — Foundry project HTTPS URL
  FOUNDRY_IQ_CONNECTION_NAME    — name of the Foundry IQ project connection
  --apply                       — verify IQ connection is reachable
"""
import argparse
import os

from _shared.config import settings
from _shared.foundry_client import project_client


def preflight() -> None:
    current = settings()
    iq_conn = os.environ.get("FOUNDRY_IQ_CONNECTION_NAME", "")
    print("Foundry IQ preflight (no cloud calls).")
    print(f"- PROJECT_ENDPOINT: {'configured' if current.project_endpoint else 'missing'}")
    print(f"- FOUNDRY_IQ_CONNECTION_NAME: {iq_conn or 'MISSING'}")
    print()
    print("Foundry IQ data flow:")
    print("  User query → Foundry agent → IQ knowledge index")
    print("  (SharePoint / OneDrive / Teams / ServiceNow)")
    print("  → grounded answer scoped to user's M365 permissions.")
    print("Set up: Foundry portal → Project → Connections → Add → Foundry IQ.")
    print("Run --apply to verify the IQ connection is reachable.")


def apply() -> None:
    iq_conn = os.environ.get("FOUNDRY_IQ_CONNECTION_NAME", "")
    if not iq_conn:
        raise SystemExit("Set FOUNDRY_IQ_CONNECTION_NAME env var.")
    client = project_client()
    try:
        conn = client.connections.get(iq_conn)
        ctype = getattr(conn, "connection_type", "?")
        endpoint = str(getattr(conn, "target", "") or "")
        print(f"Foundry IQ connection: {iq_conn}")
        print(f"  type:     {ctype}")
        print(f"  endpoint: {endpoint[:80]}")
        print("  [PASS] IQ connection found and readable.")
    except Exception as exc:
        print(f"  [FAIL] Could not retrieve connection '{iq_conn}': {exc}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Verify Foundry IQ enterprise knowledge connection.")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    if not args.apply:
        preflight()
        return
    apply()


if __name__ == "__main__":
    main()
