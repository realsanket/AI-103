# AI-103 runnable study repository

Hands-on companion for the April 16, 2026 [AI-103 skills measured](AI-103.md). It has **149 numbered Python lessons** across five exam domains, three supplemental domains, and a production-platform IaC lab. Lessons use Microsoft Foundry, Azure AI services, Azure AI Search, and Azure Storage; many make billable remote calls or change persistent cloud state.

Read [`docs/coverage.md`](docs/coverage.md) for an objective-by-objective, evidence-based map. A lesson existing here does not mean its Azure API, region, model, preview feature, or permission has been exercised in your subscription.

## Repository map

| Domain | Exam weight | Lessons | Start here |
|---|---:|---:|---|
| [01 Plan and manage](01-plan-and-manage/README.md) | 25–30% | 26 | `01_model_catalog_list.py`, `02_deployment_types.py` |
| [02 Generative AI and agents](02-generative-ai-and-agents/README.md) | 30–35% | 30 | `01_first_api_call.py`, `23_mcp_tool_preflight.py`, `29_cloud_evaluation.py` |
| [03 Computer vision](03-computer-vision/README.md) | 10–15% | 15 | `01_multimodal_understanding.py`, `10_reference_media_preflight.py`, `15_cu_visual_handoff.py` |
| [04 Text and speech](04-text-and-speech/README.md) | 10–15% | 25 | `05_language_pii.py`, `20_language_sentiment.py`, `21_speech_mcp_preflight.py`, `25_text_speech_governance_preflight.py` |
| [05 Information extraction](05-information-extraction/README.md) | 10–15% | 21 | `00_search_index_setup.py`, `03_search_hybrid_semantic.py`, `18_search_monitoring.py` |
| [06 Model customization and delivery](06-model-customization-other/README.md) | Supplemental | 14 | `00_customization_preflight.py`, `05_submit_training.py`, `10_quota_ptu_preflight.py` |
| [07 Production platform](07-production-platform-other/README.md) | Cross-domain | 6 | `01_bicep_preflight.py`, then local platform preflights |
| [08 Advanced agents and current Foundry operations](08-advanced-agents-other/README.md) | Supplemental | 6 | `01_foundry_iq_connection_preflight.py`, `03_a2a_agent_card_preflight.py`, `04_routines_preflight.py` |
| [09 Current Azure AI Document Intelligence](09-current-ai-services-other/README.md) | Supplemental | 6 | `01_read_ocr.py`, `02_layout_markdown_tables.py`, `05_custom_neural_preflight.py` |

Shared clients live in [`_shared/`](./_shared/); sample inputs live under `_shared/sample_data/`. `AI-103.md` is local study-guide source, `Slides.md` is extracted study material, and `.context/azure-ai-docs/` is local reference documentation. Domain READMEs are source of truth for individual prerequisites, preview status, input formats, and side effects.

## Resource topology

```text
Microsoft Foundry resource
├── https://<resource>.services.ai.azure.com
│   ├── FOUNDRY_ENDPOINT: control-plane account name for D1 lessons 03 and 05
│   ├── PROJECT_ENDPOINT: /api/projects/<project> for AIProjectClient
│   ├── CU_ENDPOINT: Content Understanding REST
│   └── VOICE_LIVE_ENDPOINT: wss://.../voice-live/realtime
├── https://<resource>.openai.azure.com
│   └── Azure OpenAI-compatible OpenAI client: Responses, images, embeddings,
│       video, LangChain, and LangGraph
└── https://<resource>.cognitiveservices.azure.com
    └── Language, Speech, Content Safety, Document Intelligence, and their MCP URLs

Separate resources
├── Azure AI Search: https://<search>.search.windows.net
│   └── SEARCH_CONNECTION_NAME: existing Foundry project connection for D2 L25
├── Azure Blob Storage: source documents, Search ingestion, CU SAS inputs,
    and batch Speech input
└── Azure Document Intelligence: single-service custom subdomain for D9
    Microsoft Entra-authenticated v4 client calls

Translator is different: shared helper calls
https://api.cognitive.microsofttranslator.com directly with Entra auth and
`TRANSLATOR_RESOURCE_ID` as `Ocp-Apim-ResourceId`.
```

