# Domain 1: Plan and manage Microsoft Foundry

> Study guide and runnable labs for deployment planning, access, guardrails,
> agents, evaluation concepts, and operations. Run commands from repository
> root: `uv run python 01-plan-and-manage/<lesson>.py`.
>
> This domain explains service behavior; a script is evidence only for its
> documented path. Preview availability, quota, model support, and permissions
> remain subscription and region specific.

## What this domain teaches

A production AI feature is more than a model call:

```text
Choose model and deployment
        ↓
Plan residency, throughput, quota, cost, and fallback
        ↓
Authenticate workload and grant least privilege
        ↓
Apply guardrails at input, tool, and output boundaries
        ↓
Evaluate changes, trace runtime behavior, and release through CI/CD
```

The lessons follow that lifecycle. They do not create a complete production
application or prove every Foundry feature. They teach decisions, boundaries,
and the smallest runnable evidence for each subject.

## Foundry mental model

### Resource, project, deployment, endpoint

| Term | Meaning | Important distinction |
|---|---|---|
| **Microsoft Foundry resource** | Azure resource that owns account-level configuration, deployments, quota context, and access boundaries. | A resource is not a model deployment. |
| **Foundry project** | Workspace beneath a Foundry resource for project APIs, agents, and collaboration. | Project scope can be narrower than resource scope. |
| **Model** | Underlying model family/version, such as `gpt-4.1-mini`. | A model name is not necessarily callable. |
| **Deployment** | Named, configured instance of a model with SKU/capacity. | `model=` normally receives deployment name, not model-family label. |
| **Endpoint** | URL/API surface called by a client. | Endpoint determines API and RBAC assumptions; do not swap URLs. |
| **Guardrail** | Configured policy applied at service intervention points. | It is not identical to an explicit Content Safety API request. |

One model can have multiple deployments: development and production, different
regions, or different capacity and policy decisions. A deployment name is the
stable application configuration value. List deployments before assuming a
name exists.

### Endpoint map: same organization, different surfaces

| Surface | Environment setting | Shape | Typical use | Starting role |
|---|---|---|---|---|
| Foundry account/control plane helper | `FOUNDRY_ENDPOINT` | `https://<resource>.services.ai.azure.com` | D1 deployment/quota account lookup | Appropriate control-plane role |
| Foundry project API | `PROJECT_ENDPOINT` | `https://<resource>.services.ai.azure.com/api/projects/<project>` | Project APIs, hosted-agent list, project Responses client | `Foundry User` at project/resource |
| Direct Azure OpenAI-compatible API | `AZURE_OPENAI_ENDPOINT` | `https://<resource>.openai.azure.com` | Direct Responses/Chat Completions calls | `Cognitive Services OpenAI User` on direct resource |
| Azure AI Content Safety | `CONTENT_SAFETY_ENDPOINT` | `https://<resource>.cognitiveservices.azure.com` | Explicit moderation, shields, Task Adherence, blocklists | Appropriate Content Safety access |

`FOUNDRY_ENDPOINT` and `PROJECT_ENDPOINT` are not interchangeable. A direct
OpenAI client does not infer its endpoint or authorization from a project URL.
Similarly, a Foundry project role does not automatically mean a principal has
the direct Azure OpenAI data action required by a different resource surface.

### Planes and responsibility boundaries

```text
Control plane: create/configure Azure resources and deployments
  CognitiveServicesManagementClient, Azure portal, IaC

Data plane: send inference requests and use project/agent APIs
  OpenAI or project client, application identity

Application plane: decide retry, block/escalate, redact/log, and release
  Your code and operational process
```

A control-plane role such as `Owner` or `Contributor` does not by itself grant
every inference data action. Conversely, an inference role does not grant
permission to deploy models. Match both the endpoint and action.

## Before running a lesson

### Setup

From repository root:

```bash
uv sync
cp .env.example .env
az login
```

Use a nonproduction Foundry resource for deployment, blocklist, and guardrail
experiments. Never commit `.env`, API keys, connection strings, customer
content, or production prompts.

Populate values appropriate to the lesson:

```dotenv
# Foundry resource and project
FOUNDRY_ENDPOINT=https://<resource>.services.ai.azure.com
PROJECT_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<project>
AZURE_OPENAI_ENDPOINT=https://<resource>.openai.azure.com

# Deployment names, not model-family labels
DEFAULT_MODEL=<deployment-name>
MODEL_ROUTER_DEPLOYMENT=model-router

# Content Safety and management context
CONTENT_SAFETY_ENDPOINT=https://<content-safety-resource>.cognitiveservices.azure.com
AZURE_SUBSCRIPTION_ID=<subscription-id>
AZURE_RESOURCE_GROUP=<resource-group>

# Optional: lesson 18 manual telemetry export
APPLICATIONINSIGHTS_CONNECTION_STRING=<connection-string>
```

`DefaultAzureCredential` commonly uses Azure CLI authentication after `az login`
on a workstation. In Azure, it commonly uses a managed identity or workload
identity. Credential-chain success does **not** prove which credential supplied
the token; use identity and service logs when that distinction matters.

For a managed identity, enable or attach the identity, then assign roles to its
**principal object ID**. Do not substitute its client ID in a role assignment.

