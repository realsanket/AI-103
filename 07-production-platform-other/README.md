# Domain 7: Production Foundry platform

Production platform lab for Microsoft Foundry. It provisions one private, keyless regional cell using **one** IaC engine: Bicep **or** Terraform. It uses current `AIServices` resource and project APIs. It contains no Azure ML workspace, hub, classic agent, API key, connection string, model deployment, or stored secret.

The lab is intentionally a platform baseline, not an application deployment. Bring model deployments, agents, Standard Agent Service capability hosts, data schemas, and workload-specific RBAC only after this baseline passes review.

## Numbered local entrypoints

Each numbered entrypoint reads repository assets only and ends with `No cloud calls made.` It accepts no secrets. Only Bicep, Terraform, and policy support `--apply`; that explicit flag invokes persistent Azure changes. CI/CD, diagnostics, and HA/DR remain reviewed local guidance.

| Lab | Asset | Default |
|---|---|---|
| `01_bicep_preflight.py` | Bicep cell | Local asset and control validation |
| `02_terraform_preflight.py` | Terraform cell | Local asset and control validation |
| `03_policy_preflight.py` | Policy definition and assignment | Local Deny-policy validation |
| `04_cicd_preflight.py` | Reference GitHub Actions workflow | Local OIDC/manual-apply validation |
| `05_diagnostics_preflight.py` | Bicep and Terraform diagnostics | Local category validation |
| `06_ha_dr_preflight.py` | HA/DR operating guidance | Local regional-recovery validation |

```bash
python 07-production-platform-other/01_bicep_preflight.py
python 07-production-platform-other/02_terraform_preflight.py
python 07-production-platform-other/03_policy_preflight.py
python 07-production-platform-other/04_cicd_preflight.py
python 07-production-platform-other/05_diagnostics_preflight.py
python 07-production-platform-other/06_ha_dr_preflight.py
```

For a reviewed Bicep deployment, `--apply` still requires `--resource-group`, `--location`, and `--prefix`. Policy also requires an explicit `--allowed-category`; Terraform reads its uncommitted local `terraform.tfvars`. Run `scripts/deploy.py` without `--apply` for its cloud-read-only Bicep what-if or Terraform plan.

## What deploys

```text
VNet
├── private-endpoints subnet
│   ├── Microsoft Foundry account private endpoint
│   ├── Key Vault private endpoint
│   └── Storage Blob private endpoint
└── agent-injection subnet, delegated to Microsoft.App/environments

Foundry account (AIServices) + project
├── user-assigned managed identity
├── public network disabled and local authentication disabled
├── Key Vault CMK
├── Log Analytics diagnostic setting
└── CanNotDelete lock

Key Vault (RBAC, soft delete, purge protection) + RSA CMK
Storage account (GZRS) + private Blob endpoint
Private DNS zones linked to VNet
```

The account endpoint uses three private zones: `privatelink.cognitiveservices.azure.com`, `privatelink.openai.azure.com`, and `privatelink.services.ai.azure.com`. The private endpoint uses group ID `account`. Key Vault and Blob use their own private zones. Private DNS changes only resolve private IPs from linked networks; test them from the VNet, VPN, or ExpressRoute-connected network.

The Bicep and Terraform configurations are alternatives. Do not apply both to the same resource group.

Network injection is created with the account and can't be added or changed later. Recreate a project in a new account to change this decision. The dedicated subnet is delegated to `Microsoft.App/environments`; use RFC 1918 space and size it beyond the `/27` minimum when hosted agents need production headroom.

## Before any Azure change

Use a subscription where selected region supports Foundry, CMK, and required models. CMK requires Key Vault and Foundry in same region. CMK availability is limited by underlying Azure AI Search regional capacity. Enabling CMK on a project is one-way; it can't return to Microsoft-managed keys.

Required control-plane access spans resources:

