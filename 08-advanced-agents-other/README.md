# Domain 8: Advanced agents and current Foundry operations

> Preflight-first labs for advanced Foundry agent capabilities: enterprise knowledge, Toolbox and Skills governance, A2A, routines, gateway, optimization, hosted tools, Microsoft IQ, and current preview tool boundaries. Run commands from repository root: `uv run python 08-advanced-agents-other/<lesson>.py`.
>
> Every default command is a local preflight and makes no cloud call. Every remote write requires `--apply`. This directory uses the current agent object model (stable endpoint + unique agent identity) — do NOT create Agent Application resources or use application endpoints.

## What this domain teaches

Advanced Foundry agents are not one API — they are a set of independent capabilities layered on the current agent model:

```text
Deploy an agent (domain 2 lessons 08-16)
        ↓
Attach knowledge: Foundry IQ MCP connection (Lab 01)
        ↓
Centralize approved tools: Toolbox with immutable versions (Lab 02)
        ↓
Expose to other agents: A2A v1.0 endpoint + agent card (Lab 03)
        ↓
Schedule unattended work: Routines (Lab 04)
        ↓
Distribute to consumers: AI Gateway + pinned stable endpoint (Lab 05)
        ↓
Improve continuously: Agent Optimizer over reviewed baseline (Lab 06)
        ↓
Operate hosted runtime + MCP safely (Labs 07–19)
        ↓
Govern Toolbox/Skills versions and policies (Labs 20–21)
        ↓
Choose public and enterprise grounding correctly (Labs 22–23)
        ↓
Bound high-authority preview tools before use (Labs 24–27)
        ↓
Read common non-content operational health signals (Lab 28)
```

Lessons follow this progression in thirteen stages, each optional. These are supplemental to the AI-103 exam objectives, not a replacement for the core agent lessons in domain 02.

## Advanced agent mental model

### Current object model (what these labs assume)

| Concept | Where it lives | Immutability |
|---|---|---|
| **Agent** | Foundry project | Named + versioned; each version immutable once created |
| **Stable endpoint** | `<project>/agents/<name>/endpoint/...` | Traffic routed via `version_selector` rules |
| **Agent identity** | Managed identity on the agent | Persists across versions |
| **Toolbox version** | Foundry project | Immutable once published; default version routable |
| **Routine** | Foundry project | Config + schedule; disabled until enabled |
| **Foundry IQ connection** | Project connection (kind: remote-tool) | Managed by azd; keyless via project MI |
| **Agent card** | Under agent endpoint | v1.0 protected by Entra ID; not anonymously discoverable |

The current publishing model targets the agent's stable endpoint — NOT the deprecated Agent Application resource. Migration from Agent Applications is out of scope here.

### Two endpoint URL patterns to remember

```text
# Toolbox — consumer resolves current default version
{PROJECT_ENDPOINT}/toolboxes/{TOOLBOX_NAME}/mcp?api-version=v1

# Toolbox — developer targets one immutable version
{PROJECT_ENDPOINT}/toolboxes/{TOOLBOX_NAME}/versions/{VERSION}/mcp?api-version=v1

# Foundry IQ knowledge base MCP
{SEARCH_ENDPOINT}/knowledgebases/{KB}/mcp?api-version=2026-05-01-preview

# A2A v1.0
{PROJECT_ENDPOINT}/agents/{AGENT}/endpoint/protocols/a2a
{PROJECT_ENDPOINT}/agents/{AGENT}/endpoint/protocols/a2a/agentCard/v1.0
```

### RBAC boundaries

| Operation | Additional role or decision |
|---|---|
| Foundry IQ indexing + retrieval | `Search Index Data Reader` to project MI (add `Contributor` only for writes) |
| Toolbox runtime | `Foundry User` to agent identity; connections own authentication |
| Incoming A2A caller | `Foundry Agent Consumer` to calling identity at project/agent scope |
| Routines | Agent must have its own configured identity; routines cannot delegate end-user identity |
| AI Gateway | Eligible APIM v2 instance + required Foundry/APIM roles |
| Microsoft 365 / Teams publish | Bot Service permissions + tenant policy + admin approval |
| Agent Optimizer | Python hosted-agent azd project only |

## Glossary

| Term | Definition |
|---|---|
| **Foundry IQ** | Managed knowledge layer on Azure AI Search with agentic retrieval (planning + citations); connected via MCP endpoint |
| **Knowledge base** | Foundry IQ artifact combining sources + permissions + retrieval plan; addressed by name |
| **Toolbox** | Foundry project container centralizing approved tools behind one MCP-compatible endpoint |
| **Toolbox version** | Immutable snapshot of a toolbox; one version marked default for consumer endpoint |
| **A2A (Agent-to-Agent)** | Protocol standard for one agent to call another; v1.0 is the current target |
| **Agent card** | Discovery metadata for an A2A endpoint (description, skills, version); Entra-protected |
| **Routine** | Trigger + action pair (one agent invocation); unattended execution — no delegated user identity |
| **AI Gateway** | Foundry-integrated APIM v2 layer for quotas, token limits, governance, observability |
| **Stable endpoint** | Agent endpoint URL whose traffic is routed via `version_selector` rules to specific agent versions |
| **`FixedRatio` rule** | Version selector rule pinning a fraction (100% here) of traffic to one agent version |
| **Agent Optimizer** | Job that generates + scores candidate agent configurations against baseline + evaluators |
| **Baseline** | `.agent_configs/baseline/` — starting config that Agent Optimizer improves upon |
| **`eval.yaml`** | azd project file declaring evaluators + seed data for Agent Optimizer runs |
| **Project managed identity** | Managed identity attached to the Foundry project; used for keyless data-plane calls |
| **RemoteTool connection** | Project connection kind for MCP tools; `project-managed-identity` auth type is keyless |
| **Skill** | Preview immutable task instructions describing how work is performed; not a callable tool |
| **Private catalog** | Azure API Center-backed organizational discovery for approved tools or Skills |
| **Fabric IQ** | Preview access to Fabric ontology, semantic model, or data-agent assets |
| **Work IQ** | Preview delegated-user access to Microsoft 365 work context; app-only auth unsupported |
| **Reminder tool** | Preview hosted-agent follow-up in the same conversation; not a Routine/calendar |
| **Computer Use** | Preview model-driven UI action loop requiring sandboxing and safety acknowledgement |

## Setup

### Environment

Install and authenticate without adding secrets:

```bash
uv sync
az login
azd auth login
azd ext install microsoft.foundry
# Routines require the preview extension
azd extension install azure.ai.routines
```

Signed-in identity needs `Foundry User` on the project for every `--apply`. Additional roles per lab (see RBAC table above).

### Env variables (non-secret only)

```dotenv
PROJECT_ENDPOINT=https://<account>.services.ai.azure.com/api/projects/<project>
FOUNDRY_IQ_SEARCH_ENDPOINT=https://<search>.search.windows.net
FOUNDRY_IQ_KNOWLEDGE_BASE=<kb-name>
FOUNDRY_IQ_CONNECTION_NAME=foundry-iq-kb
FOUNDRY_TOOLBOX_NAME=<toolbox-name>
FOUNDRY_AGENT_NAME=<agent-name>
FOUNDRY_SKILL_NAME=<skill-name>
API_CENTER_RESOURCE_ID=/subscriptions/.../providers/Microsoft.ApiCenter/services/<name>
BING_PROJECT_CONNECTION_ID=<connection-id>
BING_CUSTOM_SEARCH_INSTANCE=<optional-instance>
FABRIC_IQ_CONNECTION_ID=<connection-id>
WORK_IQ_CONNECTION_ID=<connection-id>
FABRIC_DATA_AGENT_CONNECTION_ID=<connection-id>
SHAREPOINT_CONNECTION_ID=<connection-id>
BROWSER_PROJECT_CONNECTION_ID=<connection-id>
COMPUTER_USE_MODEL=computer-use-preview
```

Never add API keys, connection strings, or bearer tokens to `.env`, manifests, prompts, agent cards, or routine inputs. Credentials live in project connections, managed identity, Key Vault, or your CI secret store.

### Safe run order

1. **Preflight every lab first** — every default command reads local input only.
2. Confirm region + preview access + billing + network path + role assignments outside these labs.
3. **Lab 01 --apply** first if agents will use knowledge — grant `Search Index Data Reader` before apply.
4. **Lab 02 --apply** to publish toolbox after knowledge connection exists.
5. **Lab 03 --apply** after agent deployed; run `--apply --verify` to confirm card is live.
6. **Lab 04 --apply** ONLY after inspecting manifest; add `--dispatch` for one controlled run before enabling schedule.
7. **Lab 05 --apply** ONLY after gateway is `Enabled` on both gateway + project in Foundry portal.
8. **Lab 06 --apply** ONLY against a Python hosted-agent azd project with reviewed `eval.yaml`.
9. Run **20** before promoting/deleting Toolbox versions or cloning a policy version.
10. Run **21** before creating preview Skills or configuring API Center catalogs.
11. Run **22–23** before selecting public Bing, Search-backed IQ, Fabric, or Microsoft 365 grounding.
12. Run **24–27** locally before any hosted reminder, UI automation, enterprise-data, or image tool integration.
13. Run **28** locally before its optional read-only Log Analytics query; keep content tables excluded.

### Costs and side effects

| Lesson | Cost / side effect |
|---|---|
| 01 preflight | Local; validates env + URL shape. |
| 01 `--apply` | Creates/updates project connection. Search indexing + retrieval billing follows knowledge-base usage separately. |
| 02 preflight | Local; scans manifest for secrets + required fields. |
| 02 `--apply` | Creates toolbox + first version (default). Version is immutable. |
| 03 preflight | Local; prints URL templates. |
| 03 `--apply` | PATCHes agent card + enables Responses + A2A protocols. Callers need `Foundry Agent Consumer` role. |
| 03 `--apply --verify` | Additional GET on v1.0 card URL. |
| 04 preflight | Local; validates manifest, rejects secrets. |
| 04 `--apply` | Creates routine (disabled). |
| 04 `--apply --dispatch` | One controlled run; agent invocation cost applies. |
| 05 preflight | Local; prints gateway/publishing checklist. |
| 05 `--apply` | PATCHes stable endpoint to pin one version. APIM v2 gateway billing follows separately. |
| 06 preflight | Local; validates azd asset layout. |
| 06 `--apply --optimize-model` | Runs optimization job: candidate generation + evaluator runs = tokens billable. |
| 06 `--apply --apply-candidate` | Modifies local source only — no deployment cost. |
| 20 default | Local lifecycle/policy preflight. |
| 20 `--apply` | Lists/gets versions or creates/promotes/deletes persistent Toolbox versions. |
| 21 default | Local Skills/API Center preflight. |
| 21 `--apply` | Lists or creates/promotes/deletes preview Skill versions. |
| 22–27 default | Local typed request/configuration builders only; no cloud call. |
| 28 default | Local signal map and KQL only. |
| 28 `--apply` | Read-only Log Analytics query; requires workspace Reader role. |