### Safe learning order

1. Run **02** first: local deployment-type reference, no cloud call.
2. Run **01** and **05** next: inventory and quota reads.
3. Make **07** pass before treating project-authenticated lessons as usable.
4. Use **04**, **06**, **09–14**, **16**, and **17** with a low-cost,
   nonproduction deployment; each makes live service calls where stated.
5. Review model, region, SKU, capacity, and cost before **03**.
6. Treat **08** as an access review; leave its mutation helper commented unless
   intentionally changing access.
7. Run **15** only when ready to create a persistent lab blocklist.
8. Run **18** only after reviewing telemetry destination and data handling.

### Costs and side effects

| Lesson(s) | Side effect or cost |
|---|---|
| 01, 05, 08 | Live read; 05 needs subscription-level quota visibility. |
| 02, 12 | Local reference only. |
| 03 | Creates or updates a deployment; allocation and billing implications. |
| 04, 06, 07, 09–11, 13–14, 16–18 | Model and/or Content Safety requests; input, output, retries, and selected model affect cost. |
| 15 | Creates/updates persistent `northwind-exam-blocklist` and items; matching can take time to propagate. |
| 18 | May export prompt previews, output-derived attributes, token metadata, and latency to telemetry. |

Provisioned deployments reserve PTU capacity and incur hourly capacity cost
while present, including idle time. A PTU is reserved throughput capacity, **not
a prepaid token bucket** and not per-token billing. PTU quota approval does not
guarantee capacity in every requested region.

## Glossary

| Term | Study definition |
|---|---|
| **LLM / SLM** | Large models favor broad capability; smaller models often reduce latency and cost for bounded tasks. |
| **Multimodal** | Model accepts or generates more than one modality, such as text and image. |
| **SKU** | Deployment tier/configuration that affects residency, billing, and throughput behavior. |
| **Region** | Specific Azure datacenter geography location, such as `eastus`. |
| **Data zone** | Multi-region geographic boundary, such as EU, US, or APAC; not one named Azure region. |
| **Global deployment** | Inference may be processed across eligible global infrastructure; validate data handling for your workload. |
| **Regional deployment** | Inference constrained to selected Azure region, subject to feature/model support. |
| **TPM / RPM** | Tokens per minute and requests per minute rate limits. Either can cause HTTP 429. |
| **PTU** | Provisioned Throughput Unit: reserved hourly capacity for supported provisioned deployments. |
| **429** | Too Many Requests; use bounded backoff for transient throttling, then surface/queue/fail safely. |
| **Guardrail** | Deployment/agent policy that can annotate or block at defined intervention points. |
| **Content Safety API** | Explicit service API for text/image moderation and related safety capabilities. |
| **Prompt Shield** | Injection-defense control for direct user attacks or indirect document/tool-content attacks. |
| **Spotlighting** | Preview document-trust defense; only Chat Completions, no agents. |
| **PII filter** | Preview output/completion guardrail behavior for personally identifiable information. |
| **Task Adherence** | Preview signal that compares agent tool-plan behavior to user intent. |
| **Blocklist** | Domain-specific terms/patterns that generic harm classifiers do not cover. |
| **Evaluator** | Repeatable rubric/scoring process for model output; an LLM self-review is not automatically a Foundry evaluation run. |
| **Trace / span** | Structured record of an operation and attributes such as latency and token metadata. |
| **RBAC** | Azure role-based access control: principal, role, scope, and action must all align. |

## Decision tables

### Choose model capability before deployment mechanics

| Need | Starting choice | Validate |
|---|---|---|
| Broad reasoning or complex synthesis | Strong general/reasoning model | Latency, price, quality on representative tasks. |
| Narrow, high-volume classification/extraction | Smaller model | Accuracy edge cases, language coverage, fallback behavior. |
| Text plus image/audio | Compatible multimodal model | Input formats, token/image pricing, regional availability. |
| Embeddings/retrieval | Embedding deployment | Dimensions, index compatibility, retrieval quality. |
| Language, translation, speech, moderation | Purpose-built Azure AI service where suitable | Feature limits and endpoint/role model. |
| Mixed prompt complexity | Model Router deployment | Router availability, allowed models, cost/quality behavior. |

Do not choose by benchmark headline alone. Test representative prompts, safety
behavior, latency, required region, tool use, and total request cost.

### Deployment and residency decision flow

```text
Need strict one-region inference residency?
  Yes → Regional Standard or Regional Provisioned, if model/region supports it.
  No  → Need a geographic data boundary?
           Yes → Data Zone Standard / Data Zone Provisioned / Data Zone Batch.
           No  → Global Standard is common default where policy permits.

Need predictable reserved capacity at sustained utilization?
  Yes → evaluate supported Provisioned/PTU deployment and its hourly cost.
  No  → Standard pay-as-you-go usually starts simpler.

Large asynchronous workload and supported model/tier?
  Yes → evaluate Batch.
  No  → online deployment.
```

