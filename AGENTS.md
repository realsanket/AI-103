# AI-103 / Microsoft Foundry repository

## Purpose

Hands-on, current Microsoft Foundry and Azure AI learning repository. It has
**224 numbered Python lessons** across five AI-103 domains plus four current
supplemental domains. Domain READMEs are teaching source of truth; this file is
the operational handoff for future coding sessions.

**Scope rule:** add current GA capabilities or clearly labeled active previews
only. Do not add legacy, deprecated, retired, or migration-only services as
new labs.

## Start here

| Area | Lessons | Read first |
|---|---:|---|
| 01 Plan and manage | 35 | `01-plan-and-manage/README.md` |
| 02 Generative AI and agents | 49 | `02-generative-ai-and-agents/README.md` |
| 03 Computer vision | 16 | `03-computer-vision/README.md` |
| 04 Text and speech | 30 | `04-text-and-speech/README.md` |
| 05 Information extraction | 29 | `05-information-extraction/README.md` |
| 06 Model customization and delivery | 20 | `06-model-customization-other/README.md` |
| 07 Production platform | 10 | `07-production-platform-other/README.md` |
| 08 Advanced agents | 28 | `08-advanced-agents-other/README.md` |
| 09 Document Intelligence v4 | 7 | `09-current-ai-services-other/README.md` |

Also read:

- `README.md` -- setup, resource topology, safe run order.
- `docs/coverage.md` -- evidence-based AI-103 mapping and honest boundaries.
- `AI-103.md` -- local official exam-skills source.
- `.context/azure-ai-docs/` -- local Microsoft documentation source.
- `_shared/` -- endpoint factories, configuration, clients, sample data.

## Architecture contract

Do not exchange these endpoint/client pairs:

| Workload | Environment variable | Client |
|---|---|---|
| Direct Responses, images, embeddings, video | `AZURE_OPENAI_ENDPOINT` (`*.openai.azure.com`) | `_shared/openai_client.py` |
| Foundry projects, prompt/hosted agents, project tools | `PROJECT_ENDPOINT` (`*/api/projects/*`) | `_shared/foundry_client.py` |
| Foundry account management | `FOUNDRY_ENDPOINT` | management-plane lessons |
| Content Understanding | `CU_ENDPOINT` | `_shared/cu_client.py` |
| Language, Speech, Content Safety, Document Intelligence | service `*.cognitiveservices.azure.com` endpoint | respective shared client |
| Translator Text v3 | global Translator endpoint + `TRANSLATOR_RESOURCE_ID` | `_shared/translator_client.py` |
| Azure AI Search | `SEARCH_ENDPOINT` | `_shared/search_client.py` |

`model=` normally takes a **deployment name**, not a model-family name.
Use Entra ID and least-privilege RBAC. A successful
`DefaultAzureCredential` chain does not prove endpoint-specific authorization.

### Environment-variable groups

Copy `.env.example` to `.env`; blank values and any value containing a
`<placeholder>` are treated as unset. Read environment values through
`_shared.config.settings()`/`env()`, or call `load_env()` before `os.getenv`.
Do not add runtime secrets to the template.

| Group | Representative variables | Used by |
|---|---|---|
| Foundry core | `FOUNDRY_ENDPOINT`, `PROJECT_ENDPOINT`, `AZURE_OPENAI_ENDPOINT`, `DEFAULT_MODEL` | All domains |
| Model specialization | `REASONING_MODEL`, `IMAGE_MODEL`, `VIDEO_MODEL`, `EMBEDDING_MODEL`, `MODEL_ROUTER_DEPLOYMENT` | D1-D3, D6 |
| AI services | `LANGUAGE_ENDPOINT`, `SPEECH_ENDPOINT`, `CONTENT_SAFETY_ENDPOINT`, `DOCUMENT_INTELLIGENCE_ENDPOINT` | D1, D4, D9 |
| Extraction/retrieval | `CU_ENDPOINT`, `CU_API_VERSION`, `SEARCH_ENDPOINT`, `SEARCH_INDEX_VECTOR` | D3, D5 |
| Storage | `STORAGE_ACCOUNT`, `STORAGE_CONTAINER` | D3-D5 |
| Monitoring/control plane | `APPLICATIONINSIGHTS_CONNECTION_STRING`, `AZURE_SUBSCRIPTION_ID`, `AZURE_RESOURCE_GROUP` | D1, D2, D6-D8 |

