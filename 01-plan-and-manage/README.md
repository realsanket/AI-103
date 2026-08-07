# Domain 1: Plan and manage Microsoft Foundry

> Study guide and runnable labs for deployment planning, access, guardrails, agents, evaluations, observability, and operations. Run commands from repository root: `uv run python 01-plan-and-manage/<lesson>.py`.
>
> This domain explains service behavior; a script is evidence only for its documented path. Preview availability, quota, model support, and permissions remain subscription and region specific.

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

The lessons follow that lifecycle. They do not create a complete production application or prove every Foundry feature. They teach decisions, boundaries, and the smallest runnable evidence for each subject.

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

One model can have multiple deployments: development and production, different regions, or different capacity and policy decisions. A deployment name is the stable application configuration value. List deployments before assuming a name exists.

### Endpoint map: same organization, different surfaces

| Surface | Environment setting | Shape | Typical use | Starting role |
|---|---|---|---|---|
| Foundry account/control plane helper | `FOUNDRY_ENDPOINT` | `https://<resource>.services.ai.azure.com` | D1 deployment/quota account lookup | Appropriate control-plane role |
| Foundry project API | `PROJECT_ENDPOINT` | `https://<resource>.services.ai.azure.com/api/projects/<project>` | Project APIs, hosted-agent list, project Responses client | `Foundry User` at project/resource |
| Direct Azure OpenAI-compatible API | `AZURE_OPENAI_ENDPOINT` | `https://<resource>.openai.azure.com` | Direct Responses/Chat Completions calls | `Cognitive Services OpenAI User` on direct resource |
| Azure AI Content Safety | `CONTENT_SAFETY_ENDPOINT` | `https://<resource>.cognitiveservices.azure.com` | Explicit moderation, shields, Task Adherence, blocklists | Appropriate Content Safety access |

`FOUNDRY_ENDPOINT` and `PROJECT_ENDPOINT` are not interchangeable. A direct OpenAI client does not infer its endpoint or authorization from a project URL. Similarly, a Foundry project role does not automatically mean a principal has the direct Azure OpenAI data action required by a different resource surface.

### Planes and responsibility boundaries

```text
Control plane: create/configure Azure resources and deployments
  CognitiveServicesManagementClient, Azure portal, IaC

Data plane: send inference requests and use project/agent APIs
  OpenAI or project client, application identity

Application plane: decide retry, block/escalate, redact/log, and release
  Your code and operational process
```

A control-plane role such as `Owner` or `Contributor` does not by itself grant every inference data action. Conversely, an inference role does not grant permission to deploy models. Match both the endpoint and action.

## Before running a lesson

### Setup

From repository root:

```bash
uv sync
cp .env.example .env
az login
```

Use a nonproduction Foundry resource for deployment, blocklist, and guardrail experiments. Never commit `.env`, API keys, connection strings, customer content, or production prompts.

For Entra token auth, configure a custom subdomain on the Foundry resource. Foundry and Azure OpenAI clients request the `https://ai.azure.com/.default` scope; an endpoint URL is not an OAuth scope. Agents and evaluation APIs require Entra ID: an API key is not a fallback for those paths.

Populate values appropriate to the lesson:

```dotenv
# Foundry resource and project
FOUNDRY_ENDPOINT=https://<resource>.services.ai.azure.com
PROJECT_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<project>
AZURE_OPENAI_ENDPOINT=https://<resource>.openai.azure.com

# Deployment names, not model-family labels
DEFAULT_MODEL=<deployment-name>
MODEL_ROUTER_DEPLOYMENT=model-router
# Lesson 03 management-plane deployment declaration
DEPLOYMENT_NAME=<new-deployment-alias>
DEPLOYMENT_MODEL_NAME=<model-family>
DEPLOYMENT_MODEL_VERSION=<optional-pinned-version>

# Content Safety and management context
CONTENT_SAFETY_ENDPOINT=https://<content-safety-resource>.cognitiveservices.azure.com
AZURE_SUBSCRIPTION_ID=<subscription-id>
AZURE_RESOURCE_GROUP=<resource-group>

# Optional: lesson 18 manual telemetry export
APPLICATIONINSIGHTS_CONNECTION_STRING=<connection-string>

# Advanced optional labs
PROVENANCE_SOURCE_URL=<https-blob-or-sas-uri>
AZURE_AI_PROJECT_ENDPOINT=<project-endpoint-for-evaluation-labs>
AZURE_AI_AGENT_NAME=<target-agent-name>
AZURE_AI_MODEL_DEPLOYMENT_NAME=<evaluation-judge-deployment>
```

`DefaultAzureCredential` commonly uses Azure CLI authentication after `az login` on a workstation. In Azure, it commonly uses a managed identity or workload identity. Credential-chain success does **not** prove which credential supplied the token; use identity and service logs when that distinction matters.

For a managed identity, enable or attach the identity, then assign roles to its **principal object ID**. Do not substitute its client ID in a role assignment.

### Safe learning order

1. Run **02** first: local deployment-type reference, no cloud call.
2. Run **01** and **05** next: inventory and quota reads.
3. Make **07** pass before treating project-authenticated lessons as usable.
4. Use **04**, **06**, **09–14**, **16**, and **17** with a low-cost,
nonproduction deployment; each makes live service calls where stated.
5. Review model, region, SKU, capacity, and cost before **03**.
6. Treat **08** as an access review; use its `--apply`,
`--assign-principal-id`, and `--role` flags only when intentionally changing access.
7. Run **15 --apply** only when ready to create a persistent lab blocklist.
8. Run **18** only after reviewing telemetry destination and data handling.
9. Run **19–21** with `--run` only after reviewing Content Safety region,
input, and Storage access requirements.
10. Run **22–25** with `--apply` only in a disposable nonproduction project.
    They can create datasets, evaluations, monitoring rules, telemetry, or scans.
11. Run **26** first when adopting Foundry-native tracing; it is local preflight
    only and explains the portal-side setup that remains necessary.

### Costs and side effects

| Lesson(s) | Side effect or cost |
|---|---|
| 01, 05, 08 | Live read; 05 needs subscription-level quota visibility. |
| 02, 12 | Local reference only. |
| 03 | Creates or updates a deployment; allocation and billing implications. |
| 04, 06, 07, 09–11, 13–14, 16–18 | Model and/or Content Safety requests; input, output, retries, and selected model affect cost. |
| 15 | Creates/updates persistent `northwind-exam-blocklist` and items; matching can take time to propagate. |
| 18 | May export governed model/token/latency/safety metadata to telemetry; it does not add prompt/output text as span attributes. |
| 19–20 | Content Safety requests only with `--run`; supported region, role, and input limits apply. |
| 21 | Async Blob-backed provenance request only with `--run`; service identity needs Blob read access. |
| 22–23 | Dataset/evaluation/rule creation only with `--apply`; persistent state and evaluator costs. |
| 24 | Appends feedback telemetry only when application code calls its opt-in helper. |
| 25 | Red-team scan only with `--apply`; use purple environment and synthetic target. |
| 26 | Local preflight only; connecting App Insights is an explicit portal/IaC decision. |

Provisioned deployments reserve PTU capacity and incur hourly capacity cost while present, including idle time. A PTU is reserved throughput capacity, **not a prepaid token bucket** and not per-token billing. PTU quota approval does not guarantee capacity in every requested region.

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

Do not choose by benchmark headline alone. Test representative prompts, safety behavior, latency, required region, tool use, and total request cost.

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

Model availability, SKU names, quotas, supported regions, capacity units, and billing are service-version dependent. Read current portal/docs before making a production commitment.

### Throughput and rate-limit decisions

