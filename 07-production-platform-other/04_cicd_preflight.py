# Run: uv run python 07-production-platform-other/04_cicd_preflight.py
# Practice-question coverage: Q49, Q89.
"""Locally validate CI/CD reference workflow; no automated apply.

Reads `github/workflows/production-platform.yml` and confirms it uses
`workflow_dispatch:`, defaults manual apply to `false`, runs the offline
preflight step, and authenticates via `azure/login@v2` (OIDC federated
credentials, not stored secrets).

Copying this workflow to `.github/workflows/` is a manual, reviewed step. It
requires four preconditions: (1) Azure OIDC federated credentials for the
GitHub repo, (2) nonsecret repo variables `AZURE_CLIENT_ID`,
`AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`, `PLATFORM_RESOURCE_GROUP`,
`PLATFORM_LOCATION`, `PLATFORM_PREFIX`, (3) a self-hosted runner labelled
`foundry-vnet` inside the private DNS/VNet path (public runners cannot
resolve private endpoints), (4) approved remote Terraform state if the
Terraform path is selected.

No `--apply` mode. Copying the workflow is an intentional out-of-band action.

Code path:
  `entrypoint_preflight("cicd")` reads workflow YAML, greps for required
  markers, prints `Reference workflow keeps manual apply disabled and uses
  OIDC variables`.

What to watch. Preflight only. Any missing marker fails with the list of
absent strings — fix workflow before copying.

Prerequisites / env vars:
  none — local read-only check
"""
from scripts.preflight import entrypoint_main


if __name__ == "__main__":
    entrypoint_main("cicd")
