# Domain 7: Production Foundry platform

> IaC-first labs for provisioning a private, keyless Foundry cell (Bicep OR Terraform), governance policy, CI/CD, diagnostics, and HA/DR. Run commands from repository root: `uv run python 07-production-platform-other/<lesson>.py`.
>
> Every lab defaults to a local read-only preflight and ends with `No cloud calls made.` Only lessons 01, 02, and 03 accept `--apply`; those explicitly mutate Azure. CI/CD, diagnostics, and HA/DR are reviewed-only guidance validators — they never touch Azure.

## What this domain teaches

A production Foundry deployment is a platform artifact chain, not a runtime script:

```text
Reviewed IaC (Bicep XOR Terraform) with policy + diagnostics + locks
        ↓
Offline preflight (asset presence + control markers) in CI
        ↓
Subscription policy: Deny unapproved Foundry connection categories
        ↓
Manual --apply of one regional cell (VNet, PEs, DNS, KV, Storage, Foundry)
        ↓
Verify: publicNetworkAccess Disabled, localAuth Disabled, PE resolves privately, RBAC assigned
        ↓
CI/CD reference workflow: OIDC + self-hosted runner in VNet + manual dispatch
        ↓
HA/DR: two independent regional cells + tested traffic switch (no auto-failover)
```

Lessons follow this chain in five stages. They do NOT provision model deployments, agents, Agent Service capability hosts, data schemas, or workload-specific RBAC. Those come after this baseline passes review.

## Foundry platform mental model

### One private regional cell

```text
VNet
├── private-endpoints subnet
│   ├── Microsoft Foundry account PE (group: account)
│   ├── Key Vault PE
│   └── Storage Blob PE
└── agent-injection subnet (delegated to Microsoft.App/environments)

Foundry account (AIServices) + project
├── user-assigned managed identity
├── publicNetworkAccess: Disabled
├── disableLocalAuth: true (Entra-only)
├── Key Vault CMK (RSA)
├── Log Analytics diagnostic setting (Audit, RequestResponse, AzureOpenAIRequestUsage, AllMetrics)
└── CanNotDelete lock

Key Vault: RBAC auth, soft delete, purge protection
Storage: GZRS with Blob PE
Private DNS zones linked to VNet:
  - privatelink.cognitiveservices.azure.com
  - privatelink.openai.azure.com
  - privatelink.services.ai.azure.com
  - Key Vault + Blob zones
```

### One-way decisions

| Decision | Locked in when | Consequence |
|---|---|---|
| Network injection | Account creation | Cannot change; recreate project in new account |
| Delegated subnet | Cell creation | Must be sized beyond `/27` for hosted-agent headroom |
| CMK on project | First enable | One-way — cannot return to Microsoft-managed |
| Region | Cell creation | Foundry, KV, Search regional capacity must all align |
| Foundry account name | Creation | Globally unique; used in FQDN forever |

### Two IaC engines, choose one per cell

| Engine | Best for | Trade-off |
|---|---|---|
| Bicep | Azure-only shops, ARM-native declarations | State stays in Azure Resource Graph; no separate backend |
| Terraform | Multi-cloud, existing HCL practice | Requires encrypted remote backend + state management |

Do NOT apply both to the same resource group.

### Control-plane roles

| Action | Minimum role |
|---|---|
| Create cell, VNet, PEs, diagnostics, locks | `Contributor` (+ `Owner` for locks) |
| Link private DNS zones | `Private DNS Zone Contributor` |
| Grant CMK identity access | `Owner` or `User Access Administrator` on Key Vault |
| Create/assign policy | `Resource Policy Contributor` or `Owner` |
| Deploy/use project | Foundry + data-plane roles assigned separately at smallest scope |

## Glossary