| Action | Minimum starting access |
|---|---|
| Create cell, VNet, private endpoints, diagnostics, locks | `Contributor`; `Owner` also needed for locks. |
| Link private DNS zones | `Private DNS Zone Contributor`. |
| Grant CMK identity | `Owner` or `User Access Administrator` on Key Vault. |
| Create or assign policy | `Resource Policy Contributor` or `Owner`. |
| Deploy or use project | Assign Foundry and data-plane roles separately, at smallest scope. |

Do not grant broad standing delete rights. Delete locks protect ARM resources, not data-plane deletes. Use a dedicated user-assigned identity per project; recreating a system-assigned identity changes its principal ID and makes recovery slower.

Run offline preflight first. It reads local files only:

```bash
python 07-production-platform-other/scripts/preflight.py --engine bicep
python 07-production-platform-other/scripts/preflight.py --engine terraform
```

Expected final line: `Offline preflight passed; no Azure requests or changes made`.

## Bicep: plan, then apply

Create a resource group first. Replace placeholders with nonsecret identifiers. Never put a key, connection string, token, or SAS URL in parameter files.

```bash
az group create --name <production-resource-group> --location <primary-region>

# Azure read/what-if only. No persistent resource mutation.
python 07-production-platform-other/scripts/deploy.py \
  --engine bicep \
  --resource-group <production-resource-group> \
  --location <primary-region> \
  --prefix <unique-production-prefix>

# Explicit mutation gate.
python 07-production-platform-other/scripts/deploy.py \
  --engine bicep --apply \
  --resource-group <production-resource-group> \
  --location <primary-region> \
  --prefix <unique-production-prefix>
```

`bicep/main.bicep` creates no model deployment. Check Foundry model and quota availability before creating a separate workload deployment. Do not substitute a model family name for a deployment name in applications.

Deploy policy as a separately reviewed subscription deployment. Test categories and scope in nonproduction before this step because `Deny` blocks deployment:

```bash
# What-if
az deployment sub what-if \
  --location <policy-deployment-region> \
  --template-file 07-production-platform-other/bicep/policy.bicep \
  --parameters resourceGroupName=<production-resource-group> \
               allowedCategories='["<approved-category>"]'

# Explicit policy definition and assignment creation.
az deployment sub create \
  --location <policy-deployment-region> \
  --template-file 07-production-platform-other/bicep/policy.bicep \
  --parameters resourceGroupName=<production-resource-group> \
               allowedCategories='["<approved-category>"]'
```

The policy denies only Foundry account and project connection categories not listed in `allowedCategories`. It does not pretend to enforce private endpoint or CMK aliases that must be validated for your tenant before use.

## Terraform: plan, then apply

Terraform state can contain sensitive resource metadata. Use an approved, encrypted remote backend with least-privilege access before team use. Backend configuration is deliberately not hardcoded because organization backends vary.

```bash
cd 07-production-platform-other/terraform
cp terraform.tfvars.example terraform.tfvars
# Edit only identifiers and tags. Keep terraform.tfvars uncommitted.
terraform fmt -check
terraform init
terraform validate
terraform plan
```

Or use same explicit wrapper:

```bash
python 07-production-platform-other/scripts/deploy.py --engine terraform
python 07-production-platform-other/scripts/deploy.py --engine terraform --apply
```

Terraform defaults `assign_connection_policy` to `false`. First create and review definition only. Set it to `true` only after testing an explicit `allowed_connection_categories` list in nonproduction. Never use an empty allow-list in a production assignment unless blocking every new connection is intentional.

## CI/CD

`github/workflows/production-platform.yml` is a contained reference, not an active repository workflow. Copy it to `.github/workflows/` only after:

1. Creating Azure OIDC federated credentials for GitHub Actions.
1. Setting nonsecret repository variables: `AZURE_CLIENT_ID`,
`AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`, `PLATFORM_RESOURCE_GROUP`, `PLATFORM_LOCATION`, and `PLATFORM_PREFIX`.
1. Installing a self-hosted runner labeled `foundry-vnet` inside the private
DNS/VNet path.
1. Configuring approved remote Terraform state if Terraform is selected.

