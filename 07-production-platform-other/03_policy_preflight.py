# Run: uv run python 07-production-platform-other/03_policy_preflight.py [--apply --resource-group <rg> --location <region> --allowed-category <cat>]
"""Locally validate policy assets; --apply creates the Deny policy definition + assignment.

Confirms `policy/deny-unapproved-foundry-connections.json` uses effect `Deny`,
the Bicep definition targets subscription scope, and the assignment is at
resource-group scope. Default run makes no cloud call.

`--apply` runs `az deployment sub create` against `bicep/policy.bicep`. This
creates a subscription-scoped policy definition and a resource-group-scoped
assignment. Because effect is `Deny`, any Foundry connection whose category is
not in `--allowed-category` will be REJECTED at deployment time — including
future workload connections. Test the allow-list in nonproduction first.

The policy denies only Foundry account/project connection categories. It does
NOT enforce private endpoint or CMK aliases — validate those for your tenant
before assuming coverage. Repeatable `--allowed-category` builds the list.

Code path:
  Default: `entrypoint_preflight("policy")` reads and parses JSON + Bicep
  templates. Asserts `effect == "Deny"`, `targetScope = 'subscription'`, and
  `policyAssignments` present.
  `--apply`: `az deployment sub create --location <region> --template-file
  bicep/policy.bicep --parameters resourceGroupName=<rg>
  allowedCategories='["<cat>", ...]'`.

What to watch. Preflight: `Policy definition, assignment, and Deny effect
validated locally`. `--apply`: az deployment stream with `provisioningState:
Succeeded`. Rejected downstream deployments surface as `RequestDisallowedByPolicy`.

Prerequisites / env vars:
  --apply                    — permit persistent Azure changes
  --resource-group RG        — target RG for assignment (required with --apply)
  --location REGION          — deployment location (required with --apply)
  --allowed-category CAT     — repeat for each approved category (required with --apply)
"""
from scripts.preflight import entrypoint_main


if __name__ == "__main__":
    entrypoint_main("policy")