| Deployment family | Residency scope | Billing/capacity concept | Best fit | Caution |
|---|---|---|---|---|
| Global Standard | Eligible global infrastructure | Pay for usage; quota applies | General default when policy permits | Not single-region residency. |
| Data Zone Standard | Geographic zone | Pay for usage; zone/model quota | Geographic residency requirement | Zone is not a single region. |
| Regional Standard | One Azure region | Pay for usage; regional quota | Strict locality/latency constraints | Often lower availability/quota than global. |
| Provisioned (Global/Data Zone/Regional where offered) | Tier-specific | Reserved PTUs, hourly capacity cost | Stable high utilization/predictability | Capacity is reserved rate, not token billing. |
| Batch | Global/Data Zone where offered | Asynchronous discounted processing | Large noninteractive jobs | Availability and completion expectations vary. |
| Developer | Limited development scenario where offered | Service-defined development limits | Testing supported scenarios | Never assume production SLA/lifetime. |
| Managed compute / MaaS | Model/service-specific | GPU-hour or Marketplace/service pricing | Partner/OSS model scenarios | Different service, pricing, and operations model. |

Model availability, SKU names, quotas, supported regions, capacity units, and
billing are service-version dependent. Read current portal/docs before making a
production commitment.

### Throughput and rate-limit decisions

| Symptom | Likely cause | First response |
|---|---|---|
| HTTP 429 | RPM/TPM, quota, or transient saturation | Honor retry guidance where present; bounded exponential backoff with jitter. |
| Persistent 429 | Sustained demand exceeds capacity/limit | Queue, reduce demand, request quota, use supported spillover/fallback, or change deployment design. |
| High latency without 429 | Model size, output length, network, tool/RAG path | Measure spans, cap output, test model/region, profile full path. |
| `404 DeploymentNotFound` | Model family used instead of deployment name, wrong endpoint, or deployment absent | List deployments; correct setting. Do not retry blindly. |
| `401` / `403` | Wrong endpoint, role, scope, or identity | Inspect endpoint and effective principal/assignment. Do not retry blindly. |

A deployment `capacity` value is not a universal TPM conversion. Standard quota
can be pooled by subscription, model/SKU, and location or zone; use lesson 05
and service quota views rather than assuming every deployment owns an isolated
bucket. For provisioned SKUs, capacity represents PTUs and model-specific
throughput differs by model and configuration.

## Lesson map

| # | Lesson | Runnable objective | Status / limitation |
|---:|---|---|---|
| 01 | [Model catalog](01_model_catalog_list.py) | List Foundry project deployments. | Live read. |
| 02 | [Deployment types](02_deployment_types.py) | Compare deployment families. | Local reference; availability varies. |
| 03 | [Deploy model](03_deploy_model.py) | Create/update Global Standard deployment through management plane. | Writes cloud state and can allocate billable capacity. |
| 04 | [Model Router](04_model_router.py) | Route Responses API requests through router; print selected model. | Live inference; router deployment required. |
| 05 | [Quotas](05_quotas_and_tpm.py) | List deployments and location usage. | Live control-plane read; subscription permission. |
| 06 | [Backoff](06_rate_limit_backoff.py) | Retry transient Responses API errors. | Five live calls. |
| 07 | [Identity smoke test](07_managed_identity_agent.py) | Validate project Entra auth, hosted-agent listing, project Responses call. | Live read and inference. |
| 08 | [RBAC policies](08_rbac_role_policies.py) | List role assignments; opt-in assignment helper. | Read by default. |
| 09 | [Safety filters](09_content_safety_filters.py) | Compare deployment guardrail and explicit Content Safety calls. | Live calls; intentionally unsafe test text. |
| 10 | [User Prompt Shields](10_prompt_shields_user.py) | Detect direct jailbreak attempts. | Live safety; deployment guardrail path optional. |
| 11 | [Document Prompt Shields](11_prompt_shields_docs.py) | Detect injection in OCR/document content. | Live safety; actual channel caveat applies. |
| 12 | [Spotlighting](12_spotlighting.py) | Inspect documented preview request/integration boundary. | Local reference only. |
| 13 | [PII filter](13_pii_filter.py) | Inspect output filter annotations with synthetic data. | Live inference; preview. |
| 14 | [Task Adherence](14_task_adherence.py) | Analyze aligned/misaligned tool plans. | Live preview API; app must act on signal. |
| 15 | [Blocklists](15_blocklists.py) | Create/update and test Content Safety blocklist. | Persistent write; propagation delay. |
| 16 | [Agent basics](16_agent_basics.py) | Code-defined instructions and linked Responses turns. | Live inference; not a Foundry agent resource. |
| 17 | [Self-critique](17_evaluator_groundedness.py) | Draft, critique, regenerate. | Live inference; not a built-in evaluator/run. |
| 18 | [Manual tracing](18_agent_tracing.py) | Emit application OpenTelemetry span and metadata. | Live calls; not full Foundry tracing. |

## Lessons 01–08: plan, deploy, operate, secure

### 01 — Model catalog list

**Question answered:** What can this project call right now?

Run:

```bash
uv run python 01-plan-and-manage/01_model_catalog_list.py
```

The script lists existing deployments from project context. Capture the
**deployment name**, model, and type before configuring `DEFAULT_MODEL` or
writing calls. Treat a catalog listing as an inventory snapshot, not proof that
a deployment is healthy, affordable, or authorized for every principal.