Runtime-only values such as SAS URLs, batch Speech SAS, Document Intelligence
document URLs, custom training container URLs, or document-translation keys
belong in shell, Key Vault, or CI secret store. Never put them in
`.env.example`.

## Domain-specific contracts

### 01: plan and manage

- Management plane uses `CognitiveServicesManagementClient`; inference uses
  project/direct clients.
- `DEPLOYMENT_NAME`, `DEPLOYMENT_MODEL_NAME`, and optional
  `DEPLOYMENT_MODEL_VERSION` are only for deployment automation. `DEFAULT_MODEL`
  remains an existing inference deployment alias.
- Guardrail, Content Safety API, evaluator, and manual tracing are distinct
  surfaces. Preserve that distinction in code and coverage claims.

### 02: generative AI and agents

- Function/OpenAPI/MCP/A2A calls are model proposals, never authorization.
  Validate schema, caller identity, tenant, business rule, timeout,
  idempotency, and approval before consequence.
- Agent/project work uses `PROJECT_ENDPOINT`; direct LangChain/OpenAI
  embeddings use `AZURE_OPENAI_ENDPOINT/openai/v1`.
- Hosted-agent assets in D2 are local/preflight references until explicitly
  deployed. Do not claim A2A/Toolbox/MCP connection success from preflight.

### 03: computer vision

- Base64 data URLs, local multipart image files, and Blob SAS URLs are
  different trust and transport paths.
- Image moderation, model guardrails, OCR injection, provenance, and visual
  policy are separate controls.
- Sora/CU jobs are asynchronous: preserve bounded polling, terminal failure
  diagnostics, cleanup, and output retention rules.

### 04: text and speech

- Language, Translator, Speech SDK, MAI transcription, and Voice Live have
  separate endpoint/auth/region contracts.
- Translator global Entra flow requires `TRANSLATOR_RESOURCE_ID`.
- Batch Speech uses a runtime-only SAS. Voice Live and Custom Speech require
  explicit audio, consent, retention, and cleanup handling.

### 05: information extraction

- Azure AI Search is corpus retrieval; Content Understanding/Document
  Intelligence are document extraction. Do not merge their claims.
- Search indexing contract spans `index.json`, `data_source.json`,
  `skillset.json`, and `indexer.json`; change them as one unit.
- Enforce ACL/security trimming before retrieved chunks enter a model prompt.
  Preserve chunk/source/indexer/skillset/version provenance.

### 06: model customization

- Fine-tuning, distillation, and RFT are expensive asynchronous lifecycle
  operations. Dataset quality, consent, grader calibration, baseline
  evaluation, capacity, model support, and rollback come before submission.
- Do not train on secrets, unsupported IP, unreviewed customer content, or
  unvalidated synthetic output.

### 07: production platform

- Bicep/Terraform/Policy assets are authoritative infrastructure examples.
  Their numbered entrypoints are local preflight or plan/what-if by default.
- Private endpoints, CMK, policy, and DR need subscription permissions and
  disposable/nonproduction validation. Never make `--apply` implicit.

### 08: advanced agents

- Foundry IQ, Toolbox, A2A, routines, gateway, and optimizer are current
  platform capabilities with feature/region/role prerequisites.
- Agent cards/endpoints, knowledge bases, browser/tool authority, and
  publishing are security boundaries. Use least privilege and approval.

### 09: current Azure AI services

- Document Intelligence v4 is current GA and complements CU with deterministic
  OCR/layout/prebuilt fields and confidence semantics.
- Face recognition stays out of scope; Face liveness remains deferred until
  approved access exists.

## Safe cloud-development workflow

1. Start with local preflight and static asset validation.
2. Identify target resource, principal, scope, region, API version, model,
   quota, price meter, retention, and cleanup owner.
3. Test using synthetic/authorized data in disposable resources.
4. Use an explicit `--apply` or `--run` only after reviewing side effects.
5. Capture operation IDs, deployed versions, effective roles, costs, output
   locations, and failures without recording secrets/content.
6. Delete temporary agents, files, vector stores, analyzers, jobs, blobs,
   deployments, and resource groups according to the lesson's cleanup path.
