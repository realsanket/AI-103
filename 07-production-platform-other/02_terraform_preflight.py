# Run: uv run python 07-production-platform-other/02_terraform_preflight.py [--apply]
"""Locally validate Terraform platform assets; --apply provisions the private Foundry cell.

Terraform alternative to lesson 01. Default validates `terraform/main.tf`,
`variables.tf`, `outputs.tf`, `terraform.tfvars.example`, and the policy JSON,
plus the same Bicep control markers (baseline is the authoritative reference).
Do NOT apply both Bicep and Terraform to the same resource group.

Terraform state contains sensitive resource metadata. Configure an approved
encrypted remote backend with least-privilege access before team use. Backend
config is intentionally not hardcoded — organizations differ. Local
`terraform.tfvars` must stay uncommitted.

`--apply` runs `terraform plan` first, then `terraform apply` on approval. It
mutates Azure state and can incur cost immediately. `assign_connection_policy`
defaults to `false` — set to `true` only after testing an explicit
`allowed_connection_categories` list in nonproduction.

Code path:
  Default: `entrypoint_main("terraform")` validates asset presence + control
  markers. `--apply`: subprocess `deploy.py --engine terraform --apply` which
  reads `terraform.tfvars` and runs plan then apply.

What to watch. Preflight: `terraform: N required assets found`, control-marker
confirmations, and `Offline preflight passed`. `--apply`: terraform plan
output then apply stream.

Prerequisites / env vars:
  terraform.tfvars     — uncommitted per-env values file (required for --apply)
  approved backend     — remote state configured before team use
  --apply              — permit persistent Azure changes
"""
from scripts.preflight import entrypoint_main


if __name__ == "__main__":
    entrypoint_main("terraform")
