# Run: uv run python 07-production-platform-other/01_bicep_preflight.py [--apply --resource-group <rg> --location <region> --prefix <prefix>]
# Practice-question coverage: Q129.
"""Locally validate Bicep platform assets; --apply provisions the private Foundry cell.

Default run reads `bicep/main.bicep`, `bicep/main.bicepparam`, and the policy
JSON. Confirms required control markers are present: `publicNetworkAccess:
'Disabled'`, `enablePurgeProtection: true`, `Key Vault Crypto User`,
`privateDnsZones`, `networkInjections`, `diagnosticSettings`, `CanNotDelete`.
Never touches Azure without `--apply`.

`--apply` invokes `scripts/deploy.py --engine bicep --apply` which runs
`az deployment group create` against the named resource group. This mutates
Azure state and can incur cost immediately (Log Analytics, Storage, Key Vault,
private endpoints, Foundry account/project). The delete-lock is added by the
template itself — subsequent teardown needs an explicit lock removal.

Network injection is created with the account and cannot be added or changed
later. Choose subnet delegation to `Microsoft.App/environments` deliberately.
CMK on a project is one-way: cannot return to Microsoft-managed keys.

Code path:
  Default: `entrypoint_main("bicep")` → validates asset presence + control
  markers via `entrypoint_preflight("bicep")`. Prints results and exits.
  `--apply`: subprocess `deploy.py --engine bicep --apply --resource-group
  <rg> --location <region> --prefix <prefix> --project-name <project>`.

What to watch. Preflight: `bicep: N required assets found`, control-marker
confirmations, and `Offline preflight passed; no Azure requests or changes
made`. `--apply`: `+` command line printed then Azure deployment stream.

Prerequisites / env vars:
  --apply              — permit persistent Azure changes
  --resource-group RG  — target RG (required with --apply)
  --location REGION    — Azure region (required with --apply)
  --prefix STR         — unique naming prefix (required with --apply)
  --project-name STR   — Foundry project name (default: production)
"""
from scripts.preflight import entrypoint_main


if __name__ == "__main__":
    entrypoint_main("bicep")