Preview features (Foundry IQ portal surfaces, Toolbox tool search, A2A, Routines) can change region/subscription/model availability. Recheck feature state immediately before applying.

## Decision tables

### Foundry IQ vs manual Search index

| Signal | Choose |
|---|---|
| Multi-source knowledge with permission enforcement + planned retrieval + citations | Foundry IQ + MCP connection |
| Direct BM25/vector queries in application code | Domain 05 lessons (manual RAG) |
| Agent chooses when to retrieve | Foundry IQ or managed search tool (domain 05 lesson 20) |
| Need custom skillset transforms in indexer | Domain 05 lessons (skillset + WebApiSkill) |

### Toolbox vs raw MCP tools per agent

| Signal | Choose |
|---|---|
| Multiple agents share the same tools | Toolbox (single MCP endpoint, versioned) |
| One-off per-agent tool | Direct MCP per agent (domain 02 lesson 25) |
| Need immutable rollback point | Toolbox versions |
| Large catalog — model needs to select tools | Toolbox + tool search |

### A2A vs direct Responses call

| Signal | Choose |
|---|---|
| Agent calls another agent via standard discovery | A2A v1.0 + agent card |
| App orchestrates two agents in code | Direct Responses per agent |
| Third-party agent must discover skills | A2A card (Entra-protected) |

### Routine vs workflow

| Signal | Choose |
|---|---|
| One trigger + one agent action | Routine |
| Branching, approvals, multiple agents, stateful | Workflow (domain 02 lessons 15-16) |
| Recurrence on cron schedule | Routine (`type: schedule`) |
| Event-driven unattended | Routine (supported event triggers) |

## Practice questions

After completing this domain, use the [Domain 8 question review](questions/README.md) for Computer Use, grounding, and MCP mappings.

## Lesson map

| # | Lesson | Runnable objective | Status / limitation |
|---:|---|---|---|
| 01 | [Foundry IQ connection](01_foundry_iq_connection_preflight.py) | Create keyless RemoteTool MCP connection to a knowledge base | `--apply` creates project connection; does not build the knowledge base |
| 02 | [Toolbox publish](02_toolbox_publish_preflight.py) | Publish first immutable Toolbox version from manifest | `--apply` creates toolbox + first version (becomes default) |
| 03 | [A2A agent card](03_a2a_agent_card_preflight.py) | Enable A2A v1.0 + write agent card | `--apply` PATCHes agent; `--verify` fetches card |
| 04 | [Routines](04_routines_preflight.py) | Create scheduled routine with disabled default | `--apply` creates routine; `--dispatch` runs once |
| 05 | [Gateway + publish](05_gateway_publishing_preflight.py) | Pin stable endpoint to one reviewed agent version | `--apply` PATCHes `version_selector`; channel publish is portal-only |
| 06 | [Agent Optimizer](06_agent_optimizer_preflight.py) | Run optimization or apply candidate locally | `--apply` requires Python hosted-agent azd project; never deploys |
| 07 | [Hosted agent deploy](07_hosted_agent_deploy_preflight.py) | Preflight + `azd deploy` a Python hosted agent | `--apply` containers bill immediately |
| 08 | [Hosted agent env vars](08_hosted_agent_env_preflight.py) | Set runtime env var (or KV ref) on hosted agent | `--apply` PATCHes agent; use KV ref for secrets |
| 09 | [MCP get started](09_mcp_get_started.py) | Connect agent to MCP server; force the MCP tool with `tool_choice`; print discovered tools | `--apply` creates a temporary agent version + deletes it |
| 10 | [MCP security preflight](10_mcp_security_preflight.py) | Validate MCP security checklist + optional policy JSON | Local; no cloud call |
| 11 | [Agent memory](11_agent_memory.py) | Create vector store, upload fact, attach to agent, verify recall, cleanup | `--apply` creates + deletes cloud resources |
| 12 | [Agent routines preflight](12_agent_routines_preflight.py) | Validate routine JSON (cron/event trigger definition) | Local; no cloud call |
| 13 | [Agent 365 preflight](13_agent_365_preflight.py) | Check Entra M365 permissions for Agent 365 integration | `--apply` calls Graph API read |
| 14 | [Browser automation preflight](14_browser_automation_preflight.py) | Probe browser tool discovery on ephemeral agent | `--apply` creates + deletes agent |
| 15 | [Foundry toolbox preflight](15_foundry_toolbox_preflight.py) | List toolbox connections configured in this project | `--apply` reads project connections |
| 16 | [Foundry IQ preflight](16_foundry_iq_preflight.py) | Verify Foundry IQ enterprise knowledge connection | `--apply` reads project connection |
| 17 | [Agent optimizer](17_agent_optimizer.py) | Create optimizer dataset + submit optimization job | `--apply` submits cloud job (preview) |
| 18 | [Custom code interpreter](18_custom_code_interpreter_preflight.py) | Validate MCP_SERVER_URL reachability for ACA-backed code interpreter | `--apply` probes endpoint |
| 19 | [Azure Functions tool](19_azure_functions_tool_preflight.py) | Validate AzureFunctionTool queue definition + storage endpoint | `--apply` probes storage endpoint |
| 20 | [Toolbox lifecycle + governance](20_toolbox_lifecycle_governance.py) | List/get/clone-policy/promote/delete immutable versions | Remote operation requires `--apply`; promotion/deletion affect consumers |
| 21 | [Skills + private catalogs](21_skills_private_catalog_preflight.py) | Build bounded Skill; manage preview versions; explain API Center catalogs | Skills are preview; catalogs require API Center |
| 22 | [Grounding with Bing](22_bing_grounding_preflight.py) | Build standard or Custom Search typed tool payload | Local; Bing uses billed public egress |
| 23 | [Microsoft IQ tools](23_microsoft_iq_tools_preflight.py) | Compare Foundry/Fabric/Work IQ and build typed preview tools | Local; tenant/network/license prerequisites remain |
| 24 | [Reminder tool](24_reminder_tool_preflight.py) | Build connectionless hosted-agent Reminder payload | Local; preview; does not schedule |
| 25 | [Computer Use](25_computer_use_preflight.py) | Enforce pending-safety-check approval payload | Local; preview; no UI/model call |
| 26 | [Enterprise data tools](26_enterprise_data_tools_preflight.py) | Build Fabric data-agent or SharePoint typed tool payload | Local; preview delegated-user auth |
| 27 | [Image-generation agent tool](27_image_generation_tool_preflight.py) | Build typed ImageGenTool payload | Local; preview; no media generated |
| 28 | [Cross-domain observability](28_cross_domain_observability.py) | Map Domain 01–09 signals and query non-content health telemetry | Local by default; `--apply` is read-only |

---

## Stage 1 — Knowledge via Foundry IQ (lesson 01)

Bring managed retrieval to the agent through a keyless MCP connection. This is the foundation for any advanced agent that answers from private knowledge.

### 01 — Foundry IQ connection

**Question answered:** How do I connect an agent to a Foundry IQ knowledge base without embedding Search credentials?

**Background.** Foundry IQ is a managed knowledge layer on Azure AI Search with agentic retrieval — combines sources, enforces permissions, plans retrieval, returns citations. The connection uses `remote-tool` kind + `project-managed-identity` auth + audience `https://search.azure.com/`. No key ever leaves the project MI.

**Before code.** Assign `Search Index Data Reader` to the project MI. Foundry IQ is partially GA — portal + some agentic surfaces stay preview-dependent. Confirm region + subscription + feature availability first.

```bash
export PROJECT_ENDPOINT="https://<account>.services.ai.azure.com/api/projects/<project>"
export FOUNDRY_IQ_SEARCH_ENDPOINT="https://<search>.search.windows.net"
export FOUNDRY_IQ_KNOWLEDGE_BASE="<kb-name>"
export FOUNDRY_IQ_CONNECTION_NAME="foundry-iq-kb"

# Preflight (local read-only)
uv run python 08-advanced-agents-other/01_foundry_iq_connection_preflight.py

# Apply (creates project connection via azd)
uv run python 08-advanced-agents-other/01_foundry_iq_connection_preflight.py --apply
```

**Code path.**
1. `project_endpoint()` — HTTPS + `.services.ai.azure.com` + `/api/projects/` + no credentials.
2. `knowledge_base_mcp_endpoint()` — builds `https://<search>/knowledgebases/<kb>/mcp?api-version=2026-05-01-preview`.
3. `connection_command()` — assembles `azd ai connection create <name> --kind remote-tool --target <mcp> --auth-type project-managed-identity --audience https://search.azure.com/ --project-endpoint <endpoint>`.
4. `--apply` runs subprocess with `AZURE_DEV_USER_AGENT=microsoft_foundry_skill`.

**What to watch.** Preflight: `Validated Foundry IQ MCP endpoint: <url>` + `Apply command: azd ai connection create ...`. `--apply`: azd stream ending with connection-created confirmation.

**What this does NOT do.**
- Does not create the knowledge base. Build knowledge sources + KB via Foundry portal or Search operations first.
- Does not query the KB. Attach the connection to an agent (via Toolbox in lesson 02 or directly).
- Does not grant Search access — that role assignment is a separate reviewed step.