**Study points**

- `model=` is generally deployment name. A model-family name causes
  `DeploymentNotFound` unless it happens to equal a deployment name.
- A deployment's name is an application contract; isolate it in environment or
  deployment configuration, not scattered literals.
- Model selection includes capability, region, compliance, quota, throughput,
  context, modality, price, and evaluation results.

### 02 — Deployment types

**Question answered:** Which deployment type fits residency, traffic, and cost?

Run locally:

```bash
uv run python 01-plan-and-manage/02_deployment_types.py
```

Use this as a decision reference, then validate exact model/SKU availability in
the current Foundry portal and documentation.

**Region concepts**

- An Azure **region** is a particular datacenter geography location.
- A **geography/data zone** spans multiple regions inside a broader boundary.
- Global capacity can improve availability and quota options, but it changes
  residency assumptions.
- Regional deployment is for a concrete location requirement, not a generic
  "EU" requirement.

**Exam traps**

- Data Zone is not one region.
- PTUs reserve hourly capacity; they do not pre-buy tokens or make all 429s
  impossible under every workload condition.
- Batch is an asynchronous workload pattern, not a low-latency serving tier.
- Managed compute and serverless partner-model offerings can have a different
  billing/operations model from Azure OpenAI Standard deployments.

### 03 — Deploy a model

**Question answered:** How is deployment configuration automated safely?

Run only after selecting model, SKU, region, capacity, and cleanup owner:

```bash
uv run python 01-plan-and-manage/03_deploy_model.py
```

The lesson uses `CognitiveServicesManagementClient`, which is a **management
plane** client. It derives account name from `FOUNDRY_ENDPOINT`, then performs
create-or-update for one Global Standard deployment. It is intentionally an
idempotent-style automation example, not a deployment policy engine.

Before production automation, pin or deliberately manage version selection,
validate model availability and allowed SKU, set desired naming conventions,
record ownership/tags, and plan rollback. A successful provisioning state does
not prove the application has correct data-plane permissions or that a
workload meets its SLO.

### 04 — Model Router through Responses API

**Question answered:** When can one router deployment select model per request?

Run after creating supported `model-router` deployment:

```bash
uv run python 01-plan-and-manage/04_model_router.py
```

The script calls the **project-scoped Responses API** with
`model=MODEL_ROUTER_DEPLOYMENT`, then prints `response.model` to show the
model chosen for that request. Router is Responses-supported in this lab. Do
not revive older guidance claiming router only works through Chat Completions.

Router can simplify an application that receives mixed-complexity prompts, but
it is not a substitute for product evaluation. Measure quality, latency, cost,
allowed model set, regional availability, safety behavior, and observability.
Keep a deliberate fallback plan for router unavailability or workloads needing
strict model selection.

### 05 — Quotas and throughput

**Question answered:** Where is capacity allocated and how close am I to quota?

```bash
uv run python 01-plan-and-manage/05_quotas_and_tpm.py
```

The lesson lists account deployments and `usages.list(location)`. Quota is a
control-plane observation, not an invoice. It needs a subscription-level role
such as `Cognitive Services Usages Reader` or subscription `Reader`; resource
scope alone can be insufficient.

Use quota output to locate allocation and pool pressure. It does not tell you
actual prompt mix, output lengths, retry amplification, end-user latency, or
monthly spend. Combine it with application metrics and cost management data.

### 06 — Rate-limit backoff

**Question answered:** Which failures are safe to retry, and how?

```bash
uv run python 01-plan-and-manage/06_rate_limit_backoff.py
```

The lesson sends five requests and retries `RateLimitError` and transient
connection failures with bounded exponential backoff plus jitter. Jitter avoids
synchronized retry storms; a maximum attempt count prevents infinite waiting.

```text
429 / transient connection failure
  → wait with exponential backoff + jitter
  → retry within a bounded budget
  → surface failure or queue work after budget exhausted
```

Do **not** retry a configuration or access bug as though it were transient:
`400`, `401`, `403`, and `404` need diagnosis. At scale, complement client
retry with backpressure, request shaping, idempotency where an operation can
mutate state, circuit breaking, queueing, and explicit user-facing degradation.

### 07 — Managed identity and keyless project auth

**Question answered:** Can this workload use Entra ID end-to-end?

```bash
uv run python 01-plan-and-manage/07_managed_identity_agent.py
```

This is the practical must-pass smoke test. It creates a project client with
`DefaultAzureCredential`, lists hosted agents, obtains the project-scoped
OpenAI client, and makes one Responses request. Passing proves that path can
reach the project and configured deployment; it does not identify the selected
credential-chain member.

Credential chain mental model:

```text
local development: Azure CLI token after az login
CI/CD:             workload identity or service principal configuration
Azure workload:    managed identity
                  ↓
            Entra token for endpoint/scope
                  ↓
            RBAC assignment at valid scope
```

Use managed identity in deployed workloads instead of stored secrets whenever
supported. Scope roles to project/resource and principal minimum needed.

### 08 — RBAC role policies

**Question answered:** Which principal can manage, infer, or inspect?

```bash
uv run python 01-plan-and-manage/08_rbac_role_policies.py
```

