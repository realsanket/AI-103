# Run: uv run python 07-production-platform-other/09_dr_verify_preflight.py [--run --region <secondary-region>]
"""DR verification preflight: check Foundry account exists in a second region.

Lesson 06 validates the HA/DR guidance in the README. This lesson goes one
step further: reads the management plane to confirm both primary and a named
secondary Foundry account actually exist, comparing their kinds + locations.
Proves "warm standby infrastructure is deployed" not just documented.

Default preflight validates env; `--run` lists all Foundry accounts in the
subscription and flags which ones match the primary account's kind and are
in the requested secondary region.

Recovery exercise is still manual: deploy agents, rebuild indexes, switch
traffic. This lesson only proves the IaC has run in both regions.

Code path:
  --run: CognitiveServicesManagementClient.accounts.list_by_subscription()
  → filter kind == primary kind + location == secondary region → print.

What to watch. Preflight: env status. `--run`: one or more accounts in the
secondary region with same kind as primary. Zero rows = standby cell not
deployed yet.

Prerequisites / env vars:
  AZURE_SUBSCRIPTION_ID  — subscription to scan
  FOUNDRY_ENDPOINT       — used to derive primary account name + kind
  --region REGION        — secondary Azure region to verify (e.g., westus2)
  --run                  — perform read-only scan
"""
import argparse

from azure.identity import DefaultAzureCredential
from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient

from _shared.config import settings
from _shared.foundry_management import foundry_account_name


def preflight() -> None:
    current = settings()
    print("DR verification preflight (no cloud calls).")
    print(f"- subscription: {'configured' if current.azure_subscription_id else 'missing'}")
    print(f"- foundry_endpoint: {'configured' if current.foundry_endpoint else 'missing'}")
    print("- --run --region <region> lists Foundry accounts in that secondary region.")
    print("- Zero results means standby cell not yet deployed.")


def run(secondary_region: str) -> None:
    current = settings()
    sub = current.require("AZURE_SUBSCRIPTION_ID")
    client = CognitiveServicesManagementClient(DefaultAzureCredential(), sub)
    primary_name = foundry_account_name(current.require("FOUNDRY_ENDPOINT"))
    primary_kind = None
    results = []
    for account in client.accounts.list_by_subscription():
        if account.name == primary_name:
            primary_kind = account.kind
        if account.location and account.location.replace(" ", "").lower() == secondary_region.lower():
            results.append(account)
    if primary_kind is None:
        print(f"Primary account '{primary_name}' not found in subscription.")
        return
    secondary = [a for a in results if a.kind == primary_kind]
    print(f"Primary: {primary_name} (kind={primary_kind})")
    if not secondary:
        print(f"No {primary_kind} accounts found in region '{secondary_region}'. Deploy standby cell.")
        return
    for a in secondary:
        print(f"Standby account found: {a.name} kind={a.kind} location={a.location}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Verify DR standby Foundry account exists.")
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--region", default="", help="Secondary Azure region name.")
    args = parser.parse_args(argv)
    if not args.run:
        preflight()
        return
    if not args.region:
        parser.error("--run requires --region.")
    run(args.region)


if __name__ == "__main__":
    main()