**References:** [Foundry IQ concepts](https://learn.microsoft.com/azure/foundry/agents/concepts/what-is-foundry-iq) · [Foundry IQ agent connection](https://learn.microsoft.com/azure/foundry/agents/how-to/foundry-iq-connect)

---

## Stage 2 — Approved tools via Toolbox (lesson 02)

Centralize tools behind one versioned MCP endpoint. Connections own authentication; manifests must be credential-free.

### 02 — Toolbox publish

**Question answered:** How do I publish a Toolbox version safely without embedding credentials?

**Background.** Toolbox groups approved tools behind one MCP endpoint. Versions are immutable — the first version becomes the default. Test a version-specific developer endpoint BEFORE flipping the consumer endpoint's default.

**Before code.** Copy `toolbox.example.yaml` outside source control (e.g., `toolbox.local.yaml`), replace connection names, keep it credential-free. Review tool descriptions, auth, approval policy, region/model support, data flows, owner, cost, cleanup.

```bash
cp 08-advanced-agents-other/toolbox.example.yaml toolbox.local.yaml

# Preflight (secret scan + required-field check)
uv run python 08-advanced-agents-other/02_toolbox_publish_preflight.py \
  --manifest toolbox.local.yaml

# Apply — first version becomes default
uv run python 08-advanced-agents-other/02_toolbox_publish_preflight.py \
  --apply --toolbox-name support-knowledge --manifest toolbox.local.yaml
```

**Code path.**
1. `validate_manifest()` — reject secret markers (`client_secret`, `api_key`, `authorization=`, `connection_string`, `password:`); require `connections:` or `tools:` or `skills:`.
2. `toolbox_endpoint()` — builds consumer or developer URL depending on version arg.
3. `create_command()` — `azd ai toolbox create <name> --from-file <manifest> --project-endpoint <endpoint>`.
4. `--apply` runs subprocess with `AZURE_DEV_USER_AGENT=microsoft_foundry_skill`.

**What to watch.** Preflight: `Validated credential-free manifest: <path>` + both endpoint templates. `--apply`: azd stream ending `Created Toolbox <name>. Test its version-specific endpoint before consumer rollout.`

**Endpoint discipline.**
- Test against `.../versions/{VERSION}/mcp?api-version=v1` before flipping default.
- Consumer endpoint `.../mcp?api-version=v1` always resolves current default.
- Tool search reduces tool-definition context on large catalogs but does NOT authorize a tool or make one safe.

**References:** [Toolbox concepts](https://learn.microsoft.com/azure/foundry/agents/concepts/toolbox-overview) · [Toolbox management](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/toolbox)

---

## Stage 3 — A2A discovery (lesson 03)

Expose an agent for discovery by other agents via the A2A v1.0 protocol.

### 03 — A2A agent card

**Question answered:** How do I enable one Foundry agent to be discovered + called by other agents?

**Background.** Agent-to-Agent (A2A) is the standard for one agent to call another. New callers should target v1.0. The agent card is Entra-protected — NOT anonymously discoverable. Enabling A2A does not grant caller access; that's a separate role assignment.

**Before code.** Agent must already be deployed (domain 02 lessons 08-16). Grant `Foundry Agent Consumer` to each caller identity at project or agent scope. Decide on-behalf-of vs service-identity auth deliberately.

```bash
export FOUNDRY_AGENT_NAME="support-agent"

# Preflight (prints URLs)
uv run python 08-advanced-agents-other/03_a2a_agent_card_preflight.py

# Apply + verify (PATCHes card, then fetches v1.0 card)
uv run python 08-advanced-agents-other/03_a2a_agent_card_preflight.py --apply --verify
```

**Code path.**
1. `a2a_urls()` — builds base + `/agentCard/v1.0`.
2. `patch_body()` — JSON with agent_card (description, version 1.0, skills) + agent_endpoint (protocol_configuration: `responses`, `a2a`).
3. `patch_command()` — `az rest --method patch --url .../agents/<name>?api-version=v1 --resource https://ai.azure.com --body <json>`.
4. `a2a_tool()` builds an outbound `A2APreviewTool`; remote card fetch is anonymous by default.
5. `--verify` — additional `az rest --method get` on the incoming Foundry card URL.

**What to watch.** Preflight: both A2A URLs printed. `--apply`: PATCH success + `Enabled current Responses and A2A protocols. v1.0 card: <url>`. `--verify`: fetched card JSON printed.

**What this does NOT do.**
- Does not grant callers access. Assign `Foundry Agent Consumer` role separately.
- Does not make an existing Responses endpoint A2A-capable — the PATCH is required.
- Does not migrate deprecated Agent Applications.
- Does not make outbound protected cards work automatically. Pass a project connection and `send_credentials_for_agent_card=true`; keep the protected card HTTPS and on the same host as `base_url`.

**References:** [Incoming A2A](https://learn.microsoft.com/azure/foundry/agents/how-to/enable-agent-to-agent-endpoint) · [A2A authentication](https://learn.microsoft.com/azure/foundry/agents/concepts/agent-to-agent-authentication) · [Configure agent](https://learn.microsoft.com/azure/foundry/agents/how-to/configure-agent)

---

## Stage 4 — Unattended execution via Routines (lesson 04)

Schedule an agent invocation for cron or supported event triggers. One trigger + one action per routine.

### 04 — Routines

**Question answered:** How do I schedule an agent invocation with reviewed inputs and no delegated user identity?

**Background.** A routine = one trigger + one action. Use for timers, schedules, supported events invoking one agent. Use workflow (domain 02 lessons 15-16) for branching, approvals, multiple agents, or stateful coordination. Routines execute unattended — inputs cannot include secrets, PATs, or delegated user credentials.

**Before code.** Agent must use its own configured identity (routines cannot delegate end-user identity). Copy `routine.example.yaml` outside source control and edit only nonsecret values.

```bash
cp 08-advanced-agents-other/routine.example.yaml routine.local.yaml

# Preflight (secret scan + required-field check)
uv run python 08-advanced-agents-other/04_routines_preflight.py \
  --manifest routine.local.yaml

# Apply (creates routine, disabled by default)
uv run python 08-advanced-agents-other/04_routines_preflight.py \
  --apply --routine-name weekday-support-summary --manifest routine.local.yaml

# Apply + one controlled test dispatch
uv run python 08-advanced-agents-other/04_routines_preflight.py \
  --apply --dispatch --routine-name weekday-support-summary \
  --manifest routine.local.yaml
```

Inspect after apply:

```bash
azd ai routine show weekday-support-summary --project-endpoint "$PROJECT_ENDPOINT"
azd ai routine run list weekday-support-summary --project-endpoint "$PROJECT_ENDPOINT"
```

**Code path.**
1. `validate_manifest()` — strip comment lines, reject secret markers (`secret`, `password`, `api_key`, `authorization:`, `bearer `). Require `triggers:`, `type: schedule`, `cron_expression:`, `time_zone:`, `action:`, `type: invoke_agent_responses_api`.
2. `routine_command()` — `azd ai routine create <name> --file <manifest> --project-endpoint <endpoint>`.
3. `--dispatch` — additional `azd ai routine dispatch <name>` call.

**What to watch.** Preflight: `Validated reviewed routine manifest: <path>` + inspection guidance. `--apply`: azd success. `--dispatch`: `Dispatched once. Review run history before relying on its schedule.`

**Enable schedule ONLY after** reviewing trace, output, tool behavior, data exposure, cost.

**References:** [Routines](https://learn.microsoft.com/azure/foundry/agents/how-to/use-routines) · [Configure agent](https://learn.microsoft.com/azure/foundry/agents/how-to/configure-agent)

---

## Stage 5 — Distribution via AI Gateway (lesson 05)

Pin the agent's stable endpoint to a reviewed version before distributing to consumers or channels.

### 05 — Gateway + stable-endpoint pinning

**Question answered:** How do I pin 100% of stable-endpoint traffic to one reviewed agent version before distribution?

**Background.** AI Gateway = Foundry-integrated APIM v2 for quotas, token limits, governance, observability. Enable in Foundry portal Operate → Admin console; confirm both gateway AND project show `Enabled`. Existing projects require explicit addition to a configured gateway.

**Before code.** Verify response quality, tool permissions, gateway behavior, end-user data handling, Bot Service permissions, tenant policy, and approval scope. Do NOT use deprecated Agent Application publishing.

```bash
# Preflight (checklist print)
uv run python 08-advanced-agents-other/05_gateway_publishing_preflight.py

# Apply — pin 100% of stable-endpoint traffic to agent version N
uv run python 08-advanced-agents-other/05_gateway_publishing_preflight.py \
  --apply --agent-name "$FOUNDRY_AGENT_NAME" --agent-version 2
```

**Code path.**
1. `endpoint_patch(agent_version)` — JSON with `version_selector.version_selection_rules: [{"type": "FixedRatio", "agent_version": "2", "traffic_percentage": 100}]`.
2. `patch_command()` — `az rest --method patch --url .../agents/<name>?api-version=v1 --headers Content-Type=application/merge-patch+json --body <json>`.

**What to watch.** Preflight: gateway + publishing checklist. `--apply`: PATCH success + `Stable endpoint pinned. Publish to Microsoft 365 Copilot or Teams only through reviewed portal flow.`

**Channel publish is portal-only.**
- Microsoft 365 Copilot / Teams distribution happens in Foundry portal after gateway + RBAC + privacy + channel review.
- Do NOT script channel publish — the review scope demands human approval.
- Migrate deprecated Agent Applications separately (see [migrate-agent-applications](https://learn.microsoft.com/azure/foundry/agents/how-to/migrate-agent-applications)).

**References:** [AI Gateway](https://learn.microsoft.com/azure/foundry/configuration/enable-ai-api-management-gateway-portal) · [Configure agent](https://learn.microsoft.com/azure/foundry/agents/how-to/configure-agent) · [Current publishing model](https://learn.microsoft.com/azure/foundry/agents/how-to/migrate-agent-applications)

---

## Stage 6 — Continuous improvement via Agent Optimizer (lesson 06)

Generate + score candidate agent configurations from a baseline. Applies local source only — deployment is a separate reviewed step.

### 06 — Agent Optimizer

**Question answered:** How do I generate + score improved agent configurations without automatic deployment?

**Background.** Agent Optimizer runs against Python hosted-agent azd projects only. Requires `azure.yaml`, `eval.yaml`, and `.agent_configs/baseline/` in the agent root. Optimizer generates candidates, scores against evaluators + seed data, and produces a ranked list. Applying a candidate modifies local source only — never deploys.

**Before code.** Review `eval.yaml` ownership, seed data, evaluators, and baseline. Optimizer job runs use tokens billable per candidate + evaluator run.

```bash
# Preflight (assets check)
uv run python 08-advanced-agents-other/06_agent_optimizer_preflight.py \
  --agent-root <hosted-agent-root>

# Apply — start optimization job
uv run python 08-advanced-agents-other/06_agent_optimizer_preflight.py \
  --agent-root <hosted-agent-root> --apply \
  --optimize-model <approved-optimizer-deployment>

# Apply candidate to LOCAL source only (never deploys)
uv run python 08-advanced-agents-other/06_agent_optimizer_preflight.py \
  --agent-root <hosted-agent-root> --apply \
  --apply-candidate <candidate-id>
```

Monitor:

```bash
azd ai agent optimize status <operation-id> --watch
```

**Code path.**
1. `validate_hosted_agent_root()` — check for `azure.yaml`, `eval.yaml`, `.agent_configs/baseline/`.
2. `--apply --optimize-model`: `azd ai agent optimize --optimize-model <model> [--service <svc>]`.
3. `--apply --apply-candidate`: `azd ai agent optimize apply --candidate <id> [--service <svc>]`.

**What to watch.** Preflight: assets-OK OR missing-list. `--apply --optimize-model`: `Optimization started.` `--apply --apply-candidate`: `Candidate applied locally. Review diff and deploy separately.`

**Deployment discipline.**
- Review candidate diff, evaluator results, safety behavior, tool changes, latency, cost.
- Deploy candidate via separate `azd deploy` after review — this lab never triggers deploy.
- Optimizer targets Python hosted agents only (not prompt agents from portal).

**References:** [Configure agent](https://learn.microsoft.com/azure/foundry/agents/how-to/configure-agent) · [Foundry IQ concepts](https://learn.microsoft.com/azure/foundry/agents/concepts/what-is-foundry-iq)

---

## Stage 7 — Hosted agent lifecycle + MCP (lessons 07–10)

Lessons 07–10 cover the two biggest operational gaps: deploying and configuring Python hosted agents, and wiring MCP tools securely.

### 07 — Hosted agent deploy

**Question answered:** How do I package and deploy a Python hosted agent to Foundry managed hosting?

**Background.** A hosted agent = Python code in an azd project with `azure.yaml`. `azd deploy` builds and pushes the container image to Foundry hosting. Foundry manages the runtime, endpoint routing, and identity. Never bake secrets into code — use env vars (lesson 08) or KV refs.

```bash
uv run python 08-advanced-agents-other/07_hosted_agent_deploy_preflight.py --agent-root <path>
uv run python 08-advanced-agents-other/07_hosted_agent_deploy_preflight.py --apply --agent-root <path>
```

**Code path.** Preflight: check `azure.yaml` + deps file exist. `--apply`: `azd deploy [--service <svc>]` in agent-root.

**What to watch.** Preflight: asset pass/fail. `--apply`: azd stream with `Endpoint: https://...` — use that URL in PROJECT_ENDPOINT for env-var and telemetry lessons.

**References:** [Deploy hosted agent](https://learn.microsoft.com/azure/foundry/agents/how-to/deploy-hosted-agent) · [Deploy hosted-agent code](https://learn.microsoft.com/azure/foundry/agents/how-to/deploy-hosted-agent-code) · [Hosted-agent contract](https://learn.microsoft.com/azure/foundry/agents/concepts/hosted-agent-contract) · [azure.yaml reference](https://learn.microsoft.com/azure/foundry/agents/concepts/azure-yaml-reference) · [Invoke hosted agent](https://learn.microsoft.com/azure/foundry/agents/how-to/invoke-hosted-agent) · [Test hosted agent](https://learn.microsoft.com/azure/foundry/agents/how-to/test-hosted-agent)

### 08 — Hosted agent env vars

**Question answered:** How do I set runtime environment variables on a deployed hosted agent without baking them into the container?

**Background.** Runtime env vars are set after deploy via PATCH on the agent resource. Secrets must use Key Vault reference syntax: `@Microsoft.KeyVault(SecretUri=...)`. This lesson validates the value syntax and PATCHes one env var.

```bash
uv run python 08-advanced-agents-other/08_hosted_agent_env_preflight.py
uv run python 08-advanced-agents-other/08_hosted_agent_env_preflight.py --apply \
  --agent-name support-agent --env-name DB_ENDPOINT --env-value https://my.db.example
```

**Code path.** `az rest --method patch --url .../agents/<name>?api-version=v1 --body {"runtime": {"env_vars": [{"name": KEY, "value": VALUE}]}}`.

**What to watch.** PATCH success. Confirm in portal: Foundry → agent → Settings → Environment variables. KV refs show the ref string, not the resolved secret.

**References:** [Configure hosted-agent env variables](https://learn.microsoft.com/azure/foundry/agents/how-to/configure-hosted-agent-env-variables) · [Hosted-agent permissions](https://learn.microsoft.com/azure/foundry/agents/concepts/hosted-agent-permissions) · [Monitor hosted-agent logs](https://learn.microsoft.com/azure/foundry/agents/how-to/monitor-hosted-agent-logs) · [Set up Key Vault connection](https://learn.microsoft.com/azure/foundry/how-to/set-up-key-vault-connection)

### 09 — MCP get started

**Question answered:** How do I connect a Foundry agent to an MCP server, make it call the MCP tool every time, and see which tools the server exposes?

**Background.** MCP lets agents discover and call tools on any MCP-compatible server, such as a knowledge base exposed as an MCP endpoint. A prompt agent gets an `MCPTool(server_label, server_url, project_connection_id)`; authenticated servers use a project connection so tokens never live in the agent definition. With `tool_choice="auto"` the model can skip the knowledge base and answer from its weights (no grounded citations). `"required"` forces *some* tool. `ToolChoiceMCP(server_label=..., name=...)` — JSON `{"type": "mcp", "server_label": ..., "name": ...}` — forces the MCP tool on every run. The lesson sets it on the agent definition; one Responses call can also pass `tool_choice`.

```bash
export MCP_SERVER_URL=https://<mcp-server>/mcp
export MCP_CONNECTION_NAME=my-mcp-connection   # optional; authenticated servers only
export MCP_TOOL_NAME=kbsearch                  # optional; force one specific tool
uv run python 08-advanced-agents-other/09_mcp_get_started.py            # prints agent definition, no cloud call
uv run python 08-advanced-agents-other/09_mcp_get_started.py --apply    # temporary agent version, one question
```

**Code path.**
1. `mcp_definition()` validates the HTTPS, non-localhost URL and builds `PromptAgentDefinition(tools=[MCPTool(...)], tool_choice=ToolChoiceMCP(...))`. `require_approval` stays `"always"` unless `--trust-server`.
2. `--apply`: `client.connections.get(MCP_CONNECTION_NAME).id` (when set) → `agents.create_version()` → `responses.create(agent_reference)`.
3. `print_mcp_items()` prints the `mcp_list_tools` discovery item (tool names), any `mcp_approval_request` (not approved by the probe), and `mcp_call` results.
4. `agents.delete_version()` in `finally`.

**What to watch.** The `mcp_list_tools` line lists the server's tools. With approval `"always"`, the run stops at an approval request — approve reviewed read-only calls as in Domain 2 lesson 25. Zero tools = wrong URL/connection or an empty server.

**Exam cues.** Agent sometimes answers without calling the knowledge-base MCP tool → set `tool_choice` to the MCP type (and tool name). `response_format` shapes output; tool definitions (`tools`/toolset) only make tools available.

**References:** [MCP tool for agents](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/model-context-protocol) · [MCP get started](https://learn.microsoft.com/azure/foundry/mcp/get-started) · [MCP available tools](https://learn.microsoft.com/azure/foundry/mcp/available-tools)

### 10 — MCP security preflight

**Question answered:** Does my MCP integration satisfy the security checklist before wiring to a production agent?

**Background.** MCP tools call arbitrary external servers — they are a lateral-movement risk if not governed. Security posture requires approved server list, managed-identity auth, tool schema review, and logging. This lesson validates those requirements locally and optionally parses a JSON policy file.

```bash
uv run python 08-advanced-agents-other/10_mcp_security_preflight.py
uv run python 08-advanced-agents-other/10_mcp_security_preflight.py --policy-file mcp-policy.json
```

**Code path.** Env-var checks (endpoint HTTPS, no embedded bearer). Optional policy JSON parse: `approved_servers`, `auth_type == managed_identity`, `logging_enabled`, `tool_allowlist`.

**What to watch.** All `[PASS]`. Any `[FAIL]` = gap before production wiring. `auth_type` not managed identity = `[WARN]`.

**References:** [MCP security best practices](https://learn.microsoft.com/azure/foundry/mcp/security-best-practices) · [Toolbox management](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/toolbox)

---

## Stage 8 — Memory, routines, 365, browser, toolbox, IQ, optimizer (lessons 11–17)

Stage 8 covers the advanced agent lifecycle: persistent memory, scheduled routines, M365 data access, browser-driven automation, the toolbox catalog, enterprise knowledge (Foundry IQ), and continuous prompt optimization.

### 11 — Agent memory (vector store)

**Question answered:** How do I attach a vector store to an agent and verify the agent recalls a fact from it?

**Background.** Agent memory persists information across sessions via a Foundry vector store indexed with `file_search`. The agent retrieves relevant chunks automatically on each turn. This lesson proves the create→attach→query→cleanup cycle on an ephemeral agent, so no persistent artifacts are left behind.

```bash
uv run python 08-advanced-agents-other/11_agent_memory.py
uv run python 08-advanced-agents-other/11_agent_memory.py --apply
```

**Code path.**
1. `agents.vector_stores.create()` → `agents.vector_stores.files.upload_and_poll()`.
2. `agents.create_version(tools=[{"type":"file_search","file_search":{"vector_store_ids":[vs.id]}}])`.
3. `agents.threads.create()` → `messages.create(user query)` → `runs.create_and_process()`.
4. `messages.list()` → print assistant reply → `agents.delete()` + `vector_stores.delete()`.

**What to watch.** Assistant answer contains the uploaded fact. No recall = indexing not yet complete (the `upload_and_poll` call waits, but rerun if needed).

**References:** [Agent memory concepts](https://learn.microsoft.com/azure/foundry/agents/concepts/what-is-memory) · [Vector stores](https://learn.microsoft.com/azure/foundry/agents/concepts/vector-stores) · [Memory quickstart](https://learn.microsoft.com/azure/foundry/agents/quickstarts/quickstart-memory-hosted-agent)

---

### 12 — Agent routines preflight

**Question answered:** Is my agent routine definition JSON valid before I register it in the Foundry portal?

**Background.** Agent routines let hosted agents run on a cron schedule or event trigger without a user initiating the conversation. A routine JSON specifies trigger type (cron/event/webhook), the agent name, and the initial message. This lesson validates the JSON locally — registration is done in the Foundry portal or via `az` CLI.

```bash
uv run python 08-advanced-agents-other/12_agent_routines_preflight.py
uv run python 08-advanced-agents-other/12_agent_routines_preflight.py --policy-file my-routine.json
```

**Code path.** `json.loads(path)` → validate `agent_name` (str), `initial_message` (str), `trigger` (dict with `type` in `{cron, event, webhook}`, `schedule` for cron) → print PASS/FAIL per key.

**What to watch.** All PASS before registering. Missing `initial_message` = agent starts with no context at trigger time.

**References:** [Agent routines concepts](https://learn.microsoft.com/azure/foundry/agents/concepts/routines) · [Foundry agent overview](https://learn.microsoft.com/azure/foundry/agents/overview)

---

### 13 — Agent 365 preflight

**Question answered:** Have the Microsoft Graph API permissions been granted for my Agent 365 M365 integration?

**Background.** Agent 365 lets hosted agents access M365 data (emails, calendar, Teams, SharePoint) via Microsoft Graph. This requires an Entra app registration with admin-consented Graph permissions. This lesson validates that the service principal for the app has the required `oauth2PermissionGrants` scopes.

```bash
uv run python 08-advanced-agents-other/13_agent_365_preflight.py
uv run python 08-advanced-agents-other/13_agent_365_preflight.py --apply
```

**Code path.** `az rest GET graph.microsoft.com/v1.0/servicePrincipals?$filter=appId eq '{client_id}'` → check `oauth2PermissionGrants` scopes vs `{Mail.Read, Calendars.Read, Sites.ReadWrite.All, Chat.Read}` → print PASS/FAIL per permission.

**What to watch.** All permissions PASS before wiring. Missing consent = agent cannot access M365 data at runtime even with correct credentials.

**References:** [Agent 365 integration](https://learn.microsoft.com/azure/foundry/agents/concepts/agent-365-integration) · [Agent 365 how-to](https://learn.microsoft.com/azure/foundry/agents/how-to/agent-365) · [Grant Agent 365 permissions](https://learn.microsoft.com/azure/foundry/agents/how-to/grant-agent-365-permissions)

---

### 14 — Browser automation preflight

**Question answered:** Is the browser tool connection valid and discovered by an ephemeral probe agent?

**Background.** Browser Automation preview uses an Azure Playwright workspace connection to navigate and interact with websites. It is distinct from Computer Use lesson 25. The workspace/connection and browser authority need isolated test sites, domain/action limits, tracing, and approval.

```bash
uv run python 08-advanced-agents-other/14_browser_automation_preflight.py
uv run python 08-advanced-agents-other/14_browser_automation_preflight.py --apply
```

**Code path.** `browser_tool()` builds `BrowserAutomationPreviewTool` with `BrowserAutomationToolParameters(connection.project_connection_id)` → `agents.create_version()` → `agents.list_tools()` → check `browser_automation_preview` → `agents.delete()`.

**What to watch.** Set `BROWSER_PROJECT_CONNECTION_ID`, not a generic connection name. `Foundry Project Manager` creates the connection; temporary `Contributor` is needed only while provisioning the Playwright workspace. Private website access remains private preview. Trace `browser_automation_preview_call` events.

**References:** [Browser automation how-to](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/browser-automation) · [Computer use](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/computer-use) · [Tool best practices](https://learn.microsoft.com/azure/foundry/agents/concepts/tool-best-practice)

---

### 15 — Foundry toolbox preflight

**Question answered:** Which project connections could support direct or Toolbox agent tools?

**Background.** Project connections store downstream endpoint/auth configuration. They can support direct agent tools or Toolbox tools, but a connection is not a Toolbox version, does not prove publication, and does not prove runtime authorization. Connectionless tools such as Reminder do not appear here.

```bash
uv run python 08-advanced-agents-other/15_foundry_toolbox_preflight.py
uv run python 08-advanced-agents-other/15_foundry_toolbox_preflight.py --apply
```

**Code path.** `project_client().connections.list()` → filter known tool-related connection markers → print candidate name, type, endpoint.

**What to watch.** Use this only as inventory. Inspect the actual agent/Toolbox version definition and downstream role assignments before claiming the tool is usable.

**References:** [Toolbox overview](https://learn.microsoft.com/azure/foundry/agents/concepts/toolbox-overview) · [Toolbox tools](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/use-toolbox-hosted-agent) · [Tool catalog](https://learn.microsoft.com/azure/foundry/agents/concepts/tool-catalog)

---

### 16 — Foundry IQ preflight

**Question answered:** Is the Foundry IQ enterprise knowledge connection present and readable in this project?

**Background.** Foundry IQ connects agents to enterprise data (SharePoint, OneDrive, Teams, ServiceNow) through a knowledge index. The agent retrieves grounded answers from live organizational data scoped to the user's M365 permissions. Configure the connection in Foundry portal → Project → Connections before wiring to an agent.

```bash
uv run python 08-advanced-agents-other/16_foundry_iq_preflight.py
uv run python 08-advanced-agents-other/16_foundry_iq_preflight.py --apply
```

**Code path.** `project_client().connections.get(FOUNDRY_IQ_CONNECTION_NAME)` → print `connection_type`, endpoint, PASS/FAIL.

**What to watch.** PASS = IQ connection found and readable. Not found = wrong `FOUNDRY_IQ_CONNECTION_NAME` or IQ not provisioned.

**References:** [Foundry IQ tutorial](https://learn.microsoft.com/azure/foundry/agents/how-to/foundry-iq-tutorial-private-inbound) · [Foundry IQ connect](https://learn.microsoft.com/azure/foundry/agents/how-to/foundry-iq-connect) · [What is Foundry IQ](https://learn.microsoft.com/azure/foundry/agents/concepts/what-is-foundry-iq)

---

### 17 — Agent optimizer

**Question answered:** How do I create an optimizer dataset and submit an agent optimization job?

**Background.** The Agent Optimizer (preview) improves a hosted agent's prompts by running it against a labeled dataset, evaluating outputs via LLM-as-judge, then suggesting system-prompt edits. This closed-loop cycle avoids manual prompt iteration. This lesson creates a 3-sample dataset and submits a coherence-targeting job without modifying any production agent.

```bash
uv run python 08-advanced-agents-other/17_agent_optimizer.py
uv run python 08-advanced-agents-other/17_agent_optimizer.py --apply --agent-name <agent>
```

**Code path.**
1. Build JSON-Lines: `[{input, expected_output, context}, ...]`.
2. `client.agents.optimizer.datasets.create(name, data=BytesIO, filename)` → `dataset.id`.
3. `client.agents.optimizer.jobs.create(agent_name, dataset_id, target_metric="coherence")` → print `job.id`.
4. Poll: `agents.optimizer.jobs.get(job_id)`. Review: Foundry portal → Agent → Optimizer.

**What to watch.** `job_id` returned = job queued. Poll until `status=="Completed"`. Suggested prompt changes appear in portal.

**References:** [Agent optimizer overview](https://learn.microsoft.com/azure/foundry/agents/concepts/agent-optimizer-overview) · [Make agent optimizer ready](https://learn.microsoft.com/azure/foundry/agents/how-to/make-agent-optimizer-ready) · [Optimize agent targets](https://learn.microsoft.com/azure/foundry/agents/how-to/optimize-agent-targets) · [Create optimizer dataset](https://learn.microsoft.com/azure/foundry/agents/how-to/create-optimizer-dataset)

---

## Stage 9 — Custom code interpreter + Azure Functions tool (lessons 18–19)

These two lessons cover sandboxed Python execution and asynchronous function integration: the key patterns for agents that need custom compute or enterprise queue-based tools.

### 18 — Custom code interpreter (ACA-backed)

**Question answered:** Is my custom code interpreter MCP server endpoint reachable and correctly configured?

**Background.** Custom code interpreter runs your Python code in an Azure Container Apps Dynamic Sessions sandbox — you choose the packages and compute. The interpreter exposes an MCP server at a `mcpServerEndpoint` URL output from your Bicep deployment. Agents connect via `MCPTool(server_url=MCP_SERVER_URL)` wrapped in a Toolbox. This is NOT the built-in code interpreter (which uses an Azure-managed sandbox with fixed packages) — it requires pre-provisioned ACA infrastructure. Preview feature registration required: `az feature register --namespace Microsoft.App --name SessionPoolsSupportMCP`.

```bash
uv run python 08-advanced-agents-other/18_custom_code_interpreter_preflight.py
uv run python 08-advanced-agents-other/18_custom_code_interpreter_preflight.py --apply
```

**Code path.**
1. Preflight: checks `MCP_SERVER_URL`, `MCP_CONNECTION_ID`, `PROJECT_ENDPOINT` set.
2. Prints `MCPToolboxTool` + `MCPTool` definition (server_url, require_approval="never").
3. `--apply`: HTTP GET to `MCP_SERVER_URL` → HTTP 200 or 405 = reachable; 401 = auth needed; 404 = wrong URL.

**What to watch.** `[OK] HTTP 405` is the expected result — MCP root expects POST for JSON-RPC, not GET. 404 = Bicep deployment did not complete or `mcpServerEndpoint` not used. Always require `require_approval="never"` for code interpreter (runs in isolated session).

**Exam cues.** Custom code interpreter = MCP tool over ACA Dynamic Sessions. Built-in code interpreter = zero-config managed sandbox. ACA session pool `poolManagementEndpoint` ≠ `mcpServerEndpoint` — use the latter.

**References:** [Custom code interpreter how-to](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/custom-code-interpreter) · [MCP tools how-to](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/model-context-protocol) · [Toolbox overview](https://learn.microsoft.com/azure/foundry/agents/concepts/toolbox-overview)

---

### 19 — Azure Functions tool (queue-based)

**Question answered:** Is my Azure Function tool's queue endpoint reachable and is the AzureFunctionTool definition correct?

**Background.** Azure Functions can serve as agent tools via queue-based integration: the agent writes a JSON message to an input queue, the function app processes it, and writes a result (with `CorrelationId`) to an output queue. This is asynchronous and decoupled — unlike function calling (lesson 35, domain 02), which executes Python in-process. AzureFunctionTool requires Standard agent setup (not Basic). The `CorrelationId` in the function response must match the incoming message — without it, the agent cannot match the result to the tool call.

```bash
uv run python 08-advanced-agents-other/19_azure_functions_tool_preflight.py
uv run python 08-advanced-agents-other/19_azure_functions_tool_preflight.py --apply
```

**Code path.**
1. Preflight: checks `STORAGE_QUEUE_ENDPOINT`, prints `AzureFunctionTool` definition with input/output queue bindings.
2. `--apply`: HTTP GET to `STORAGE_QUEUE_ENDPOINT/?comp=list` → HTTP 403/401 = storage reachable (auth required); connection error = wrong URL or egress blocked.

**What to watch.** `[OK] HTTP 403` — storage endpoint reachable (auth required, as expected). AzureFunctionTool definition: `input_binding.storage_queue.queue_name` ≠ `output_binding.storage_queue.queue_name`. Function response MUST include `CorrelationId` from the incoming message.

**Exam cues.** AzureFunctionTool requires Standard agent setup. Queue-based = async. In-process function calling (lesson 35) = synchronous. `CorrelationId` is the match key — missing it = agent never receives the result.

**References:** [Azure Functions tool how-to](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/azure-functions) · [Function calling how-to](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/function-calling)

---

## Stage 10 — Toolbox lifecycle, guardrails, and Skills (lessons 20–21)

Publishing is not governance. These lessons add immutable-version inspection, tested promotion, rollback/deletion boundaries, versioned RAI policy, preview Skills, allowed-tool scoping, and Azure API Center catalog prerequisites.

### 20 — Toolbox lifecycle and governance

**Question answered:** How do I add a Toolbox RAI policy and promote or retire versions without silently changing consumers?

**Background.** The consumer endpoint follows mutable `default_version`; the developer endpoint pins an immutable version. Adding tools, Skills, connections, or `ToolboxPolicies(RaiConfig(...))` creates a new version. Test that version before promotion and retain an approved previous version for rollback.

```bash
uv run python 08-advanced-agents-other/20_toolbox_lifecycle_governance.py \
  --rai-policy northwind-safe-tools
uv run python 08-advanced-agents-other/20_toolbox_lifecycle_governance.py \
  --apply --list
uv run python 08-advanced-agents-other/20_toolbox_lifecycle_governance.py \
  --apply --clone-with-rai 1 --rai-policy northwind-safe-tools
uv run python 08-advanced-agents-other/20_toolbox_lifecycle_governance.py \
  --apply --promote-version 2
```

**Code path.**
1. `toolbox_policies()` builds `ToolboxPolicies(rai_config=RaiConfig(...))`.
2. `toolboxes.list_versions()` / `get_version()` read immutable state.
3. `--clone-with-rai` copies tools/Skills/metadata into a new policy version and does not promote it.
4. `toolboxes.update(default_version=...)` changes every unversioned consumer.
5. `toolboxes.delete_version(...)` is destructive and requires pinned-consumer inventory.

**What to watch.** A cloned version prints its version-specific MCP endpoint. Test tools, identities, guardrails, latency, cost, and failure behavior there before promotion.

**What this does not prove.** It does not configure AI Gateway policies, downstream authorization, private DNS, or human approval for consequential tool calls.

**References:** [Create and manage Toolbox](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/toolbox) · [Tool governance](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/governance) · [Tool authentication](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/tool-authentication) · [Toolbox network isolation](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/toolbox-network-isolation)

### 21 — Skills and private catalogs

**Question answered:** How do Skills differ from tools, and what is required for private organizational catalogs?

**Background.** A Skill is preview, immutable task guidance following the Skill format; it describes **how** to perform work. `allowed_tools` constrains which tools the Skill may use. Private tool/Skill catalogs use Azure API Center for curated discovery, but catalog registration neither adds an artifact to a Toolbox nor grants runtime access.

```bash
uv run python 08-advanced-agents-other/21_skills_private_catalog_preflight.py
uv run python 08-advanced-agents-other/21_skills_private_catalog_preflight.py \
  --apply --create --skill-name incident-summary
uv run python 08-advanced-agents-other/21_skills_private_catalog_preflight.py \
  --apply --promote-version 1 --skill-name incident-summary
```

**Code path.**
1. `SkillInlineContent(..., allowed_tools=[])` creates a deliberately tool-free teaching Skill.
2. `project.beta.skills.create(..., default=False)` creates a non-default preview version.
3. `skills.update(default_version=...)` promotes only after review; `delete_version()` removes an exact version.
4. `ToolboxSkillReference(name, version)` pins the reviewed Skill in a Toolbox.

**What to watch.** The preflight distinguishes project Skills from API Center catalog entries. Current Skills API documentation does not support private endpoint access.

**Catalog boundary.** Private catalogs require Azure API Center, registered artifacts, and Azure API Center Data Reader. Remote MCP credentials stay in API Center/Foundry connections, never in catalog descriptions or Skill content.

**References:** [Skills](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/skills) · [Private Skill catalog](https://learn.microsoft.com/azure/foundry/agents/how-to/private-skill-catalog) · [Private tool catalog](https://learn.microsoft.com/azure/foundry/agents/how-to/private-tool-catalog) · [Toolbox overview](https://learn.microsoft.com/azure/foundry/agents/concepts/toolbox-overview)

---

## Stage 11 — Public and enterprise grounding (lessons 22–23)

Choose grounding by data owner and identity. Bing uses public web egress; Foundry IQ uses Search knowledge bases; Fabric IQ uses Fabric assets; Work IQ uses delegated Microsoft 365 context.

### 22 — Grounding with Bing

**Question answered:** When do I use Grounding with Bing instead of the built-in Web Search tool?

**Background.** Grounding with Bing uses a Foundry project connection to a Bing resource. Bing Custom Search preview also requires a named custom configuration. This differs from direct Responses Web Search and from Azure AI Search private corpus retrieval.

```bash
uv run python 08-advanced-agents-other/22_bing_grounding_preflight.py
uv run python 08-advanced-agents-other/22_bing_grounding_preflight.py \
  --connection-id <bing-connection-id>
uv run python 08-advanced-agents-other/22_bing_grounding_preflight.py \
  --connection-id <bing-connection-id> --custom-instance northwind-only
```

**Code path.**
1. Standard path builds `BingGroundingTool` with one `BingGroundingSearchConfiguration`.
2. Custom path builds `BingCustomSearchPreviewTool` with connection ID and `instance_name`.
3. `.as_dict()` proves the current typed payload without creating an agent or search request.

**What to watch.** Bing uses billed public egress even from network-secured Foundry. `Foundry Project Manager` creates connections; `Foundry User` creates/runs agents. Do not claim private routing.

**References:** [Grounding with Bing tools](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/bing-tools) · [Manage Grounding with Bing](https://learn.microsoft.com/azure/foundry/agents/how-to/manage-grounding-with-bing) · [Web Search tool](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/web-search)

### 23 — Foundry IQ, Fabric IQ, and Work IQ

**Question answered:** Which Microsoft IQ surface matches my data, identity, and network?

| Surface | Data | Identity | Network boundary |
|---|---|---|---|
| Foundry IQ | Search knowledge bases over Blob, OneLake, SharePoint, indexes, or remote sources | Project managed identity; optional per-user query token for trimming | Private tutorial supports private agent-to-Search and Search-to-storage paths with documented exceptions |
| Fabric IQ (preview) | Fabric ontology, semantic model, or data agent | Connection-specific delegated/managed OAuth patterns | Partial network-isolation support |
| Work IQ (preview) | Microsoft 365 email, meetings, files, chats, and business context | Delegated user/OBO only; app-only unsupported | Not supported in network-isolated Foundry projects |

```bash
uv run python 08-advanced-agents-other/23_microsoft_iq_tools_preflight.py
uv run python 08-advanced-agents-other/23_microsoft_iq_tools_preflight.py \
  --kind fabric --connection-id <id>
uv run python 08-advanced-agents-other/23_microsoft_iq_tools_preflight.py \
  --kind work --connection-id <id>
```

**Code path.** `iq_tool()` builds `FabricIQPreviewTool(require_approval="always")` or `WorkIQPreviewTool`. Existing lessons 01 and 16 cover Foundry IQ connection/inspection.

**What to watch.** Work IQ requires tenant admin setup, user consent, licensing/billing, and same-tenant delegated access. Foundry IQ permission trimming requires explicit per-user query authorization; project-only retrieval is not automatically user-trimmed.

**References:** [Foundry IQ overview](https://learn.microsoft.com/azure/foundry/agents/concepts/what-is-foundry-iq) · [Foundry IQ FAQ](https://learn.microsoft.com/azure/foundry/agents/concepts/foundry-iq-faq) · [Connect Foundry IQ](https://learn.microsoft.com/azure/foundry/agents/how-to/foundry-iq-connect) · [Private retrieval tutorial](https://learn.microsoft.com/azure/foundry/agents/how-to/foundry-iq-tutorial-private-retrieval) · [Fabric IQ](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/fabric-iq) · [Work IQ](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/work-iq)

---

## Stage 12 — Bounded preview tools (lessons 24–27)

These lessons stop at typed payloads and authorization gates. They do not create reminders, control a desktop, query enterprise data, or generate media without approved resources and an explicit remote path.

### 24 — Reminder tool

**Question answered:** Is Reminder a calendar, Routine, or hosted-agent conversation capability?

**Background.** Reminder preview is a connectionless Toolbox tool for hosted agents. It schedules a follow-up in the same conversation from 1 through 43,200 minutes; it is not an external calendar or a general workflow scheduler.

```bash
uv run python 08-advanced-agents-other/24_reminder_tool_preflight.py
```

**Code path.** `ReminderPreviewToolboxTool(name, description)` renders the current `reminder_preview` payload locally.

**What to watch.** Define explicit user intent, confirmation/cancellation UX, time-zone handling, duplicate behavior, retention, and unavailable-conversation behavior before use.

**References:** [Reminder tool](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/reminder-tool) · [Routines](https://learn.microsoft.com/azure/foundry/agents/how-to/use-routines)

### 25 — Computer Use

**Question answered:** Where must an application stop before executing a model-proposed UI action?

**Background.** Computer Use preview proposes browser/desktop actions against a sandbox. The application executes the loop and must stop on `pending_safety_checks`. This differs from Browser Automation lesson 14, which uses an Azure Playwright project connection.

```bash
uv run python 08-advanced-agents-other/25_computer_use_preflight.py
uv run python 08-advanced-agents-other/25_computer_use_preflight.py --example-approved
```

**Code path.** `acknowledge_safety_checks()` raises without explicit approval and only then creates `computer_call_output` with `acknowledged_safety_checks`.

**What to watch.** Use a disposable VM, domain/action allowlists, bounded steps/time, restricted egress/data, screenshot review, no ambient credentials, and governed recording retention.

**References:** [Computer Use](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/computer-use) · [Browser Automation](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/browser-automation)

### 26 — Fabric data agent and SharePoint

**Question answered:** How do delegated enterprise-data tools preserve user permissions?

**Background.** Fabric data agent preview requires same tenant/region and user READ permission on the agent and underlying sources; service-principal auth is unsupported. SharePoint preview uses delegated user access, supports one SharePoint tool per agent, and currently is not supported in Teams.

```bash
uv run python 08-advanced-agents-other/26_enterprise_data_tools_preflight.py
uv run python 08-advanced-agents-other/26_enterprise_data_tools_preflight.py \
  --kind fabric --connection-id <id>
uv run python 08-advanced-agents-other/26_enterprise_data_tools_preflight.py \
  --kind sharepoint --connection-id <id>
```

**Code path.** `enterprise_tool()` wraps one `ToolProjectConnection` in `MicrosoftFabricPreviewTool` or `SharepointPreviewTool`.

**What to watch.** Connection success is not permission-trimming evidence. Test with one asset the user can read and one they cannot, and verify no result or citation leaks.

**References:** [Fabric data agent](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/fabric) · [SharePoint](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/sharepoint) · [Tool authentication](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/tool-authentication)

### 27 — Image-generation agent tool

**Question answered:** How is an agent image tool different from a direct image API call?

**Background.** The preview agent tool lets an orchestrator decide when to call a compatible image deployment in the same project/region. The application still owns authorization, prompt moderation, output disclosure/provenance, storage, retention, and cost.

```bash
uv run python 08-advanced-agents-other/27_image_generation_tool_preflight.py
```

**Code path.** `ImageGenTool(model=IMAGE_MODEL, quality="low", size="1024x1024")` renders the typed `image_generation` payload without creating an agent or media.

**What to watch.** A valid payload does not prove GPT Image approval, model/orchestrator compatibility, region capacity, safety, or output governance.

**References:** [Image-generation tool](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/image-generation) · [Image generation in Foundry](https://learn.microsoft.com/azure/foundry/openai/how-to/dall-e)

---

## Stage 13 — Cross-domain observability (lesson 28)

Observability must join platform health with domain-specific quality, safety, cost, provenance, and data-governance signals. One generic trace query cannot replace those specialized controls.

### 28 — Cross-domain operational health

**Question answered:** What common non-content health evidence can I read across Domains 01–09 without querying prompts or outputs?

**Background.** The lesson maps each domain to its operational owner/signals, then supplies one Log Analytics query over `AppRequests`, `AppDependencies`, `AppTraces`, and `AppEvents`. It summarizes volume, failures, and latency and intentionally excludes `AppGenAIContent`.

```bash
uv run python 08-advanced-agents-other/28_cross_domain_observability.py
uv run python 08-advanced-agents-other/28_cross_domain_observability.py \
  --apply --workspace-id <log-analytics-workspace-guid>
```

**Code path.**
1. `DOMAIN_SIGNALS` maps all nine domains to their specialized operational evidence.
2. `KQL` uses `column_ifexists()` across four non-content tables and aggregates operation count, failures, and duration.
3. `LogsQueryClient.query_workspace(..., timespan=24h)` performs one read-only query.
4. Partial/failure status raises; empty tables print missing evidence rather than success.

**What to watch.** High failure count and latency identify operational triage targets. They do not measure answer quality, safety, relevance, permission trimming, transcription accuracy, extraction confidence, training quality, or DR readiness.

**Governance boundary.** Prompts, outputs, documents, tool arguments, and `AppGenAIContent` are excluded. If content recording is approved elsewhere, use separate protected-table RBAC, retention, redaction, and audit controls.

**References:** [Trace data](https://learn.microsoft.com/azure/foundry/observability/concepts/trace-data) · [Monitor hosted-agent logs](https://learn.microsoft.com/azure/foundry/agents/how-to/monitor-hosted-agent-logs) · [Sensitive content in traces](https://learn.microsoft.com/azure/foundry/observability/how-to/traces-sensitive-content) · [Observability troubleshooting](https://learn.microsoft.com/azure/foundry/observability/how-to/troubleshooting)

---

## Feature status and hard limits

| Feature | Status | Practical boundary |
|---|---|---|
| Foundry IQ (knowledge bases + MCP) | Partial GA | Portal + some agentic surfaces stay preview-dependent |
| Toolbox versions | Supported | Versions immutable; first becomes default |
| Toolbox tool search | **Preview** | Reduces context; does not authorize or make tools safe |
| Skills / private catalogs | **Preview** | Skills API lacks private-endpoint support; catalogs require Azure API Center |
| A2A v1.0 incoming | **Preview** | Agent card Entra-protected; not anonymously discoverable |
| A2A outbound authentication | **Preview** | Card fetch is anonymous by default; protected card needs connection + credential flag |
| Grounding with Bing | Supported; Custom Search is **Preview** | Billed public egress; not private-corpus retrieval |
| Fabric IQ / Work IQ | **Preview** | Fabric network support partial; Work IQ delegated-user only |
| Reminder | **Preview** | Hosted-agent same-conversation follow-up; not a Routine/calendar |
| Browser Automation / Computer Use | **Preview** | Sandbox, approval, tracing, and bounded authority required |
| Fabric data agent / SharePoint | **Preview** | Delegated permissions plus tenant/license constraints |
| Image-generation agent tool | **Preview** | Approved image deployment + compatible orchestrator required |
| Cross-domain KQL health view | Read-only | Non-content operations only; not quality/safety/cost/provenance evidence |
| Routines | **Preview** | One trigger + one action; needs separate `azure.ai.routines` extension |
| AI Gateway (APIM v2 integration) | Supported where APIM v2 available | Gateway + project must both show `Enabled` in portal |
| Channel publishing (M365 Copilot / Teams) | Supported | Portal-only; requires Bot Service perms + tenant policy + admin approval |
| Deprecated Agent Application publishing | Deprecated | Do NOT create new Agent Applications |
| Agent Optimizer | Supported | Python hosted-agent azd projects only |

## Troubleshooting

| Symptom | Likely cause | Resolution |
|---|---|---|
| `Expected an HTTPS ... URL without credentials, query, or fragment` | Env var contains userinfo/query/fragment | Strip credentials from URL; use `PROJECT_ENDPOINT` root form |
| Preflight: `Toolbox manifest must reference project connections, never embed credentials` | Manifest contains `client_secret`/`api_key`/etc | Move credentials to project connection; reference by connection name |
| `azd ai connection create` fails with 403 | Signed-in identity lacks `Foundry User` | Assign role at project scope; log out + back in |
| Foundry IQ connection created but retrieval empty | Search Index Data Reader not on project MI | Assign role; wait a few minutes for propagation |
| Toolbox created but agent cannot list tools | Consumer endpoint hitting a version not yet default | Wait for default promotion or hit version-specific developer endpoint |
| A2A `--apply` PATCH succeeds but caller gets 401 | Caller identity lacks `Foundry Agent Consumer` | Assign role at project or agent scope |
| Protected outbound A2A card returns 401 | Card fetch defaults anonymous | Configure project connection and `send_credentials_for_agent_card=true` |
| Toolbox promotion changes unrelated agent behavior | Consumers use unversioned endpoint | Treat default change as release; test pinned version and inventory consumers |
| Skills fail only in private project | Current Skills API lacks private endpoint support | Use an approved supported path or defer; do not bypass network policy |
| Bing violates private-egress expectation | Grounding with Bing uses public egress | Use approved egress or a private corpus such as Search/Foundry IQ |
| Work IQ cannot connect | App-only token, missing consent/license, or isolated network | Use delegated same-tenant OBO and a supported network mode |
| Enterprise tool returns too much data | Negative permission-trimming case was not tested | Test readable and unreadable assets using the actual delegated user |
| Observability query returns no rows | Wrong workspace, no ingestion, or telemetry not configured | Treat as missing evidence; verify diagnostic/tracing setup and time range |
| Routine `--dispatch` succeeds but agent auth fails | Routine can't delegate end-user identity | Agent must have its own configured identity |
| `--apply` on lesson 05 fails: version selector rejected | `--agent-version` not numeric | Use immutable numeric agent version |
| Optimizer preflight `is not optimizer-ready` | Missing `azure.yaml`/`eval.yaml`/`.agent_configs/baseline/` | Add missing assets to hosted-agent root |
| Optimizer job starts but no candidates produced | Baseline + evaluators + seed data misconfigured | Review `eval.yaml`; validate baseline before job |

## CI/CD and operational release

Preview features change frequently — automate preflight in CI but keep `--apply` manual with reviewed dispatch.

```text
PR modifies manifest / config
  → CI runs all preflights (no cloud)
  → reviewer approves
  → operator dispatches --apply manually (per lesson)
  → for toolbox / agent version / gateway: test on version-specific endpoint
  → promote default OR pin stable endpoint after test
  → monitor traces, cost, error rate
  → keep rollback: previous toolbox version, prior agent version, disabled routine
```

### What to version

- Toolbox manifests + connection names (credential-free)
- Routine YAML manifests (schedule + action; no secrets)
- Agent card schema (description + skills)
- Optimizer `eval.yaml` + baseline agent configs
- Version-selection policy per stable endpoint
- Gateway policy (rate limits, token limits) if scriptable in your org

### Release gates

| Change | Minimum gate |
|---|---|
| New Foundry IQ connection | Preflight passes; Search RBAC verified; KB query test in nonprod |
| New Toolbox version | Version-specific developer endpoint tested; no regression on prior default |
| New Toolbox RAI policy | New immutable version tested; prior default retained for rollback |
| New Skill/catalog entry | Skill version pinned; allowed tools and API Center owner/RBAC reviewed |
| A2A card change | v1.0 fetch confirms new metadata; caller identities re-verified |
| Enterprise-data tool | Delegated identity; negative permission test; retention/citation review |
| UI automation tool | Disposable sandbox; domain/action limits; approval; screenshot/action audit |
| New routine | Preflight passes; one `--dispatch` run reviewed before enabling schedule |
| Stable endpoint pin | Gateway enabled; version regression tested; rollback version known |
| Optimizer candidate | Diff reviewed; evaluators pass; safety + tool + latency + cost review |

## Security, networking, and IaC

| Decision | Recommendation | Common pitfall |
|---|---|---|
| Foundry IQ auth | `project-managed-identity` + audience `https://search.azure.com/` | Embedded Search key in manifest = permanent credential leak |
| Toolbox manifest | Reference project connections only | Bearer tokens in manifest baked into immutable version |
| Toolbox policy | Version `ToolboxPolicies` with reviewed RAI policy | Assuming a policy mutates an existing immutable version |
| Skills/catalogs | Pin version; minimize `allowed_tools`; API Center Data Reader | Treating catalog registration as runtime authorization |
| A2A caller access | `Foundry Agent Consumer` per identity at agent scope | Broad project role bypasses least-privilege for one endpoint |
| Work/SharePoint/Fabric | Delegated user identity + negative trimming tests | Connection success assumed to prove user filtering |
| UI automation | Isolated runtime + approval + bounded authority | Running against logged-in workstation or production browser profile |
| Routine execution | Agent identity with its own auth (managed identity) | Delegated user tokens in routine input = shared user context |
| Gateway | Enable in portal + confirm both gateway + project `Enabled` | APIM v1 does not support Foundry AI Gateway |
| Version pin | `FixedRatio` 100% to numeric version | Non-numeric version = validation error at PATCH |
| Optimizer secrets | `eval.yaml` seed data must not include real customer prompts/PII | Optimizer replays seed data through model = data exposure |
| azd auth | `azd auth login` inherits Azure CLI identity | Separate `azd` login can drift from `az login` context |

## Common exam traps

| Claim | Correct interpretation |
|---|---|
| "Foundry IQ replaces manual Search indexing." | False. IQ builds on Search — you still need indexed knowledge sources. |
| "Toolbox tool search authorizes tool calls." | False. It reduces context for tool selection; authorization is separate. |
| "Skills are executable tools." | False. Skills are versioned instructions; tools are callable capabilities. |
| "Private catalog entry is already in every Toolbox." | False. A Toolbox version must reference selected artifacts. |
| "A2A card is publicly discoverable." | False. v1.0 card is Entra-protected. |
| "Outbound A2A always sends credentials for the card." | False. Card fetch defaults anonymous unless configured. |
| "Grounding with Bing stays inside a private Foundry network." | False. Bing grounding uses public egress. |
| "Work IQ can use app-only managed identity." | False. Current Work IQ requires delegated user/OBO auth. |
| "Reminder is a durable workflow scheduler." | False. It is a same-conversation hosted-agent preview tool. |
| "Computer Use safety checks are informational." | False. Stop and require explicit human acknowledgement. |
| "Enabling A2A grants caller access." | False. PATCHes protocol config only; assign `Foundry Agent Consumer` separately. |
| "Routines can invoke as end user." | False. Cannot delegate end-user identity; use agent's own identity. |
| "Routines can chain multiple agents." | False. Routine = one trigger + one action. Use workflow for orchestration. |
| "AI Gateway is API Management v1." | False. Requires APIM v2. |
| "First Toolbox version is mutable." | False. All versions immutable; first becomes default. |
| "Consumer endpoint targets specific version." | False. Consumer resolves current default; developer targets `.../versions/<v>/mcp`. |
| "Agent Optimizer deploys candidates automatically." | False. Applies local source only; deploy via separate `azd deploy`. |
| "Agent Application publishing is current." | False. Deprecated — use agent stable-endpoint publishing. |
| "Channel publish (M365/Teams) can be scripted." | False. Portal-only after review of Bot Service + tenant + admin approval. |

## Objective coverage and limits

Runnable evidence in this folder covers: creating keyless Foundry IQ project connections, publishing and managing immutable Toolbox versions, cloning a versioned Toolbox RAI policy, managing preview Skill versions, enabling A2A v1.0 discovery + agent cards, creating and dispatching routines, pinning stable-endpoint traffic, and running Agent Optimizer. Local typed preflights cover Bing, Fabric/Work IQ, Reminder, Computer Use safety acknowledgement, Fabric data agent, SharePoint, Browser Automation, and image-generation tools. Lesson 28 adds an opt-in read-only non-content Log Analytics health query and a Domain 01–09 signal map.

It does **not** create private catalogs/API Center, Bing/Fabric/Microsoft 365 connections, knowledge bases, Playwright workspaces, reminders, computer sessions, enterprise queries, or images. It does not publish to Microsoft 365 Copilot/Teams, deploy optimized candidates, provision APIM v2, or prove end-to-end network/permission trimming. Preview features can change region, subscription, tenant, model, and license availability independently.

## References

### Foundry IQ

- [Foundry IQ concepts](https://learn.microsoft.com/azure/foundry/agents/concepts/what-is-foundry-iq)
- [Foundry IQ agent connection](https://learn.microsoft.com/azure/foundry/agents/how-to/foundry-iq-connect)

### Toolbox + A2A

- [Toolbox concepts](https://learn.microsoft.com/azure/foundry/agents/concepts/toolbox-overview)
- [Toolbox management](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/toolbox)
- [Tool governance](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/governance)
- [Tool authentication](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/tool-authentication)
- [Toolbox network isolation](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/toolbox-network-isolation)
- [Skills](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/skills)
- [Private Skill catalog](https://learn.microsoft.com/azure/foundry/agents/how-to/private-skill-catalog)
- [Private tool catalog](https://learn.microsoft.com/azure/foundry/agents/how-to/private-tool-catalog)
- [Incoming A2A](https://learn.microsoft.com/azure/foundry/agents/how-to/enable-agent-to-agent-endpoint)
- [A2A authentication](https://learn.microsoft.com/azure/foundry/agents/concepts/agent-to-agent-authentication)

### Grounding and current preview tools

- [Grounding with Bing](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/bing-tools)
- [Fabric IQ](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/fabric-iq)
- [Work IQ](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/work-iq)
- [Reminder tool](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/reminder-tool)
- [Computer Use](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/computer-use)
- [Browser Automation](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/browser-automation)
- [Fabric data agent](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/fabric)
- [SharePoint](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/sharepoint)
- [Image-generation tool](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/image-generation)

### Observability

- [Trace data](https://learn.microsoft.com/azure/foundry/observability/concepts/trace-data)
- [Sensitive content in traces](https://learn.microsoft.com/azure/foundry/observability/how-to/traces-sensitive-content)
- [Observability troubleshooting](https://learn.microsoft.com/azure/foundry/observability/how-to/troubleshooting)

### Routines + Gateway + Publishing

- [Routines](https://learn.microsoft.com/azure/foundry/agents/how-to/use-routines)
- [AI Gateway](https://learn.microsoft.com/azure/foundry/configuration/enable-ai-api-management-gateway-portal)
- [AI Gateway (agents how-to)](https://learn.microsoft.com/azure/foundry/agents/how-to/ai-gateway)
- [Configure agent (stable endpoint)](https://learn.microsoft.com/azure/foundry/agents/how-to/configure-agent)
- [Current publishing model](https://learn.microsoft.com/azure/foundry/agents/how-to/migrate-agent-applications)

### Hosted-agent lifecycle

- [Hosted-agent contract](https://learn.microsoft.com/azure/foundry/agents/concepts/hosted-agent-contract)
- [Hosted-agent permissions](https://learn.microsoft.com/azure/foundry/agents/concepts/hosted-agent-permissions)
- [Agent identity](https://learn.microsoft.com/azure/foundry/agents/concepts/agent-identity)
- [Agent YAML reference](https://learn.microsoft.com/azure/foundry/agents/concepts/agent-yaml-reference)
- [Capability hosts](https://learn.microsoft.com/azure/foundry/agents/concepts/capability-hosts)
- [Runtime components](https://learn.microsoft.com/azure/foundry/agents/concepts/runtime-components)
- [Standard agent setup](https://learn.microsoft.com/azure/foundry/agents/concepts/standard-agent-setup)
- [Limits, quotas, regions](https://learn.microsoft.com/azure/foundry/agents/concepts/limits-quotas-regions)
- [Deploy hosted agent](https://learn.microsoft.com/azure/foundry/agents/how-to/deploy-hosted-agent)
- [Deploy hosted-agent code](https://learn.microsoft.com/azure/foundry/agents/how-to/deploy-hosted-agent-code)
- [Deploy hosted agent with private ACR](https://learn.microsoft.com/azure/foundry/agents/how-to/deploy-hosted-agent-private-azure-container-registry)
- [Configure hosted-agent env variables](https://learn.microsoft.com/azure/foundry/agents/how-to/configure-hosted-agent-env-variables)
- [Configure hosted-agent telemetry](https://learn.microsoft.com/azure/foundry/agents/how-to/configure-hosted-agent-telemetry)
- [Invoke hosted agent](https://learn.microsoft.com/azure/foundry/agents/how-to/invoke-hosted-agent)
- [Monitor hosted-agent logs](https://learn.microsoft.com/azure/foundry/agents/how-to/monitor-hosted-agent-logs)
- [Test hosted agent](https://learn.microsoft.com/azure/foundry/agents/how-to/test-hosted-agent)
- [azure.yaml reference](https://learn.microsoft.com/azure/foundry/agents/concepts/azure-yaml-reference)
- [Debug hosted agent](https://learn.microsoft.com/azure/foundry/agents/how-to/debug-hosted-agent)
- [Agent Doctor](https://learn.microsoft.com/azure/foundry/agents/how-to/agent-doctor)
- [Agent Inspector](https://learn.microsoft.com/azure/foundry/agents/how-to/agent-inspector)
- [Disable classic agents](https://learn.microsoft.com/azure/foundry/agents/how-to/disable-classic-agents)

### Private-network Foundry IQ tutorial

- [Private Foundry IQ overview](https://learn.microsoft.com/azure/foundry/agents/how-to/foundry-iq-tutorial-private-overview)
- [Private inbound](https://learn.microsoft.com/azure/foundry/agents/how-to/foundry-iq-tutorial-private-inbound)
- [Private outbound](https://learn.microsoft.com/azure/foundry/agents/how-to/foundry-iq-tutorial-private-outbound)
- [Private retrieval](https://learn.microsoft.com/azure/foundry/agents/how-to/foundry-iq-tutorial-private-retrieval)

### Agent CLI + tooling

- [Init agent project](https://learn.microsoft.com/azure/foundry/agents/how-to/init-agent-project)
- [Install CLI Foundry extensions](https://learn.microsoft.com/azure/foundry/agents/how-to/install-cli-foundry-extensions)
- [Author azure.yaml](https://learn.microsoft.com/azure/foundry/agents/how-to/author-azure-yaml)

### Agent 365 + protocols + migration

- [Agent 365](https://learn.microsoft.com/azure/foundry/agents/how-to/agent-365)
- [Agent Applications migration](https://learn.microsoft.com/azure/foundry/agents/how-to/agent-applications)
- [Add protocol adapter](https://learn.microsoft.com/azure/foundry/agents/how-to/add-protocol-adapter)
- [Connected models](https://learn.microsoft.com/azure/foundry/agents/how-to/connected-models)

### MCP

- [MCP get started](https://learn.microsoft.com/azure/foundry/mcp/get-started)
- [MCP available tools](https://learn.microsoft.com/azure/foundry/mcp/available-tools)
- [Build your own MCP server](https://learn.microsoft.com/azure/foundry/mcp/build-your-own-mcp-server)
- [MCP security best practices](https://learn.microsoft.com/azure/foundry/mcp/security-best-practices)

### Custom code interpreter + Azure Functions tool

- [Custom code interpreter how-to](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/custom-code-interpreter)
- [Azure Functions tool how-to](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/azure-functions)
- [Set up Key Vault connection](https://learn.microsoft.com/azure/foundry/how-to/set-up-key-vault-connection)

### Compliance and Responsible AI (agents)

- [Agents transparency note](https://learn.microsoft.com/azure/foundry/responsible-ai/agents/transparency-note)
- [Agents data privacy + security](https://learn.microsoft.com/azure/foundry/responsible-ai/agents/data-privacy-security)

### Related domains

- [Domain 2: Generative AI and agents](../02-generative-ai-and-agents/README.md) — core agent lifecycle
- [Domain 5: Information extraction](../05-information-extraction/README.md) — Search + RAG foundations
- [Domain 7: Production platform](../07-production-platform-other/README.md) — private cell + governance