The default behavior lists assignments. Its assignment helper is commented out
because role mutation is an administrative action. Review target principal,
role, scope, and propagation before enabling it.

| Operation | Starting role | Scope | Why |
|---|---|---|---|
| Project APIs, pre-deployed model use, project agents | `Foundry User` | Project or resource | Foundry project data-plane path. |
| Direct Azure OpenAI inference | `Cognitive Services OpenAI User` | Azure OpenAI resource | Direct OpenAI-only data actions. |
| Broader Cognitive Services data capabilities | `Cognitive Services User` where appropriate | Resource | Broader resource data actions. |
| Deployment changes | `Cognitive Services Contributor` or suitable control-plane role | Foundry resource | Management-plane operation. |
| Quota inspection | `Cognitive Services Usages Reader` or `Reader` | Subscription | Usage visibility is subscription scoped. |
| Telemetry query | `Log Analytics Reader` plus protected-table access if needed | Telemetry resource | Manual trace visibility. |

Use groups for humans, managed identities/workload identities for applications,
and resource/project scope before subscription scope. An application needing
one specific agent endpoint should not automatically receive resource-wide
management access.

## Lessons 09–15: defense in depth

### Guardrail layers and intervention points

A safe system does not rely on one classifier. Separate policy enforcement from
application decisions and place checks at the boundary where risk appears.

```text
User input ──► [user-input guardrail / Prompt Shield] ──► model or agent
                                                             │
                                      agent only: tool call ─┤
                                                             │
                                 external tool response ─► [tool-response guardrail]
                                                             │
Model/agent output ◄── [output guardrail / PII etc.] ◄──────┘

Application: pre-screen when needed, decide block/escalate/redact, log safely,
and test all routes including retrieval and tools.
```

| Intervention point | Applies to | Example risk |
|---|---|---|
| User input | Models and agents | Harmful request, direct jailbreak, untrusted upload. |
| Tool call | Agent workflows where supported | Agent attempts an action beyond task intent. |
| Tool response | Agent workflows where supported | Tool/web/RAG result contains indirect prompt injection. |
| Output | Models and agents | Harmful output, PII disclosure, protected material. |

Foundry guardrails are configured service policy and can annotate/block at
supported intervention points. The explicit Azure AI Content Safety API is a
separate application call, useful for pre-screening, independent checks, or
workflows outside a configured deployment. Your application still owns the
response to a detection signal: block, redact, ask for clarification, route to
human review, or record an audit event.

### Severity and scope distinction

| Mechanism | What it primarily handles | Result model |
|---|---|---|
| Foundry harm guardrail | Deployment/agent policy for harm categories | Safe/Low/Medium/High-style policy thresholds and filter annotations. |
| Content Safety analysis | Explicit text/image category analysis | Integer category severities, commonly 0–7. |
| Prompt Shields | Direct jailbreak or indirect document injection | Detection boolean/annotation, not harm severity. |
| PII filter | Completion/output personal-information handling | Preview annotations/filter behavior. |
| Task Adherence | Agent plan versus user intent | Preview risk signal plus details. |
| Blocklist | Organization-specific terms/patterns | Match result/filter behavior. |

Do not compare these score formats as if they were interchangeable. A safety
signal is contextual evidence, not a complete risk decision.

### 09 — Content safety filters

**Question answered:** Which path should handle harmful text or image?

```bash
uv run python 01-plan-and-manage/09_content_safety_filters.py
```

The lesson contrasts a deployment-level model guardrail with explicit Content
Safety text and image analysis. It uses intentionally unsafe test text; use
only approved synthetic test material in labs.

**Study points**

- Harm categories include hate/fairness, sexual, violence, and self-harm.
- Deployment guardrail filter results and direct API severities have different
  response shapes and scales.
- A blocked deployment request can surface as `400` with `content_filter`;
  annotation visibility depends on request path/configuration.
- Image moderation is not a defense against text hidden in OCR, RAG chunks, or
  a tool response. Use document/prompt-injection protections for that problem.

### 10 — Prompt Shields: direct user attacks

**Question answered:** Is the user's own prompt attempting to override policy?

```bash
uv run python 01-plan-and-manage/10_prompt_shields_user.py
```

A direct attack is in `userPrompt`: for example, attempted instruction override,
authority spoofing, or jailbreak framing. The explicit shield API returns a
boolean such as `userPromptAnalysis.attackDetected`. A configured deployment
path can expose `jailbreak` detection/filter data or block according to policy.

Use a pre-model explicit check when you need routing or audit logic before
inference. Use configured guardrails for consistent service-side enforcement.
Neither removes need for strong system instructions, tool allowlists, output
validation, and least-privilege tool credentials.

### 11 — Prompt Shields: document and indirect attacks

**Question answered:** Is untrusted retrieved or uploaded content trying to
control the model?

```bash
uv run python 01-plan-and-manage/11_prompt_shields_docs.py
```

A document attack differs from a direct jailbreak:

```text
Direct attack:   user message contains override instructions.
Indirect attack: innocent user asks for summary; OCR/web/RAG/tool content
                 contains the attacker instruction.
```