| Symptom | Likely cause | First response |
|---|---|---|
| HTTP 429 | RPM/TPM, quota, or transient saturation | Honor retry guidance where present; bounded exponential backoff with jitter. |
| Persistent 429 | Sustained demand exceeds capacity/limit | Queue, reduce demand, request quota, use supported spillover/fallback, or change deployment design. |
| High latency without 429 | Model size, output length, network, tool/RAG path | Measure spans, cap output, test model/region, profile full path. |
| `404 DeploymentNotFound` | Model family used instead of deployment name, wrong endpoint, or deployment absent | List deployments; correct setting. Do not retry blindly. |
| `401` / `403` | Wrong endpoint, role, scope, or identity | Inspect endpoint and effective principal/assignment. Do not retry blindly. |

A deployment `capacity` value is not a universal TPM conversion. Standard quota can be pooled by subscription, model/SKU, and location or zone; use lesson 05 and service quota views rather than assuming every deployment owns an isolated bucket. For provisioned SKUs, capacity represents PTUs and model-specific throughput differs by model and configuration.

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
| 15 | [Blocklists](15_blocklists.py) | Create/update and test Content Safety blocklist. | Persistent write; requires `--apply`; propagation delay. |
| 16 | [Agent basics](16_agent_basics.py) | Code-defined instructions and linked Responses turns. | Live inference; not a Foundry agent resource. |
| 17 | [Self-critique](17_evaluator_groundedness.py) | Draft, critique, regenerate. | Live inference; not a built-in evaluator/run. |
| 18 | [Manual tracing](18_agent_tracing.py) | Emit application OpenTelemetry span and metadata. | Live calls; not full Foundry tracing. |
| 19 | [Protected material](19_protected_material.py) | Detect protected material in synthetic English output. | GA Content Safety API; requires `--run`. |
| 20 | [Groundedness detection](20_groundedness_detection.py) | Compare synthetic generated text to sources. | Preview Content Safety API; supported region/S0 only; requires `--run`. |
| 21 | [Provenance detection](21_provenance_detection.py) | Detect C2PA/watermark provenance for Blob media. | Preview async API; Blob identity/SAS prerequisite; requires `--run`. |
| 22 | [Foundry evaluation](22_foundry_evaluation.py) | Create a dataset-backed Foundry evaluation run. | Preview; persistent/billable; requires `--apply --dataset`. |
| 23 | [Continuous evaluation](23_continuous_evaluation.py) | Create a sampled monitoring evaluation rule. | Preview; persistent/billable; requires `--apply`. |
| 24 | [Human feedback](24_human_feedback.py) | Emit correlated end-user feedback to telemetry. | Integration reference; append-only telemetry event. |
| 25 | [Red teaming](25_red_teaming.py) | Run a safe synthetic RedTeam target. | Preview/billable; purple environment; requires `--apply`. |
| 26 | [Foundry tracing setup](26_foundry_tracing_setup.py) | Preflight project/App Insights tracing governance. | Local, read-only guidance; portal setup still required. |

## Detailed implementation walkthroughs: lessons 01-18

Read a lesson in this order: **background** explains why capability exists; **before code** lists resource/identity prerequisites; **code path** maps significant statements to Azure behavior; **interpretation** explains what the result means and what it does not prove. A successful lab is a narrow observation, not production certification.

### 01 - Discover deployments before calling a model

**Background.** A model family is a capability; a deployment is its callable application alias plus selected version, SKU, capacity, rate limits, and guardrail configuration. Azure lets one team deploy the same model several times because development, production, regional, and provisioned workloads need different operational contracts.

**Before code.** Create a Foundry project, set `PROJECT_ENDPOINT`, authenticate with Entra ID, and grant the caller `Foundry User`. Do not start by guessing `DEFAULT_MODEL`: first discover what project administrators actually deployed.

**Code path.**

1. `project_client()` creates `AIProjectClient` with `DefaultAzureCredential`.
2. `client.deployments.list()` asks the project data plane for visible
deployments.
3. `name`, `model_name`, and type-like fields are read defensively because
service SDK shapes can evolve.
4. Printed `name` becomes the value passed to later `model=` calls.

**Interpretation and pitfalls.** Empty output can mean no deployment is visible *or* the identity lacks access. A listed deployment proves inventory visibility, not quota, regional eligibility, guardrail policy, or permission for a different endpoint. Record alias, underlying model/version, SKU, owner, and purpose in deployment configuration--not application literals.

### 02 - Select a deployment type from constraints

**Background.** Deployment type exists to make a trade-off explicit: where inference can process, how capacity is allocated, and how billing behaves. Global optimizes broad availability; Data Zone constrains processing to a geographic zone; Regional constrains it to one Azure region; Provisioned reserves PTUs; Batch exchanges latency for discounted asynchronous processing.

**Code path.** This local lesson intentionally prints a matrix rather than calling Azure. `_MATRIX` is a study aid: `type`, `billing`, `residency`, `throughput`, `cost`, and `when` force each choice into comparable dimensions. Instant access is preview and uses a platform global pool without creating a deployment; Managed compute serves a different model/accelerator operating model from standard Azure OpenAI deployment.

**Decision process.**

1. Start with residency/compliance: single region, data zone, or permitted
global processing.
2. Choose online versus asynchronous batch from interaction latency.
3. Use Standard for variable demand; evaluate PTU only for sustained,
measured utilization and hourly-capacity economics.
4. Validate model/SKU/region availability in portal before designing around it.

**Do not assume** Data Zone means one region, PTU means prepaid tokens, or a provisioned deployment cannot return 429 under saturation.

### 03 - Deploy a model through the management plane

**Background.** Deployment creation is Azure resource management, not inference. It exists so deployment configuration can be reviewed, versioned, and automated through SDK/CLI/IaC instead of ad-hoc portal clicks.

**Before code.** Use a nonproduction Foundry resource; set `AZURE_SUBSCRIPTION_ID`, `AZURE_RESOURCE_GROUP`, `FOUNDRY_ENDPOINT`, `DEPLOYMENT_NAME`, and `DEPLOYMENT_MODEL_NAME`. Optionally pin `DEPLOYMENT_MODEL_VERSION`. Caller needs a suitable control-plane role such as `Cognitive Services Contributor`; that role does not grant model inference.

**Code path.**

1. `settings()` separates existing `DEFAULT_MODEL` deployment alias from the
model family being created.
2. `foundry_account_name()` validates and extracts the resource name from the
Foundry endpoint instead of silently accepting an OpenAI/project URL.
3. `CognitiveServicesManagementClient` targets the Azure management plane.
4. `begin_create_or_update()` supplies `Sku(name="GlobalStandard")` and
`DeploymentModel(format="OpenAI", name=..., version=...)`.
5. Waiting on `.result()` makes the script report actual provisioning state.

**Production practice.** Pin or deliberately govern model versions, tags, region, SKU, capacity, rollback owner, and cleanup. A `Succeeded` deployment does not prove data-plane RBAC, cost fit, model quality, or an SLO.

### 04 - Route mixed work with Model Router

**Background.** Model Router is for workloads whose prompts vary in difficulty and where hard-coding one model wastes either cost or quality. It selects from an allowed set behind one router deployment; it is not an automatic production optimization strategy.

**Before code.** Deploy supported `model-router`, set `MODEL_ROUTER_DEPLOYMENT`, and obtain Foundry project access. Configure and test routing mode, allowed model subset, version, residency, tools, safety, and fallback outside this small call.

**Code path.**

1. `project_client().get_openai_client()` obtains the project-scoped
OpenAI-compatible client.
2. `responses.create(model=router, input=prompt)` invokes the router through
Responses API.
3. `response.model` reports the model chosen for this request.
4. `output_text` demonstrates that the application still receives a normal
response shape.

