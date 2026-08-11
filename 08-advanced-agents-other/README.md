# Domain 8: Advanced agents and current Foundry operations

> Preflight-first labs for advanced Foundry agent capabilities: Foundry IQ, Toolbox, incoming A2A, routines, AI Gateway, and Agent Optimizer. Run commands from repository root: `uv run python 08-advanced-agents-other/<lesson>.py`.
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
```

Lessons follow this progression in six stages, each optional. These are supplemental to the AI-103 exam objectives, not a replacement for the core agent lessons in domain 02.

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
```

Never add API keys, connection strings, or bearer tokens to `.env`, manifests, prompts, agent cards, or routine inputs. Credentials live in project connections, managed identity, Key Vault, or your CI secret store.

### Safe run order

1. **Preflight every lab first** — all six default commands read local input only.
2. Confirm region + preview access + billing + network path + role assignments outside these labs.
3. **Lab 01 --apply** first if agents will use knowledge — grant `Search Index Data Reader` before apply.
4. **Lab 02 --apply** to publish toolbox after knowledge connection exists.
5. **Lab 03 --apply** after agent deployed; run `--apply --verify` to confirm card is live.
6. **Lab 04 --apply** ONLY after inspecting manifest; add `--dispatch` for one controlled run before enabling schedule.
7. **Lab 05 --apply** ONLY after gateway is `Enabled` on both gateway + project in Foundry portal.
8. **Lab 06 --apply** ONLY against a Python hosted-agent azd project with reviewed `eval.yaml`.

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

## Lesson map

| # | Lesson | Runnable objective | Status / limitation |
|---:|---|---|---|
| 01 | [Foundry IQ connection](01_foundry_iq_connection_preflight.py) | Create keyless RemoteTool MCP connection to a knowledge base | `--apply` creates project connection; does not build the knowledge base |
| 02 | [Toolbox publish](02_toolbox_publish_preflight.py) | Publish first immutable Toolbox version from manifest | `--apply` creates toolbox + first version (becomes default) |
| 03 | [A2A agent card](03_a2a_agent_card_preflight.py) | Enable A2A v1.0 + write agent card | `--apply` PATCHes agent; `--verify` fetches card |
| 04 | [Routines](04_routines_preflight.py) | Create scheduled routine with disabled default | `--apply` creates routine; `--dispatch` runs once |
| 05 | [Gateway + publish](05_gateway_publishing_preflight.py) | Pin stable endpoint to one reviewed agent version | `--apply` PATCHes `version_selector`; channel publish is portal-only |
| 06 | [Agent Optimizer](06_agent_optimizer_preflight.py) | Run optimization or apply candidate locally | `--apply` requires Python hosted-agent azd project; never deploys |

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
4. `--verify` — additional `az rest --method get` on card URL.

**What to watch.** Preflight: both A2A URLs printed. `--apply`: PATCH success + `Enabled current Responses and A2A protocols. v1.0 card: <url>`. `--verify`: fetched card JSON printed.

**What this does NOT do.**
- Does not grant callers access. Assign `Foundry Agent Consumer` role separately.
- Does not make an existing Responses endpoint A2A-capable — the PATCH is required.
- Does not migrate deprecated Agent Applications.

**References:** [Incoming A2A](https://learn.microsoft.com/azure/foundry/agents/how-to/enable-agent-to-agent-endpoint) · [Configure agent](https://learn.microsoft.com/azure/foundry/agents/how-to/configure-agent)

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

## Feature status and hard limits

| Feature | Status | Practical boundary |
|---|---|---|
| Foundry IQ (knowledge bases + MCP) | Partial GA | Portal + some agentic surfaces stay preview-dependent |
| Toolbox versions | Supported | Versions immutable; first becomes default |
| Toolbox tool search | **Preview** | Reduces context; does not authorize or make tools safe |
| A2A v1.0 incoming | **Preview** | Agent card Entra-protected; not anonymously discoverable |
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
| A2A card change | v1.0 fetch confirms new metadata; caller identities re-verified |
| New routine | Preflight passes; one `--dispatch` run reviewed before enabling schedule |
| Stable endpoint pin | Gateway enabled; version regression tested; rollback version known |
| Optimizer candidate | Diff reviewed; evaluators pass; safety + tool + latency + cost review |

## Security, networking, and IaC

| Decision | Recommendation | Common pitfall |
|---|---|---|
| Foundry IQ auth | `project-managed-identity` + audience `https://search.azure.com/` | Embedded Search key in manifest = permanent credential leak |
| Toolbox manifest | Reference project connections only | Bearer tokens in manifest baked into immutable version |
| A2A caller access | `Foundry Agent Consumer` per identity at agent scope | Broad project role bypasses least-privilege for one endpoint |
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
| "A2A card is publicly discoverable." | False. v1.0 card is Entra-protected. |
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

Runnable evidence in this folder covers: creating keyless Foundry IQ project connections, publishing immutable Toolbox versions, enabling A2A v1.0 discovery + agent cards, creating and dispatching routines, pinning stable-endpoint traffic to a reviewed agent version, and running Agent Optimizer on Python hosted-agent projects.

It does **not** create knowledge bases, publish to Microsoft 365 Copilot or Teams channels, migrate deprecated Agent Applications, deploy optimized candidates, or provision APIM v2 gateways. It does not test end-to-end network paths — you must verify from your intended caller identity + network. Preview features can change region + subscription + model availability independently.

## References

### Foundry IQ

- [Foundry IQ concepts](https://learn.microsoft.com/azure/foundry/agents/concepts/what-is-foundry-iq)
- [Foundry IQ agent connection](https://learn.microsoft.com/azure/foundry/agents/how-to/foundry-iq-connect)

### Toolbox + A2A

- [Toolbox concepts](https://learn.microsoft.com/azure/foundry/agents/concepts/toolbox-overview)
- [Toolbox management](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/toolbox)
- [Incoming A2A](https://learn.microsoft.com/azure/foundry/agents/how-to/enable-agent-to-agent-endpoint)

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

### Compliance and Responsible AI (agents)

- [Agents transparency note](https://learn.microsoft.com/azure/foundry/responsible-ai/agents/transparency-note)
- [Agents data privacy + security](https://learn.microsoft.com/azure/foundry/responsible-ai/agents/data-privacy-security)

### Related domains

- [Domain 2: Generative AI and agents](../02-generative-ai-and-agents/README.md) — core agent lifecycle
- [Domain 5: Information extraction](../05-information-extraction/README.md) — Search + RAG foundations
- [Domain 7: Production platform](../07-production-platform-other/README.md) — private cell + governance