The explicit `shieldPrompt` flow supplies documents separately and reports
per-document analysis. That is the clean way to test an actual document
channel in this lesson.

**Critical channel caveat:** pasting document text into a Chat Completions user
message does **not** create a document-bearing channel. It can be evaluated as
user-prompt content and produce a `jailbreak` result instead. An inline
`indirect_attack` result requires an actual supported document path, such as
configured retrieval/data source or tool response, plus Document attack control.
Do not claim this sample proves that full inline document integration.

Treat all external content as data, not instructions. Preserve source identity,
minimize tool authority, scan before ingestion and at retrieval/tool boundaries,
and give the model explicit rules for handling untrusted content.

### 12 — Spotlighting (preview)

**Question answered:** What extra trust-boundary defense is available for
supported document workflows?

```bash
uv run python 01-plan-and-manage/12_spotlighting.py
```

This local reference inspects documented request shape and integration boundary.
Spotlighting is **preview**, works with **Chat Completions only**, and is **not
supported for agents**. It marks document content as lower trust through its
documented transformation/encoding behavior; it is additive to document Prompt
Shields, not a replacement.

Use it only after validating preview eligibility and token impact. Document
expansion can increase input tokens and exceed context/input limits. It cannot
replace retrieval hygiene, Prompt Shields, tool authorization, or testing real
document paths.

### 13 — PII filter (preview)

**Question answered:** How can a completion guardrail expose personal-data
handling behavior?

```bash
uv run python 01-plan-and-manage/13_pii_filter.py
```

The lesson requests synthetic values and inspects output filter annotations. PII
filter is a **preview** completion/output intervention control; it is not a
promise that all personal data is found, removed, or lawful to process. Enable
and test the matching deployment guardrail before relying on results.

Production design should minimize collection, avoid logging sensitive prompts
and outputs, restrict telemetry access, define retention, and test false
positive/negative consequences. Do not feed real personal data into this lab.

### 14 — Task Adherence (preview)

**Question answered:** Does an agent's proposed tool behavior match user intent?

```bash
uv run python 01-plan-and-manage/14_task_adherence.py
```

The lesson calls Content Safety Task Adherence with tool definitions and
conversation/tool-plan messages. It compares aligned and misaligned plans, such
as reading leave balance versus submitting leave, or drafting versus sending an
email.

Task Adherence is **preview** and returns a signal; it does not execute or
block a tool on its own. The application must stop the action, ask confirmation,
or escalate to human review. It is not a jailbreak detector and not a generic
harm classifier. Test language and workflow behavior with representative
examples before making it a release gate.

### 15 — Custom blocklists

**Question answered:** How can a policy catch organization-specific terms that
harm categories miss?

```bash
uv run python 01-plan-and-manage/15_blocklists.py
```

The lesson creates/updates `northwind-exam-blocklist`, adds lab terms, and
analyzes text for matches. It persists service state. Delete lab-only list/items
when finished if they are no longer needed.

Blocklists fit codenames, competitor names, regulated phrases, and other
explicit domain policy. They do not replace semantic moderation or injection
defense. Allow for propagation delay after changes. Content Safety blocklist
APIs and Foundry deployment custom-blocklist configuration are related concepts
with different wiring; configure and test the one your serving path uses.

## Lessons 16–18: agents, evaluation, observability

### Agent types and state model

| Type | Definition lives in | Best use | Domain 1 boundary |
|---|---|---|---|
| Code-defined / ephemeral pattern | Application call (`instructions`) | Small code-owned behavior, prototypes, tests | Lesson 16 uses this; it does not create an agent resource. |
| Prompt agent | Foundry-managed definition | Shared/versioned agent behavior | Broader lifecycle covered in Domain 2. |
| Hosted agent | Your packaged code hosted by Foundry | Custom runtime/dependencies/tooling | Lesson 07 only lists hosted agents as auth smoke test. |

"Ephemeral" describes where behavior is defined, not an absence of safety,
identity, cost, or observability responsibilities. A code-defined Responses
call can still use project access, deployment guardrails, and application
telemetry.

### 16 — Agent basics through Responses API

**Question answered:** How do instructions and multi-turn state work without
creating a Foundry agent resource?

```bash
uv run python 01-plan-and-manage/16_agent_basics.py
```

The lesson uses code-defined instructions for a single response, then links a
follow-up through `previous_response_id`. This demonstrates conversation state
without resending every prior message in the client call.

Use this pattern for bounded behavior owned and deployed with application code.
It is not a substitute for evaluating instructions, authorizing tools, setting
retention expectations, or deciding whether managed prompt/hosted agents fit
team operations better.

### Evaluation concepts: rubric versus self-critique

| Approach | What it is | What it proves |
|---|---|---|
| LLM self-critique | Model reviews draft against prompt checklist | A heuristic application pattern for this one run. |
| Built-in evaluator | Documented evaluator contract/run with inputs, metrics, and output | Evaluator results for configured dataset/run. |
| Golden-set CI gate | Repeatable representative test set and threshold | Release evidence, only as good as dataset/threshold. |
| Human review | Domain expert examines selected/flagged cases | High-value qualitative/regulated review. |