**When not to use it.** Do not use a router when one approved/pinned model is required for validation, jurisdiction, deterministic behavior, or a narrow latency/cost SLO. The smallest model in the allowed set can limit usable context; exclude unsuitable models rather than discovering that limit in production.

### 05 - Read quota before scaling demand

**Background.** Quota is a subscription-level capacity permission measured in model/tier/location-specific units. It prevents one subscription from consuming unbounded shared service capacity. It is not a utilization dashboard, invoice, or per-deployment guarantee.

**Code path.**

1. The lesson validates subscription/resource-group settings and derives the
resource name.
2. `accounts.get()` obtains the account location needed by management APIs.
3. `deployments.list()` prints configured alias, model, SKU, and capacity.
4. `usages.list(location)` prints current value, limit, and unit for quota
buckets visible in that location.

**Use results with** application tokens, request rate, retry count, latency, and Cost Management data. Standard quota can be pooled; Instant access has a separate global pool; PTUs are a different capacity model. Quota increases can propagate after a delay, and a provisioned deployment can still saturate.

### 06 - Retry transient failure without amplifying it

**Background.** A 429 or connection interruption can be temporary. Retrying every error makes outages and misconfigurations worse. Backoff exists to give a shared service time to recover; jitter stops many clients from retrying in lockstep.

**Code path.**

1. Tenacity retries only `RateLimitError` and `APIConnectionError`.
2. `retry_after_seconds()` reads `retry-after-ms`, `retry-after`, or a valid
HTTP date, bounds wait to 60 seconds, and falls back to jittered exponential delay.
3. `stop_after_attempt(6)` gives failure a bounded budget.
4. `_ask()` remains small: it performs one Responses call; retry policy wraps
it rather than every caller reimplementing behavior.

**Do not retry** 400/401/403/404: they require input, endpoint, deployment, or RBAC correction. For high volume add queueing, admission control, idempotency for mutations, circuit breaking, user degradation, and capacity/fallback design--not larger retry counts.

### 07 - Prove keyless project access

**Background.** `DefaultAzureCredential` lets local development use Azure CLI while deployed workloads use managed/workload identity. This removes stored secrets, but it does not remove the need to know exactly which principal and role the service receives.

**Code path.**

1. `project_client()` authenticates to `PROJECT_ENDPOINT`.
2. `client.agents.list()` is a project API reachability check.
3. `get_openai_client()` obtains project-scoped inference access.
4. A small Responses request verifies configured deployment use.

**Interpretation.** Passing proves that this credential chain can access this project and deployment now. It does not identify which credential won the chain, prove direct Azure OpenAI access, or prove production managed-identity assignment. Agents and evaluations require Entra ID; configure a custom subdomain and use `https://ai.azure.com/.default`.

### 08 - Grant and review least privilege

**Background.** Azure RBAC binds a principal, role definition, and scope. Least privilege limits blast radius: a user who invokes one agent should not also create deployments or query all resource-group assignments.

**Learning goal.** Understand how authorization decisions are made in Foundry and Azure AI so you can choose the minimum role at the minimum scope for each workload.

**RBAC decision model (exam mental model).**

1. Identify principal type: user, service principal, or managed identity.
2. Identify plane: control plane (manage resources) or data plane (use models/agents).
3. Identify API surface: Foundry project/resource APIs or direct Azure OpenAI resource APIs.
4. Identify minimum scope: agent, project, resource, resource group, or subscription.
5. Assign minimum role that includes required actions or dataActions.
6. Validate effective access after propagation, including inherited parent-scope assignments.

**Useful commands.**

```bash
# List aliases supported by this lesson
uv run python 01-plan-and-manage/08_rbac_role_policies.py --list-roles

# Review only direct assignments at configured scope (default)
uv run python 01-plan-and-manage/08_rbac_role_policies.py

# Review one principal across inherited parent scopes
uv run python 01-plan-and-manage/08_rbac_role_policies.py \
  --include-inherited \
  --principal-id <object-id>

# Review one role alias at a narrow project/agent/resource scope
uv run python 01-plan-and-manage/08_rbac_role_policies.py \
  --role-filter "Foundry Agent Consumer" \
  --scope "/subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.CognitiveServices/accounts/<account>/projects/<project>/agents/<agent>"
```

Use the managed identity **principal object ID**, not client ID. Prefer agent/project/resource scope over resource group/subscription. `Foundry Agent Consumer` is for endpoint-only callers; `Foundry User` is for builders. Wait for propagation and test with intended workload identity.

## Lessons 01–08: plan, deploy, operate, secure

### 01 — Model catalog list

**Question answered:** What can this project call right now?

Run:

```bash
uv run python 01-plan-and-manage/01_model_catalog_list.py
```

The script lists existing deployments from project context. Capture the **deployment name**, model, and type before configuring `DEFAULT_MODEL` or writing calls. Treat a catalog listing as an inventory snapshot, not proof that a deployment is healthy, affordable, or authorized for every principal.

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

Use this as a decision reference, then validate exact model/SKU availability in the current Foundry portal and documentation.

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

The lesson uses `CognitiveServicesManagementClient`, which is a **management plane** client. It derives account name from `FOUNDRY_ENDPOINT`, then performs create-or-update for one Global Standard deployment. It is intentionally an idempotent-style automation example, not a deployment policy engine.

Before production automation, pin or deliberately manage version selection, validate model availability and allowed SKU, set desired naming conventions, record ownership/tags, and plan rollback. A successful provisioning state does not prove the application has correct data-plane permissions or that a workload meets its SLO.

### 04 — Model Router through Responses API

**Question answered:** When can one router deployment select model per request?

Run after creating supported `model-router` deployment:

```bash
uv run python 01-plan-and-manage/04_model_router.py
```

The script calls the **project-scoped Responses API** with `model=MODEL_ROUTER_DEPLOYMENT`, then prints `response.model` to show the model chosen for that request. Router is Responses-supported in this lab. Do not revive older guidance claiming router only works through Chat Completions.

Router can simplify an application that receives mixed-complexity prompts, but it is not a substitute for product evaluation. Measure quality, latency, cost, allowed model set, regional availability, safety behavior, and observability. Keep a deliberate fallback plan for router unavailability or workloads needing strict model selection.

### 05 — Quotas and throughput

**Question answered:** Where is capacity allocated and how close am I to quota?

```bash
uv run python 01-plan-and-manage/05_quotas_and_tpm.py
```

The lesson lists account deployments and `usages.list(location)`. Quota is a control-plane observation, not an invoice. It needs a subscription-level role such as `Cognitive Services Usages Reader` or subscription `Reader`; resource scope alone can be insufficient.

Use quota output to locate allocation and pool pressure. It does not tell you actual prompt mix, output lengths, retry amplification, end-user latency, or monthly spend. Combine it with application metrics and cost management data.

### 06 — Rate-limit backoff

**Question answered:** Which failures are safe to retry, and how?

```bash
uv run python 01-plan-and-manage/06_rate_limit_backoff.py
```

The lesson sends five requests and retries `RateLimitError` and transient connection failures with bounded exponential backoff plus jitter. Jitter avoids synchronized retry storms; a maximum attempt count prevents infinite waiting.

```text
429 / transient connection failure
  → wait with exponential backoff + jitter
  → retry within a bounded budget
  → surface failure or queue work after budget exhausted
```

Do **not** retry a configuration or access bug as though it were transient: `400`, `401`, `403`, and `404` need diagnosis. At scale, complement client retry with backpressure, request shaping, idempotency where an operation can mutate state, circuit breaking, queueing, and explicit user-facing degradation.

### 07 — Managed identity and keyless project auth