| Term | Definition |
|---|---|
| **Foundry cell** | One regional deployment: VNet + PEs + KV + Storage + Foundry account + project |
| **AIServices** | Modern Foundry account resource type (not `OpenAI` classic; not ML workspace) |
| **Network injection** | Delegates a VNet subnet to `Microsoft.App/environments` for hosted agents. Immutable after account creation |
| **Private endpoint (PE)** | NIC in your VNet providing a private IP for an Azure service; disables public access when combined with `publicNetworkAccess: Disabled` |
| **Private DNS zone** | Zone linked to VNet that resolves service FQDN to private IP; three zones for Foundry (`cognitiveservices`, `openai`, `services.ai`) |
| **CMK** | Customer-Managed Key: your RSA key in Key Vault encrypts service data at rest; one-way for Foundry projects |
| **User-assigned MI** | Managed identity resource with stable principal ID; survives resource recreation. Preferred over system-assigned for recovery |
| **GZRS** | Geo-Zone-Redundant Storage: zone redundancy in primary region + async copy to secondary. Not automatic Foundry DR |
| **Delete lock** | ARM `CanNotDelete` lock protecting resources from `DELETE`. Does NOT block data-plane deletes |
| **Deny policy** | Azure Policy with `effect: Deny` that rejects noncompliant deployments before they hit the resource provider |
| **Warm standby** | DR pattern: second cell exists but is not serving traffic; reconstruction on failover |
| **RTO / RPO** | Recovery Time Objective / Recovery Point Objective — measure recovery, not marketed durability |
| **workflow_dispatch** | GitHub Actions manual trigger; the reference workflow uses it with `apply: false` default |
| **OIDC federated credential** | Federated identity for GitHub Actions → Azure — replaces stored client secret |

## Setup

### Environment variables

No `.env` required for preflight lessons. `--apply` reads flags directly:

```bash
uv sync
az login   # your identity needs Contributor + Private DNS Zone Contributor + KV UAA for --apply
```

For CI/CD (lesson 04), the reference workflow expects these repo variables (NOT secrets):

```text
AZURE_CLIENT_ID          — GitHub OIDC federated credential app registration
AZURE_TENANT_ID          — Entra tenant
AZURE_SUBSCRIPTION_ID    — target subscription
PLATFORM_RESOURCE_GROUP  — target resource group name
PLATFORM_LOCATION        — Azure region
PLATFORM_PREFIX          — unique naming prefix
```

### Safe run order

1. **04, 05, 06** first — pure read-only guidance validators. No cloud, no cost.
2. **01** or **02** (choose ONE engine) as preflight — validates all templates locally.
3. **03** as preflight — validates Deny policy definition + assignment templates.
4. **01 --apply** or **02 --apply** in nonproduction — provisions one cell.
5. Verify: `az cognitiveservices account show`, `az network private-endpoint list`, `az monitor diagnostic-settings list`, `az lock list`.
6. **03 --apply** with a tested `--allowed-category` list in nonproduction FIRST.
7. Copy `github/workflows/production-platform.yml` to `.github/workflows/` only after OIDC + self-hosted runner in VNet path are in place.
8. **06 --apply** conceptually: deploy second cell (repeat 01/02 in a different region with a different prefix).

### Costs and side effects

| Lesson(s) | Side effect or cost |
|---|---|
| 04, 05, 06 | Local read-only. Never mutates Azure. |
| 01, 02 preflight | Local read-only. |
| 03 preflight | Local read-only. |
| 01 --apply | Deploys full cell: Foundry account + project + KV + Storage GZRS + VNet + 3+ PEs + private DNS + Log Analytics diag + delete lock. Hourly costs begin immediately. |
| 02 --apply | Same cell via Terraform. Do NOT combine with Bicep in same RG. |
| 03 --apply | Creates subscription-scoped Deny policy + RG-scoped assignment. REJECTS unapproved-category connections at deploy time — test first. |

Foundry cell hourly cost includes: Log Analytics ingestion + retention, Storage GZRS, KV standard tier, private endpoints (per hour + per GB processed), private DNS zones, VNet base. Add model deployments separately.

## Decision tables

### Bicep vs Terraform

| Signal | Choose |
|---|---|
| Azure-only tenant, no multi-cloud | Bicep |
| Existing Terraform practice + remote state backend | Terraform |
| Portal-first team learning IaC | Bicep (fewer moving parts) |
| Need policy + management-group + subscription deployments | Bicep (native `targetScope`) |
| Cross-cloud consistency needed | Terraform |