Groundedness asks whether response claims are supported by supplied sources.
Response Completeness asks whether needed aspects were covered. Neither is
identical to safety, tool correctness, or user satisfaction. Preview evaluator
requirements can differ; for example, Response Completeness needs its
supported evaluation contract such as `ground_truth` and `response`.

### 17 — Self-critique and regeneration

**Question answered:** How can an application implement draft → critique →
regenerate?

```bash
uv run python 01-plan-and-manage/17_evaluator_groundedness.py
```

The lesson generates a support answer, asks another model call to return
`COMPLETE` or `MISSING` against a checklist, and regenerates when needed. This
is useful for learning how a rubric can shape revision.

**Limitation:** lesson 17 is **not** a Foundry built-in Groundedness or Response
Completeness evaluator, and it does not create an evaluation run. A model can
make the same mistake in drafting and reviewing. For production, use held-out
examples, documented evaluator contracts, human review where needed, and
monitor quality drift rather than trusting a self-approval loop.

### 18 — Manual tracing

**Question answered:** Which runtime attributes should an application record?

```bash
uv run python 01-plan-and-manage/18_agent_tracing.py
```

The lesson creates an application-owned OpenTelemetry span around a Responses
call. It records model, limited input preview, token metadata, latency, and
best-effort safety metadata; an optional Application Insights connection string
exports telemetry.

**Limitation:** this is manual application instrumentation, **not** automatic
Foundry server/client tracing and **not** proof of full Foundry Traces
integration. Treat spans as a carefully governed operational dataset: avoid
secrets and unnecessary personal data, cap previews, apply access controls,
set retention, and correlate traces with deployment version and release ID.

Useful dimensions:

| Dimension | Why record it |
|---|---|
| Model/deployment and release version | Compare behavior after routing/model/prompt change. |
| Input/output/total tokens | Explain capacity and cost changes. |
| End-to-end latency and error class | Locate SLO degradation. |
| Retry count and backoff time | Detect saturation/retry amplification. |
| Safety signal/action | Audit whether detection produced block/escalation. |
| Trace/correlation ID | Join application, tool, and telemetry events. |

## Feature status and hard limits

| Feature | Status | Practical boundary |
|---|---|---|
| Responses Model Router | Supported | Use `responses.create(model="model-router", ...)`; deployment/availability required. |
| Prompt Shields | Supported guardrail/API capability | Test document attack through actual document/tool-response channel. |
| Spotlighting | **Preview** | Chat Completions only; no agents; document expansion may exceed input limits. |
| PII filter | **Preview** | Output/completion intervention; matching configured deployment guardrail required. |
| Task Adherence | **Preview** | Explicit API returns signal; app must block/escalate; test actual workflow. |
| Response Completeness | **Preview** built-in evaluator | Requires supported evaluation run/input contract; lesson 17 does not implement it. |
| Groundedness | Built-in evaluator | Requires documented evaluation contract; lesson 17 does not implement it. |
| Lesson 18 span | Application instrumentation | Not automatic Foundry tracing or Foundry Traces integration. |

## Troubleshooting guide

| Symptom | Likely cause | Resolution |
|---|---|---|
| `CredentialUnavailableError` | No usable local/deployed credential | `az login` locally; configure workload/managed identity in deployment. |
| `401` / `403` from project API | Missing Foundry role, wrong scope, wrong principal, RBAC propagation | Verify project/resource role assignment and principal object ID; wait then retry. |
| `401` / `403` from direct OpenAI API | Foundry project role assumed to cover direct resource | Assign suitable Cognitive Services inference role on direct resource; verify endpoint. |
| `404 DeploymentNotFound` | Model family name used instead of deployment name | Run lesson 01; set deployment name in `DEFAULT_MODEL`. |
| Unsupported API/feature error | Endpoint, API surface, region, model, or preview mismatch | Check lesson feature boundary/current service docs; do not substitute another endpoint blindly. |
| `429` | RPM/TPM or capacity pressure | Use bounded retry, then queue/scale/request quota/change architecture. |
| Quota listing denied | Resource role assigned but subscription permission absent | Add subscription `Reader` or `Cognitive Services Usages Reader`. |
| Role assignment succeeds but call fails | RBAC propagation or scope mismatch | Wait briefly; inspect effective scope, principal type, and endpoint. |
| No `indirect_attack` result in L11 inline test | Text was pasted as user message; no actual document channel | Use explicit documents flow or configure supported data-source/tool-response path. |
| Spotlighting parameter rejected | Preview/gateway/configuration boundary | Treat L12 as reference; use supported Chat Completions integration only. |
| PII annotation absent | Preview feature/guardrail not configured or unsupported | Validate deployment configuration and supported model/region. |
| Task Adherence result is risky but tool still runs | API only returned analysis | Implement application block/confirmation/HITL decision before tool execution. |
| No trace in Application Insights | Connection string unset, exporter/access issue, ingestion delay | Validate exporter configuration and telemetry-resource read permission; inspect local output. |

## CI/CD and operational release discussion

Treat Foundry configuration, prompts, deployment names, guardrail policy, and
application code as a release system—not portal-only changes.