**Question answered:** Can this workload use Entra ID end-to-end?

```bash
uv run python 01-plan-and-manage/07_managed_identity_agent.py
```

This is the practical must-pass smoke test. It creates a project client with `DefaultAzureCredential`, lists hosted agents, obtains the project-scoped OpenAI client, and makes one Responses request. Passing proves that path can reach the project and configured deployment; it does not identify the selected credential-chain member.

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

Use managed identity in deployed workloads instead of stored secrets whenever supported. Scope roles to project/resource and principal minimum needed.

### 08 — RBAC role policies

**Question answered:** How does RBAC actually authorize Foundry and Azure AI operations, and how do I pick least privilege under exam pressure?

```bash
uv run python 01-plan-and-manage/08_rbac_role_policies.py
```

The script is a study aid. It helps you inspect role assignments and practice narrow-scope access reviews. The learning value is the authorization model, not the printed list itself.

**How RBAC evaluation works**

An access decision depends on all of these at once:

1. **Principal**: who is calling (user, service principal, managed identity).
2. **Role definition**: which allowed actions or dataActions the role grants.
3. **Scope**: where the role is assigned and inherited.
4. **Plane and API surface**: control-plane management operation versus data-plane runtime operation.
5. **Resource endpoint path**: Foundry project/resource endpoint versus direct Azure OpenAI endpoint.

If any one is mismatched, access fails even when another piece looks correct.

**Foundry exam anchors from Microsoft docs**

1. Foundry separates control plane and data plane permissions.
2. Microsoft Entra ID with RBAC is recommended for production least privilege.
3. Key-based auth is coarse-grained and bypasses per-principal RBAC granularity.
4. For Foundry project scenarios, use Foundry roles (`Foundry User`, `Foundry Project Manager`, and others).
5. `Foundry Agent Consumer` is least-privilege for callers that only interact with agent endpoints.
6. Agent-scope assignments are currently evaluated for agent endpoint access, not broad management permissions.

**Role-selection quick map**

| Operation | Starting role | Scope | Why |
|---|---|---|---|
| Build and develop in Foundry project with predeployed models | `Foundry User` | Project or resource | Foundry project data-plane path. |
| Interact with one or more agent endpoints only | `Foundry Agent Consumer` | Agent or project | Endpoint-only least privilege. |
| Manage project and publish agents | `Foundry Project Manager` | Resource or project | Adds management actions beyond builder role. |
| Create/manage Foundry accounts and deployments | `Foundry Account Owner` or `Foundry Owner` | Resource | High-privilege control-plane actions. |
| Direct Azure OpenAI endpoint inference (outside project API path) | `Cognitive Services OpenAI User` | Azure OpenAI resource | Direct OpenAI data actions on that resource. |
| Broad AI Services data operations on resource | `Cognitive Services User` where required | Resource | Broader data-plane capability set. |
| Quota inspection | `Cognitive Services Usages Reader` or `Reader` | Subscription | Usage visibility is subscription scoped. |
| Telemetry query | `Log Analytics Reader` (+ protected-table role if required) | Monitoring resource | Trace/log read access boundary. |

**High-yield exam traps**

1. Control-plane role does not automatically grant all data-plane inference actions.
2. Correct role at wrong scope still fails.
3. Correct role on Foundry project does not automatically grant direct Azure OpenAI resource access.
4. Using client ID instead of principal object ID for assignment causes identity confusion.
5. Broad inherited subscription roles can hide least-privilege gaps in project-level design.

Use groups for human access, managed identities or workload identities for application access, and narrow scope before broad scope. A caller that needs one agent endpoint should not receive resource-wide management rights.

### 09 - Separate model guardrails from explicit moderation

**Background.** Foundry deployment guardrails enforce configured policy while the Content Safety API gives application code a direct classification result. They solve different problems: a guardrail can stop a model response; an explicit check lets an application route, log safely, ask for clarification, or reject content before it reaches a model.

**Code path.**

1. Flow A uses Chat Completions so deployment filter annotations/block behavior
is observable. A blocked request is normally HTTP 400 `content_filter`.
2. Flow B calls `ContentSafetyClient.analyze_text()` with four harm categories.
3. Flow C calls `analyze_image()` with local bytes.
4. Results print category severities; do not compare direct API integer scores
with deployment `Safe`/`Low`/`Medium`/`High` filter policy labels.

**Use it:** explicit pre-screening, independent audit, or services outside a configured deployment. **Do not use it:** as a complete safety architecture. Image moderation does not detect an instruction hidden in OCR/RAG text; scan that as document attack instead. Use only approved synthetic unsafe examples.

### 10 - Detect direct Prompt Shield attacks

**Background.** A direct attack is authored by the user: "ignore previous instructions", authority spoofing, jailbreak framing, or attempts to bypass policy. Prompt Shields exist to detect attack patterns, not to classify harm severity or prove the user is malicious.

**Code path.**

1. `shield_user_prompt()` delegates to shared `shield_prompt()`.
2. The helper enforces official 10,000-character user prompt and document
limits before an Azure request.
3. It submits `userPrompt` and required empty `documents` array to
`text:shieldPrompt`.
4. The response's `userPromptAnalysis.attackDetected` is printed for benign
and jailbreak samples.
5. Optional Flow B reads deployment guardrail `jailbreak` annotations from
Chat Completions.

Use explicit API when the application needs pre-model decision/audit; use deployment guardrail for uniform enforcement. Keep system instructions, tool allowlists, input validation, and least-privilege credentials: a shield detection does not authorize any action.

### 11 - Detect indirect document attacks

**Background.** Indirect injection arrives in content the user did not write: retrieved pages, OCR, uploaded files, tool output, or a poisoned knowledge base. The user's request may be harmless while the document tries to control the model. This is why source provenance and tool permissions matter.

**Code path.**

1. The lesson reads `data/malicious_ocr_sample.txt` as deliberately untrusted
OCR output.
2. It keeps `_USER_PROMPT` benign and passes documents separately.
3. Shared `shield_prompt()` validates maximum five documents/10,000 total
characters, then calls the direct Shield endpoint.
4. `documentsAnalysis[i].attackDetected` identifies which document is risky.
5. The clean/mixed cases demonstrate that user-prompt and document outcomes
are different signals.

Never paste retrieved text into `messages` and claim it tested document protection: that creates user-prompt channel content. In production preserve source ID, retrieval authorization, chunk lineage, and scan decision; minimize tool authority; repeat checks at ingestion and tool-response boundaries.

### 12 - Understand Spotlighting before using it

**Background.** Spotlighting is preview, Chat-Completions-only, model-only defense that marks document data as lower trust through documented encoding. It is additive to document Prompt Shields, not a substitute for source validation, tool policy, or retrieval hygiene.

**Code path.** The lesson intentionally prints a request shape instead of sending an invented integration. `data_sources` represents a real document-bearing channel; `prompt_shield.documents.spotlighting_enabled` belongs there. A plain chat message is not a document channel.

**Use it:** eligible preview document workflows after measuring token and context impact. **Do not use it:** with agents, Responses API, or as a way to avoid implementing indirect-attack controls. Base64 expansion can exceed context limits and a model can mention encoded content.

### 13 - Treat PII filtering as output control

**Background.** PII filtering is preview Foundry guardrail behavior at completion/output boundary. It exists to detect, block, or redact personal information generated by a model. It is not a promise that every identifier is found, a lawful-processing determination, or a replacement for data minimization.

**Code path.**

1. The lesson requests only synthetic contact data.
2. Chat Completions runs against a deployment whose PII guardrail was enabled
in portal/policy.
3. `_extract_pii()` accommodates current/older annotation keys.
4. `_print_pii()` shows `detected`, `filtered`, `redacted`, optional redacted
text, and subcategories.
5. HTTP 400 path inspects filter result when policy blocks entire completion.

