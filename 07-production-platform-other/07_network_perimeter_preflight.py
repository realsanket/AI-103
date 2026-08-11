# Run: uv run python 07-production-platform-other/07_network_perimeter_preflight.py [--apply --resource-id <arm-id>]
"""Preflight and read Network Security Perimeter (NSP) association for Foundry resource.

Azure Network Security Perimeter (NSP) adds another network boundary around
PaaS resources: explicit access rules for inbound/outbound. Foundry resources
can be added to an NSP after the private-cell baseline (lesson 01) is
deployed. NSP + private endpoint together achieve full network isolation.

Default preflight explains NSP vs private endpoint distinction. `--apply`
calls `az rest` to read current NSP profile associations for the named
Foundry resource ARM ID (read-only).

NSP is distinct from private endpoint: PE controls inbound IP routing;
NSP adds identity-based inbound/outbound rules. Both can coexist.

Code path:
  --apply: `az rest --method get --url
  https://management.azure.com/<resource-id>/networkSecurityPerimeterConfigurations
  ?api-version=2023-08-01-preview` → print JSON profiles.

What to watch. Preflight: concept summary. `--apply`: JSON list of
NSP profile associations. Empty = resource not associated with any NSP.
`provisioningState: Succeeded` = association active.

Prerequisites / env vars:
  --resource-id ARM-ID  — full Foundry account ARM ID (required with --apply)
  --apply               — read-only NSP association check
"""
import argparse
import subprocess
import json


def preflight() -> None:
    print("NSP preflight (no cloud calls).")
    print("- Private endpoint: controls inbound IP routing to resource.")
    print("- NSP: adds identity-based inbound/outbound access rules.")
    print("- Both can coexist; NSP applies on top of PE for full network isolation.")
    print("- Portal: Networking → Network Security Perimeter on the Foundry resource.")


def apply(resource_id: str) -> None:
    url = (
        f"https://management.azure.com{resource_id}"
        f"/networkSecurityPerimeterConfigurations?api-version=2023-08-01-preview"
    )
    result = subprocess.run(
        ["az", "rest", "--method", "get", "--url", url],
        capture_output=True, text=True, check=True,
    )
    data = json.loads(result.stdout)
    profiles = data.get("value", [])
    if not profiles:
        print("No NSP associations found for this resource.")
        return
    for p in profiles:
        name = p.get("name", "?")
        state = p.get("properties", {}).get("provisioningState", "?")
        print(f"Profile: {name}  state: {state}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Read NSP association for a Foundry resource.")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--resource-id", help="Full Foundry account ARM resource ID.")
    args = parser.parse_args(argv)
    if not args.apply:
        preflight()
        return
    if not args.resource_id:
        parser.error("--apply requires --resource-id.")
    apply(args.resource_id)


if __name__ == "__main__":
    main()