### Private connectivity: what really works

```text
publicNetworkAccess: Disabled
  ↓
Private endpoint in VNet (group: account)
  ↓
Private DNS zones linked to VNet
  ↓
Zones: cognitiveservices.azure.com, openai.azure.com, services.ai.azure.com
  ↓
Resolve <resource>.services.ai.azure.com from VNet → private IP → TCP 443
```

Client outside VNet cannot resolve or reach the private endpoint. GitHub-hosted runners are outside — use self-hosted runners on the VNet.

### HA/DR pattern

| Signal | Pattern |
|---|---|
| Regional outage tolerance = zero | Two cells in two supported regions, tested traffic switch |
| Automatic failover expected | Not supported by Foundry — pattern is warm standby reconstruction |
| Cross-region agent state migration | Not supported — recreate agents from source in target region |
| Storage of thread files | User-uploaded thread files can be lost; define business fallback |

## Lesson map

| # | Lesson | Runnable objective | Status / limitation |
|---:|---|---|---|
| 01 | [Bicep preflight](01_bicep_preflight.py) | Validate Bicep cell assets + control markers | `--apply` provisions one cell (persistent + billable) |
| 02 | [Terraform preflight](02_terraform_preflight.py) | Validate Terraform cell assets + control markers | `--apply` provisions one cell; requires remote backend + local tfvars |
| 03 | [Policy preflight](03_policy_preflight.py) | Validate Deny-policy definition + assignment | `--apply` creates sub-scoped policy + RG-scoped assignment |
| 04 | [CI/CD preflight](04_cicd_preflight.py) | Validate reference GitHub workflow markers | Local only; copy workflow is manual reviewed step |
| 05 | [Diagnostics preflight](05_diagnostics_preflight.py) | Validate Bicep + Terraform diagnostic categories | Local only; setting provisioned by lesson 01/02 |
| 06 | [HA/DR preflight](06_ha_dr_preflight.py) | Validate README HA/DR guidance markers | Local only; second cell provisioned by re-running 01/02 |

---

## Stage 1 — IaC baseline (lessons 01–02)

Lesson 01 and 02 are alternatives, not steps. Pick the engine your organization already uses. Both deploy the same private-endpoint cell with the same control markers; the offline preflight for both greps `bicep/main.bicep` as the authoritative reference.

### 01 — Bicep private cell

**Question answered:** How do I provision one private, keyless Foundry cell via Bicep?

**Background.** Bicep is Azure-native, no separate state backend. `main.bicep` + `main.bicepparam` create VNet + PE subnet + agent-injection subnet + Foundry account with public access disabled + project + Key Vault with RBAC + Storage GZRS + Log Analytics diagnostic setting + `CanNotDelete` lock. `main.bicep` creates NO model deployment — bring that later after quota review.

**Before code.** Region must support Foundry, CMK, and required models (Foundry + KV + Search regional capacity all matter). Caller needs `Contributor` + `Owner` (for locks) + `Private DNS Zone Contributor` + `Owner`/`User Access Administrator` on KV for CMK identity grant. Create the resource group first: `az group create --name <rg> --location <region>`.

```bash
# Preflight (local read-only)
uv run python 07-production-platform-other/01_bicep_preflight.py

# What-if via wrapper (Azure read-only)
python 07-production-platform-other/scripts/deploy.py --engine bicep \
  --resource-group <rg> --location <region> --prefix <prefix>

# Apply (persistent + billable)
uv run python 07-production-platform-other/01_bicep_preflight.py --apply \
  --resource-group <rg> --location <region> --prefix <prefix>
```

**Code path.**
1. `entrypoint_preflight("bicep")` — validates `bicep/main.bicep`, `main.bicepparam`, `policy/deny-unapproved-foundry-connections.json` all present.
2. Grep `main.bicep` for control markers: `publicNetworkAccess: 'Disabled'`, `enablePurgeProtection: true`, `Key Vault Crypto User`, `privateDnsZones`, `networkInjections`, `diagnosticSettings`, `CanNotDelete`.
3. `--apply` shells out to `scripts/deploy.py --engine bicep --apply ...` which runs `az deployment group create`.