PII filtering requires preview-compatible API/guardrail support. Test false positive/negative behavior with privacy-approved cases; never use this lesson as an excuse to prompt for real data or log raw outputs.

### 14 - Check whether tool intent matches user intent

**Background.** Task Adherence is preview analysis of proposed agent tool behavior. It detects a difference between what a user asked and what a tool plan would do--for example, viewing leave balance versus submitting leave. It is neither a jailbreak detector nor an automatic tool firewall.

**Code path.**

1. `_TOOLS` defines tool names/descriptions, including read and side-effecting
operations.
2. Each scenario builds structured `Prompt`/`Completion` messages, assistant
tool calls, and optional tool results.
3. `_analyze()` posts tools/messages, tries current preview contract then
documented fallback only on request-not-found/bad-request behavior.
4. It returns `taskRiskDetected` and `details`; unhandled failures surface
rather than pretending the check passed.

**Application rule:** before calling a consequential tool, block, ask for confirmation, or escalate on risk. Consider idempotency, audit trail, authorization, and human approval independently. Validate English/region/data residency behavior in target environment; service analysis can process data in US/EU.

### 15 - Build domain-specific blocklists deliberately

**Background.** Harm classifiers are semantic and general; blocklists cover known codenames, competitor phrases, policy terms, and local abuse language. They exist for explicit organization policy, not for broad safety or injection defense.

**Code path.**

1. `BlocklistClient.create_or_update_text_blocklist()` idempotently creates
lab list metadata.
2. `add_or_update_blocklist_items()` adds terms with service-assigned IDs.
3. `AnalyzeTextOptions(blocklist_names=[...])` requests matches while
`halt_on_blocklist_hit=False` lets the lesson inspect all examples.
4. Retry loop waits for expected propagation before declaring match result.
5. Flow B demonstrates that direct Content Safety lists and Foundry deployment
custom blocklists require separate wiring.

Run only with `--apply`. Service limits are 100 items/request, 10,000 total terms, 128 characters/item. Delete lab content afterward. A blocklist hit must map to application policy--warn, block, redact, or review--not merely print.

### 16 - Learn code-defined agent state before managed agents

**Background.** A Responses call with instructions is code-defined agent behavior: simple, versioned with application code, and useful for prototypes or bounded support behavior. It is not a Foundry prompt/hosted agent resource, so it does not provide managed lifecycle, tool registration, or shared agent configuration.

**Code path.**

1. `_SYSTEM` is an instruction contract: scope, tone, and domain boundary.
2. `single_turn()` passes `instructions` and user input to one Responses call.
3. `multi_turn()` stores returned `response.id`.
4. Later calls pass `previous_response_id`, letting server-side conversation
state link turns without resending full history.

Use it when application owns behavior and state requirements are bounded. Do not mistake linked response state for retention/security policy: decide conversation lifecycle, user isolation, logging, and tool authorization explicitly. Use Domain 2 managed agents when team lifecycle/tools require it.

### 17 - Use self-critique as a pattern, not evidence

**Background.** Draft -> critique -> regenerate can improve a bounded answer when a checklist exposes omitted requirements. It exists as an application pattern, but the same model can repeat the same mistaken assumption in both roles.

**Code path.**

1. `_AGENT_INSTRUCTIONS` provides only known refund policy.
2. First Responses call produces a draft.
3. `_CRITIQUE_INSTRUCTIONS` defines completeness criteria and constrained
`COMPLETE`/`MISSING` output.
4. If missing, a second answer call receives an explicit coverage reminder.

Use it for low-risk response refinement with clear source material. Do not use it as a release evaluator, fabricated-claim detector, safety approval, or chain-of-thought store. For production use held-out data, built-in evaluators, human review, thresholds, drift monitoring, and run history--lesson 22.

### 18 - Instrument the application path safely

**Background.** A trace is a correlated record of a request and suboperations. Manual instrumentation exists for app-specific work that Foundry cannot see: custom retrieval, policy, tool adapter, cache, queue, or business operation. It complements server-side Foundry tracing; it does not enable it.

**Code path.**

1. `setup_tracing()` selects Azure Monitor exporter when connection string is
supplied or console exporter for local learning.
2. `start_as_current_span()` creates an application span around
`responses.create`.
3. Code adds model, token counts, latency, and controlled safety severity
attributes using GenAI conventions.
4. Optional `_check_safety()` classifies output; transport errors are recorded
explicitly rather than hidden as safe output.

Do not add raw prompt/output attributes by default. Design telemetry schema, retention, protected-table access, PIM/JIT review, release correlation, and incident process before enabling content capture. Lesson 26 explains the zero-code server-side tracing path after connecting Application Insights.

## Lessons 09-15: defense in depth

### Guardrail layers and intervention points

A safe system does not rely on one classifier. Separate policy enforcement from application decisions and place checks at the boundary where risk appears.

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

Foundry guardrails are configured service policy and can annotate/block at supported intervention points. The explicit Azure AI Content Safety API is a separate application call, useful for pre-screening, independent checks, or workflows outside a configured deployment. Your application still owns the response to a detection signal: block, redact, ask for clarification, route to human review, or record an audit event.

### Severity and scope distinction

| Mechanism | What it primarily handles | Result model |
|---|---|---|
| Foundry harm guardrail | Deployment/agent policy for harm categories | Safe/Low/Medium/High-style policy thresholds and filter annotations. |
| Content Safety analysis | Explicit text/image category analysis | Integer category severities, commonly 0–7. |
| Prompt Shields | Direct jailbreak or indirect document injection | Detection boolean/annotation, not harm severity. |
| PII filter | Completion/output personal-information handling | Preview annotations/filter behavior. |
| Task Adherence | Agent plan versus user intent | Preview risk signal plus details. |
| Blocklist | Organization-specific terms/patterns | Match result/filter behavior. |

Do not compare these score formats as if they were interchangeable. A safety signal is contextual evidence, not a complete risk decision.

### Guardrail implementation rules

| Rule | Why it matters |
|---|---|
| An agent guardrail overrides its model guardrail. | Tool call/response controls are unscanned unless they exist in agent policy. |
| `Annotate` is model-only; agents use annotate-and-block behavior. | Do not assume an agent can continue after annotate-only detection. |
| Tool call/response controls are preview and tool-specific. | Custom tools do not automatically gain moderation coverage. |
| Guardrails add latency at intervention points. | Budget roughly 50-100 ms per point and test full agent routes. |
| Hosted-agent attachment uses full ARM policy ID. | A bare name does not identify a policy resource. |

Use explicit Content Safety API calls when application code must decide before inference. Use deployment/agent guardrails for service-side enforcement. Both still require application block, redact, clarify, human-review, audit, and rollback behavior.

### Content Safety limits that affect lesson design

| Capability | Current documented boundary | Design response |
|---|---|---|
| Text analysis | 10,000 characters | Chunk without losing policy context. |
| Image analysis | 4 MB; 50x50-7,200x7,200; JPEG/PNG/GIF/BMP/TIFF/WEBP | Validate before upload; image severities are 0/2/4/6. |
| Prompt Shields | User prompt 10,000; five documents/10,000 total | Preserve source identity; scan ingestion/retrieval boundaries. |
| Task Adherence | 100,000 characters; best-tested English; data can process in US/EU | Confirm residency and enforce app-side HITL/block. |
| Blocklists | 100 items/request; 10,000 total; 128 chars/item | Batch updates and allow propagation before test. |
| Protected Material | English; 110-10,000 characters | Scan completion, not short user input. |

