# Run: uv run python 07-production-platform-other/08_byo_storage_preflight.py [--run]
"""Preflight for Bring-Your-Own Azure Storage binding to a Foundry project.

Foundry projects can be bound to a customer-owned GZRS storage account
instead of the default managed storage. Required for: custom data residency,
customer-managed keys at storage layer, Standard Agent Service capability
hosts (threads, agent state). Default preflight validates env; `--run`
reads current storage endpoint from the project telemetry API.

Binding BYO storage is a creation-time decision for Standard Agent Service.
Existing projects cannot swap storage binding. Plan before deploying.

Prerequisites: storage account RBAC assigned to Foundry project MI (Storage
Blob Data Contributor). Private endpoint on storage if project is in private
VNet (lesson 01 IaC already provisions this). Never commit storage connection
strings — use managed identity, not keys.

Code path:
  preflight(): validate PROJECT_ENDPOINT + STORAGE_ACCOUNT env vars.
  --run: project_client().telemetry.get_application_insights_connection_string()
  to prove project reachability (BYO storage validation requires portal or
  ARM; this proves the project credential works).

What to watch. Preflight: env status. `--run`: App Insights connection string
from project (or None if not configured). Proves Entra auth to project.

Prerequisites / env vars:
  PROJECT_ENDPOINT  — Foundry project HTTPS URL
  STORAGE_ACCOUNT   — storage account name (for preflight check)
  --run             — prove project credential works (read-only)
"""
import argparse
import os

from _shared.config import settings
from _shared.foundry_client import project_client


def preflight() -> None:
    print("BYO storage preflight (no cloud calls).")
    current = settings()
    print(f"- project_endpoint: {'configured' if current.project_endpoint else 'missing'}")
    print(f"- storage_account: {'configured' if os.environ.get('STORAGE_ACCOUNT') else 'missing'}")
    print("- BYO storage binding is a project creation-time decision.")
    print("- Grant Storage Blob Data Contributor to project MI on storage account.")
    print("- Private endpoint on storage required when project VNet is private (lesson 01).")


def run() -> None:
    client = project_client()
    try:
        cs = client.telemetry.get_application_insights_connection_string()
        print(f"Project reachable. App Insights CS: {'configured' if cs else 'not configured'}")
    except Exception as exc:
        print(f"Project credential error: {exc}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="BYO storage binding preflight.")
    parser.add_argument("--run", action="store_true", help="Prove project credential (read-only).")
    args = parser.parse_args(argv)
    if not args.run:
        preflight()
        return
    run()


if __name__ == "__main__":
    main()