**What to watch.** Preflight: `bicep: N required assets found`, `Offline preflight passed`. `--apply`: az deployment stream with `provisioningState: Succeeded` per resource.

**One-way decisions.**
- `networkInjections` (agent-injection subnet delegation) is fixed at account creation.
- CMK on project cannot revert to Microsoft-managed keys.
- Account + KV + Storage names are globally unique — pick a stable prefix.

**References:** [Create resource template (Bicep)](https://learn.microsoft.com/azure/foundry/how-to/create-resource-template) · [Configure Private Link](https://learn.microsoft.com/azure/foundry/how-to/configure-private-link) · [Agent virtual networks](https://learn.microsoft.com/azure/foundry/agents/how-to/virtual-networks) · [Encryption keys](https://learn.microsoft.com/azure/foundry/concepts/encryption-keys-portal)

### 02 — Terraform private cell

**Question answered:** How do I provision the same cell via Terraform, and what does state management require?

**Background.** Terraform alternative. Same resource shape, same control markers. State contains sensitive resource metadata — configure an approved encrypted remote backend with least-privilege access BEFORE team use. Backend config is intentionally not hardcoded because organizations differ.

**Before code.** Copy `terraform/terraform.tfvars.example` → `terraform/terraform.tfvars` and fill identifiers. Keep `terraform.tfvars` uncommitted (`.gitignore` entry required). Configure remote backend outside the repo.

```bash
# Preflight (local read-only)
uv run python 07-production-platform-other/02_terraform_preflight.py

# Manual plan
cd 07-production-platform-other/terraform
terraform fmt -check && terraform init && terraform validate && terraform plan

# Apply via wrapper
uv run python 07-production-platform-other/02_terraform_preflight.py --apply
```

**Code path.**
1. `entrypoint_preflight("terraform")` validates `main.tf`, `variables.tf`, `outputs.tf`, `terraform.tfvars.example`, policy JSON present + Bicep control markers (baseline reference).
2. `--apply` → `deploy.py --engine terraform --apply` runs `terraform plan` then `terraform apply`.

**What to watch.** Preflight: `terraform: N required assets found`. `--apply`: terraform plan output → apply confirmation → per-resource create stream.

**Terraform-specific rules.**
- `assign_connection_policy` defaults to `false`. Only set `true` after testing explicit `allowed_connection_categories` list in nonproduction.
- Never use empty allow-list in production assignment unless blocking every new connection is intentional.
- Do NOT apply Terraform + Bicep to same RG — they will fight over resource IDs.

**References:** [Create resource template (Terraform)](https://learn.microsoft.com/azure/foundry/how-to/create-resource-terraform) · [Configure Private Link](https://learn.microsoft.com/azure/foundry/how-to/configure-private-link)

---

## Stage 2 — Governance policy (lesson 03)

Guardrails at the Azure Resource Manager layer. Deny policies block noncompliant deployments before they reach the resource provider — a stronger control than after-the-fact audit.

### 03 — Deny unapproved Foundry connections

**Question answered:** How do I prevent creation of Foundry connection categories the organization has not approved?

**Background.** A Foundry connection wires the project to external services (Storage, KV, search indexes, model providers). Uncontrolled connections leak data or credentials. This policy uses effect `Deny` — every future Foundry connection creation is checked against the allow-list; noncompliant deployments are REJECTED with `RequestDisallowedByPolicy`.

**Before code.** Test the `--allowed-category` list in NONPRODUCTION first. `Deny` blocks legitimate deployments if the allow-list is wrong. Caller needs `Resource Policy Contributor` or `Owner` at subscription scope.

```bash
# Preflight (local read-only)
uv run python 07-production-platform-other/03_policy_preflight.py

# What-if
az deployment sub what-if --location <region> \
  --template-file 07-production-platform-other/bicep/policy.bicep \
  --parameters resourceGroupName=<rg> \
               allowedCategories='["<approved-category>"]'

# Apply — creates definition (sub scope) + assignment (RG scope)
uv run python 07-production-platform-other/03_policy_preflight.py --apply \
  --resource-group <rg> --location <region> \
  --allowed-category <cat1> --allowed-category <cat2>
```

**Code path.**
1. `entrypoint_preflight("policy")` parses `deny-unapproved-foundry-connections.json`; asserts `policyRule.then.effect == "Deny"`.
2. Reads `bicep/policy.bicep` and `bicep/policy-assignment.bicep`; asserts `targetScope = 'subscription'` and `policyAssignments` present.
3. `--apply` runs `az deployment sub create` with the assembled `allowedCategories` JSON array.

**What to watch.** Preflight: `Policy definition, assignment, and Deny effect validated locally`. `--apply`: `provisioningState: Succeeded`. Rejected future deployments surface as `RequestDisallowedByPolicy`.

**Scope discipline.**
- Definition at subscription; assignment at RG. This lets multiple RGs opt in with different allow-lists.
- Policy denies ONLY connection categories — does NOT enforce private endpoint or CMK aliases. Validate those aliases for your tenant separately.
- Repeatable `--allowed-category` builds the list.

**References:** [Configure Private Link](https://learn.microsoft.com/azure/foundry/how-to/configure-private-link) · [Encryption keys](https://learn.microsoft.com/azure/foundry/concepts/encryption-keys-portal)

---

## Stage 3 — CI/CD (lesson 04)

Copying the reference workflow is a manual reviewed step. This lab validates the workflow file locally — it never touches Azure or the `.github/workflows/` directory.

### 04 — Reference GitHub Actions workflow

**Question answered:** Does the reference CI/CD workflow satisfy the four operational preconditions?

**Background.** The workflow at `github/workflows/production-platform.yml` uses `workflow_dispatch:` with `apply: false` default. On dispatch it runs offline preflight, then `az deployment group what-if` (Bicep) or `terraform plan` (Terraform). Only when an operator explicitly chooses `apply: true` does it mutate Azure. OIDC federated credentials replace stored client secrets.

```bash
uv run python 07-production-platform-other/04_cicd_preflight.py
```

**Code path.**
1. `entrypoint_preflight("cicd")` reads the workflow YAML.
2. Greps for `workflow_dispatch:`, `default: false`, `Offline preflight`, `azure/login@v2`.
3. Prints `Reference workflow keeps manual apply disabled and uses OIDC variables`.

**What to watch.** Preflight only. Any missing marker fails with the list of absent strings.

**Before copying to `.github/workflows/`.**
1. Create Azure OIDC federated credentials for the GitHub repo (per-branch or per-environment).
2. Set nonsecret repo variables: `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`, `PLATFORM_RESOURCE_GROUP`, `PLATFORM_LOCATION`, `PLATFORM_PREFIX`.
3. Install self-hosted runner labelled `foundry-vnet` inside the VNet — GitHub-hosted runners cannot resolve private endpoints.
4. Configure approved remote Terraform state if the Terraform path is selected.

**References:** [Set up CI/CD](https://learn.microsoft.com/azure/foundry/agents/how-to/set-up-ci-cd-cli) · [Configure Private Link](https://learn.microsoft.com/azure/foundry/how-to/configure-private-link)

---

## Stage 4 — Diagnostics (lesson 05)

Diagnostic settings are provisioned by lesson 01/02 `--apply`. This lab validates that both templates configure the same reviewed categories, so no engine choice silently drops signal.

### 05 — Diagnostic categories reviewed

**Question answered:** Do Bicep and Terraform both configure the four reviewed diagnostic categories?

**Background.** Baseline routes `Audit`, `RequestResponse`, `AzureOpenAIRequestUsage`, and `AllMetrics` to Log Analytics. `RequestResponse` can contain prompt + completion content — set workspace retention, RBAC, export, and query access per organization policy.

```bash
uv run python 07-production-platform-other/05_diagnostics_preflight.py
```

**Code path.**
1. `entrypoint_preflight("diagnostics")` reads `bicep/main.bicep` and `terraform/main.tf`.
2. Per template, asserts each category name string appears at least once.
3. Prints `Bicep and Terraform configure reviewed Foundry diagnostic categories`.

**What to watch.** Preflight only. Missing category surfaces as `diagnostic categories missing: <list>`.

**Sensitive-content rule.**
- Do NOT add prompt or completion text to custom application telemetry by default.
- Combine with domain 01 lesson 25's `AppGenAIContent` protected-table pattern.
- Log Analytics retention drives cost — pick a bounded retention with export to cheaper archive.
- Reader on the workspace does not grant read on the `AppGenAIContent` protected table.

**References:** [Diagnostic logging](https://learn.microsoft.com/azure/foundry/how-to/diagnostic-logging) · [Configure Private Link](https://learn.microsoft.com/azure/foundry/how-to/configure-private-link)

---

## Stage 5 — HA/DR (lesson 06)

Foundry has no automatic failover. The lab validates the README HA/DR guidance still describes the correct pattern.

### 06 — HA/DR guidance markers

**Question answered:** Does the README HA/DR section still teach the correct pattern (no auto-failover, warm standby, two regions)?

**Background.** Foundry projects are regional. Cross-region agent state migration, active-active replication, and thread recovery are NOT supported. Warm standby means reconstruction: redeploy cell, recreate agents, rebuild indexes from source, test private DNS/RBAC, then move traffic.

```bash
uv run python 07-production-platform-other/06_ha_dr_preflight.py
```

**Code path.**
1. `entrypoint_preflight("ha-dr")` reads `README.md`.
2. Asserts three phrases present: `Foundry has no automatic failover`, `Warm standby`, `two supported regions`.
3. Prints `HA/DR guidance requires independent regional cells and a tested traffic switch`.

**What to watch.** Preflight only. Missing phrase surfaces as `HA/DR guidance missing: <list>`.

**Regional cell rules.**
- Deploy reviewed, equivalent cells in two supported regions. Same revision, DIFFERENT globally-unique Foundry/KV/Storage names.
- Traffic switch is application-level (front door, DNS, gateway) — this IaC does NOT redirect production traffic silently.
- Deploy model deployments in each region after separate capacity + quota review.
- For Standard Agent Service, bring your own Cosmos DB (continuous backup + zone-redundant multi-region failover), AI Search (zone redundancy), and Storage (GZRS). Add their PEs + zones in each cell.
- Store agent definitions, tool bindings, index schemas, ingestion manifests, and infrastructure in source control. Azure AI Search is a derived index, not authoritative store.
- Exercise recovery periodically: deploy standby cell, recreate agents, rebuild indexes, test private DNS/RBAC, move traffic. Record actual RTO/RPO.
- GZRS on Storage does NOT auto-fail-over a Foundry project storage binding. Do not treat generic storage settings as complete application DR.
- User-uploaded thread files can be lost. Define a business fallback (human support) before incident day.

**References:** [High availability and resiliency](https://learn.microsoft.com/azure/foundry/how-to/high-availability-resiliency) · [Agent Service disaster recovery](https://learn.microsoft.com/azure/foundry/how-to/agent-service-disaster-recovery) · [Agent virtual networks](https://learn.microsoft.com/azure/foundry/agents/how-to/virtual-networks)

---

## Feature status and hard limits

| Feature | Status | Practical boundary |
|---|---|---|
| Foundry account `AIServices` | GA | Modern account type; not `OpenAI` classic; not ML workspace |
| Private endpoint with `publicNetworkAccess: Disabled` | GA | Requires 3 private DNS zones + VNet linkage |
| Network injection (agent subnet delegation) | GA | Immutable after account creation; delegate to `Microsoft.App/environments` |
| CMK for Foundry project | GA | One-way; requires KV in same region; limited by Search regional CMK support |
| `disableLocalAuth: true` (Entra-only) | GA | Requires custom subdomain on the Foundry resource |
| Azure Policy Deny for connection categories | GA | Rejects at deploy time; doesn't enforce PE/CMK aliases |
| Standard Agent Service capability hosts | **Preview** in some regions | Bring your own Cosmos DB + AI Search + Storage |
| Foundry automatic cross-region failover | Not supported | Warm standby via two cells + application traffic switch |
| Thread state cross-region migration | Not supported | Reconstruct from source; user-uploaded files can be lost |
| Log Analytics `AppGenAIContent` protected table | **Preview** | Requires feature registration; separate role for read |

## Troubleshooting

| Symptom | Likely cause | Resolution |
|---|---|---|
| Preflight `missing required assets` | File not in expected path | Restore from git; run from repository root |
| `policy must deny unapproved Foundry connections` | Policy JSON `effect` changed | Restore effect `Deny` in `deny-unapproved-foundry-connections.json` |
| `Bicep baseline missing: <control>` | Template edit removed marker | Restore the missing control (public access, purge protection, CMK role, DNS, injection, diagnostics, lock) |
| `--apply` fails with `AuthorizationFailed` | Caller lacks `Contributor` + `Owner` (locks) + Private DNS Zone Contributor | Assign required roles; log out and back in |
| Deployment succeeds but resolves to public IP from VNet | DNS zone not linked to VNet, or wrong hostname used | Link 3 zones (`cognitiveservices`, `openai`, `services.ai`) to VNet; resolve normal FQDN, not `privatelink` |
| `RequestDisallowedByPolicy` on new deployment | Deny policy blocks a category not in allow-list | Add category to `--allowed-category` list or remove the noncompliant connection |
| Terraform apply corrupts state | Local state used in team setting | Migrate to approved encrypted remote backend before team access |
| CI/CD workflow fails to reach Foundry | Public GitHub runner cannot resolve PE | Use self-hosted runner in the VNet path |
| Log Analytics missing GenAI content | Feature not registered or table not marked protected | `az feature register --namespace Microsoft.Insights --name protectGenAISensitiveData`; mark `AppGenAIContent` protected |
| Second region cell deploys but agents missing | Cross-region agent state doesn't migrate | Recreate agents from source-controlled definitions in target region |

## CI/CD and operational release

Treat platform IaC as a release system: reviewed template → preflight → what-if → manual apply → verification → tagged release.

```text
Pull request modifies template or policy
  → 04, 05, 06 preflights run automatically
  → 01 preflight (Bicep) or 02 preflight (Terraform) run automatically
  → 03 preflight (policy) runs automatically
  → merge to main
  → workflow_dispatch triggered manually with apply: false → what-if / plan
  → reviewer approves diff → workflow_dispatch with apply: true
  → self-hosted runner in VNet executes az deployment / terraform apply
  → post-deploy verification: publicNetworkAccess, PE list, diagnostic settings, locks
  → tag release with template SHA + Foundry resource ID
```

### What to version

- Bicep + Terraform templates + param files (`*.example` only in repo)
- Policy JSON + Bicep assignment templates
- Approved connection-category allow-list per environment
- Reference GitHub workflow (until copied to `.github/workflows/`)
- Diagnostic category list + retention config
- HA/DR runbook + RTO/RPO thresholds

### Release gates

| Change | Minimum gate |
|---|---|
| Template edit | 01 or 02 preflight passes; what-if / plan reviewed |
| New allowed-category | 03 preflight passes; tested in nonprod first |
| Workflow edit | 04 preflight passes; OIDC + self-hosted runner already configured |
| Diagnostic category change | 05 preflight passes; retention + RBAC reviewed |
| Region expansion | 06 preflight passes; second cell deployed and traffic-switch tested |

## Security, networking, and IaC

| Decision | Recommendation | Common pitfall |
|---|---|---|
| Public access | `publicNetworkAccess: Disabled` from day one | Enabling public "temporarily" for one debug session leaves it open |
| Auth model | `disableLocalAuth: true`, Entra-only, custom subdomain | API keys leaked; keys don't rotate on personnel change |
| Managed identity | User-assigned (stable principal ID) | System-assigned regenerated principal breaks recovery |
| KV access | RBAC + soft delete + purge protection; grant Crypto User to Foundry MI | Access policies (legacy) alongside RBAC creates ambiguity |
| Storage | GZRS + private Blob endpoint | Do not treat GZRS as Foundry project DR |
| Delete lock | `CanNotDelete` on RG | Locks don't prevent data-plane deletes (agents, threads, models) |
| Private DNS | Link all three zones to VNet | Missing `services.ai.azure.com` zone → project API resolves publicly |
| CMK | RSA key in same region KV; grant Foundry UAMI Crypto User | One-way — cannot revert to Microsoft-managed |
| Terraform state | Encrypted remote backend with least-privilege access | Local state file in team setting = credential exposure |
| Policy allow-list | Test in nonprod first; explicit categories only | Empty allow-list in prod blocks every new connection |
| Self-hosted runner | Inside VNet path, labelled `foundry-vnet` | Public GitHub runner cannot reach private endpoints |

## Common exam traps

| Claim | Correct interpretation |
|---|---|
| "Delete lock protects Foundry data." | False. `CanNotDelete` is ARM-level only; agents/threads/models delete via data plane regardless. |
| "GZRS Storage means Foundry has cross-region DR." | False. Foundry has no auto-failover; warm standby is the pattern. |
| "Private endpoint alone blocks public access." | False. Also set `publicNetworkAccess: Disabled` on the account. |
| "OIDC federated credential is a stored secret." | False. OIDC replaces stored client secret — no repository secret needed. |
| "CMK can be turned off if project has one." | False. CMK on a Foundry project is one-way. |
| "Bicep and Terraform can both manage the same RG." | False. They fight over resource IDs — pick one per cell. |
| "Foundry account name can be changed later." | False. Name is globally unique and immutable; embedded in every FQDN. |
| "Deny policy also enforces PE + CMK." | False. This policy enforces connection categories only. |
| "Public GitHub runner can call Foundry over private endpoint." | False. Public runner cannot resolve private DNS. Use self-hosted runner in VNet. |
| "Network injection can be added after account creation." | False. Immutable after account creation — recreate to change. |
| "Foundry User role covers deploying models." | False. Control-plane deployment needs `Cognitive Services Contributor` or equivalent. |
| "diagnostic RequestResponse category is safe to query broadly." | False. Contains prompts + completions; use `AppGenAIContent` protected table + narrow RBAC. |

## Objective coverage and limits

Runnable evidence in this folder covers Bicep + Terraform IaC baselines for a private keyless Foundry cell, Deny policy for connection categories, reference GitHub Actions workflow validation, diagnostic category verification, and HA/DR guidance markers.

It does **not** provision model deployments, agents, capability hosts, workload RBAC, or Application Insights connection to a project. It does not test end-to-end private-network resolution — you must verify from inside a linked VNet. It does not fail-over Foundry projects between regions. It does not prove complete compliance for any specific standard.

## References

### IaC + private networking

- [Create resource template (Bicep)](https://learn.microsoft.com/azure/foundry/how-to/create-resource-template)
- [Create resource template (Terraform)](https://learn.microsoft.com/azure/foundry/how-to/create-resource-terraform)
- [Configure Private Link](https://learn.microsoft.com/azure/foundry/how-to/configure-private-link)
- [Agent virtual networks](https://learn.microsoft.com/azure/foundry/agents/how-to/virtual-networks)

### Governance + encryption

- [Encryption keys (CMK)](https://learn.microsoft.com/azure/foundry/concepts/encryption-keys-portal)

### Diagnostics + CI/CD

- [Diagnostic logging](https://learn.microsoft.com/azure/foundry/how-to/diagnostic-logging)
- [Set up CI/CD](https://learn.microsoft.com/azure/foundry/agents/how-to/set-up-ci-cd-cli)

### HA + DR

- [High availability and resiliency](https://learn.microsoft.com/azure/foundry/how-to/high-availability-resiliency)
- [Agent Service disaster recovery](https://learn.microsoft.com/azure/foundry/how-to/agent-service-disaster-recovery)

### Related domains

- [Domain 1: Plan and manage Foundry](../01-plan-and-manage/README.md) — RBAC, guardrails, tracing setup
- [Domain 6: Model customization and delivery](../06-model-customization-other/README.md) — deployment SKUs, PTU, Batch