Task Adherence is preview. Local official docs show both `2024-12-15-preview` and `2025-09-15-preview` examples; lesson 14 tries the newer quickstart version before documented fallback. Validate availability in the target subscription before release.

### 09 — Content safety filters

**Question answered:** Which path should handle harmful text or image?

```bash
uv run python 01-plan-and-manage/09_content_safety_filters.py
```

The lesson contrasts a deployment-level model guardrail with explicit Content Safety text and image analysis. It uses intentionally unsafe test text; use only approved synthetic test material in labs.

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

A direct attack is in `userPrompt`: for example, attempted instruction override, authority spoofing, or jailbreak framing. The explicit shield API returns a boolean such as `userPromptAnalysis.attackDetected`. A configured deployment path can expose `jailbreak` detection/filter data or block according to policy.

Use a pre-model explicit check when you need routing or audit logic before inference. Use configured guardrails for consistent service-side enforcement. Neither removes need for strong system instructions, tool allowlists, output validation, and least-privilege tool credentials.

### 11 — Prompt Shields: document and indirect attacks

**Question answered:** Is untrusted retrieved or uploaded content trying to control the model?

```bash
uv run python 01-plan-and-manage/11_prompt_shields_docs.py
```

A document attack differs from a direct jailbreak:

```text
Direct attack:   user message contains override instructions.
Indirect attack: innocent user asks for summary; OCR/web/RAG/tool content
                 contains the attacker instruction.
```

The explicit `shieldPrompt` flow supplies documents separately and reports per-document analysis. That is the clean way to test an actual document channel in this lesson.

**Critical channel caveat:** pasting document text into a Chat Completions user message does **not** create a document-bearing channel. It can be evaluated as user-prompt content and produce a `jailbreak` result instead. An inline `indirect_attack` result requires an actual supported document path, such as configured retrieval/data source or tool response, plus Document attack control. Do not claim this sample proves that full inline document integration.

Treat all external content as data, not instructions. Preserve source identity, minimize tool authority, scan before ingestion and at retrieval/tool boundaries, and give the model explicit rules for handling untrusted content.

### 12 — Spotlighting (preview)

**Question answered:** What extra trust-boundary defense is available for supported document workflows?

```bash
uv run python 01-plan-and-manage/12_spotlighting.py
```

This local reference inspects documented request shape and integration boundary. Spotlighting is **preview**, works with **Chat Completions only**, and is **not supported for agents**. It marks document content as lower trust through its documented transformation/encoding behavior; it is additive to document Prompt Shields, not a replacement.

Use it only after validating preview eligibility and token impact. Document expansion can increase input tokens and exceed context/input limits. It cannot replace retrieval hygiene, Prompt Shields, tool authorization, or testing real document paths.

### 13 — PII filter (preview)

**Question answered:** How can a completion guardrail expose personal-data handling behavior?

```bash
uv run python 01-plan-and-manage/13_pii_filter.py
```

The lesson requests synthetic values and inspects output filter annotations. PII filter is a **preview** completion/output intervention control; it is not a promise that all personal data is found, removed, or lawful to process. Enable and test the matching deployment guardrail before relying on results.

Production design should minimize collection, avoid logging sensitive prompts and outputs, restrict telemetry access, define retention, and test false positive/negative consequences. Do not feed real personal data into this lab.

### 14 — Task Adherence (preview)

**Question answered:** Does an agent's proposed tool behavior match user intent?

```bash
uv run python 01-plan-and-manage/14_task_adherence.py
```

The lesson calls Content Safety Task Adherence with tool definitions and conversation/tool-plan messages. It compares aligned and misaligned plans, such as reading leave balance versus submitting leave, or drafting versus sending an email.

Task Adherence is **preview** and returns a signal; it does not execute or block a tool on its own. The application must stop the action, ask confirmation, or escalate to human review. It is not a jailbreak detector and not a generic harm classifier. Test language and workflow behavior with representative examples before making it a release gate.

### 15 — Custom blocklists

**Question answered:** How can a policy catch organization-specific terms that harm categories miss?

```bash
uv run python 01-plan-and-manage/15_blocklists.py
```

The lesson creates/updates `northwind-exam-blocklist`, adds lab terms, and analyzes text for matches only with explicit intent:

```bash
uv run python 01-plan-and-manage/15_blocklists.py --apply
```

It persists service state. Delete lab-only list/items when finished if they are no longer needed.

Blocklists fit codenames, competitor names, regulated phrases, and other explicit domain policy. They do not replace semantic moderation or injection defense. Allow for propagation delay after changes. Content Safety blocklist APIs and Foundry deployment custom-blocklist configuration are related concepts with different wiring; configure and test the one your serving path uses.

## Lessons 16–18: agents, evaluation, observability

### Agent types and state model

| Type | Definition lives in | Best use | Domain 1 boundary |
|---|---|---|---|
| Code-defined / ephemeral pattern | Application call (`instructions`) | Small code-owned behavior, prototypes, tests | Lesson 16 uses this; it does not create an agent resource. |
| Prompt agent | Foundry-managed definition | Shared/versioned agent behavior | Broader lifecycle covered in Domain 2. |
| Hosted agent | Your packaged code hosted by Foundry | Custom runtime/dependencies/tooling | Lesson 07 only lists hosted agents as auth smoke test. |

"Ephemeral" describes where behavior is defined, not an absence of safety, identity, cost, or observability responsibilities. A code-defined Responses call can still use project access, deployment guardrails, and application telemetry.

### 16 — Agent basics through Responses API

**Question answered:** How do instructions and multi-turn state work without creating a Foundry agent resource?

```bash
uv run python 01-plan-and-manage/16_agent_basics.py
```

The lesson uses code-defined instructions for a single response, then links a follow-up through `previous_response_id`. This demonstrates conversation state without resending every prior message in the client call.

Use this pattern for bounded behavior owned and deployed with application code. It is not a substitute for evaluating instructions, authorizing tools, setting retention expectations, or deciding whether managed prompt/hosted agents fit team operations better.

### Evaluation concepts: rubric versus self-critique

| Approach | What it is | What it proves |
|---|---|---|
| LLM self-critique | Model reviews draft against prompt checklist | A heuristic application pattern for this one run. |
| Built-in evaluator | Documented evaluator contract/run with inputs, metrics, and output | Evaluator results for configured dataset/run. |
| Golden-set CI gate | Repeatable representative test set and threshold | Release evidence, only as good as dataset/threshold. |
| Human review | Domain expert examines selected/flagged cases | High-value qualitative/regulated review. |

Groundedness asks whether response claims are supported by supplied sources. Response Completeness asks whether needed aspects were covered. Neither is identical to safety, tool correctness, or user satisfaction. Preview evaluator requirements can differ; for example, Response Completeness needs its supported evaluation contract such as `ground_truth` and `response`.

### 17 — Self-critique and regeneration

**Question answered:** How can an application implement draft → critique → regenerate?

```bash
uv run python 01-plan-and-manage/17_evaluator_groundedness.py
```

The lesson generates a support answer, asks another model call to return `COMPLETE` or `MISSING` against a checklist, and regenerates when needed. This is useful for learning how a rubric can shape revision.

**Limitation:** lesson 17 is **not** a Foundry built-in Groundedness or Response Completeness evaluator, and it does not create an evaluation run. A model can make the same mistake in drafting and reviewing. For production, use held-out examples, documented evaluator contracts, human review where needed, and monitor quality drift rather than trusting a self-approval loop.

### 18 — Manual tracing

**Question answered:** Which runtime attributes should an application record?

```bash
uv run python 01-plan-and-manage/18_agent_tracing.py
```