The workflow runs offline preflight, then `what-if` or `terraform plan` by default. An operator must choose `apply: true` in manual dispatch to mutate Azure. OIDC replaces stored Azure credentials. Private endpoints mean a public GitHub-hosted runner can't resolve or reach Foundry, Key Vault, or private ACR data planes.

## Diagnostics and operational checks

The baseline sends `Audit`, `RequestResponse`, `AzureOpenAIRequestUsage`, and `AllMetrics` to Log Analytics. Request/response logs can contain sensitive operational data. Set workspace retention, RBAC, export, and query access to your organization policy. Do not write prompt or completion content to custom application telemetry by default.

After apply, run from a principal and network with appropriate access:

```bash
az cognitiveservices account show \
  --resource-group <production-resource-group> \
  --name <foundry-name> \
  --query '{publicNetworkAccess:properties.publicNetworkAccess,localAuth:properties.disableLocalAuth}' \
  --output json

az network private-endpoint list \
  --resource-group <production-resource-group> \
  --output table

az monitor diagnostic-settings list \
  --resource <foundry-resource-id> \
  --output json

az lock list --resource-group <production-resource-group> --output table
```

From inside linked network, resolve the normal hostname, not a `privatelink` hostname. Confirm it resolves to private IP, then test TCP 443. An approved private endpoint does not grant RBAC. A successful DNS lookup does not prove model, project, Key Vault, Storage, or agent authorization.

## HA and DR lab

Foundry has no automatic failover or disaster recovery. A Foundry project is regional. Treat a regional cell and its project as an independent recovery unit.

1. Deploy reviewed, equivalent cells in two supported regions. Maintain both
configurations from same revision, but use different globally unique Foundry, Key Vault, and Storage names.
1. Keep a documented application traffic switch or gateway failover decision.
This IaC intentionally does not silently redirect production traffic.
1. Deploy required model deployments in each region after capacity and quota
review. Keep endpoint/deployment routing outside client source code.
1. For Standard Agent Service, bring your own Azure Cosmos DB, Azure AI
Search, and Storage resources. Configure Cosmos DB continuous backup and zone-redundant, automatic multi-region failover; configure zone redundancy for Search and GZRS for Storage where supported. Add their private endpoints and zones in each cell. Do not claim this baseline's Blob storage makes Agent Service state replicated.
1. Store agent definitions, tool bindings, index schemas, ingestion manifests,
and infrastructure in source control. Azure AI Search is a derived index, not the authoritative store.
1. Exercise recovery periodically: deploy standby cell, recreate
infrastructure and agents, rebuild indexes from source data, test private DNS/RBAC, move traffic, then record actual RTO/RPO.

Warm standby is reconstruction, not promotion of replicated Foundry project state. Cross-region agent state migration, active-active replication, and thread recovery aren't supported. User-uploaded thread files can be lost. Define a business fallback such as human support before incident day.

The Bicep cell uses GZRS for its Storage account, but GZRS does not automatically fail over a Foundry project storage binding. Select workload recovery topology deliberately; never use a generic storage setting as proof of complete application DR.

## Local references used

- `.context/azure-ai-docs/articles/foundry/how-to/create-resource-template.md`
- `.context/azure-ai-docs/articles/foundry/how-to/create-resource-terraform.md`
- `.context/azure-ai-docs/articles/foundry/how-to/configure-private-link.md`
- `.context/azure-ai-docs/articles/foundry/agents/how-to/virtual-networks.md`
- `.context/azure-ai-docs/articles/foundry/concepts/encryption-keys-portal.md`
- `.context/azure-ai-docs/articles/foundry/how-to/diagnostic-logging.md`
- `.context/azure-ai-docs/articles/foundry/how-to/high-availability-resiliency.md`
- `.context/azure-ai-docs/articles/foundry/how-to/agent-service-disaster-recovery.md`
- `.context/azure-ai-docs/articles/foundry/agents/how-to/set-up-ci-cd-cli.md`