Do not exchange these endpoints:

| Client or workload | Setting | Endpoint shape | Client in this repo |
|---|---|---|---|
| Azure OpenAI data plane | `AZURE_OPENAI_ENDPOINT` | `https://<resource>.openai.azure.com` | `_shared/openai_client.py` |
| Foundry project, prompt agents | `PROJECT_ENDPOINT` | `https://<resource>.services.ai.azure.com/api/projects/<project>` | `_shared/foundry_client.py` |
| Foundry account control plane helper | `FOUNDRY_ENDPOINT` | `https://<resource>.services.ai.azure.com` | D1 lessons 03, 05 |
| Language, Speech, Content Safety | service endpoint settings | `https://<resource>.cognitiveservices.azure.com` | respective shared clients |
| Content Understanding | `CU_ENDPOINT` | `https://<resource>.services.ai.azure.com` | `_shared/cu_client.py` |
| Document Intelligence v4.0 | `DOCUMENT_INTELLIGENCE_ENDPOINT` | single-service `https://<resource>.cognitiveservices.azure.com` | D9 lessons |
| AI Search | `SEARCH_ENDPOINT` | `https://<search>.search.windows.net` | `_shared/search_client.py` |

`FOUNDRY_ENDPOINT` is not interchangeable with `PROJECT_ENDPOINT`; direct OpenAI code does not use either one. Deployment variables are deployment names, not model-family labels.

## Setup

### Install and authenticate

