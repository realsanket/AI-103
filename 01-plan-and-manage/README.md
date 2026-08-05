# Domain 1: Plan and manage Microsoft Foundry

Runnable labs for deployment planning, access, guardrails, agents, and operations.
Run commands from repository root:

```bash
uv run python 01-plan-and-manage/01_model_catalog_list.py
```

These labs use live Azure resources unless marked **local**. Read prerequisites and
cost warnings before running them.

## Prerequisites

### Resources

Create or identify:

- Microsoft Foundry resource and project. Set `FOUNDRY_ENDPOINT` to project
  endpoint expected by this repository.
- Model deployment for `DEFAULT_MODEL`.
- Optional `model-router` deployment for lesson 04.
- Azure AI Content Safety resource for lessons 09–15. Set
  `CONTENT_SAFETY_ENDPOINT`.
- Azure subscription and resource group for lessons 03, 05, and 08. Set
  `AZURE_SUBSCRIPTION_ID` and `AZURE_RESOURCE_GROUP`.
- Optional Application Insights connection string for lesson 18.

Use a nonproduction resource for destructive or configuration-changing lessons.

### Roles and credentials

Sign in locally:

```bash
az login
```

`DefaultAzureCredential` commonly gets a developer token from Azure CLI locally
and a managed identity token when running on Azure. It chooses first available
credential in its chain; it doesn't prove which one succeeded.

Assign roles at smallest applicable scope:

| API path | Minimum starting role | Scope | Notes |
|---|---|---|---|
| Project-scoped Foundry API, agents, project Responses API | `Foundry User` | Project or Foundry resource | Build and call pre-deployed models. |
| Direct Azure OpenAI resource inference | `Cognitive Services OpenAI User` | Azure OpenAI resource | OpenAI-only data actions. `Cognitive Services User` covers broader resource capabilities. |
| Deploy or change model deployments | Suitable control-plane role, such as `Cognitive Services Contributor` | Foundry resource | `Owner` or `Contributor` alone doesn't grant all inference data actions. |
| View subscription quota | `Cognitive Services Usages Reader` or subscription `Reader` | Subscription | Required for quota visibility; not resource scope. |
| View manual/Application Insights telemetry | `Log Analytics Reader` | Connected telemetry resource | Add protected-table reader access when applicable. |

For a managed identity, enable system-assigned identity on caller or attach
user-assigned identity, then assign same role to identity's **principal object
ID**. Do not use client ID in a role assignment.

### Environment

Copy repository environment template, then set required values. Never commit
keys, connection strings, or `.env`.

```dotenv
FOUNDRY_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<project>
DEFAULT_MODEL=<deployment-name>
MODEL_ROUTER_DEPLOYMENT=model-router
CONTENT_SAFETY_ENDPOINT=https://<content-safety-resource>.cognitiveservices.azure.com
AZURE_SUBSCRIPTION_ID=<subscription-id>
AZURE_RESOURCE_GROUP=<resource-group>
# Optional: sends lesson 18's manual span to Azure Monitor
APPLICATIONINSIGHTS_CONNECTION_STRING=<connection-string>
```

Direct Azure OpenAI and project-scoped Foundry endpoints are different surfaces.
Don't interchange their URLs or role assumptions.

## Safe learning order

1. Start with **01**, **02**, and **05**. They list or print information.
1. Run **07** only after roles and endpoint work.
1. Run **04**, **06**, **09–15**, **16**, and **17** against a low-cost
   nonproduction deployment.
1. Run **03** only after reviewing model, SKU, capacity, and region.
1. Treat **08** as an access review. Leave `assign_role` commented unless
   deliberately changing access.
1. Run **18** after confirming telemetry destination and access controls.

## Lessons