```text
Pull request
  → lint/test application behavior
  → run deterministic unit tests and contract checks
  → run curated evaluation/golden set in safe environment
  → inspect safety, quality, cost, latency, and tool-authority regressions
  → approval for high-risk prompt/model/guardrail changes
  → deploy IaC/configuration and application
  → canary or staged traffic where supported
  → monitor traces, errors, quota, cost, and quality signals
  → rollback deployment/configuration on regression
```

### What to version

- Infrastructure and deployment SKU/region/capacity intent.
- Deployment names, model version-selection policy, and router configuration.
- Prompt/instruction templates, tool schemas, allowlists, and output validators.
- Guardrail/filter/blocklist configuration and synthetic test cases.
- Evaluation datasets, rubric versions, thresholds, and reviewed exceptions.
- Telemetry schema, redaction rules, alert thresholds, release identifiers.
- RBAC role assignments as IaC where organization policy allows; never store
  secrets in repository variables.

### Practical release gates

| Change | Minimum gate |
|---|---|
| Prompt/instruction | Golden cases, safety regressions, tool-plan checks, human review for high impact. |
| Model/deployment/router | Quality, latency, token cost, availability, residency, fallback, and quota test. |
| Guardrail/filter | Benign and harmful synthetic cases; inspect false positives/negatives and block UX. |
| Tool/action agent | Least privilege, allowlist, Task Adherence/HITL behavior, idempotency/audit trail. |
| Telemetry change | Redaction, access, retention, correlation, and ingestion verification. |
| RBAC change | Test with intended workload identity at least scope; confirm no privileged fallback. |

Avoid using a single score as a deployment decision. A higher aggregate quality
score can hide a critical safety, residency, latency, cost, or tool-action
failure. Keep rollback ownership and a known-good configuration.

## Common exam traps

| Claim | Correct interpretation |
|---|---|
| "Global Standard keeps inference in my chosen region." | False. Choose a regional/data-zone option when policy requires its corresponding boundary. |
| "Data Zone means one Azure region." | False. It is a multi-region geographic zone. |
| "PTU means tokens are prepaid." | False. PTUs reserve hourly capacity; token/billing concepts are separate. |
| "Every deployment capacity number equals the same TPM value." | False. Capacity units and quota mappings are model/SKU specific. |
| "Quota is isolated per deployment." | Not necessarily. It can be subscription/zone/location/model/SKU pooled. Inspect actual usage and limits. |
| "Retry every API error." | False. Retry transient throttling/network failures with a bound; fix 400/401/403/404 causes. |
| "Owner grants inference everywhere." | False. Control plane and data-plane permissions/endpoints are distinct. |
| "Foundry User and Cognitive Services OpenAI User are interchangeable." | False. Choose role for project Foundry versus direct Azure OpenAI API surface. |
| "Prompt Shield detects harmful content severity." | False. It detects prompt-injection attack patterns; harm classification is separate. |
| "Pasting OCR text into user message tests document guardrail channel." | False. It commonly tests user-prompt channel; use actual document/tool-response path. |
| "Spotlighting replaces Prompt Shields and works with agents." | False. It is additive, preview, Chat Completions only, and no agents. |
| "Task Adherence blocks tools automatically." | False. It returns preview analysis; application enforces block/HITL. |
| "Self-critique is a Foundry evaluator run." | False. Lesson 17 is an application pattern, not built-in evaluator execution. |
| "Manual OpenTelemetry span proves Foundry tracing is configured." | False. Lesson 18 is application instrumentation only. |

## Objective coverage and limits

Runnable evidence in this folder covers deployment selection/control-plane API,
quota inspection, retry behavior, project credential validation, assignment
inspection, Content Safety and Prompt Shield calls, blocklist lifecycle,
Responses conversation state, self-critique pattern, and manual telemetry.

It does **not** prove production readiness, regional feature availability,
complete compliance, service-side agent tracing, full evaluation-run setup,
guardrail coverage on every route, or a secure tool-execution design. Preview
features can change. A successful call proves only that call under its current
identity, resource, configuration, and time.

## References

Local links:

- [Repository setup and endpoint topology](../README.md)
- [AI-103 skills measured](../AI-103.md)
- [Objective coverage map](../docs/coverage.md)
- [Domain 2: Generative AI and agents](../02-generative-ai-and-agents/README.md)

Microsoft documentation:

- [Deployment types](https://learn.microsoft.com/azure/ai-foundry/foundry-models/concepts/deployment-types)
- [Quota management](https://learn.microsoft.com/azure/ai-foundry/openai/how-to/quota)
- [Responses Model Router](https://learn.microsoft.com/azure/ai-foundry/openai/how-to/responses-model-routing)
- [Foundry RBAC](https://learn.microsoft.com/azure/ai-foundry/concepts/rbac-foundry)
- [Prompt Shields and Spotlighting](https://learn.microsoft.com/azure/ai-foundry/openai/concepts/content-filter-prompt-shields)
- [Task Adherence](https://learn.microsoft.com/azure/ai-services/content-safety/concepts/task-adherence)
- [Built-in evaluators](https://learn.microsoft.com/azure/ai-foundry/concepts/built-in-evaluators)
- [Client-side agent tracing](https://learn.microsoft.com/azure/ai-foundry/observability/how-to/trace-agent-client-side)