Prerequisites: Python 3.12+, [uv](https://docs.astral.sh/uv/), and [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli).

```bash
uv sync
cp .env.example .env
az login
```

`DefaultAzureCredential` is used throughout. Locally it commonly obtains an Azure CLI token; deployed workloads can use managed identity. Credential-chain selection does not prove which credential succeeded.

### Configure `.env`

Start from [`.env.example`](.env.example). It contains endpoint/name placeholders and no keys. Do not commit `.env`, connection strings, Blob SAS URLs, or production data.

| Group | Variables |
|---|---|
| Foundry and deployments | `FOUNDRY_ENDPOINT`, `AZURE_OPENAI_ENDPOINT`, `PROJECT_ENDPOINT`, `DEFAULT_MODEL`, `REASONING_MODEL`, `IMAGE_MODEL`, `VIDEO_MODEL`, `EMBEDDING_MODEL`, `MODEL_ROUTER_DEPLOYMENT` |
| Language and Translator | `LANGUAGE_ENDPOINT`, `LANGUAGE_MCP_URL`, `TRANSLATOR_RESOURCE_ID` |
| Speech and Voice Live | `SPEECH_REGION`, `SPEECH_ENDPOINT`, `SPEECH_MCP_URL`, `VOICE_LIVE_ENDPOINT`, `CUSTOM_SPEECH_ENDPOINT_ID` |
| Content Understanding | `CU_ENDPOINT`, `CU_API_VERSION` |
| Document Intelligence v4.0 | `DOCUMENT_INTELLIGENCE_ENDPOINT`, `DI_CUSTOM_NEURAL_MODEL_ID`, `DI_CUSTOM_NEURAL_PREFIX` |
| Content Safety | `CONTENT_SAFETY_ENDPOINT` |
| Search | `SEARCH_ENDPOINT`, `SEARCH_INDEX`, `SEARCH_INDEX_VECTOR`, `SEARCH_INDEXER`, `SEARCH_SKILLSET` |
| Storage | `STORAGE_ACCOUNT`, `STORAGE_CONTAINER`, `STORAGE_CONNECTION_STRING` |
| Monitoring and RBAC | `APPLICATIONINSIGHTS_CONNECTION_STRING`, `AZURE_SUBSCRIPTION_ID`, `AZURE_RESOURCE_GROUP` |
| Domain 1 advanced labs and D2 cloud evaluation | `DEPLOYMENT_NAME`, `DEPLOYMENT_MODEL_NAME`, `DEPLOYMENT_MODEL_VERSION`, `PROVENANCE_SOURCE_URL`, `AZURE_AI_PROJECT_ENDPOINT`, `AZURE_AI_AGENT_NAME`, `AZURE_AI_MODEL_DEPLOYMENT_NAME` |
| Domain 2 external-tool preflights and D5 managed Search agent | `NORTHWIND_MCP_ENDPOINT`, `NORTHWIND_MCP_CONNECTION`, `SEARCH_CONNECTION_NAME` |
| Domain 2 OpenAPI sample | `ORDERS_FN_ENDPOINT` |
| Domain 8 advanced Foundry-agent labs | `FOUNDRY_IQ_SEARCH_ENDPOINT`, `FOUNDRY_IQ_KNOWLEDGE_BASE`, `FOUNDRY_IQ_CONNECTION_NAME`, `FOUNDRY_TOOLBOX_NAME`, `FOUNDRY_AGENT_NAME` |

Template defaults currently include `gpt-4.1-mini`, `o4-mini`, `gpt-image-1`, `sora`, `text-embedding-3-large`, `model-router`, `northwind-docs`, and `northwind-docs-vector`. Replace model values with deployment names available to your resource. `settings()` treats placeholder values beginning with `<` as unset.

Lesson-local environment inputs are deliberately not template defaults:

| Lesson area | Additional value |
|---|---|
| CU document lessons | `CU_READ_SOURCE_URL`, `CU_LAYOUT_SOURCE_URL`, `SAMPLE_INVOICE_URL`, `CU_SUPPORT_NOTICE_URL`, `CU_PRO_SOURCE_URLS`, `CU_MARKDOWN_SOURCE_URL` |
| D9 Document Intelligence document lessons | `DI_READ_SOURCE_URL`, `DI_LAYOUT_SOURCE_URL`, `DI_INVOICE_SOURCE_URL`, `DI_ID_SOURCE_URL`, `DI_TRAINING_CONTAINER_URL`: runtime-only HTTPS URLs that can contain a Blob SAS; never commit them. |
| D3 hosted visual media | `SAMPLE_IMAGE_URL`, `SAMPLE_VIDEO_URL`: service-reachable HTTPS URL or short-lived read-only Blob SAS; never `file://` |
| Batch STT | `BATCH_STT_CONTAINER_SAS`: runtime-only container SAS with read and list permission; use shell, Key Vault, or CI secret store, never `.env.example` or source |
| Translator document batch | `TRANSLATOR_DOCUMENT_KEY`: runtime-only secret for D4 L23; use Key Vault/CI secret store, never `.env.example` or source |
| OpenAPI agent | `ORDERS_FN_ENDPOINT`: deployed Function URL; Agent Service cannot call `localhost` |

Set `CU_API_VERSION=2025-11-01` for standard CU lessons. Domain 5 lesson 13 requires its documented preview value, `2025-05-01-preview`. `SPEECH_REGION` is needed by batch Speech REST and LLM Speech preview URLs; normal `SpeechConfig` uses `SPEECH_ENDPOINT`.

### Minimal path versus full path

| Path | Create/configure | Lessons unlocked |
|---|---|---|
| Local orientation | `uv sync`; no Azure resources | D1 lesson 02, D5 lesson 06, and D5 lessons 16–20 preflights execute locally. |
| First live model call | `az login`, `AZURE_OPENAI_ENDPOINT`, `DEFAULT_MODEL` | D2 lesson 01; D3 lesson 01 and D4 L01–L03 use same OpenAI surface. |
| Foundry project work | Add `PROJECT_ENDPOINT` and project access | D1 L01/L07/L16; D2 agents; D4 L09/L18; D5 prompt agent. |
| Foundry tools | Add Language, Speech, Content Safety, and CU endpoints as needed | D1 safety, D3 CU/moderation, D4 Language/Speech. |
| Full retrieval path | Add Search, Storage, embedding deployment, subscription/resource-group values, and managed-identity roles | D5 Search pipeline and manual RAG. |

Do not set `STORAGE_CONNECTION_STRING` merely because it exists in the template: Search pipeline JSON uses managed identity and a storage resource-ID connection, not a stored storage key.

## Authentication and RBAC

Use least privilege at project/resource scope. Domain 1 documents these starting roles; exact assignments depend on your resource configuration.

| Operation | Starting role | Scope |
|---|---|---|
| Project APIs, agents, pre-deployed model use | `Foundry User` | Project or Foundry resource |
| Direct Azure OpenAI inference | `Cognitive Services OpenAI User` | Azure OpenAI resource |
| Deployment changes | suitable control-plane role, such as `Cognitive Services Contributor` | Foundry resource |
| Subscription quota read | `Cognitive Services Usages Reader` or `Reader` | Subscription |
| Application Insights/manual telemetry read | `Log Analytics Reader` | telemetry resource |
| Search ingestion identity reads Blob | `Storage Blob Data Reader` | storage account/container |
| Search ingestion identity calls embeddings | `Cognitive Services OpenAI User` | Azure OpenAI/Foundry resource |

For managed identity, enable or attach identity first and assign roles to its **principal object ID**, not client ID. D1 lesson 08 reads assignments by default; its mutation helper remains commented out.

## Safe run sequence

Run every command from repository root:

```bash
uv run python 01-plan-and-manage/02_deployment_types.py
uv run python 01-plan-and-manage/01_model_catalog_list.py
uv run python 02-generative-ai-and-agents/01_first_api_call.py
```

Then follow each domain README:

1. Domain 1: learn deployment types, quota reads, identity, safety, and
telemetry before creating deployments or persistent blocklists.
2. Domain 2: run Responses lessons 01–07, then agents 08–13. Lessons 23–25
and 29 default to local preflights; use `--apply` only after their connection, data, RBAC, lifecycle, and cost checks. Lessons 26–28 validate local hosted-agent assets; their contained deploy wrapper also requires `--apply`.
3. Domain 3: run L10, L12–L15 without `--apply`/`--run` first, then
local-image understanding/captions before image/video generation or CU URL analysis.
4. Domain 4: work through Language/Translator before Speech. Run
`20_language_sentiment.py` after L07. L21–L25 default to local preflights; use their remote flags only after their domain README checks.
5. Domain 5: provision index, skillset, then indexer (`--run`); wait for its
successful run before vector, hybrid, or manual-RAG queries. Lessons 16–20 default to local preflights; use their documented explicit flags for any remote call.
6. Domain 6: run dataset and delivery preflights first. Every cloud action
requires `--apply`; validate data, baseline, model support, quota/capacity, region, roles, retention, and cost before applying.
7. Domain 7: run offline preflight, select Bicep or Terraform, then run
`what-if`/`plan`. Its explicit `--apply` gate follows networking, CMK, policy, diagnostics, and DR review.
8. Domain 8: run current Foundry-agent preflights before `--apply`. Confirm
feature availability, region, role assignments, gateway state, and cost; these labs use current agent endpoints, never Agent Applications.
9. Domain 9: run every Document Intelligence preflight first. Use
`--apply` only after identity, document-data, Storage, network, region, quota, and cost review. The local DI-versus-CU chooser never calls Azure.

Examples:

```bash
uv run python 04-text-and-speech/20_language_sentiment.py
uv run python 05-information-extraction/00_search_index_setup.py
uv run python 05-information-extraction/05_search_skillset.py
uv run python 05-information-extraction/04_search_indexer_setup.py --run
uv run python 05-information-extraction/18_search_monitoring.py
uv run python 05-information-extraction/20_managed_search_agent_tool.py
uv run python 02-generative-ai-and-agents/23_mcp_tool_preflight.py
uv run python 02-generative-ai-and-agents/26_hosted_agent_responses.py
uv run python 02-generative-ai-and-agents/29_cloud_evaluation.py --dataset cases.jsonl
uv run python 06-model-customization-other/00_customization_preflight.py
uv run python 06-model-customization-other/10_quota_ptu_preflight.py
uv run python 08-advanced-agents-other/01_foundry_iq_connection_preflight.py
uv run python 08-advanced-agents-other/03_a2a_agent_card_preflight.py
uv run python 09-current-ai-services-other/01_read_ocr.py
uv run python 09-current-ai-services-other/06_di_vs_cu_decision.py --scenario standard-form
```

## Cross-domain chooser

| Need | Choose | Do not confuse with |
|---|---|---|
| OpenAI-compatible Responses, image, embedding, or video call | Azure OpenAI endpoint | Foundry project endpoint |
| Agent/project creation or versioning | Foundry `AIProjectClient` | OpenAI Responses client |
| Managed vector retrieval in Foundry | D2 File Search | Azure AI Search indexer/skillset pipeline |
| App-owned retrieved citations | D5 manual RAG | Agent autonomously querying a Search tool; this repo does not configure one |
| Text translation at volume or glossary work | Translator REST | Speech Translation or LLM translation |
| Spoken-language translation | `TranslationRecognizer` | Translator Text REST |
| Standard entities/PII/sentiment | Azure AI Language | flexible LLM prompting |
| Novel entities, tone-preserving translation, multi-task output | Responses model | compliance-grade PII redaction |
| Single file / live audio / many files | Fast STT / real-time STT / batch STT | each other |
| Document structure and fields | Content Understanding | Search enrichment/indexing |
| Standard structured invoice or ID | Document Intelligence v4 prebuilt | Content Understanding analyzer for unstructured, inferred, or multimodal work |
| OCR or layout only | Content Understanding prebuilt analyzer | DI v4 Read/Layout contract lesson; choose by validated workload needs |
| Vector retrieval / hybrid / semantic ranking | Azure AI Search | File Search |
| Content moderation | Content Safety | Prompt Shields, which targets prompt injection |
| Prompt injection with document text | Prompt Shields document flow | content moderation |
| Standard CU / Pro CU | individual extraction / multi-document reasoning preview | Pro mode accepts multiple document URLs |

## Availability, cost, and mutation warnings

| Area | What changes or costs |
|---|---|
| D1 L03 | Creates/updates deployment and allocates billable capacity. |
| D1 L04, L06–L18 | Inference and Content Safety calls; L15 persists blocklist/items only with `--apply`; L18 can export governed token/latency/safety telemetry without prompt/output attributes. |
| D1 L19–L21 | Content Safety checks; L21 polls a Blob-backed provenance job only with `--run`. |
| D1 L22–L25 | Evaluations, monitoring rules, telemetry feedback, and red-team scans only with explicit `--apply`; can persist state and bill. |
| D1 L26 | Local tracing/App Insights preflight only; no Azure call or mutation. |
| D2 L01–L22 | Model/tool calls; agent versions, vector stores/files, memory stores/items, workflow assets, Functions, and telemetry can persist or bill. |
| D2 L23–L25 | Default commands are local preflights. `--apply` for L23/L25 creates, invokes, then deletes a temporary agent version; L24 creates a persistent Toolbox version and deletes one only with explicit version and `--apply`. |
| D2 L26–L28 | Local hosted-agent contract/A2A/CI-CD asset checks. Contained `deploy.py --apply` can provision or deploy hosted-agent resources; no deployment is performed by default. |
| D2 L29–L30 | L29 default is local JSONL/lifecycle preview; `--apply` uploads an eval file, creates evaluation/run records, and invokes model/evaluators. L30 only reads local configuration. |
| D3 | L01–L09 contain remote-call paths; L02–L05 can overwrite generated files after successful responses. L10/L11/L15 are local preflights unless `--apply`; L12/L13 are local preflights unless `--run`; L14 is local only. These opt-in paths are not evidence of a successful live call. Sora 2, provenance, and CU availability remain service/region/version dependent. |
| D4 L01–L20 | Remote-call paths; batch STT uses Blob and Speech processing. L18 creates then deletes an agent version and is protocol-only, not end-to-end voice playback. |
| D4 L21–L25 | L21/L22/L23/L24 default to no-cloud-call preflights; `--run` lists Speech MCP tools (L21), sends reviewed text (L22), or streams Voice Live audio (L24). L23 `--apply` submits, inspects, or cancels a billable Document Translation batch with persistent Blob output. L25 reads local configuration only. These paths are not live-tested here. |
| D5 | L00–L05 and L07–L15 contain documented cloud-call or persistent-resource paths; L06 is local. Indexer runs invoke embeddings. L16–L20 default to local preflights: L16 `--apply` submits CU input; L17 `--apply` mutates Search (`--run` starts indexing); L18/L19 `--run` are read-only; L20 requires `--enable` plus `--apply` and/or `--run`. These paths are not evidence of a successful live operation. |
| D6 | L00–L03 and L13 are local only. L04 creates teacher-generated local candidates only with `--apply`; L05 uploads data and submits a training job only with `--apply`; L06 reads a job only with `--apply`; L07 creates/updates a deployment only with `--apply`; L08, L11, and L12 make billable inference calls only with `--apply`; L09 uploads input and creates a Batch job only with `--apply`; L10 reads management-plane quota/deployments only with `--apply`. These paths are not evidence of a successful live operation. |
| D7 | Offline preflight reads local IaC only. Bicep defaults to Azure `what-if`; Terraform defaults to `plan`. Each engine mutates Azure only with explicit `--apply`. The separate policy deployment can deny unapproved connections after nonproduction review. No live deployment, private connectivity, CMK, CI/CD, failover, or recovery success is claimed. |
| D8 | All six labs default to local preflight. `--apply` can create a Foundry IQ connection or Toolbox, patch an A2A card or stable endpoint, create/dispatch a routine, or start/apply an Agent Optimizer candidate. These operations can persist cloud state or bill; no successful live operation is evidenced. M365/Teams distribution remains an explicit Foundry portal step. |
| D9 | All six labs default to local preflight or a local decision. `--apply` submits one Document Intelligence v4 analysis or starts one custom neural build. These operations can bill or persist a model; no successful live operation is evidenced. |

Preview examples include Foundry Memory, workflows, agent evaluators, Sora 2, Content Understanding, MAI-Transcribe, Language/Speech MCP, Voice Live, and several D1 guardrail features. Their availability changes independently of this repository. Use disposable study resources, short prompts, small sample files, and delete lab-created resources when finished.

## Practical checks

No external link checker is required. Validate local Python/JSON after editing:

```bash
python -m compileall -q 01-plan-and-manage 02-generative-ai-and-agents 03-computer-vision 04-text-and-speech 05-information-extraction 06-model-customization-other 08-advanced-agents-other 09-current-ai-services-other _shared
python -m json.tool 05-information-extraction/skillset_configs/index.json >/dev/null
python -m json.tool 05-information-extraction/skillset_configs/data_source.json >/dev/null
python -m json.tool 05-information-extraction/skillset_configs/skillset.json >/dev/null
python -m json.tool 05-information-extraction/skillset_configs/indexer.json >/dev/null
python 07-production-platform-other/scripts/preflight.py --engine bicep
python 07-production-platform-other/scripts/preflight.py --engine terraform
az bicep build --file 07-production-platform-other/bicep/main.bicep --stdout >/dev/null
terraform -chdir=07-production-platform-other/terraform validate
```

Use `uv run python <lesson>` only after the lesson's domain README confirms its resource, role, endpoint, preview, and data-handling prerequisites.