The lesson creates an application-owned OpenTelemetry span around a Responses call. It records model, token metadata, latency, and best-effort safety metadata without adding prompt or output text as span attributes; an optional Application Insights connection string exports telemetry.

**Limitation:** this is manual application instrumentation, **not** automatic Foundry server/client tracing and **not** proof of full Foundry Traces integration. Treat spans as a carefully governed operational dataset: avoid secrets and unnecessary personal data, cap previews, apply access controls, set retention, and correlate traces with deployment version and release ID.

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
| Protected Material text | GA Content Safety API | Lesson 19 checks synthetic English completion only. |
| Groundedness detection | **Preview** Content Safety API | Lesson 20 is a source-support signal, not a Foundry evaluator run. |
| Provenance detection | **Preview** async Content Safety API | Lesson 21 requires Blob read access and detects markers, not authenticity. |
| Evaluation / continuous evaluation | **Preview** | Lessons 22-23 create billable persistent state only with `--apply`. |
| Human feedback / trace annotations | **Preview** | Lesson 24 shows append-only correlated telemetry path. |
| AI Red Teaming Agent | **Preview** | Lesson 25 defaults to a safe synthetic callback; use purple environment. |
| Server-side Foundry tracing | Platform setup | Lesson 26 is read-only preflight; App Insights connection enables tracing. |

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

Treat Foundry configuration, prompts, deployment names, guardrail policy, and application code as a release system—not portal-only changes.

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

Avoid using a single score as a deployment decision. A higher aggregate quality score can hide a critical safety, residency, latency, cost, or tool-action failure. Keep rollback ownership and a known-good configuration.

## Advanced production path: lessons 19-26

Lessons 01-18 establish basic planning, safety, and application telemetry. Lessons 19-26 add output safety, groundedness, provenance, evaluations, feedback, red teaming, and Foundry-native observability. Each answers a different operational question; none replaces the others.

```text
Application identity
  ├── Foundry project: agent, deployment, guardrail, evaluation, traces
  ├── Content Safety: moderation, shields, grounding, provenance
  ├── Storage: source media and datasets
  ├── Application Insights / Log Analytics: telemetry, feedback, retention
  └── Key Vault / network policy / RBAC: security boundaries
```

A Foundry project connection is not permission to access Storage, Key Vault, Search, Content Safety, or Log Analytics. Each is a separate Azure resource with its own identity, network, role, cost, and retention boundary.

| Question | Use | Do not confuse with |
|---|---|---|
| Is generated output known protected text? | Protected Material API | A copyright ownership decision. |
| Is an answer supported by supplied sources? | Groundedness detection/evaluator | Harm moderation or factual truth outside sources. |
| Does media contain a recognized origin marker? | Provenance detection | Proof that unmarked media is human-created or safe. |
| Did a release meet measurable quality/safety criteria? | Foundry evaluation run | Self-critique of one response. |
| Did a real user judge one response useful? | Correlated feedback/trace annotation | A detached application log. |
| What adversarial weaknesses exist? | Red-team scan in purple environment | Production traffic test. |
| What did Foundry observe end-to-end? | Project-connected App Insights tracing | A manual client span only. |

### 19 - Protected Material detection

**What:** GA Content Safety output check for known protected English text. **Why:** route a completion to abstention, attribution, legal review, or policy handling. **How:** send a model completion to `text:detectProtectedMaterial`; inspect `protectedMaterialAnalysis.detected`. **Use it:** after generation where reproduction risk matters. **Do not use it:** for user prompts, harm classification, short snippets, or legal conclusions.

```bash
uv run python 01-plan-and-manage/19_protected_material.py
uv run python 01-plan-and-manage/19_protected_material.py --run
```

Requires Content Safety, `CONTENT_SAFETY_ENDPOINT`, and `Cognitive Services User`. It accepts 110-10,000 English characters; the lab sends synthetic text and creates no persistent state. Keep real output out of logs unless retention and reviewer access are approved.

### 20 - Groundedness detection

**What:** preview Content Safety API for unsupported answer spans. **Why:** a fluent RAG answer can still invent claims. **How:** compare generated `text` to `groundingSources`, then use `ungroundedDetected`, `ungroundedPercentage`, and `ungroundedDetails`. The percentage is a proportion, not confidence. **Use it:** summaries and answers backed by curated content. **Do not use it:** as authorization, citation storage, or universal truth test.

```bash
uv run python 01-plan-and-manage/20_groundedness_detection.py
uv run python 01-plan-and-manage/20_groundedness_detection.py --run
```

Requires S0 Content Safety in a supported region, `Cognitive Services User`, and `CONTENT_SAFETY_ENDPOINT`; F0 is unsupported. The preview API is `2024-09-15-preview`. Text and optional QnA query allow 7,500 characters; sources total 55,000. Reasoning mode additionally needs an eligible GPT-4o deployment and `llmResource`; do not enable it by accident.

### 21 - Provenance detection

**What:** preview asynchronous detection of C2PA and supported invisible watermark markers in media. **Why:** add an origin signal before trusting or publishing media. **How:** submit `content.uri` to `operations:detect`, poll its operation ID, and handle `ProvenanceDetected`, `NoProvenanceDetected`, or failure. **Use it:** media review workflows. **Do not use it:** as a safety classifier, ownership proof, or authenticity guarantee.

```bash
uv run python 01-plan-and-manage/21_provenance_detection.py
uv run python 01-plan-and-manage/21_provenance_detection.py --run
```

Requires `PROVENANCE_SOURCE_URL` (HTTPS Blob/SAS URI), `CONTENT_SAFETY_ENDPOINT`, `Cognitive Services User` for caller, and `Storage Blob Data Reader` for Content Safety's managed identity. Prefer managed identity over a long-lived SAS. This uses `2026-07-01-preview`; local docs do not list a fixed region matrix, so verify availability before a production design.

### 22 - Evaluation runs, not self-critique

Lesson 17 is draft -> critique -> regenerate. It teaches a pattern, but it does not create a dataset, metric, run, trend, or release gate. A Foundry evaluation is repeatable evidence with a documented input mapping.

```bash
uv run python 01-plan-and-manage/22_foundry_evaluation.py
uv run python 01-plan-and-manage/22_foundry_evaluation.py \
  --apply --dataset path/to/tests.jsonl [--rubric reviewed-rubric-name]
```

The first command is preflight. Applying uploads data, creates an evaluation and run, calls the agent/evaluators, and can bill. It needs JSONL `query` fields, `AZURE_AI_PROJECT_ENDPOINT`, `AZURE_AI_AGENT_NAME`, `AZURE_AI_MODEL_DEPLOYMENT_NAME`, a target agent/deployment, and `Foundry User`.

| Evaluator | Input / purpose | Distinction |
|---|---|---|
| Rubric / Quality | Judge deployment plus reviewed criteria | Product-specific release quality. |
| Risk and safety | Usually query + response; hosted safety model | Does not need the judge deployment-name constructor. |
| Agent | Tool definitions/calls or response | Measures tool behavior, not only prose. |
| Groundedness Pro | Binary Content Safety-backed score | Different from model-based 1-5 Groundedness. |
| Response Completeness | `ground_truth` and response | Different from grounding and safety. |

Task Adherence has three surfaces: lesson 14's Content Safety REST signal (`tools` plus conversation messages), Foundry guardrail runtime annotation, and `builtin.task_adherence` evaluator over evaluation data. Choose real-time enforcement, runtime policy, or offline measurement deliberately. Rows are limited to 2 MB; batches to 100,000 rows; evaluator region support varies.

### 23 - Continuous evaluation

**What:** sampled post-deployment evaluation rule. **Why:** catch regression after release. **How:** evaluates completed responses on a bounded schedule. **Use it:** monitored production quality/safety signals. **Do not use it:** as a synchronous safety block or a dump of unrestricted sensitive traffic.