7. Update README/coverage status only with evidence. Unsupported preview or
   blocked network paths are valid **Partial** results, not reasons to fake a
   fallback.

## Safe change rules

1. Read affected domain README, lesson code, shared callers, and relevant local
   Microsoft docs before editing.
2. Reuse `_shared` clients/settings. Fix shared root cause rather than every
   caller.
3. Never commit `.env`, API keys, tokens, SAS URLs, connection strings,
   customer media, transcripts, prompts, tool results, or sensitive telemetry.
4. Default new cloud operations to local **Preflight**. Require explicit
   `--apply` or `--run` for remote/persistent/billable action.
5. State resource, identity, RBAC, region, preview, pricing, retention, and
   cleanup requirements next to every cloud lesson.
6. Preserve truth labels in `docs/coverage.md`: **Runnable**, **Preflight**,
   **Opt-in**, **Local**, **Partial**, **Gap**. Never convert a path to live
   success without real evidence.
7. Add focused no-cloud tests for nontrivial parsing, branching, request
   construction, mutation gates, or lifecycle behavior.
8. When adding numbered lessons, update root counts, domain lesson map,
   `.env.example`, `docs/coverage.md`, and relevant README commands.

## Current boundaries

- All remote Azure paths are intentionally treated as unproven unless explicitly
  live-tested. `live-azure-acceptance` is blocked pending a disposable
  subscription, configured resources/RBAC, supported regions, and approval for
  billable calls.
- Current previews are documented in-place and can change by region/tenant/API
  version. Do not silently substitute another service when unavailable.
- Document Intelligence v4 is included in Domain 09. Face liveness is deferred
  until approved resource access exists. Face recognition and legacy Azure AI
  services are out of scope.
- Search/CU content, agent tools, voice/media, traces, evaluation data, and
  Blob SAS URLs are security boundaries. Enforce ACLs before model context and
  minimize/log-govern data.

## Validation

Run from repository root after meaningful changes:

```bash
uv lock --check
uv run python -m unittest discover -s tests -p 'test_*.py'
uv run python -m compileall -q \
  01-plan-and-manage 02-generative-ai-and-agents 03-computer-vision \
  04-text-and-speech 05-information-extraction 06-model-customization-other \
  07-production-platform-other 08-advanced-agents-other \
  09-current-ai-services-other _shared
python -m json.tool 05-information-extraction/skillset_configs/index.json >/dev/null
python -m json.tool 05-information-extraction/skillset_configs/data_source.json >/dev/null
python -m json.tool 05-information-extraction/skillset_configs/skillset.json >/dev/null
python -m json.tool 05-information-extraction/skillset_configs/indexer.json >/dev/null
git diff --check
```

For Domain 07, also run its numbered preflights and Bicep/Terraform validation
documented in `07-production-platform-other/README.md`. Do not run an Azure
apply unless its resource, identity, cost, and cleanup plan are explicit.

### Test selection

| Change | Minimum validation |
|---|---|
| Shared endpoint/client/config change | `tests/test_shared_runtime.py` plus affected domain tests |
| One domain lesson | that domain's `test_domain_*.py` files and compile target |
| Search schema/skillset | four JSON parse commands plus D5 tests |
| Infrastructure asset | numbered D7 preflight, Bicep build/what-if or Terraform init/validate/plan as applicable |
| README/docs only | local links/commands, lesson count, `git diff --check` |
| Cross-domain change | full test discovery and full compile command |

## Future-session checklist

Before ending a coding session, record:

- changed lesson numbers/counts and updated root/coverage/environment files;
- exact current/preview status and external Microsoft docs relied upon;
- tests/preflights executed and their result;
- intentionally untested Azure paths and why;
- cloud state created, its cleanup owner, and deletion status;
- any new blocked dependency, especially live Azure acceptance.

## Documentation standard

Every domain README should explain each lesson progressively:

- what it is, why it exists, how it works, when to use/not use it;
- prerequisites, dependencies, architecture, code path, expected output;
- real-world use, best practices, pitfalls, security/cost/region limits;
- decision trade-offs, troubleshooting, AI-103/interview notes, and official
  source references.

Keep `AGENTS.md` short and operational. Put detailed teaching in domain
READMEs, not here.
