# Run: uv run python 01-plan-and-manage/27_control_plane_fleet_inventory.py [--apply]
"""Read Foundry accounts + deployments across a subscription for Control Plane fleet view.

Foundry Control Plane (Operate → Assets in portal) shows agents, models, and
tools across all Foundry accounts in a subscription. There's no dedicated
Control Plane SDK — the underlying data comes from
`CognitiveServicesManagementClient` iterating accounts + deployments.

This lab reproduces the "fleet inventory" view read-only. Default preflight
validates env; `--apply` calls `.accounts.list_by_subscription()` then per
account `.deployments.list()`. Prints one row per (account, deployment).

Caller needs subscription `Reader` or `Cognitive Services Usages Reader`.
Portal Control Plane also merges Application Insights runs/cost data — this
CLI view intentionally shows only static inventory (no telemetry join).

Code path:
  --apply: CognitiveServicesManagementClient(cred, sub).accounts
  .list_by_subscription() → for each Foundry-kind account: .deployments.list
  (rg, name) → print (account, region, deployment, model, sku, capacity).

What to watch. Preflight: env status. `--apply`: table of every Foundry
deployment in the subscription. Missing account = missing role at that
resource. Empty rows = the account has no deployments yet.

Prerequisites / env vars:
  AZURE_SUBSCRIPTION_ID  — target subscription
  --apply                — perform control-plane read
"""
import argparse

from azure.identity import DefaultAzureCredential
from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient

from _shared.config import settings


def preflight() -> None:
    print("Control Plane fleet inventory preflight (no cloud calls).")
    current = settings()
    print(f"- subscription: {'configured' if current.azure_subscription_id else 'missing'}")
    print("- --apply reads accounts + deployments subscription-wide (read-only).")


def apply() -> None:
    sub = settings().require("AZURE_SUBSCRIPTION_ID")
    client = CognitiveServicesManagementClient(DefaultAzureCredential(), sub)
    print(f"{'account':<30} {'region':<15} {'deployment':<28} {'model':<28} {'sku':<18} {'cap':>4}")
    print("-" * 125)
    for account in client.accounts.list_by_subscription():
        if not account.kind or account.kind not in ("AIServices", "OpenAI"):
            continue
        rg = account.id.split("/resourceGroups/")[1].split("/")[0]
        for d in client.deployments.list(rg, account.name):
            model = getattr(getattr(d.properties, "model", None), "name", "?") if d.properties else "?"
            sku = d.sku.name if d.sku else "?"
            cap = d.sku.capacity if d.sku else 0
            print(f"{account.name:<30} {account.location:<15} {d.name:<28} {model:<28} {sku:<18} {cap:>4}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Read Control Plane fleet inventory.")
    parser.add_argument("--apply", action="store_true", help="Perform subscription-wide read.")
    args = parser.parse_args(argv)
    if not args.apply:
        preflight()
        return
    apply()


if __name__ == "__main__":
    main()