| # | File | Runnable objective | Status and side effect |
|---:|---|---|---|
| 01 | [`01_model_catalog_list.py`](01_model_catalog_list.py) | List project deployments. | Live read. |
| 02 | [`02_deployment_types.py`](02_deployment_types.py) | Compare standard, provisioned, batch, and developer deployment types. | **Local** reference; model availability varies. |
| 03 | [`03_deploy_model.py`](03_deploy_model.py) | Create or update one Global Standard deployment. | **Writes resource; creates billable deployment/quota allocation.** |
| 04 | [`04_model_router.py`](04_model_router.py) | Route Responses API prompts through `model-router`; log selected model. | Live inference cost; requires router deployment. |
| 05 | [`05_quotas_and_tpm.py`](05_quotas_and_tpm.py) | List deployments and location usage. | Live control-plane read; needs subscription permission. |
| 06 | [`06_rate_limit_backoff.py`](06_rate_limit_backoff.py) | Retry transient Responses API failures with exponential backoff. | Five live inference calls. |
| 07 | [`07_managed_identity_agent.py`](07_managed_identity_agent.py) | Validate project-scoped Entra ID auth, agent listing, and one response. | Live read plus inference cost. |
| 08 | [`08_rbac_role_policies.py`](08_rbac_role_policies.py) | List role assignments; contains opt-in role assignment helper. | Read by default. Uncommenting helper changes access. |
| 09 | [`09_content_safety_filters.py`](09_content_safety_filters.py) | Compare deployment guardrail and Content Safety text/image analysis. | Live safety calls; uses intentionally unsafe test text. |
| 10 | [`10_prompt_shields_user.py`](10_prompt_shields_user.py) | Detect direct user-prompt jailbreaks. | Live Content Safety and optional deployment call. |
| 11 | [`11_prompt_shields_docs.py`](11_prompt_shields_docs.py) | Detect indirect attack in local OCR document sample. | Live Content Safety call; no fake Chat Completions document test. |
| 12 | [`12_spotlighting.py`](12_spotlighting.py) | Inspect documented Spotlighting request shape and integration boundary. | **Local** reference; Spotlighting is preview. |
| 13 | [`13_pii_filter.py`](13_pii_filter.py) | Inspect PII completion-filter annotations using synthetic values. | Live inference; PII filter is preview. |
| 14 | [`14_task_adherence.py`](14_task_adherence.py) | Analyze aligned and misaligned tool plans with Content Safety API. | Live preview API call; English-focused. |
| 15 | [`15_blocklists.py`](15_blocklists.py) | Create/update a Content Safety blocklist and test it. | **Writes persistent blocklist and items; propagation delay.** |
| 16 | [`16_agent_basics.py`](16_agent_basics.py) | Call Responses API with code-defined instructions and linked turns. | Live inference; not a Foundry agent resource. |
| 17 | [`17_evaluator_groundedness.py`](17_evaluator_groundedness.py) | Demonstrate LLM self-critique and regeneration. | Live inference; **not** a Foundry evaluation run. |
| 18 | [`18_agent_tracing.py`](18_agent_tracing.py) | Emit manual OpenTelemetry span, token metadata, latency, and safety metadata. | Live inference and safety call; **not** full Foundry tracing. |

## Cost and side-effect controls

- **Lesson 03** can create a deployment. Delete intentional experiments in
  Foundry portal or Azure portal when done.
- **Lessons 04, 06, 07, 09–18** can send model or Content Safety requests.
  Prompt length, output, model, and retry behavior affect cost.
- **Lesson 05** reports quota, not actual bill. Standard quota units and
  RPM/TPM ratios are model-specific.
- **Provisioned deployments** reserve PTUs and incur hourly cost while present,
  even if idle. PTU quota doesn't guarantee regional capacity.
- **Lesson 15** persists a named blocklist (`northwind-exam-blocklist`).
  Delete lab-only list and items after use if no longer needed.
- **Lesson 18** can export prompt previews and output-derived attributes.
  Do not send production secrets or personal data to console or telemetry.

## Documented feature status

| Feature | Status | Practical limit |
|---|---|---|
| Responses Model Router | Documented supported | Use `responses.create(model="model-router", ...)`; deployment and availability still required. |
| Prompt Shields | Documented guardrail | Test document attacks only through actual document-bearing user-input or tool-response path. |
| Spotlighting | **Preview** | Chat Completions only; not agents; base64 increases document tokens and can exceed input limits. |
| PII filter | **Preview** | Completion/output intervention point; configured deployment guardrail required. |
| Task Adherence | **Preview** | Explicit Content Safety API returns a signal; application must block/escalate. Test against actual workflow. |
| Response Completeness | **Preview** built-in evaluator | Requires evaluation run plus `ground_truth` and `response`; lesson 17 doesn't implement it. |
| Groundedness | Built-in evaluator | Requires documented evaluation contract; lesson 17 doesn't implement it. |
| Manual OpenTelemetry | Application instrumentation | A manual span isn't automatic Foundry server/client tracing or Foundry Traces integration. |

## Objective coverage

Runnable evidence exists only for objectives represented by scripts above:

- Deployment selection, deployment control-plane API, quota inspection, and
  request retry.
- Project credential validation, managed-identity-compatible credential path,
  and RBAC assignment inspection.
- Content Safety analysis, Prompt Shields direct and document API flows, PII
  guardrail annotation inspection, Task Adherence API, and blocklist lifecycle.
- Responses API conversation state, self-critique pattern, and manual
  OpenTelemetry instrumentation.

Read-only reference lessons do not prove service configuration. Preview features
can change, and a successful request does not prove production readiness.

## Official documentation

- [Deployment types](https://learn.microsoft.com/azure/ai-foundry/foundry-models/concepts/deployment-types)
- [Quota management](https://learn.microsoft.com/azure/ai-foundry/openai/how-to/quota)
- [Responses Model Router](https://learn.microsoft.com/azure/ai-foundry/openai/how-to/responses-model-routing)
- [Foundry RBAC](https://learn.microsoft.com/azure/ai-foundry/concepts/rbac-foundry)
- [Prompt Shields and Spotlighting](https://learn.microsoft.com/azure/ai-foundry/openai/concepts/content-filter-prompt-shields)
- [Task Adherence](https://learn.microsoft.com/azure/ai-services/content-safety/concepts/task-adherence)
- [Built-in evaluators](https://learn.microsoft.com/azure/ai-foundry/concepts/built-in-evaluators)
- [Client-side agent tracing](https://learn.microsoft.com/azure/ai-foundry/observability/how-to/trace-agent-client-side)