```bash
uv run python 01-plan-and-manage/23_continuous_evaluation.py
uv run python 01-plan-and-manage/23_continuous_evaluation.py --apply
```

Applying creates persistent evaluation/rule state and incurs sampling, evaluator, and telemetry cost. Requires project/agent identifiers, Application Insights, and `Foundry User` for project managed identity. The lesson caps at 10 runs/hour; change only after privacy, cost, alert, owner, and rollback review.

### 24 - Human feedback and HITL

**What:** structured quality signal linked to an exact response. **Why:** automated metrics cannot replace user/domain-expert judgment. **How:** emit `gen_ai.evaluation.result` while original response span is active; portal annotations are append-only history. **Use it:** approved review and feedback flows. **Do not use it:** for silent sensitive-data capture.

```bash
uv run python 01-plan-and-manage/24_human_feedback.py
```

The lesson prints integration guidance; a handler calls `emit_end_user_feedback(..., apply=True)` with the original span. It requires project-connected Application Insights, tracing packages, and governed retention. Reviewers need `Foundry User` plus Reader; template management needs `Foundry Project Manager`. Human templates are preview; the default binary `task_completion` path must preserve trace/span correlation.

### 25 - AI Red Teaming Agent

**What:** preview adversarial scan with Attack Success Rate evidence. **Why:** find systematic failures before users do. **How:** generate approved attacks against an explicit target. **Use it:** nonproduction purple environment with an incident/mitigation owner. **Do not use it:** against production tools, customer content, or unapproved endpoints.

```bash
uv run python 01-plan-and-manage/25_red_teaming.py
AZURE_AI_PROJECT=<project-endpoint> \
  uv run python 01-plan-and-manage/25_red_teaming.py --apply
```

The apply lesson deliberately uses only a fixed safe synthetic callback; no real model, tool, or application receives the generated attacks. It requires Python 3.10-3.13, `azure-ai-evaluation[redteam]`, Entra identity, Foundry project, and `Foundry User` for project managed identity. Scans bill and region support is preview-sensitive; verify it before targeting a real nonproduction system.

### 18 and 26 - manual versus Foundry-native tracing

```bash
uv run python 01-plan-and-manage/18_agent_tracing.py
uv run python 01-plan-and-manage/26_foundry_tracing_setup.py
```

Lesson 18 adds application-owned `gen_ai.*` attributes and token counts around a Responses call. `AZURE_OPENAI_ENDPOINT` is required; `CONTENT_SAFETY_ENDPOINT` and `APPLICATIONINSIGHTS_CONNECTION_STRING` are optional. Prompts and outputs are not span attributes. It is not server-side Foundry tracing.

Lesson 26 is local/read-only preflight. Foundry-native tracing starts after Application Insights is connected to project; supported prompt/hosted agent and workflow paths then trace automatically. Trace access needs project access and Log Analytics Reader; protected sensitive-content tables also require Privileged Monitoring Data Reader.

| Operational rule | Why |
|---|---|
| Record content only for approved development/debugging. | Prompt/output data increases privacy and incident scope. |
| Use protected `AppGenAIContent` access, RBAC, PIM/JIT, and short retention. | Sensitive GenAI attributes need stronger control. |
| Treat `protectGenAISensitiveData` as subscription mutation. | It is preview and intentionally not scripted. |
| Download cluster-analysis CSV before leaving. | Preview clustering results are not persisted. |
| Sanitize trace-to-dataset samples. | Production traces can contain customer and tool data. |

### Security, networking, IaC, and release

| Decision | Recommendation | Common pitfall |
|---|---|---|
| Identity | Managed/workload identity in Azure; Azure CLI only locally | Agents/evaluations require Entra ID; custom subdomain is required for token auth. |
| Scope | Project/resource/agent scope; `Foundry Agent Consumer` for endpoint-only callers | Owner/Contributor management rights do not grant data-plane inference. |
| Network | Choose public/IP rules, Private Link, managed VNet, or customer VNet from compliance and outbound needs | Fully private deployments need SDK/CLI configuration; portal alone is insufficient. |
| Keys | Microsoft-managed by default; CMK only for requirement | CMK needs regional Key Vault, soft delete, purge protection, identity, Crypto User. |
| IaC | Portal to learn; Bicep/Terraform for reviewed repeatability | Do not maintain portal, CLI, and IaC as competing sources of truth. |
| Resilience | Independent regional resources plus app routing | Global/Data Zone is not automatic application failover. |

Release model: provision identity/network/diagnostics through reviewed IaC; verify workload identity and least privilege; run unit contracts, curated evaluations, safety regressions, and bounded red teaming; approve measurable quality/latency/cost/rollback evidence; deploy progressively; monitor traces, safety, quota, and cost; roll back known-good configuration on regression.

**Troubleshoot:** `Custom subdomain required` means token-auth prerequisite is missing. `401`/`403` means inspect endpoint, principal object ID, role, scope, and propagation--do not retry. Missing evaluations/red team usually mean feature-specific region, preview access, managed-identity role, or bad mapping. Missing traces usually mean App Insights connection, ingestion delay, Log-Analytics/protected-table role, or retention. Provenance file-not-found usually means unreachable Blob URI or missing Storage Blob Data Reader.

### Interview prompts and takeaways

1. Why is a deployment name not a model name? Deployment alias also selects
version, capacity, filters, and limits; application calls alias while automation declares model/version.
2. Groundedness API or evaluation? API is immediate source-support signal;
evaluation is repeatable offline/release evidence.
3. How do model and agent guardrails interact? Assigned agent guardrail
overrides its model guardrail; tool controls must exist in agent policy.
4. What proves safe release? Least privilege, policy tests, representative
evaluation, bounded red team, human review, governed telemetry, rollout, and rollback--never one score.

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

Runnable evidence in this folder covers deployment selection/control-plane API, quota inspection, retry behavior, project credential validation, assignment inspection, Content Safety and Prompt Shield calls, blocklist lifecycle, Responses conversation state, self-critique pattern, and manual telemetry.

It does **not** prove production readiness, regional feature availability, complete compliance, service-side agent tracing, full evaluation-run setup, guardrail coverage on every route, or a secure tool-execution design. Preview features can change. A successful call proves only that call under its current identity, resource, configuration, and time.

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
- [Azure AI Content Safety](https://learn.microsoft.com/azure/ai-services/content-safety/)
- [Foundry guardrails](https://learn.microsoft.com/azure/ai-foundry/guardrails/guardrails-overview)
- [Foundry architecture](https://learn.microsoft.com/azure/ai-foundry/concepts/architecture)
- [Foundry authentication](https://learn.microsoft.com/azure/ai-foundry/concepts/authentication-authorization)
- [Private Link](https://learn.microsoft.com/azure/ai-foundry/how-to/configure-private-link)
- [Foundry observability](https://learn.microsoft.com/azure/ai-foundry/observability/concepts/observability)
- [Tracing setup](https://learn.microsoft.com/azure/ai-foundry/observability/how-to/trace-agent-setup)
- [Agent evaluation](https://learn.microsoft.com/azure/ai-foundry/observability/how-to/evaluate-agent)
- [Human evaluation](https://learn.microsoft.com/azure/ai-foundry/observability/how-to/human-evaluation)
- [AI Red Teaming Agent](https://learn.microsoft.com/azure/ai-foundry/concepts/ai-red-teaming-agent)
- [Bicep resource template](https://learn.microsoft.com/azure/ai-foundry/how-to/create-resource-template)
- [Terraform resource deployment](https://learn.microsoft.com/azure/ai-foundry/how-to/create-resource-terraform)
