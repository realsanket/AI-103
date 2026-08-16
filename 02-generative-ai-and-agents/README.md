--- ai-usage: ai-assisted ---

# Domain 2: Implement generative AI and agentic solutions

> Runnable labs for Azure OpenAI Responses, Foundry prompt and hosted agents, tools, memory, workflow migration, evaluation, observability, and LangChain/LangGraph integration. Run every numbered lesson from repository root: `uv run python 02-generative-ai-and-agents/<lesson>.py`
>
> Code proves one narrow path per lesson. It is not a production deployment, authorization design, data-retention policy, or representative evaluation result.

## What this domain teaches

```text
Direct Responses call
    → Built-in managed tools (web search, code interpreter, file search, structured output)
    → Prompt agents with function tools, OpenAPI, conversation, memory, workflow
    → Local frameworks (Agent Framework, multi-agent routing, LangChain, LangGraph)
    → Evaluation and observability (local evaluators, cloud evaluation, tracing, preflight)
    → Governed external tools (MCP, Toolbox, Azure AI Search)
    → Hosted agent delivery (Responses runtime, A2A boundary, OIDC CI/CD)
```

An LLM call predicts useful next content. An agentic application adds state, tools, policy, and an execution loop. Those layers have separate failure modes and owners. Domain 2 walks you through all seven layers so you can compare them side by side, understand their boundaries, and choose the right runtime for each need.

## Agentic runtime mental model

```text
User or event
    |
    v
Input policy, identity, tenant/user scope, and request validation
    |
    v
Model / agent definition ---- tool selection ---- retrieval or external API
    |                                  |                     |
    |                                  v                     v
    |                         Application authorization   Tool result
    |                                  |                     |
    +------------ conversation / workflow / graph state --+
    |
    v
Output validation, grounding/citation checks, human approval, telemetry
```

A model can *request* a tool. A model cannot safely be *trusted to authorize* a tool. The application validates arguments, checks caller authority, performs the least-privileged action, returns a bounded result, and records the decision.

### Runtime selection

```text
Need one generated response and application owns all state/tools?
  Yes → Direct Responses API (lessons 01–07)
  No  → Need stored Foundry agent definition/version and Foundry tools?
           Yes → Prompt Agent through project endpoint (lessons 08–16)
           No  → Need local Python orchestration / framework portability?
                    Yes → Agent Framework, LangChain, or LangGraph locally (lessons 17–20)
                    No  → Need managed long-running deployed runtime?
                             Yes → Package and deploy a hosted agent (lessons 28–30)
                             No  → Start with direct Responses API
```

---

## Service and endpoint map

| Term | Meaning | Do not confuse it with |
|---|---|---|
| **Foundry resource** | Azure resource holding account-level config, deployments, access, quota. | A project or a callable model. |
| **Foundry project** | Workspace under a Foundry resource for project APIs, agents, connections. | Direct Azure OpenAI endpoint. |
| **Model family** | Capability/version label such as `gpt-4.1-mini`. | A deployment name. |
| **Deployment** | Named configured instance of a model. | A model family label or endpoint. |
| **Direct client** | OpenAI SDK client calling Azure OpenAI-compatible APIs. | `AIProjectClient`. |
| **Project client** | `AIProjectClient` for project and prompt-agent APIs. | Direct OpenAI SDK client. |
| **Hosted agent** | Deployed managed runtime with packaging, identity, ingress, and lifecycle. | Local `AgentFramework` process. |

| Surface | Setting | URL shape | Used for |
|---|---|---|---|
| Direct Azure OpenAI data plane | `AZURE_OPENAI_ENDPOINT` | `https://<resource>.openai.azure.com` | Lessons 01–07, 19–21, 23 |
| Foundry project API | `PROJECT_ENDPOINT` | `https://<resource>.services.ai.azure.com/api/projects/<project>` | Lessons 08–18, 24 |
| Application Insights | `APPLICATIONINSIGHTS_CONNECTION_STRING` | Connection string | Optional lesson 23 export; lesson 24 checks it |

`_shared/openai_client.py` constructs `<AZURE_OPENAI_ENDPOINT>/openai/v1`. `_shared/foundry_client.py` constructs `AIProjectClient` with `PROJECT_ENDPOINT`. Do not replace either URL with the other — both can contain the same resource name but have different SDK routes, API contracts, and RBAC expectations.

---

## Glossary

| Term | Study definition |
|---|---|
| **Responses API** | Unified response-generation API that can emit messages and tool calls. |
| **Prompt agent** | Foundry stored, versioned definition containing model, instructions, and tools. |
| **Agent reference** | Request body reference selecting agent name and optional version. |
| **Conversation** | Server-managed turn history identified by `conversation.id`. |
| **Function tool** | Schema advertised to model; application executes the requested call. |
| **Built-in tool** | Tool executed by service: web search, code interpreter, or file search. |
| **OpenAPI tool** | Service-created callable operations from an OpenAPI contract and reachable backend. |
| **MCP** | Model Context Protocol: protocol for discovering/invoking tools through an MCP server. |
| **Toolbox** | Foundry-managed versioned collection of tools and connections; not generic MCP. |
| **A2A** | Agent-to-agent protocol for communicating with an external agent; not a function call. |
| **RAG** | Retrieval-augmented generation: retrieve evidence, then generate grounded answer. |
| **Vector store** | Indexed chunks plus embeddings for similarity retrieval. |
| **Embedding** | Numeric representation used for semantic comparison, not a chat response. |
| **Memory** | Managed preview long-term memory extraction/retrieval, scoped by identity/context. |
| **Workflow** | Preview visual/YAML orchestration asset; retires December 1, 2026. |
| **Graph state** | Explicit application-controlled state passed between LangGraph nodes. |
| **Trace** | Structured execution record containing spans, timing, attributes, and possibly content. |
| **Evaluation** | Repeatable scoring over defined inputs/outputs/traces; not a single model answer. |
| **Grounding** | Answer claims supported by retrieved/tool evidence. |
| **Human approval** | Explicit authorization checkpoint before consequential side effect. |

---

## Setup

### Environment variables

```dotenv
FOUNDRY_ENDPOINT=https://<resource>.services.ai.azure.com
PROJECT_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<project>
AZURE_OPENAI_ENDPOINT=https://<resource>.openai.azure.com
DEFAULT_MODEL=<chat-deployment-name>
REASONING_MODEL=<reasoning-deployment-name>
EMBEDDING_MODEL=<embedding-deployment-name>
ORDERS_FN_ENDPOINT=https://<reachable-function-app>
APPLICATIONINSIGHTS_CONNECTION_STRING=<optional-connection-string>

# Lessons 25–27: existing project connections and Search index
NORTHWIND_MCP_ENDPOINT=https://<app>.azurewebsites.net/runtime/webhooks/mcp
NORTHWIND_MCP_CONNECTION=<project-connection-id>
SEARCH_CONNECTION_NAME=<foundry-project-connection-name>
SEARCH_ENDPOINT=https://<search-service>.search.windows.net
SEARCH_INDEX=<vector-capable-index-name>

# Lesson 22: durable cloud evaluation target
AZURE_AI_PROJECT_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<project>
AZURE_AI_MODEL_DEPLOYMENT_NAME=<evaluation-target-or-judge-deployment>
```

`ORDERS_FN_ENDPOINT` has no `/api` suffix — lesson 12 appends it. `APPLICATIONINSIGHTS_CONNECTION_STRING` is optional; lesson 23 still runs without it but exports no spans. `AZURE_AI_PROJECT_ENDPOINT` in lesson 22 may differ from `PROJECT_ENDPOINT` when evaluating a separate project; set to the same value only when intentional.

All lessons use `DefaultAzureCredential`. Run `az login` on a workstation; use managed identity in Azure. A successful credential chain proves some credential obtained a token — it does not prove the correct RBAC role at the correct scope for the endpoint being called.

### Safe run order

| Stage | Run | Gate |
|---|---|---|
| Direct baseline | 01, 02, 03 | 03 needs `REASONING_MODEL` deployment |
| Managed tools | 04, 05, 06, 07 | 06 creates files/vector store — confirm cleanup plan |
| Prompt-agent basics | 08 then 09, then 10–13 | 08 must run before 09 can resolve agent by name |
| Durable/preview state | 14, then 15 and 16 | 14 needs embedding model; 16 needs 15 intake agent |
| Local frameworks | 17, 18, 19, 20 | 20 needs embedding model for FAISS index |
| Evaluation and observability | 21, 22, 23, 24 | 22 needs `--apply` for cloud run; 23 needs App Insights string |
| External tool boundaries | 25, 26, 27 | Preflights safe; `--apply` creates/deletes cloud state |
| Hosted deployment | 28, 29, 30 | Local-only; contained deployment uses explicit `--apply` |
| OpenAI advanced + LangChain | 31, 32, 33, 34, 35 | All need `--apply`; 31 also needs `--model <embedding-deployment>` |
| Reasoning + web search | 36, 37 | Both need `--apply`; 36 also needs `--model <o-deployment>` |
| Structured outputs + webhooks | 38, 39 | Both need `--apply`; 39 `--apply` creates a persistent webhook endpoint |

### Costs and side effects

| Lesson | What it writes / costs |
|---|---|
| 01–05, 07 | Model tokens; 05 uses code-interpreter sandbox |
| 06 | Files and vector store (persists until deleted); embedding and retrieval tokens |
| 08, 10–16 | Agent versions (persist); model tokens |
| 09, 11, 18 | Agent invocation + function-tool round trips; model tokens |
| 12 | Agent invocation + OpenAPI backend calls; model tokens |
| 14 (`--apply`) | Memory store (persists; delete manually); scope data cleaned up; embedding + chat tokens; begin_update_memories LRO |
| 17 | Model tokens via PROJECT_ENDPOINT |
| 19–20 | Model + embedding tokens via AZURE_OPENAI_ENDPOINT |
| 21 | Evaluator model tokens (local SDK, no cloud state) |
| 22 (`--apply`) | Uploaded evaluation file (30-day expiry), evaluation run, model/evaluator tokens |
| 23 | Model tokens; App Insights spans if connection string set |
| 24 | Local only; `--check-connection` calls project telemetry API |
| 25 (`--apply`) | Temporary agent version (deleted in `finally`) |
| 26 (`--apply`, `--invoke`) | Toolbox version persists; invocation uses model tokens and can call tools with their own cost/data boundaries |
| 27 (`--apply`) | Temporary agent version (deleted in `finally`) |
| 28–30 | Local/read-only; contained `deploy.py --apply` deploys to Azure |
| 31 (`--apply`) | Embedding tokens |
| 32 (`--apply`) | Model tokens |
| 33 (`--apply`) | Model tokens (2 requests) |
| 34 (`--apply`) | Model tokens (3 requests) |
| 35 (`--apply`) | Model tokens (2 requests) |
| 36 (`--apply`) | Model + reasoning tokens |
| 37 (`--apply`) | Model tokens + Bing search lookup |
| 38 (`--apply`) | Model tokens |
| 39 (`--apply`) | Creates persistent webhook endpoint; secret shown once |

---

## Decision tables

### Tool selection

| Need | Use | Key limit |
|---|---|---|
| Fresh public information | Web search (built-in) | Results are untrusted; cite and verify |
| Calculation / data analysis | Code interpreter (built-in) | Sandbox output is not production compute |
| Small uploaded corpus | File search (built-in) | Upload lifecycle and retrieval quality still matter |
| Existing Python action | Function tool | Model requests; app authorizes and executes |
| Existing HTTP API | OpenAPI tool | Backend must be deployed and reachable; auth must align |
| Reusable protocol tool server | Remote MCP | Auth, allowlist, network policy, and data boundary matter |
| Governed reusable Foundry tools | Toolbox | Versioned catalog; not arbitrary MCP |
| Delegate to another agent | A2A or agent-as-tool | Identity, task boundary, and delegated authority need design |
| Deterministic local routing | Application code / LangGraph edge | Do not treat probabilistic routing as deterministic |

### State selection

```text
Need previous turns only inside one interaction?
  Yes → conversation ID (lesson 13)
  No  → Need durable user preference/fact recall across conversations?
           Yes → preview Foundry Memory with explicit user scope (lesson 14)
           No  → Need deterministic workflow data/state transitions?
                    Yes → application/graph state or database (lesson 20)
                    No  → stateless Responses call (lessons 01–07)
```

### RAG paths

| Path | Lesson | Good for | Hard limit |
|---|---|---|---|
| Managed file search | 06 | Fast learning path, small corpus | Upload/vector-store lifecycle; no ACL |
| Foundry Memory | 14 | Scoped durable preference recall | Preview; async/debounced extraction |
| Local FAISS | 20 | Graph/RAG orchestration learning | Ephemeral; no service RBAC, indexing, or governance |
| Azure AI Search | 27 | Production retrieval path | Requires ingestion, schema, ACL, monitoring, evaluation |

---

## Lesson map

| # | File | Runnable objective | Default side effect |
|---|---|---|---|
| 01 | `01_first_api_call.py` | Direct Responses call via DefaultAzureCredential | Model tokens |
| 02 | `02_model_behavior.py` | Temperature comparison across three values | Model tokens |
| 03 | `03_reasoning.py` | Streaming reasoning model call | Model tokens (higher cost) |
| 04 | `04_web_search_tool.py` | Responses call with built-in web search | Model + search tokens |
| 05 | `05_code_interpreter.py` | Responses call with built-in code interpreter | Model + sandbox tokens |
| 06 | `06_file_search_tool.py` | Upload PDFs, create vector store, query file search | Files + vector store (persists) |
| 07 | `07_structured_output.py` | Structured JSON extraction with `strict=True` schema | Model tokens |
| 08 | `08_prompt_agent_create.py` | Register IT HelpDesk Prompt Agent version | Agent version |
| 09 | `09_prompt_agent_invoke.py` | Invoke agent, execute function tools safely | Model tokens |
| 10 | `10_agent_web_search.py` | Register agent with built-in web search tool | Agent version |
| 11 | `11_agent_function_tools.py` | End-to-end create + invoke + function loop | Agent version + model tokens |
| 12 | `12_agent_openapi_tools.py` | Agent with OpenAPI tool and deployed Function backend | Agent version + model + API tokens |
| 13 | `13_conversation_thread.py` | Multi-turn conversation via `conversation.id` | Agent version + model tokens |
| 14 | `14_foundry_memory.py` | Memory store lifecycle + agent recall + remember/forget + direct API update/search | Memory store persists (preview); scope cleaned up |
| 15 | `15_workflow_intake.py` | Intake agent producing structured triage JSON | Agent version + model tokens |
| 16 | `16_workflow_conditional.py` | Preview YAML conditional workflow definition | Agent versions + preview workflow |
| 17 | `17_agent_framework_local.py` | Local Agent Framework call to Foundry model | Model tokens via PROJECT_ENDPOINT |
| 18 | `18_multi_agent_coord.py` | Router delegating to billing/technical specialists | Agent versions + model tokens |
| 19 | `19_langchain_agent.py` | LangChain agent with local tools and Azure model | Model tokens via AZURE_OPENAI_ENDPOINT |
| 20 | `20_langgraph_agent.py` | LangGraph agent with local FAISS RAG | Model + embedding tokens |
| 21 | `21_evaluator_task_adherence.py` | Local SDK evaluators against one agent turn | Evaluator model tokens |
| 22 | `22_cloud_evaluation.py` | Preflight; `--apply` uploads JSONL + starts cloud eval run | **Read-only** until `--apply` |
| 23 | `23_langchain_tracing.py` | LangChain agent with OpenTelemetry export | Model tokens; optional App Insights spans |
| 24 | `24_production_observability_preflight.py` | Observability config guide and preflight | **Read-only**; `--check-connection` calls telemetry API |
| 25 | `25_mcp_tool_preflight.py` | MCP tool preflight; `--apply --approve` for reviewed read calls | **Read-only** until `--apply` |
| 26 | `26_toolbox_tool_catalog_preflight.py` | Publish a Toolbox version, connect through MCP, and run a local agent | **Read-only** until `--apply` or `--invoke` |
| 27 | `27_agent_azure_ai_search_preflight.py` | AI Search agent preflight; `--apply` tests integration | **Read-only** until `--apply` |
| 28 | `28_hosted_agent_responses.py` | Validate Responses hosted-agent runtime contract | Local only |
| 29 | `29_hosted_agent_a2a.py` | Verify A2A boundary — Responses ≠ A2A | Local only |
| 30 | `30_hosted_agent_cicd.py` | Inspect OIDC CI/CD reference and deployment guard | Local only |
| 31 | [Embeddings](31_openai_embeddings.py) | Call embeddings deployment; print dim + magnitude | `--apply --model` required |
| 32 | [JSON schema mode](32_openai_json_mode.py) | Force structured output via json_schema; parse response | `--apply` requires json_schema-capable model |
| 33 | [Prompt caching](33_openai_prompt_caching.py) | Prove cache hit via two calls; report cached_tokens | `--apply` sends 2 requests |
| 34 | [LangChain memory](34_langchain_memory.py) | Multi-turn conversation with ChatMessageHistory | `--apply` sends 3 requests |
| 35 | [Function calling](35_openai_function_calling.py) | Two-step direct Responses API function call loop | `--apply` sends 2 requests |
| 36 | [Reasoning models](36_openai_reasoning_models.py) | o-series thinking tokens: call o1/o3, report reasoning_tokens count | `--apply --model <o-deployment>` required |
| 37 | [Web search tool](37_openai_web_search.py) | Built-in web_search_preview tool; print grounded answer + citations | `--apply` sends 1 request with Bing lookup |
| 38 | [Structured outputs](38_openai_structured_outputs.py) | Pydantic beta.chat.completions.parse — typed Python object from model | `--apply` sends 1 request |
| 39 | [Webhooks preflight](39_openai_webhooks_preflight.py) | Register webhook endpoint; print payload; `--apply` POSTs to REST API | **Read-only** until `--apply` |

---

## Stage 1 — Direct model calls (lessons 01–03)

These three lessons use only `AZURE_OPENAI_ENDPOINT` and make no Azure agent or project API calls. They validate your direct client, credential chain, and deployment names before introducing any Foundry-specific surface. Run these first to isolate endpoint and credential issues from agent issues.

### 01 — First Responses API call

**Question answered:** Does a direct Azure OpenAI-compatible Responses call work with keyless auth?

**Background.** The Responses API is the unified endpoint for Azure OpenAI completions. Lesson 01 is the minimal smoke test: one `responses.create()` call, no tools, no agent definition, no conversation. DefaultAzureCredential picks up `az login` on a workstation and managed identity in Azure.

```bash
uv run python 02-generative-ai-and-agents/01_first_api_call.py
```

**Code path.**
1. `openai_client()` → builds `OpenAI(base_url=AZURE_OPENAI_ENDPOINT/openai/v1, …)` with bearer token
2. `client.responses.create(model=DEFAULT_MODEL, input=…)` → single completion call
3. Prints `response.output_text`

**What to watch in the output.** Printed answer confirms endpoint, credential, and deployment name work together. 401/403 → check endpoint URL and data-plane RBAC assignment (needs Azure OpenAI User or Contributor on the resource).

**What this proves / does NOT prove.** Proves direct endpoint + credential chain. Does NOT prove project endpoint access, tool use, throughput, or production authorization.

**References:** [Responses API quickstart](https://learn.microsoft.com/azure/foundry/agents/quickstarts/responses-api) · [Authentication and authorization in Foundry](https://learn.microsoft.com/azure/foundry/concepts/authentication-authorization-foundry)

---

### 02 — Model behavior (temperature)

**Question answered:** How does the `temperature` parameter change output across the same prompt?

**Background.** Temperature controls sampling entropy: 0.0 collapses the distribution toward the most likely token; 2.0 spreads it widely. This lesson runs the same prompt at 0.0, 1.0, and 2.0 to make the difference visible. The model is hard-coded to `gpt-4.1` because temperature range support is model-specific.

```bash
uv run python 02-generative-ai-and-agents/02_model_behavior.py
```

**Code path.**
1. For `t` in `(0.0, 1.0, 2.0)`: `client.responses.create(model="gpt-4.1", temperature=t, input=…)`
2. Prints `r.output_text` under each temperature header

**What to watch in the output.** Temperature 0.0 output is nearly identical on repeated runs. Temperature 2.0 output diverges significantly. Compare several runs at each value — do not draw conclusions from one run.

**Exam cues.** Temperature is NOT a safety, truth, grounding, or quality guarantee. Exact support and range are model/API dependent. Check deployment capability before using temperature > 1.0.

**References:** [Responses API quickstart](https://learn.microsoft.com/azure/foundry/agents/quickstarts/responses-api) · [Foundry models overview](https://learn.microsoft.com/azure/foundry/concepts/foundry-models-overview)

---

### 03 — Reasoning model

**Question answered:** How is a reasoning-tier model request configured differently from a standard call?

**Background.** Reasoning-tier models (o3, o4-mini) use a separate parameter surface. The `temperature` parameter is replaced by `reasoning={"effort": "high", "summary": "detailed"}`. These deployments think silently and emit a structured summary before the final answer. They cost more and have higher latency — benchmark against representative problems before choosing effort level.

```bash
uv run python 02-generative-ai-and-agents/03_reasoning.py
```

**Code path.**
1. `client.responses.create(model=REASONING_MODEL, reasoning={"effort": "high", "summary": "detailed"}, stream=True)`
2. Iterates stream events: `response.reasoning_summary_text.delta` → prints reasoning summary; `response.output_text.delta` → prints answer

**What to watch in the output.** Two event types arrive in sequence: the thinking summary first, then the final answer. Run with a standard model for comparison to see the latency and cost difference.

**Exam cues.** `reasoning={"effort": …}` not `temperature`. `REASONING_MODEL` must be a compatible deployment name — not a model family label. High effort ≠ correct.

**References:** [Responses API quickstart](https://learn.microsoft.com/azure/foundry/agents/quickstarts/responses-api) · [Foundry models overview](https://learn.microsoft.com/azure/foundry/concepts/foundry-models-overview)

---

## Stage 2 — Built-in managed tools (lessons 04–07)

Built-in tools run service-side: the model emits a tool call, the Azure service executes it, and the result arrives in the same response. No application executor needed. These lessons use `AZURE_OPENAI_ENDPOINT` directly (same as Stage 1) with no agent definition.

### 04 — Web search tool

**Question answered:** How can a model obtain current public information without application code?

**Background.** The built-in `web_search` tool is executed by the Azure OpenAI service, not your application. The model decides when to invoke it unless `tool_choice="required"` is set. Search results are untrusted public-web text — verify citations and obey source data-use requirements.

```bash
uv run python 02-generative-ai-and-agents/04_web_search_tool.py
```

**Code path.**
1. `client.responses.create(tools=[{"type": "web_search"}], tool_choice="required", stream=True)`
2. Streams response; model emits web search event then final text with citations

**What to watch in the output.** Citation lines confirm the model fetched and attributed external sources. `tool_choice="required"` forces search for teaching purposes — remove it in production to let the model decide.

**What this proves / does NOT prove.** Proves service-side tool invocation. Does NOT prove citation accuracy, completeness, or fitness for sensitive decisions.

**References:** [Web search tool how-to](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/web-search) · [Tool best practices](https://learn.microsoft.com/azure/foundry/agents/concepts/tool-best-practice)

---

### 05 — Code interpreter

**Question answered:** When should the model calculate rather than narrate a calculation?

**Background.** The built-in `code_interpreter` tool runs Python inside an isolated sandbox managed by Azure OpenAI. It handles precise numeric computation, data analysis, and chart generation. The sandbox is managed service infrastructure, not production compute — treat generated code and outputs as untrusted results.

```bash
uv run python 02-generative-ai-and-agents/05_code_interpreter.py
```

**Code path.**
1. `client.responses.create(tools=[{"type": "code_interpreter", …}])`
2. Response contains `code_interpreter_call` items with the Python code generated
3. Lesson prints the generated code and execution output before the final answer

**What to watch in the output.** The generated Python code appears before the answer. Independently verify the formula and input assumptions — sandbox execution does not make assumptions correct.

**Exam cues.** Code interpreter runs in a managed sandbox, not your machine. It cannot access your local filesystem or network. Never treat it as unrestricted production compute.

**References:** [Code interpreter how-to](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/code-interpreter) · [Tool best practices](https://learn.microsoft.com/azure/foundry/agents/concepts/tool-best-practice)

---

### 06 — File search (managed RAG)

**Question answered:** What is the smallest managed RAG path without Azure AI Search?

**Background.** File search uploads documents, creates a managed vector store, handles chunking and embeddings, and retrieves relevant chunks at query time — all service-side. No Azure AI Search or external index required. This is useful for small corpora and rapid learning, but creates persistent cloud files and a vector store that incur charges and require cleanup.

```bash
uv run python 02-generative-ai-and-agents/06_file_search_tool.py
```

**Code path.**
1. Validates local PDFs from `_shared/sample_data/northwind_policies/`
2. Uploads each PDF to Azure OpenAI Files API with `purpose="assistants"`
3. Creates named vector store and attaches uploaded file IDs
4. `client.responses.create(tools=[{"type": "file_search", "vector_store_ids": [vs.id]}])`
5. Prints grounded answer with retrieved chunk evidence

**What to watch in the output.** Answer cites policy content from uploaded PDFs. Record the vector store ID for cleanup — normal lesson completion deletes it, but interrupted runs leave persistent state.

**What this proves / does NOT prove.** Proves managed file ingestion + retrieval pipeline. Does NOT prove retrieval quality, ACL, citation accuracy, or production-grade document governance.

**References:** [File search tool how-to](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/file-search) · [Vector stores concept](https://learn.microsoft.com/azure/foundry/agents/concepts/vector-stores) · [Tool best practices](https://learn.microsoft.com/azure/foundry/agents/concepts/tool-best-practice)

---

### 07 — Structured output

**Question answered:** How can model extraction have a machine-valid schema contract?

**Background.** Passing "respond in JSON" to a model is advisory — the model may deviate. `text.format` with `type: "json_schema"` and `strict: true` constrains the token sampler so the response is mechanically guaranteed to match the schema. This is what makes generative extraction production-grade instead of best-effort.

```bash
uv run python 02-generative-ai-and-agents/07_structured_output.py
```

**Code path.**
1. Defines JSON Schema with `additionalProperties: false` and all fields in `required`
2. `client.responses.create(text={"format": {"type": "json_schema", "strict": True, "schema": _SCHEMA}})`
3. Parses `response.output_text` with `json.loads()` — guaranteed to succeed with strict schema

**What to watch in the output.** Parsed Python dict with `entities` and `topics` arrays. Try removing `strict: true` and rerunning — outputs may sometimes violate the schema.

**Exam cues.** Schema conformance does NOT prove extraction accuracy or business validity. Validate content, missing facts, and downstream constraints separately.

**References:** [Responses API quickstart](https://learn.microsoft.com/azure/foundry/agents/quickstarts/responses-api) · [Structured outputs](https://learn.microsoft.com/azure/foundry/openai/how-to/structured-outputs) · [Tool best practices](https://learn.microsoft.com/azure/foundry/agents/concepts/tool-best-practice)

---

## Stage 3 — Prompt agents and state (lessons 08–16)

Prompt agents are stored, versioned definitions in Foundry: model + instructions + tools. Unlike direct Responses calls, they live in the project and can be invoked by name. This stage uses `PROJECT_ENDPOINT` through `AIProjectClient`.

### 08 — Prompt-agent creation

**Question answered:** What does a versioned Foundry Prompt Agent definition contain?

**Background.** A Prompt Agent stores a model, instructions, and tool schemas as a named versioned entity in Foundry. Each `create_version()` call increments the version. Registering a `FunctionTool` schema advertises the tool to the model — it does NOT run any local Python function until invoked by the application in lesson 09.

```bash
uv run python 02-generative-ai-and-agents/08_prompt_agent_create.py
```

**Code path.**
1. `project_client()` → `AIProjectClient` via PROJECT_ENDPOINT
2. Defines three `FunctionTool` schemas: `get_password_reset_steps`, `get_vpn_troubleshooting_steps`, `get_software_install_guide`
3. `client.agents.create_version(agent_name=AGENT_NAME, definition=PromptAgentDefinition(…))`
4. Prints agent id, name, version — save for lesson 09

**What to watch in the output.** Version number increments on each re-run. Changing instructions or tool schemas and re-running creates a new version, not in-place mutation.

**Exam cues.** `strict=True` on `FunctionTool` constrains argument schema, not execution authorization. Each version persists and incurs potential costs — clean up stale lab versions.

**References:** [Prompt agent quickstart](https://learn.microsoft.com/azure/foundry/agents/quickstarts/prompt-agent) · [Function calling how-to](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/function-calling) · [Development lifecycle](https://learn.microsoft.com/azure/foundry/agents/concepts/development-lifecycle)

---

### 09 — Prompt-agent invocation and safe tool loop

**Question answered:** How does the application execute the tools a Prompt Agent requests?

**Background.** Lesson 08 registered the agent definition. This lesson invokes it. The model emits `function_call` items; this application is the executor. It validates each tool name against an allowlist, parses JSON arguments, rejects unexpected keys or missing required fields, executes the local helpdesk function, and returns `function_call_output` items with the original `call_id`. The loop caps at `MAX_TOOL_ROUNDS = 8`.

```bash
uv run python 02-generative-ai-and-agents/09_prompt_agent_invoke.py
```

**Code path.**
1. `project.agents.get(AGENT_NAME)` → resolves latest version; `ResourceNotFoundError` if lesson 08 not run
2. `openai.conversations.create()` → server-managed conversation id
3. `openai.responses.create(conversation=conv.id, input=user_message, extra_body={"agent_reference": ref})`
4. For each `function_call` item: validate name + args → execute → collect `function_call_output`
5. Send tool outputs back in same conversation; repeat until no more tool calls

**What to watch in the output.** "→ tool: get_vpn_troubleshooting_steps({})" lines show which tool was called with what arguments. The final answer uses the tool's returned text as grounding. A mismatched `call_id` causes the model to error.

**Exam cues.** Run lesson 08 first — lesson 09 will `SystemExit` if the agent does not exist. Tool allowlisting happens in application code, not in the model schema.

**References:** [Function calling how-to](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/function-calling) · [Tool best practices](https://learn.microsoft.com/azure/foundry/agents/concepts/tool-best-practice) · [Tool catalog](https://learn.microsoft.com/azure/foundry/agents/concepts/tool-catalog)

---

### 10 — Agent with built-in web search

**Question answered:** How is a built-in tool persisted in an agent definition and then exercised from a simple test call?

**Background.** Lesson 04 attached web search ad-hoc per Responses call. This lesson stores it in a named Prompt Agent definition via `WebSearchTool()`. The stored definition is callable by name from any client without re-specifying the tool on each request. This lesson both creates the definition and proves it works by sending one simple prompt through the agent reference.

```bash
uv run python 02-generative-ai-and-agents/10_agent_web_search.py
```

**Code path.**
1. `client.agents.create_version(agent_name=AGENT_NAME, definition=PromptAgentDefinition(model=..., instructions=..., tools=[WebSearchTool()]))`
2. Builds an agent reference for the newly created version.
3. Calls `openai.responses.create(..., extra_body={"agent_reference": reference})` with a simple question.
4. Prints the agent id, name, version, and the returned response text.

**What to watch in the output.** The agent id/name/version confirms the definition is stored, and the response text shows that the stored agent can be invoked successfully. This is a lightweight smoke test, not a multi-step tool loop.

**Exam cues.** Creating a new agent version costs accumulating version state. Web search queries leave your application's data boundary — confirm DPA, retention, residency, and cost before use.

**References:** [Web search tool how-to](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/web-search) · [Prompt agent quickstart](https://learn.microsoft.com/azure/foundry/agents/quickstarts/prompt-agent)

---

### 11 — End-to-end function-tool agent

**Question answered:** What does the entire model → tool → model cycle look like in a single file?

**Background.** Lessons 08 and 09 split creation and invocation. This lesson runs the complete cycle in one file so you can see the full agentic loop end-to-end: create definition → pin version reference → open conversation → model picks tool → app validates and executes → model gets result → final answer.

```bash
uv run python 02-generative-ai-and-agents/11_agent_function_tools.py
```

**Code path.**
1. `create_version(IT-HelpDesk-Agent-Demo)` → pins `active_agent_reference(agent)` so version is immutable for this run
2. `openai.conversations.create()` → conversation id
3. First `responses.create()` → model emits tool calls
4. Validates tool names, args; executes local functions; submits outputs with `call_id`
5. Second `responses.create()` → final grounded answer

**What to watch in the output.** Tool call lines show the agentic request/execute/respond cycle. Compare against lesson 09 to see the create+invoke unified pattern.

**Exam cues.** `active_agent_reference()` pins the version so a re-run mid-way does not silently switch to a newer version. No idempotency key, per-user authorization, or audit sink is implemented — these are production requirements not shown here.

**References:** [Function calling how-to](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/function-calling) · [Tool best practices](https://learn.microsoft.com/azure/foundry/agents/concepts/tool-best-practice)

---

### 12 — OpenAPI tool and Function backend

**Question answered:** How does Foundry turn a reachable OpenAPI spec into agent tools?

**Background.** The Foundry Agent Service reads an OpenAPI 3.0 spec and auto-wraps each operation as a callable tool — no glue code. The operation's `description` field is what the model reads to decide when to call which endpoint. The backend must be deployed and reachable from Agent Service; `localhost` is not reachable. This sample uses anonymous auth for static demo orders only.

**Before code.** Deploy the Function App and set `ORDERS_FN_ENDPOINT` (without `/api` suffix):
```bash
cd 02-generative-ai-and-agents/azure_functions_orders
func start   # local contract test only — Agent Service cannot reach localhost
curl http://localhost:7071/api/orders
func azure functionapp publish <your-function-app-name>
```

```bash
uv run python 02-generative-ai-and-agents/12_agent_openapi_tools.py
```

**Code path.**
1. Loads `azure_functions_orders/northwind_spec.json`; overrides `servers[0].url` with `ORDERS_FN_ENDPOINT/api`
2. `OpenApiFunctionDefinition(spec=spec, auth=OpenApiAnonymousAuthDetails())` → wraps spec operations
3. `client.agents.create_version(…tools=[OpenApiTool(openapi=fn_def)])` → registers agent
4. Invokes agent with order query → model calls spec operation → prints result

**What to watch in the output.** Model calls the deployed Function's order endpoint and returns grounded order data. If Agent Service cannot reach the backend, the tool call fails with a network error.

**Exam cues.** `func start` only validates the local Function contract. Production path: protect API with API key or Entra auth, select matching OpenAPI auth details, verify Agent Service egress/DNS.

**References:** [OpenAPI tools how-to](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/openapi) · [Tool authentication](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/tool-authentication)

---

### 13 — Conversation thread

**Question answered:** How is multi-turn context retained without resending messages?

**Background.** In a stateless Responses call, the application must resend prior messages on each turn. With `conversations.create()`, Foundry manages the transcript server-side: subsequent `responses.create(conversation=conv.id, …)` calls automatically have access to previous turns. The second message can reference "it" and the model resolves it from server-managed context.

```bash
uv run python 02-generative-ai-and-agents/13_conversation_thread.py
```

**Code path.**
1. `create_version(northwind-support-agent-conv)` → inline agent creation (self-contained, no prior setup needed)
2. `openai.conversations.create()` → new `conv.id`
3. First `responses.create(conversation=conv.id, input="My order #4521 is late.")` → model responds
4. Second `responses.create(conversation=conv.id, input="Can you escalate it?")` → model resolves "it" from transcript

**What to watch in the output.** Second response correctly refers to order #4521 without you resending it. Change to a new conversation id to verify blank-slate behavior.

**Exam cues.** Conversation context is NOT durable profile memory. It is scoped to one conversation. Scope, retention, user isolation, and deletion policy require explicit design.

**References:** [Responses API quickstart](https://learn.microsoft.com/azure/foundry/agents/quickstarts/responses-api) · [Isolate sessions per user](https://learn.microsoft.com/azure/foundry/agents/how-to/isolate-sessions-per-user)

---

### 14 — Foundry Memory (preview)

**Question answered:** How do memory stores persist preferences across sessions, and how do direct memory APIs differ from agent-mediated recall?

**Background.** Foundry Memory is a preview managed service that extracts user preferences and conversation facts from agent interactions and retrieves them in later conversations. Three surfaces exist: (1) `MemorySearchPreviewTool` on an agent — the model calls it automatically per turn; (2) remember/forget commands — `responses.create` with the memory tool where the model returns `memory_command_call` items for explicit user instructions; (3) direct `begin_update_memories` and `search_memories` APIs — synchronous fact injection and retrieval without an agent involved. Writes via the agent tool are **debounced** — a preference stated in one turn may not be recalled immediately. Direct `update_delay=0` bypasses debouncing. This is NOT a database, consent platform, or PII vault.

```bash
# Preflight — check env vars + print API structure
uv run python 02-generative-ai-and-agents/14_foundry_memory.py

# Full flow — all 4 parts + cleanup
uv run python 02-generative-ai-and-agents/14_foundry_memory.py --apply

# Skip 65-second debounce wait (recall may miss the preference)
uv run python 02-generative-ai-and-agents/14_foundry_memory.py --apply --skip-wait
```

**Code path.**

*Part 1 — store lifecycle:*
1. `project.beta.memory_stores.list()` — reuse if name matches; else create.
2. `MemoryStoreDefaultOptions(chat_summary_enabled=True, user_profile_enabled=True, procedural_memory_enabled=True, default_ttl_seconds=timedelta(days=30), user_profile_details=...)`.
3. `project.beta.memory_stores.create(name, definition=MemoryStoreDefaultDefinition(chat_model, embedding_model, options=...), description=...)`.

*Part 2 — agent conversation recall:*
4. `MemorySearchPreviewTool(memory_store_name=..., scope="{{$userId}}", update_delay=1)` — scope resolved from `x-memory-user-id` header per request.
5. `project.agents.create_version(agent_name, definition=PromptAgentDefinition(..., tools=[tool]))`.
6. Conv 1: `openai.conversations.create()` → `responses.create(input=..., conversation=conv.id, extra_headers={"x-memory-user-id": user_id})` — states preference.
7. Sleep 65s (debounce). Conv 2: new conversation, same header → model may recall preference.

*Part 3 — remember/forget commands:*
8. `responses.create(model=..., tools=[{"type": "memory_search_preview", "memory_store_name": ..., "scope": user_id}], input="Remember that...")`.
9. Iterate `response.output` → items with `type == "memory_command_call"` show `arguments` (action + content) and `status`.

*Part 4 — direct API:*
10. `project.beta.memory_stores.begin_update_memories(name, scope, items=[msg_dict], update_delay=0).result()` → `.memory_operations` list.
11. Chain: second call with `previous_update_id=update_poller.update_id`.
12. `project.beta.memory_stores.search_memories(name, scope, items=[query_dict], options=MemorySearchOptions(max_memories=5))` → `.memories` list.

*Cleanup:*
13. `project.beta.memory_stores.delete_scope(name, scope)` — removes test user's data; store persists.
14. `project.agents.delete_version(agent_name, agent_version)` — removes ephemeral agent.

**What to watch in the output.**
- Conv 2 answer: model may or may not echo the stored preference — async extraction is non-deterministic. Never invent a fact not retrieved from memory.
- `memory_command_call` items in Part 3 output: `action=remember` or `action=forget`, `status=completed`.
- `memory_operations` in Part 4: each shows `kind` (e.g. `upsert`) + `memory_id` + `content` extracted by the service.
- `memories` in search: ranked by semantic similarity to the query; `memory_id` + `content` of each stored fact.

**Exam cues.**
- `project.beta` surface = preview; shape can change between SDK versions.
- `scope="{{$userId}}"` in tool → resolved per-request from `x-memory-user-id` header. Static scope string for direct API calls — must match exactly.
- `update_delay=1` means 1 second of inactivity before extraction. Default is 300 (5 min). Use 0 only in `begin_update_memories` for immediate injection.
- `memory_command_call` appears in `response.output`, not `output_text` — parse the output list.
- `begin_update_memories` is a long-running operation (LRO) — call `.result()` or fire-and-forget.
- TTL `default_ttl_seconds` is set at store creation only (in current preview). Recreate store to change TTL.
- `procedural_memory_enabled` enables step-by-step instruction storage (e.g. "always greet user by name").
- Deleting scope removes one user's data; deleting store removes all data across all scopes (irreversible).

**References:** [Memory concept](https://learn.microsoft.com/azure/foundry/agents/concepts/what-is-memory) · [Memory usage how-to](https://learn.microsoft.com/azure/foundry/agents/how-to/memory-usage) · [Memory quickstart](https://learn.microsoft.com/azure/foundry/agents/quickstarts/quickstart-memory-hosted-agent)

---

### 15 — Workflow intake prerequisite

**Question answered:** How does an intake agent emit structured data required for a conditional route?

**Background.** Foundry workflows (retiring December 1, 2026) require structured routing data. Lesson 15 creates a `wf-IntakeAgent` that classifies customer messages into a strict JSON schema (`wf_intake_schema.json`). This agent is the prerequisite for lesson 16 — the workflow YAML references it by name. Run lesson 15 before lesson 16.

```bash
uv run python 02-generative-ai-and-agents/15_workflow_intake.py
```

**Code path.**
1. Loads `workflows/wf_intake_schema.json` — the routing schema
2. Creates `wf-IntakeAgent` with `PromptAgentDefinition` and `strict json_schema` response format
3. `openai.responses.create(input=_SAMPLE_TICKET, text={"format": {"type": "json_schema", …}})` → classifies ticket
4. Prints structured triage JSON with `category`, `refund_related`, and `priority` fields

**What to watch in the output.** The printed JSON must match the schema for lesson 16's workflow to route correctly. Try ambiguous tickets to see classification behavior.

**Exam cues.** Classification can be wrong even with valid JSON. This is preview preparation, not workflow deployment. Workflow retires December 1, 2026.

**References:** [Workflow concept](https://learn.microsoft.com/azure/foundry/agents/concepts/workflow) · [Prompt agent quickstart](https://learn.microsoft.com/azure/foundry/agents/quickstarts/prompt-agent)

---

### 16 — Conditional workflow (preview)

**Question answered:** What does a preview YAML conditional workflow definition look like?

**Background.** Foundry preview workflows route between agents using YAML conditional edges. This lesson creates the leaf agents (Knowledge + Ticket), verifies the intake agent from lesson 15 exists, then creates/updates the `wf-Triage` preview workflow version. Workflows retire December 1, 2026 — use this as a study artifact and plan migration to Agent Framework/hosted agent.

**Before code.** Run lesson 15 first — `wf-IntakeAgent` must exist:
```bash
uv run python 02-generative-ai-and-agents/15_workflow_intake.py
uv run python 02-generative-ai-and-agents/16_workflow_conditional.py
```

**Code path.**
1. Creates `wf-KnowledgeAgent` and `wf-TicketAgent` as leaf agents inline
2. Verifies `wf-IntakeAgent` exists (exits with clear error if lesson 15 not run)
3. Loads `workflows/wf_triage.yml` — defines `OnConversationStart → InvokeAzureAgent(wf-IntakeAgent) → ConditionGroup → leaf agents`
4. `client.agents.create_version(workflow_name=WORKFLOW_NAME, definition=…)` → registers preview workflow version

**What to watch in the output.** Workflow version created. Test in Foundry portal → Agents playground → wf-Triage while preview remains active.

**Exam cues.** This is NOT a hosted-agent deployment, CI/CD workflow, or durable job run. Study the YAML routing logic, then plan the Agent Framework equivalent path for production.

**References:** [Workflow concept](https://learn.microsoft.com/azure/foundry/agents/concepts/workflow) · [Development lifecycle](https://learn.microsoft.com/azure/foundry/agents/concepts/development-lifecycle)

---

## Stage 4 — Local frameworks and orchestration (lessons 17–20)

All four lessons run locally on your machine. None deploy, package, or host anything in Azure. They show four local framework/orchestration patterns side by side so you can compare before choosing.

| Lesson | Framework | Endpoint | Auto-traces? |
|---|---|---|---|
| 17 | Microsoft Agent Framework | `PROJECT_ENDPOINT` | Yes — when App Insights connected |
| 18 | Multi-agent router (app pattern) | `PROJECT_ENDPOINT` | No |
| 19 | LangChain + `@tool` | `AZURE_OPENAI_ENDPOINT` | No — needs lesson 23 tracer |
| 20 | LangGraph + FAISS RAG | `AZURE_OPENAI_ENDPOINT` | No — needs lesson 23 tracer |

### 17 — Local Agent Framework

**Question answered:** What does the Microsoft Agent Framework look like calling a Foundry model locally?

**Background.** Microsoft Agent Framework is a Python library for building agents that call Foundry models. This lesson runs entirely on your machine — it is not deployed, packaged, or hosted anywhere. The framework handles the async run loop; your application supplies instructions. Contrast with lesson 08 (prompt agent: stored versioned Foundry definition) and lessons 28–30 (hosted agent: deployed managed runtime with lifecycle). Agent Framework natively integrates with Foundry tracing: when Application Insights is connected to the project, traces appear in the Foundry portal automatically with no additional instrumentation.

```bash
uv run python 02-generative-ai-and-agents/17_agent_framework_local.py
```

**Code path.**
1. `FoundryChatClient(project_endpoint=PROJECT_ENDPOINT, model=DEFAULT_MODEL, credential=DefaultAzureCredential())`
2. `Agent(client=chat_client, instructions=…)`
3. `await agent.run("Give me a one-line summary of Northwind's mission.")` → prints `result.text`

**What to watch in the output.** One-line response from the Foundry model via the Agent Framework local process. If App Insights is connected, a trace appears in the portal without any extra code.

**Exam cues.** Local Agent Framework code does NOT deploy anything. It is not a hosted agent. For a deployed runtime, see lessons 28–30. LangChain and LangGraph (lessons 19–20) do NOT have this automatic tracing integration — they need explicit instrumentation (lesson 23).

**References:** [Framework hosted agents](https://learn.microsoft.com/azure/foundry/how-to/develop/framework-hosted-agents) · [Agent tracing setup](https://learn.microsoft.com/azure/foundry/observability/how-to/trace-agent-setup) · [Development lifecycle](https://learn.microsoft.com/azure/foundry/agents/concepts/development-lifecycle)

---

### 18 — Multi-agent coordination

**Question answered:** How can a router delegate to specialists through a tool loop?

**Background.** This lesson implements the "agent-as-tool" application pattern: each specialist is exposed as a `FunctionTool` that wraps a Responses API call to the target agent's name. The router model decides which specialist to invoke per turn — no hardcoded routing. This is an application-controlled pattern, NOT Foundry A2A protocol.

```bash
uv run python 02-generative-ai-and-agents/18_multi_agent_coord.py
```

**Code path.**
1. Creates two specialists: `northwind-billing-specialist` and `northwind-tech-specialist`
2. Router is given two `FunctionTool` schemas: `ask_billing_specialist` and `ask_tech_specialist`
3. Router `responses.create()` → model emits a function call for one specialist
4. Executor invokes target agent via `responses.create(extra_body={"agent_reference": ref})` and returns result
5. Loop caps at `MAX_TOOL_ROUNDS = 8`

**What to watch in the output.** The router routes to billing or technical based on question content. Try a mixed question (billing + technical) to see which specialist the model picks.

**Exam cues.** Probabilistic routing means the model can pick the wrong specialist. No escalation, authorization propagation, budgeting, or specialist trust policy is implemented. This is NOT A2A.

**References:** [Agent-to-agent tools](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/agent-to-agent) · [Agent-to-agent authentication](https://learn.microsoft.com/azure/foundry/agents/concepts/agent-to-agent-authentication) · [Tool best practices](https://learn.microsoft.com/azure/foundry/agents/concepts/tool-best-practice)

---

### 19 — LangChain agent

**Question answered:** How does LangChain reuse local tools with an Azure OpenAI-compatible model?

**Background.** LangChain's `create_agent()` wires `@tool`-decorated Python functions to a `ChatOpenAI` model. Auth is keyless: `ChatOpenAI` points at the Azure OpenAI-compatible `/openai/v1` endpoint with a bearer token from `DefaultAzureCredential` via a callable token provider. Use this pattern when you already have LangChain chains or tools. LangChain does NOT trace automatically — see lesson 23 for explicit tracing.

```bash
uv run python 02-generative-ai-and-agents/19_langchain_agent.py
```

**Code path.**
1. `azure_openai_token_provider()` → callable returning bearer token (refreshes per call)
2. `ChatOpenAI(base_url=AZURE_OPENAI_ENDPOINT/openai/v1, api_key=token_provider, model=DEFAULT_MODEL)`
3. `create_agent(model=model, tools=[get_order_status, get_inventory])` → agent executor
4. Agent answers both order and inventory sub-questions via the two tools

**What to watch in the output.** Final answer addresses both order and inventory after the model has invoked both tools. Do not point `ChatOpenAI` at `PROJECT_ENDPOINT` — it uses direct Azure OpenAI endpoint.

**Exam cues.** `token_provider()` returns a token when the model object is built — production must account for credential refresh and retries. LangChain does NOT use `PROJECT_ENDPOINT`.

**References:** [LangChain agents how-to](https://learn.microsoft.com/azure/foundry/how-to/develop/langchain-agents) · [LangChain integration](https://learn.microsoft.com/azure/foundry/how-to/develop/langchain)

---

### 20 — LangGraph local RAG agent

**Question answered:** How do explicit graph state and a tool loop create a local RAG agent?

**Background.** LangGraph adds explicit graph state and conditional edges to a LangChain agent. This lesson builds a local FAISS index over Northwind policy PDFs and binds a `search_northwind_policies` tool to a graph that loops model → tool → model while the model requests tool calls. This is about graph orchestration, NOT production RAG — FAISS is local, in-memory, rebuilt on every run, with no ACL, persistence, or evaluation. Use Azure AI Search (lesson 27 / Domain 5) for production retrieval.

```bash
uv run python 02-generative-ai-and-agents/20_langgraph_agent.py
```

**Code path.**
1. Loads Northwind PDFs via `PyPDFLoader`, splits into chunks, builds `FAISS.from_documents(chunks, embeddings)`
2. `StateGraph(MessagesState)` with two nodes: model node + `ToolNode([search_northwind_policies])`
3. Conditional edge: model has tool calls → go to tool node; no tool calls → END
4. `graph.invoke({"messages": [HumanMessage(query)]})` → loop runs until model stops requesting tools

**What to watch in the output.** "Loaded N pages across Northwind policies" and "Split into N chunks" confirm FAISS index was built. Final answer cites policy content. Index rebuilds on every run.

**Exam cues.** Both `ChatOpenAI` and `OpenAIEmbeddings` use `AZURE_OPENAI_ENDPOINT/openai/v1` — not `PROJECT_ENDPOINT`. LangGraph does NOT auto-trace — needs lesson 23 instrumentation.

**References:** [LangChain agents how-to](https://learn.microsoft.com/azure/foundry/how-to/develop/langchain-agents) · [Retrieval-augmented generation concept](https://learn.microsoft.com/azure/foundry/concepts/retrieval-augmented-generation) · [RAG evaluators](https://learn.microsoft.com/azure/foundry/concepts/evaluation-evaluators/rag-evaluators)

---

## Stage 5 — Evaluation and observability (lessons 21–24)

Understand what to measure (21–22) before you instrument it (23–24). Evaluation tells you whether your agent is correct. Observability tells you where it went wrong. These are distinct concerns.

| Dimension | Lesson 21 — local evaluator | Lesson 22 — cloud evaluation |
|---|---|---|
| Where it runs | In your Python process | Foundry cloud (managed) |
| Cloud state created | None | Uploaded dataset, evaluation definition, run record |
| Meaningful at one case | No | Only with a representative dataset |
| When to use | Iterative dev, evaluator input contract check | Pre-release gating, CI/CD, shared datasets |
| Env var | `AZURE_OPENAI_ENDPOINT` | `AZURE_AI_PROJECT_ENDPOINT` |
| Trigger | Always runs | Read-only until `--apply` |

### 21 — Local evaluator SDK

**Question answered:** What is a local evaluator call and what does a complete agent-turn input look like?

**Background.** The `azure-ai-evaluation` SDK evaluates agent output against rubrics using a model-as-judge pattern. This is a local invocation — no dataset, evaluation definition, or run record is created in Foundry. The evaluator is still an LLM call: it sends the conversation to your Azure OpenAI deployment and consumes tokens. Task Adherence evaluates the whole agent turn, not just the final text. One synthetic trace demonstrates the input contract only — it is NOT representative evidence.

```bash
uv run python 02-generative-ai-and-agents/21_evaluator_task_adherence.py
```

**Code path.**
1. Builds `_QUERY` (system + user messages) and `_TOOL_CALL` + `_TOOL_DEFINITIONS` in evaluator-format dicts
2. `TaskAdherenceEvaluator(credential=…, azure_openai_endpoint=…, deployment_name=…)`
3. `evaluator(query=…, response=[assistant_turn, tool_call_turn, tool_result_turn, final_answer])`
4. Prints `task_adherence` score and reasoning from the judge model
5. Also runs `ToolCallAccuracyEvaluator` on the same turn

**What to watch in the output.** Score (0–5) and reasoning string. An empty `response` list → evaluator errors. A response with only final text → poor tool evaluation — the full conversation thread is needed.

**Exam cues.** One case is statistically meaningless. Build a versioned representative dataset before drawing conclusions. See lesson 22 for durable cloud evaluation.

**References:** [Agent evaluators](https://learn.microsoft.com/azure/foundry/concepts/evaluation-evaluators/agent-evaluators) · [Task adherence concept](https://learn.microsoft.com/azure/ai-services/content-safety/concepts/task-adherence) · [Evaluate agent how-to](https://learn.microsoft.com/azure/foundry/observability/how-to/evaluate-agent)

---

### 22 — Cloud evaluation

**Question answered:** How is a durable cloud evaluation run created with a reviewed JSONL dataset?

**Background.** Lesson 21 invokes evaluators locally. This lesson optionally uploads reviewed JSONL, creates a persisted Foundry evaluation definition, and starts a durable cloud run. Cloud evaluation suits shared datasets, scale, pre-deployment evidence, and CI gates. Each row needs a non-empty `query` string. Dataset uploads, evaluator calls, model tokens, and stored results all incur cost.

```bash
# Local validation first (no cloud calls):
uv run python 02-generative-ai-and-agents/22_cloud_evaluation.py --dataset cases.jsonl
# Cloud run (uploads data, creates evaluation, starts run):
uv run python 02-generative-ai-and-agents/22_cloud_evaluation.py --dataset cases.jsonl --apply
```

**Code path.**
1. `validate_dataset(dataset)` → validates JSONL shape locally (no Azure call)
2. `--apply`: `evals.files.create(file=dataset, purpose="evals", expires_after={"days": 30})` → uploads dataset
3. `evals.create(data_source_config=…, testing_criteria=[TaskAdherence criterion])` → creates evaluation definition
4. `evals.runs.create(name=…, run_id=eval.id)` → starts cloud run; prints dataset file id, eval id, run id
5. Does NOT poll to completion — check results in Foundry portal

**What to watch in the output.** Default (no `--apply`): describes what would be created. With `--apply`: prints dataset file id, evaluation id, run id. Results appear in Foundry portal after the run completes.

**Exam cues.** `AZURE_AI_PROJECT_ENDPOINT` may differ from `PROJECT_ENDPOINT` if targeting a separate evaluation project. Data uploaded with 30-day expiry. Never upload credentials, customer secrets, or unredacted PII.

**References:** [Cloud evaluation how-to](https://learn.microsoft.com/azure/foundry/how-to/develop/cloud-evaluation) · [Evaluate agent](https://learn.microsoft.com/azure/foundry/observability/how-to/evaluate-agent) · [Agent evaluators](https://learn.microsoft.com/azure/foundry/concepts/evaluation-evaluators/agent-evaluators)

---

### 23 — LangChain tracing

**Question answered:** How can LangChain calls export an OpenTelemetry trace to Azure Monitor?

**Background.** Unlike Agent Framework (lesson 17), LangChain and LangGraph do NOT automatically emit traces when App Insights is connected to the project. They require explicit instrumentation with `AzureAIOpenTelemetryTracer`. Content recording is intentionally disabled here — enabling it captures prompts, tool arguments, and model outputs, which requires privacy and compliance approval before production use.

```bash
uv run python 02-generative-ai-and-agents/23_langchain_tracing.py
```

**Code path.**
1. If `APPLICATIONINSIGHTS_CONNECTION_STRING` set: `AzureAIOpenTelemetryTracer(connection_string=…, enable_content_recording=False)`
2. Otherwise: prints warning, agent still runs without tracer
3. `create_agent(model=model, tools=[…], callbacks=[tracer] if tracer else [])` → agent with optional tracing
4. Agent answers order/inventory question; spans export to App Insights

**What to watch in the output.** If tracing is enabled, spans appear in App Insights → Transaction Search after propagation delay (2–5 min). Query by the printed `agent_id`. Missing traces ≠ request did not run.

**Exam cues.** `enable_content_recording=False` is the safe default. Metadata-only tracing can still be sensitive and incur ingestion/retention cost. Tracing is observability, not evaluation.

**References:** [LangChain traces how-to](https://learn.microsoft.com/azure/foundry/how-to/develop/langchain-traces) · [Framework tracing how-to](https://learn.microsoft.com/azure/foundry/observability/how-to/trace-agent-framework) · [Sensitive content in traces](https://learn.microsoft.com/azure/foundry/observability/how-to/traces-sensitive-content)

---

### 24 — Production observability preflight

**Question answered:** What are the three observability layers and is my environment configured for them?

**Background.** Trace, evaluation, and retrieval data carry operational, privacy, and cost obligations. This lesson explains the three observability layers and checks your local configuration before you connect telemetry, change retention, or send production traffic. It makes no Azure calls by default; `--check-connection` calls the project telemetry API.

```bash
uv run python 02-generative-ai-and-agents/24_production_observability_preflight.py
uv run python 02-generative-ai-and-agents/24_production_observability_preflight.py --check-connection
```

**Code path.**
1. `preflight()` → reads `settings()` and reports whether App Insights, project, direct Azure OpenAI, and Search endpoints are configured
2. Prints server-side setup steps, framework tracing comparison (Agent Framework vs LangChain), and client-side instrumentation pattern
3. `--check-connection`: `client.telemetry.get_application_insights_connection_string()` → verifies App Insights is connected to the project

**What to watch in the output.** Three observability layers:
  1. Server-side (automatic for Foundry-hosted agents — connect App Insights in portal)
  2. Framework tracing (automatic for Agent Framework; explicit for LangChain/LangGraph)
  3. Client-side instrumentation (`AIProjectInstrumentor()`)

"Configured" does NOT mean reachable, authorized, healthy, compliant, or cost-approved.

**Exam cues.** Register `protectGenAISensitiveData` feature flag before September 30, 2026 to route sensitive span attributes to the protected `AppGenAIContent` table.

**References:** [Trace agent setup](https://learn.microsoft.com/azure/foundry/observability/how-to/trace-agent-setup) · [Client-side tracing](https://learn.microsoft.com/azure/foundry/observability/how-to/trace-agent-client-side) · [Sensitive content in traces](https://learn.microsoft.com/azure/foundry/observability/how-to/traces-sensitive-content) · [Observability concept](https://learn.microsoft.com/azure/foundry/concepts/observability)

---

## Stage 6 — Governed external tools (lessons 25–27)

External tool boundaries: each lesson starts with a no-cloud preflight. `--apply` creates/connects real cloud state. Review owner, data boundary, auth, region, retention, logging, and cost before using `--apply`.

### 25 — MCP tool preflight and approval

**Question answered:** What does connecting a remote MCP server to a Foundry agent require, and what is the approval model?

**Background.** MCP (Model Context Protocol) is a protocol for an agent to discover and invoke remote tools. It reduces custom adapter work; it does not make a server, server output, identity, or requested action trustworthy. This lesson enforces that boundary explicitly before attaching the [`northwind_mcp/`](northwind_mcp/README.md) Azure Function server. All tool calls require `require_approval="always"` and `--approve` to execute.

**Before code.** Deploy `northwind_mcp/`, create a Foundry project connection for its HTTPS MCP endpoint, then set `NORTHWIND_MCP_ENDPOINT` and `NORTHWIND_MCP_CONNECTION`.

```bash
# No-cloud preflight:
uv run python 02-generative-ai-and-agents/25_mcp_tool_preflight.py
# Create temp agent (no tool calls):
uv run python 02-generative-ai-and-agents/25_mcp_tool_preflight.py --apply
# Execute reviewed read tools with approval:
uv run python 02-generative-ai-and-agents/25_mcp_tool_preflight.py --apply --approve
```

**Code path.**
1. Validates `NORTHWIND_MCP_ENDPOINT` is HTTPS and not localhost; `NORTHWIND_MCP_CONNECTION` is set
2. `MCPTool(endpoint=…, connection_id=…, allowed_tools=["get_order_status", "list_customer_orders"], require_approval="always")`
3. Agent emits `mcp_approval_request` → app prints name/arguments and returns `approved=True` only with `--approve`
4. `finally` deletes temporary agent version

**What to watch in the output.** Default: "No cloud calls made." With `--apply --approve`: approval decision, answer, deletion message. Without `--approve`: tool call is blocked.

**Exam cues.** MCP ≠ function tools (app executes them) ≠ Toolbox (Foundry-managed catalog) ≠ A2A (delegated agent protocol). Project connection authenticates service, not end user.

**References:** [MCP tools how-to](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/model-context-protocol) · [MCP authentication](https://learn.microsoft.com/azure/foundry/agents/how-to/mcp-authentication) · [Tool authentication](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/tool-authentication)

---

### 26 — Toolbox and tool catalog

**Question answered:** How do I publish a governed tool collection and call it from an Agent Framework agent?

**Background.** Foundry Toolbox packages a curated tool collection behind one MCP-compatible endpoint. Teams build and version tools centrally; MCP-compatible runtimes discover and invoke them without embedding every backend integration in agent code. Toolbox centralizes connection management, authentication, governance, observability, and version rollout, but it does not authorize a business action merely because a tool schema exists.

```text
Developer identity
  → create immutable Toolbox version
  → test version-specific MCP endpoint
  → review tools, auth, data flow, and results
  → promote a tested version as default

Local or hosted agent
  → FoundryChatClient calls DEFAULT_MODEL
  → MCPStreamableHTTPTool discovers Toolbox tools
  → Entra token authenticates each MCP request
  → Toolbox selects its configured connection/identity for the downstream tool
  → tool result returns to the model
```

#### Build, discover, consume, and govern

| Lifecycle area | Toolbox responsibility | Application responsibility |
|---|---|---|
| Build | Store curated tool definitions and immutable versions. | Review contracts, owners, descriptions, schemas, and downstream effects. |
| Discover | Expose tools through MCP; Tool Search can expose `tool_search` and `call_tool` instead of every definition. | Give the model enough intent and context to select correctly; do not assume selection is authorization. |
| Consume | Offer one MCP-compatible endpoint to Agent Framework and other MCP clients. | Authenticate to the endpoint, constrain prompts, validate results, and close sessions. |
| Govern | Centralize connections, credential handling, guardrails, versioning, and telemetry. | Enforce tenant/business policy, human approval, idempotency, rate limits, and incident response. |

`ToolSearchToolboxTool` reduces context cost for larger catalogs. It does not inspect whether a caller is allowed to perform the discovered operation and it does not make write tools safe.

#### Endpoint contract

| Endpoint | Shape | Use |
|---|---|---|
| Developer | `{PROJECT_ENDPOINT}/toolboxes/{name}/versions/{version}/mcp?api-version=v1` | Test one immutable version before promotion. |
| Consumer | `{PROJECT_ENDPOINT}/toolboxes/{name}/mcp?api-version=v1` | Follow the toolbox's current default version in a reviewed deployed consumer. |

The lesson deliberately invokes the **developer endpoint**. This prevents a default-version change from silently changing the lab while you test. The first version becomes default automatically; later versions must be tested and promoted through the supported management workflow.

#### Authentication layers

1. `DefaultAzureCredential` identifies the local developer or deployed workload.
2. `get_bearer_token_provider(..., "https://ai.azure.com/.default")` acquires the Foundry data-plane token.
3. `_ToolboxAuth` requests a fresh token for every MCP HTTP request instead of caching a raw secret in source.
4. Toolbox applies the connection/authentication configured for each downstream tool. That identity can differ from the identity connecting to Toolbox.

Grant `Foundry User` at the project to identities that manage or consume the toolbox as required by the scenario. Downstream systems still need least-privilege authorization for project managed identity, agent identity, user passthrough, OAuth, or connection-based authentication.

The current Agent Framework import is `from agent_framework.foundry import FoundryChatClient`. Current `api-version=v1` Toolbox examples do not send the older `Foundry-Features: Toolboxes=V1Preview` header; use the current SDK/docs contract instead of copying a stale preview header.

```bash
# No-cloud preflight:
uv run python 02-generative-ai-and-agents/26_toolbox_tool_catalog_preflight.py

# Publish version (persists — record the printed version):
uv run python 02-generative-ai-and-agents/26_toolbox_tool_catalog_preflight.py --apply

# Test an existing immutable version with the local Agent Framework agent:
uv run python 02-generative-ai-and-agents/26_toolbox_tool_catalog_preflight.py \
  --invoke --toolbox-version 1 \
  --prompt "What tools are available? Explain what each one is for."

# Create a version and immediately test that returned version:
uv run python 02-generative-ai-and-agents/26_toolbox_tool_catalog_preflight.py \
  --apply --invoke \
  --prompt "Find current public information about Microsoft Foundry Toolbox."

# Delete version (only after checking consumers):
uv run python 02-generative-ai-and-agents/26_toolbox_tool_catalog_preflight.py --apply --delete-version <version>
```

**Code path.**
1. `catalog_tools()` returns named `WebSearchToolboxTool` plus `ToolSearchToolboxTool`.
2. `--apply` calls `client.toolboxes.create_version(...)` and prints the immutable version plus both endpoint shapes.
3. `toolbox_mcp_url(..., version)` constructs the developer endpoint with required `api-version=v1`.
4. `_ToolboxAuth` injects a fresh `https://ai.azure.com/.default` bearer token into each MCP request.
5. `MCPStreamableHTTPTool(..., load_prompts=False)` discovers the Toolbox tools without loading MCP prompt templates.
6. `FoundryChatClient(project_endpoint=PROJECT_ENDPOINT, model=DEFAULT_MODEL)` creates an ephemeral local agent with the MCP tool.
7. `await agent.run(prompt)` lets the model discover and call relevant tools, then prints `response.text`.
8. `finally` closes the MCP session, HTTP client, and credential even when invocation fails.
9. `--apply --delete-version` calls `client.toolboxes.delete_version(...)`; it cannot be combined with invocation.

**What to watch in the output.** Publishing prints the version-specific developer endpoint and default consumer endpoint. Invocation prints the exact endpoint and deployment before the response. A response describing tools proves the MCP connection and model loop; it does not prove every downstream tool can authenticate or safely execute.

**Safety and cost boundary.**

- `--invoke` is a real model request. The model might call Web Search, which can send approved prompt content outside your Foundry data boundary and incur tool costs.
- Treat a model tool request as a proposal. Validate caller, tenant, arguments, business rules, timeout, idempotency, and approval before consequential actions.
- Do not send secrets, customer content, privileged instructions, or regulated data merely to test discovery.
- Version deletion can break agents pinned to that version. Default promotion can change every consumer endpoint user without an agent redeployment.
- A local Agent Framework agent is not a persisted prompt agent or deployed hosted agent. Production runtime identity and network access need separate validation.

**Exam cues.** Toolbox is Foundry-homed but MCP-compatible, so it is not limited to Foundry-hosted agents. Toolbox versions are immutable. Developer endpoints pin a version; consumer endpoints follow default. MCP authentication to Toolbox is separate from each downstream tool's authentication. Tool Search improves discovery/context use, not authorization.

**References:** [Toolbox overview](https://learn.microsoft.com/azure/foundry/agents/concepts/toolbox-overview) · [Toolbox how-to](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/toolbox) · [Toolbox quickstart](https://learn.microsoft.com/azure/foundry/agents/quickstarts/quickstart-toolbox-agent) · [Tool authentication](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/tool-authentication) · [Tool Search](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/tool-search) · [Tool catalog](https://learn.microsoft.com/azure/foundry/agents/concepts/tool-catalog) · [Agent Framework Responses quickstart](https://learn.microsoft.com/azure/foundry/agents/quickstarts/responses-api)

---

### 27 — Azure AI Search agent tool

**Question answered:** What does connecting a vector-capable Azure AI Search index to an agent look like?

**Background.** This is the production-RAG direction: Agent Service queries a vector-capable Azure AI Search index through an existing Foundry project connection. It contrasts with lesson 06 (managed file search) and lesson 20 (ephemeral local FAISS). Search supplies durable indexing, ACL, and retrieval operations — it does not make retrieved documents tenant-authorized. Security trimming, source lifecycle, and retrieval quality evaluation are separate requirements.

**Before code.** Create Search service, index, and Foundry project connection. Set `SEARCH_CONNECTION_NAME` and `SEARCH_INDEX`.

```bash
# No-cloud preflight:
uv run python 02-generative-ai-and-agents/27_agent_azure_ai_search_preflight.py
# Create temp agent, query, delete (does NOT create/delete Search data):
uv run python 02-generative-ai-and-agents/27_agent_azure_ai_search_preflight.py --apply
```

**Code path.**
1. Resolves `SEARCH_CONNECTION_NAME` → connection object → `connection_id`
2. `AzureAISearchTool(indexes=[AISearchIndexResource(project_connection_id=…, index_name=…, query_type=VECTOR_SEMANTIC_HYBRID, top_k=3)])`
3. Creates temp agent with `require_tool_calls=True`; invokes with query → prints citation lines
4. `finally` deletes temp agent version (does NOT delete Search data)

**What to watch in the output.** Citation lines with source URLs confirm retrieval. Preflight (`no --apply`) prints configuration requirements and exits cleanly.

**Exam cues.** Grant project managed identity `Search Index Data Contributor` and `Search Service Contributor` for keyless access. Key-based Search auth is NOT supported for private-network scenarios.

**References:** [Azure AI Search tool how-to](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/ai-search) · [AI Search agentic retrieval index](https://learn.microsoft.com/azure/search/agentic-retrieval-how-to-create-index) · [RAG evaluators](https://learn.microsoft.com/azure/foundry/concepts/evaluation-evaluators/rag-evaluators)

---

## Stage 7 — Hosted agent delivery (lessons 28–30)

Hosted agents run packaged application code under Foundry Agent Service with a managed runtime, deployment lifecycle, and identity. The contained [`hosted_agent_responses/`](hosted_agent_responses/README.md) project is part of lessons 28–30, not a separate lesson. All three lesson scripts are local-only; actual deployment uses explicit `--apply` in the contained sample.

### 28 — Responses hosted-agent preflight

**Question answered:** What is the Responses hosted-agent runtime contract and what does a preflight check verify?

**Background.** A hosted agent is NOT a local Agent Framework process (lesson 17). It is packaged application code with a deployment lifecycle, container image, managed identity, platform-injected environment, and a defined HTTP protocol. The Responses adapter owns the contract: Linux amd64 remote build, port 8088, GET /readiness, POST /responses, and SIGTERM shutdown. This lesson validates the contained `hosted_agent_responses/` sample against that contract — it never deploys.

```bash
uv run python 02-generative-ai-and-agents/28_hosted_agent_responses.py
# Then validate locally:
cd 02-generative-ai-and-agents/hosted_agent_responses
azd ai agent run
azd ai agent invoke --local "Give a one-line deployment status."
curl -sS http://localhost:8088/readiness
```

**Code path.**
1. `28_hosted_agent_responses.py` → `subprocess.run([sys.executable, "preflight.py"], cwd=hosted_agent_responses/)`
2. `preflight.py` validates `azure.yaml` contract: protocol, port, build spec
3. Prints adapter contract: Linux amd64 remote build, port 8088, /readiness, /responses, SIGTERM

**What to watch in the output.** Contract validation output confirms the sample is correctly configured. Any contract drift causes the preflight to fail with a specific error.

**Exam cues.** Platform injects `FOUNDRY_PROJECT_ENDPOINT` — do not redeclare it. Do not bundle macOS/Windows/ARM wheels. `python deploy.py` is a dry run; `--apply` deploys.

**References:** [Hosted agents concept](https://learn.microsoft.com/azure/foundry/agents/concepts/hosted-agents) · [Hosted-agent contract](https://learn.microsoft.com/azure/foundry/agents/concepts/hosted-agent-contract) · [Hosted-agent quickstart](https://learn.microsoft.com/azure/foundry/agents/quickstarts/quickstart-hosted-agent)

---

### 29 — Hosted agent A2A boundary

**Question answered:** Is the Responses endpoint an A2A endpoint?

**Background.** Responses (`POST /responses`) is an OpenAI-compatible user/application protocol. A2A is a separate preview agent-to-agent protocol with agent discovery, task lifecycle, caller authentication, delegated authority, and data-sharing design. They are not interchangeable. This lesson explicitly verifies the contained sample does NOT declare A2A — preventing false protocol claims before integration.

```bash
uv run python 02-generative-ai-and-agents/29_hosted_agent_a2a.py
```

**Code path.**
1. Calls `preflight.py --a2a` in `hosted_agent_responses/`
2. `preflight.py --a2a` reads `azure.yaml`, verifies `protocol: responses` (NOT `a2a`)
3. Prints "`POST /responses` is not A2A" — no Azure call, no deployment, no agent version

**What to watch in the output.** Confirmation that the sample declares Responses protocol and not A2A. This is a contractual check, not a functional test.

**Exam cues.** To implement A2A: enable incoming A2A on target, create A2A project connection with target base path and auth, select `A2APreviewTool`, and design caller/target authorization, consent, tasks, timeout, audit, and fallback.

**References:** [Agent-to-agent tools](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/agent-to-agent) · [Enable A2A endpoint](https://learn.microsoft.com/azure/foundry/agents/how-to/enable-agent-to-agent-endpoint) · [A2A authentication](https://learn.microsoft.com/azure/foundry/agents/concepts/agent-to-agent-authentication)

---

### 30 — Hosted-agent CI/CD

**Question answered:** What does an OIDC-based CI/CD pipeline for a hosted agent look like?

**Background.** Delivery must reproduce build, identity, deployment, smoke test, telemetry, and rollback conditions. The contained `hosted-agent-cd.yml` is a reference CI/CD asset using GitHub OIDC rather than long-lived client secrets. The deployment wrapper only mutates cloud state with `--apply`.

```bash
uv run python 02-generative-ai-and-agents/30_hosted_agent_cicd.py
cd 02-generative-ai-and-agents/hosted_agent_responses
python deploy.py          # plan only — prints what would be deployed
python deploy.py --apply  # deploy only after environment review
```

**Code path.**
1. `30_hosted_agent_cicd.py` → prints paths to `hosted-agent-cd.yml`, `deploy.py`, and deployment guide
2. `hosted-agent-cd.yml` uses `id-token: write`, `azure/login` with OIDC, `Azure/setup-azd`, then runs local preflight, explicit deployment wrapper, and smoke prompt
3. `deploy.py` orders optional `azd provision` before `azd deploy`; never mutates without `--apply`

**What to watch in the output.** Lesson 30 prints file paths only — it makes no cloud calls. Read `hosted-agent-cd.yml` to understand the pipeline structure.

**Exam cues.** OIDC login can succeed while deployment identity lacks Foundry Project Manager, ACR, or resource permissions. Smoke test must exercise the deployed endpoint, identity, required tool egress, safe failure, and observability — not only build success.

**References:** [Hosted-agent CI/CD quickstart](https://learn.microsoft.com/azure/foundry/agents/quickstarts/set-up-cicd-hosted-agent) · [Deploy hosted agent](https://learn.microsoft.com/azure/foundry/agents/how-to/deploy-hosted-agent) · [Hosted-agent code deployment](https://learn.microsoft.com/azure/foundry/agents/how-to/deploy-hosted-agent-code)

---

## Stage 8 — OpenAI advanced + LangChain patterns (lessons 31–35)

Lessons 31–35 deepen the Responses API and LangChain integration started in stages 1–4. They add dense signal: embeddings (vector foundations), structured output enforcement (json_schema), cost optimisation (prompt caching), multi-turn memory, and the raw function-calling loop that underlies every agent tool.

### 31 — Embeddings

**Question answered:** How do I get a vector representation of text for semantic search or RAG?

**Background.** Embeddings are fixed-length float vectors that encode semantic meaning. Same embedding model → same vector space → comparable. Different model or version → incompatible index. Embedding deployments are separate from chat deployments.

```bash
uv run python 02-generative-ai-and-agents/31_openai_embeddings.py
uv run python 02-generative-ai-and-agents/31_openai_embeddings.py --apply --model <embeddings-deployment>
```

**Code path.** `openai_client().embeddings.create(model=deployment, input=[texts])` → per item: `len(embedding)`, first-4 values, magnitude.

**What to watch.** `dim: 1536` (small/ada) or `3072` (large). Magnitude ≈ 1.0 (normalized). All inputs share same dim — mismatch means wrong deployment. Compare with domain 05 lessons 02-03 which use server-side vectorization via Search.

**References:** [Embeddings](https://learn.microsoft.com/azure/foundry/openai/how-to/embeddings)

### 32 — JSON schema mode

**Question answered:** How do I enforce a typed schema on model output, not just valid JSON?

**Background.** `json_schema` with `strict: true` constrains structure + types at the service layer. Failure to match schema raises a service error rather than returning an invalid shape. Stronger than older `json_mode` (valid JSON, any shape).

```bash
uv run python 02-generative-ai-and-agents/32_openai_json_mode.py
uv run python 02-generative-ai-and-agents/32_openai_json_mode.py --apply
```

**Code path.** `responses.create(response_format={"type": "json_schema", "json_schema": {"name": ..., "strict": True, "schema": SCHEMA}})` → `json.loads(output_text)`.

**What to watch.** All schema fields present with correct types. `additionalProperties: false` enforces no extra fields. Compare with lesson 07 (Pydantic wrapper over same mechanism).

**References:** [JSON mode](https://learn.microsoft.com/azure/foundry/openai/how-to/json-mode)

### 33 — Prompt caching

**Question answered:** How do prompt cache hits reduce token cost, and how do I verify them?

**Background.** Repeated long prefix tokens (system instructions, RAG blocks, few-shot examples) are cached at service side. Cache hits surface as `usage.input_tokens_details.cached_tokens`. Minimum prefix varies by model (~1024 tokens for gpt-4o). Prefix must be byte-identical.

```bash
uv run python 02-generative-ai-and-agents/33_openai_prompt_caching.py
uv run python 02-generative-ai-and-agents/33_openai_prompt_caching.py --apply
```

**Code path.** Two `responses.create()` calls with same long system prompt + different user messages. Print `cached_tokens` from each `usage.input_tokens_details`.

**What to watch.** Call 1 `cached_tokens: 0` (cold). Call 2 `cached_tokens > 0` (warm, ~50% cheaper). If both 0: prefix too short or cache TTL expired.

**References:** [Prompt caching](https://learn.microsoft.com/azure/foundry/openai/how-to/prompt-caching) · [Latency](https://learn.microsoft.com/azure/foundry/openai/how-to/latency)

### 34 — LangChain memory

**Question answered:** How do I maintain multi-turn conversation state with LangChain?

**Background.** Beyond single-turn calls (lesson 19), production agents need conversation history. `RunnableWithMessageHistory` wraps a chain with a session-scoped `ChatMessageHistory`. In-memory for this demo — production uses Redis, Cosmos DB, or Foundry Memory (lesson 14).

```bash
uv run python 02-generative-ai-and-agents/34_langchain_memory.py
uv run python 02-generative-ai-and-agents/34_langchain_memory.py --apply
```

**Code path.** `AzureChatOpenAI` + `ChatMessageHistory` store + `RunnableWithMessageHistory`. Three turns; same `session_id` key threads history. Turn 3 asks about a fact from turn 1 — should answer without re-prompting.

**What to watch.** Turn 3 correctly references context from turn 1. Compare with lesson 13 (`previous_response_id` native approach) — LangChain adds middleware but same underlying state.

**References:** [LangChain memory](https://learn.microsoft.com/azure/foundry/how-to/develop/langchain-memory) · [LangChain models](https://learn.microsoft.com/azure/foundry/how-to/develop/langchain-models)

### 35 — Direct function calling

**Question answered:** What does the raw two-step Responses API function-calling loop look like?

**Background.** Lesson 11 wraps function tools in a prompt agent. This lesson shows the raw pattern: send tool schema → model returns `function_call` item → app executes tool locally → send `function_call_output` back → model returns final text. Foundation for all agent tool behavior.

```bash
uv run python 02-generative-ai-and-agents/35_openai_function_calling.py
uv run python 02-generative-ai-and-agents/35_openai_function_calling.py --apply
```

**Code path.** Step 1: `responses.create(tools=[weather_tool])` → `output` contains `function_call`. Step 2: `_fake_weather(city)` locally. Step 3: `responses.create(input=[function_call_output], previous_response_id=r1.id)` → final `output_text`.

**What to watch.** Step 1 prints `Tool call: get_weather({city: "Seattle"})`. Step 3 prints a weather sentence integrating the fake result. Model extracted city from prompt — never asked user.

**References:** [Function calling](https://learn.microsoft.com/azure/foundry/openai/how-to/function-calling)

---

## Stage 9 — Reasoning models + grounded web search (lessons 36–37)

Reasoning models and live web search are the two Responses API capabilities most absent from traditional chat completions training. Lesson 36 proves thinking tokens are real and billable; lesson 37 proves grounding in live Bing results without a Bing API key.

### 36 — Reasoning models (o-series)

**Question answered:** How many thinking tokens did the model spend reasoning through this problem?

**Background.** o1, o3, and o3-mini generate an internal chain of thought before answering. Thinking tokens appear in `usage.output_tokens_details.reasoning_tokens` — they are billed at output token rates but not shown in `output_text`. `reasoning_effort` (low/medium/high) controls the thinking budget. Higher effort improves accuracy on complex problems at higher cost. This is NOT the same as prompting the model to "think step by step" — reasoning happens inside the model before output begins.

```bash
uv run python 02-generative-ai-and-agents/36_openai_reasoning_models.py
uv run python 02-generative-ai-and-agents/36_openai_reasoning_models.py --apply --model o3-mini
uv run python 02-generative-ai-and-agents/36_openai_reasoning_models.py --apply --model o3-mini --effort high
```

**Code path.**
1. `openai_client().responses.create(model=O_MODEL, input=prompt, reasoning={"effort": effort})`.
2. `usage.output_tokens_details.reasoning_tokens` → thinking token count.
3. `output_text` → final answer only (thinking chain not exposed).

**What to watch.** `reasoning_tokens > 0` confirms reasoning is active. Compare `reasoning_tokens` between `low` and `high` effort to see the budget difference.

**References:** [Reasoning models](https://learn.microsoft.com/azure/foundry/openai/how-to/reasoning) · [Responses API](https://learn.microsoft.com/azure/foundry/openai/how-to/responses) · [Working with models](https://learn.microsoft.com/azure/foundry/openai/how-to/working-with-models)

---

### 37 — Built-in web search

**Question answered:** How does the Responses API ground an answer in live Bing results without a Bing API key?

**Background.** Adding `{"type": "web_search_preview"}` to the `tools` list activates the built-in Bing search tool. The model decides when to call it, sends a query to Bing, receives top results, and uses them as context for the answer. URL citations appear in `annotations` on output items. This is NOT the same as the Bing Search SDK, Azure AI Search, or an agent with a Bing connection — it is a zero-config built-in for the Responses API only.

```bash
uv run python 02-generative-ai-and-agents/37_openai_web_search.py
uv run python 02-generative-ai-and-agents/37_openai_web_search.py --apply
uv run python 02-generative-ai-and-agents/37_openai_web_search.py --apply --query "Latest Azure AI Foundry SDK release notes"
```

**Code path.**
1. `openai_client().responses.create(model=..., input=query, tools=[{"type": "web_search_preview"}])`.
2. `response.output_text` → grounded answer.
3. Iterate `response.output` items → collect `annotation.url` entries → print citations.

**What to watch.** `output_text` reflects live information. `annotations` list holds cited Bing URLs. Empty annotations = model answered from training data without triggering search (short/obvious queries may not trigger web search).

**References:** [Web search how-to](https://learn.microsoft.com/azure/foundry/openai/how-to/web-search) · [Responses API](https://learn.microsoft.com/azure/foundry/openai/how-to/responses) · [Tool search](https://learn.microsoft.com/azure/foundry/openai/how-to/tool-search)

---

## Stage 10 — Structured outputs + webhooks (lessons 38–39)

These two lessons cover distinct output-contract mechanisms: lesson 38 uses `beta.chat.completions.parse` to return a typed Pydantic object (not the Responses API json_schema mode from lessons 07/32); lesson 39 shows async push delivery via webhooks, which invert the polling pattern — the service calls your listener on events.

### 38 — Structured outputs (Pydantic parse)

**Question answered:** How do I get a typed Python object back from a model call, without writing a JSON parser?

**Background.** `client.beta.chat.completions.parse(response_format=PydanticModel)` runs on the Chat Completions API and returns `completion.choices[0].message.parsed` — a fully typed Python instance. If the model refuses (safety, policy), `message.refusal` is set instead of `parsed`. This is distinct from lesson 07 (Responses API json_schema + strict=True) and lesson 32 (json_schema via responses.create): all three enforce schema, but different APIs and return different types.

```bash
uv run python 02-generative-ai-and-agents/38_openai_structured_outputs.py
uv run python 02-generative-ai-and-agents/38_openai_structured_outputs.py --apply
```

**Code path.**
1. Define `class CalendarEvent(BaseModel)` with `name: str`, `date: str`, `participants: list[str]`.
2. `raw_client.beta.chat.completions.parse(model=..., messages=..., response_format=CalendarEvent)`.
3. `completion.choices[0].message.parsed` → typed `CalendarEvent` instance.
4. If `message.refusal` set → model refused extraction.

**What to watch.** `parsed.name`, `parsed.date`, `parsed.participants` populated as Python objects. `finish_reason: stop` with no `refusal` confirms successful extraction.

**Exam cues.** `beta.chat.completions.parse` uses Chat Completions API — NOT Responses API. Schema is encoded in Pydantic class, not a JSON dict. `message.parsed` is None if model refused; check `message.refusal` first.

**References:** [Structured outputs](https://learn.microsoft.com/azure/foundry/openai/how-to/structured-outputs) · [JSON mode](https://learn.microsoft.com/azure/foundry/openai/how-to/json-mode)

---

### 39 — Webhooks preflight

**Question answered:** How does my application receive notifications when an Azure OpenAI event fires, without polling?

**Background.** Webhooks register a public HTTPS URL that Azure OpenAI calls on events (`response.completed`, `realtime.call.incoming`). Registration is via REST — no SDK wrapper. Each delivery is HMAC-signed; verify with `client.webhooks.unwrap(request.data, request.headers)`. This is NOT polling, NOT WebSocket, NOT a Responses API call — it is an outbound HTTP POST from Azure to your server.

```bash
uv run python 02-generative-ai-and-agents/39_openai_webhooks_preflight.py
uv run python 02-generative-ai-and-agents/39_openai_webhooks_preflight.py --apply --webhook-url https://myapp.azurewebsites.net/webhook
```

**Code path.**
1. Build `payload = {name, url, event_types}`.
2. `POST /openai/v1/dashboard/webhook_endpoints` with `api-key` header.
3. Response contains `id` (save for deletion), `secret` (store in Key Vault — shown once only).
4. Listener verifies delivery: `client.webhooks.unwrap(request.data, request.headers)` → typed `event`.

**What to watch.** `webhook_id` and `secret` in response. Return HTTP 200 from your listener to acknowledge — Azure retries on non-200. Verify `event.type` before processing.

**References:** [Webhooks how-to](https://learn.microsoft.com/azure/foundry/openai/how-to/webhooks)

---

## Feature status and hard limits

| Feature | Status | Practical boundary |
|---|---|---|
| Responses API | GA | Direct Azure OpenAI-compatible; tool availability is model-dependent |
| Prompt agents | GA | Versioned; each `create_version()` persists a new version; clean up stale lab versions |
| Conversation threads | GA | Turn-scoped context; not durable profile memory |
| Built-in tools (web, code, file) | GA | Managed service-side execution; usage and residency apply |
| Function tools / OpenAPI tools | GA | App executes; model requests; backend must be deployed and reachable |
| Foundry Memory | Preview | Async/debounced writes via agent tool (update_delay); synchronous via begin_update_memories (update_delay=0); `project.beta` surface; TTL set at creation only |
| Workflows | Preview → retiring Dec 1, 2026 | Study as artifact; migrate to Agent Framework/hosted agent |
| Agent Framework | GA | Local process; not deployed; no packaging, identity, or lifecycle |
| Multi-agent (agent-as-tool) | GA | Application-controlled pattern; not A2A |
| LangChain/LangGraph on Azure | GA | Requires explicit tracing instrumentation |
| Local SDK evaluation | GA | Local process; no cloud state; one case is not evidence |
| Cloud evaluation | GA | Persisted runs; dataset upload; cost incurred |
| App Insights tracing | GA | Content recording disabled by default; opt-in with governance approval |
| MCP | GA | External trust boundary; allowlist + approval required |
| Toolbox | GA | Foundry-managed versioned catalog; version deletion breaks consumers |
| Azure AI Search agent tool | GA | Requires existing index + project connection; no ingestion in lesson |
| Hosted agents (Responses) | GA | Full deployment lifecycle; not local Agent Framework |
| A2A | Preview | Separate protocol from Responses; requires explicit enablement |

---

## Troubleshooting

| Symptom | Likely cause | Resolution |
|---|---|---|
| `401`/`403` direct call | Wrong endpoint, missing role, or credential chain failure | Use `AZURE_OPENAI_ENDPOINT`; assign Azure OpenAI User role on resource |
| `401`/`403` project agent call | Wrong project URL or missing Foundry project access role | Use `PROJECT_ENDPOINT`; assign Foundry User on project |
| `404 DeploymentNotFound` | Deployment name/endpoint mismatch | List deployments; use configured name, not model family label |
| Lesson 03 fails | Reasoning deployment absent or incompatible | Deploy supported reasoning model; set `REASONING_MODEL` to deployment name |
| Lesson 09 exits: agent not found | Lesson 08 not run | Run `08_prompt_agent_create.py` first |
| Function result rejected | Missing/mismatched `call_id` or invalid loop | Preserve each `call_id`; submit all outputs in same conversation |
| Tool loop runs forever | Ambiguous instructions or repeated failure | Inspect loop; keep `MAX_TOOL_ROUNDS`; return bounded errors |
| Lesson 12 rejects endpoint | `ORDERS_FN_ENDPOINT` empty or localhost | Deploy backend; use HTTPS URL without `/api` suffix |
| MCP `--apply` fails | Localhost endpoint, missing auth, or unreachable backend | Use HTTPS MCP endpoint reachable from Agent Service |
| Lesson 25 tool blocked | `--approve` absent, tool not in allowlist | Review printed tool name and arguments; approve only reviewed allowlisted read actions |
| Lesson 26 version removal breaks agent | Consumer references deleted version | Inventory consumers; promote/test replacement before deleting |
| Lesson 27 fails | Connection name, index name, RBAC, or private DNS mismatch | Verify `SEARCH_CONNECTION_NAME`, `SEARCH_INDEX`, identity role, agent-to-Search route |
| Memory misses preference | Different user header, async delay, or extraction miss | Use same `x-memory-user-id`; never invent a recalled fact |
| Lesson 16 fails | Lesson 15 not run or preview SDK changed | Create intake agent first; inspect supported preview surface |
| Low evaluator score | One case, weak trace, or out-of-scope rubric | Build representative dataset; inspect failure distribution |
| No lesson 23 traces | Missing connection string or telemetry propagation delay | Set `APPLICATIONINSIGHTS_CONNECTION_STRING`; wait 2–5 min |
| Lesson 28 preflight fails | Runtime contract or dependency drift | Preserve Responses adapter, port 8088, Linux amd64 remote build contract |
| Hosted deploy succeeds but invoke fails | Version inactive, wrong protocol, RBAC, or private DNS | Poll version status; invoke correct protocol; test identity from deployed runtime |
| LangChain/LangGraph error | Wrong endpoint or deployment name | Use `AZURE_OPENAI_ENDPOINT/openai/v1`; use deployment names |
| FAISS embedding fails | Chat model used as embedding deployment | Set `EMBEDDING_MODEL` to a compatible embedding deployment |

---

## CI/CD and operational release

```text
Commit code, prompts, schemas, infrastructure, evaluation fixtures
    → lint / type / test deterministic application code
    → run schema and contract tests against mock/isolated backend
    → provision / update least-privileged non-production resources through IaC
    → deploy versioned agent / hosted runtime / tool backend
    → smoke test endpoint, identity, tool reachability, and safe failure paths
    → run evaluation dataset and policy checks
    → approve promotion with model / prompt / tool / corpus version evidence
    → canary or staged release with traces, alerts, rollback
    → evaluate production-like failures and remove stale versions/resources
```

| Release gate | Minimum evidence |
|---|---|
| Identity | Workload identity selected; roles scoped to endpoint/action; no user shared credentials |
| Network | Tool backends and MCP endpoints reachable from runtime; DNS/egress/ingress tested |
| Secrets | Secret store/managed identity; no keys in repository, prompts, tool schema, or logs |
| Tool safety | Allowlist, strict schema, semantic validation, caller authorization, timeout, approval |
| Evaluation | Versioned dataset, thresholds, regression comparison, failure triage, release owner |
| Resilience | Rate limit policy, bounded retry, timeout, circuit/queue/fallback behavior, rollback |
| Cost | Token/tool/storage/telemetry budget, quotas, alerts, cleanup owner |

---

## Security, networking, and IaC

| Decision | Recommendation | Common pitfall |
|---|---|---|
| Identity in deployed workloads | Managed or workload identity; no user-shared credentials | `az login` tokens are personal — not suitable for deployed workloads |
| Secrets | Project connection or Key Vault-backed connection | Secrets in `.env`, tool descriptions, or trace attributes |
| Network boundary | Private endpoints for Foundry, Azure OpenAI, Search, App Insights, tool backends; test from actual runner | Private endpoint ≠ RBAC; DNS + egress + ingress each need verification |
| Tool backend auth | API key or Entra auth in production; align OpenAPI auth details | Anonymous demo auth from lesson 12 is NOT production auth |
| MCP server trust | Allowlist tools, require approval, least-privilege identity, timeout, audit | `--approve` is client-side; backend still enforces authorization |
| Content recording | Disabled by default; opt-in only with data governance approval | Content recording can retain sensitive prompts, tool args, model outputs |
| IaC scope | Resource groups, networking, private endpoints, RBAC, tags, monitoring | Manual portal clicks drift; record every production setting in IaC |

---

## Common exam traps

| Claim | Correct interpretation |
|---|---|
| "Same resource name → same endpoint" | `services.ai.azure.com` project URL ≠ `openai.azure.com` direct URL |
| "Model family name in `DEFAULT_MODEL`" | `model=` needs the configured deployment name, not family label |
| "Tool schema = execution permission" | Schema constrains model input; application authorizes execution |
| "`strict=True` = true content" | Constrains response structure; does not validate content accuracy |
| "Local curl = Agent Service reachability" | Agent Service cannot reach laptop localhost |
| "Anonymous OpenAPI = production auth" | Demo auth is for static data only; protect production APIs |
| "MCP = Toolbox = A2A = function calling" | Distinct integration layers solving different problems |
| "Conversation = memory" | Conversation is turn context; Memory is preview durable extraction |
| "65 seconds = guaranteed memory recall" | Async debounced extraction is non-deterministic |
| "update_delay=0 in tool = immediate write" | `update_delay=0` bypasses debounce in `begin_update_memories` API only; agent tool uses `update_delay` seconds of inactivity |
| "memory_command_call appears in output_text" | It appears as an item in `response.output` list, not in `output_text` |
| "scope={{$userId}} resolves everywhere" | Only when using the agent tool + `x-memory-user-id` header; direct API calls require explicit scope string |
| "TTL can be updated after store creation" | Current preview: TTL set at creation only; recreate store to change |
| "Workflow YAML = long-term runtime" | Workflows retire December 1, 2026 |
| "Local Agent Framework = hosted agent" | Local process does not deploy or host anything |
| "One evaluator result = cloud evaluation" | Local SDK call ≠ persisted Foundry run with dataset |
| "Trace = evaluation" | Trace observes execution; evaluator scores it |
| "Content recording is harmless" | Can retain sensitive data; requires governance approval |
| "LangChain uses PROJECT_ENDPOINT" | Lessons 19–20, 23 use `AZURE_OPENAI_ENDPOINT/openai/v1` |
| "Embedding model = chat model" | Use compatible embedding deployment name |
| "FAISS demo = production RAG" | Ephemeral in-process index with no ACL, governance, or persistence |
| "Toolbox = MCP server you operate" | Foundry-managed versioned catalog with MCP-compatible endpoint |
| "Responses hosted agent = A2A" | Requires separate explicit A2A protocol declaration |
| "Private endpoint = private runtime path" | DNS, egress, ingress, and RBAC still each need verification |
| "Cloud evaluation run = release approval" | Evidence to review against thresholds and policy — not automatic approval |
| "`--apply` = harmless preview" | Can upload, create, invoke, or delete durable cloud assets |

---

## Objective coverage and limits

Domain 2 covers: direct Responses API calls; built-in managed tools (web search, code interpreter, file search, structured output); Prompt Agent creation, invocation, function tools, OpenAPI tools, conversation threads, Foundry Memory, and workflow preview; local Microsoft Agent Framework, multi-agent routing, LangChain agents, and LangGraph RAG; local SDK evaluation, cloud evaluation runs, LangChain tracing, and production observability preflight; MCP tool integration with approval, Toolbox versioning and local Agent Framework consumption, and Azure AI Search agent integration; and Responses hosted-agent contract validation, A2A boundary verification, and OIDC CI/CD reference.

It does **not** fully implement: remote MCP OAuth/Entra setup, credential rotation, or server lifecycle; incoming A2A endpoint deployment, delegated-identity policy, or task lifecycle; Azure AI Search ingestion, ACL/security trimming, reranking, or index lifecycle; hosted-agent private networking, supply-chain policy, scaling, or incident operations; cloud-evaluation completion polling, continuous evaluation, or safety/RAG evaluator selection; human approval workflows for write tools, idempotent writes, or durable queues.

---

## References

### Responses API and direct model calls

- [Responses API quickstart](https://learn.microsoft.com/azure/foundry/agents/quickstarts/responses-api)
- [Foundry models overview](https://learn.microsoft.com/azure/foundry/concepts/foundry-models-overview)
- [Authentication and authorization in Foundry](https://learn.microsoft.com/azure/foundry/concepts/authentication-authorization-foundry)

### Prompt agents and tools

- [Prompt agent quickstart](https://learn.microsoft.com/azure/foundry/agents/quickstarts/prompt-agent)
- [Function calling how-to](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/function-calling)
- [OpenAPI tools how-to](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/openapi)
- [Web search tool](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/web-search)
- [Code interpreter tool](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/code-interpreter)
- [File search tool](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/file-search)
- [Tool authentication](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/tool-authentication)
- [Tool best practices](https://learn.microsoft.com/azure/foundry/agents/concepts/tool-best-practice)
- [Tool catalog](https://learn.microsoft.com/azure/foundry/agents/concepts/tool-catalog)
- [Vector stores concept](https://learn.microsoft.com/azure/foundry/agents/concepts/vector-stores)

### State: conversation, memory, and workflow

- [Memory concept](https://learn.microsoft.com/azure/foundry/agents/concepts/what-is-memory)
- [Memory usage how-to](https://learn.microsoft.com/azure/foundry/agents/how-to/memory-usage)
- [Memory quickstart](https://learn.microsoft.com/azure/foundry/agents/quickstarts/quickstart-memory-hosted-agent)
- [Workflow concept](https://learn.microsoft.com/azure/foundry/agents/concepts/workflow)
- [Isolate sessions per user](https://learn.microsoft.com/azure/foundry/agents/how-to/isolate-sessions-per-user)

### Local frameworks and orchestration

- [Framework hosted agents](https://learn.microsoft.com/azure/foundry/how-to/develop/framework-hosted-agents)
- [LangChain agents how-to](https://learn.microsoft.com/azure/foundry/how-to/develop/langchain-agents)
- [LangChain integration](https://learn.microsoft.com/azure/foundry/how-to/develop/langchain)
- [LangChain traces](https://learn.microsoft.com/azure/foundry/how-to/develop/langchain-traces)
- [Retrieval-augmented generation concept](https://learn.microsoft.com/azure/foundry/concepts/retrieval-augmented-generation)
- [Agent-to-agent tools](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/agent-to-agent)
- [A2A authentication](https://learn.microsoft.com/azure/foundry/agents/concepts/agent-to-agent-authentication)

### Evaluation and observability

- [Agent evaluators concept](https://learn.microsoft.com/azure/foundry/concepts/evaluation-evaluators/agent-evaluators)
- [Task adherence concept](https://learn.microsoft.com/azure/ai-services/content-safety/concepts/task-adherence)
- [Cloud evaluation how-to](https://learn.microsoft.com/azure/foundry/how-to/develop/cloud-evaluation)
- [Evaluate agent how-to](https://learn.microsoft.com/azure/foundry/observability/how-to/evaluate-agent)
- [RAG evaluators](https://learn.microsoft.com/azure/foundry/concepts/evaluation-evaluators/rag-evaluators)
- [Risk and safety evaluators](https://learn.microsoft.com/azure/foundry/concepts/evaluation-evaluators/risk-safety-evaluators)
- [Trace agent setup](https://learn.microsoft.com/azure/foundry/observability/how-to/trace-agent-setup)
- [Client-side tracing](https://learn.microsoft.com/azure/foundry/observability/how-to/trace-agent-client-side)
- [Framework tracing how-to](https://learn.microsoft.com/azure/foundry/observability/how-to/trace-agent-framework)
- [Sensitive content in traces](https://learn.microsoft.com/azure/foundry/observability/how-to/traces-sensitive-content)
- [Observability concept](https://learn.microsoft.com/azure/foundry/concepts/observability)
- [Trace data concept](https://learn.microsoft.com/azure/foundry/observability/concepts/trace-data)

### Governed external tools

- [MCP tools how-to](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/model-context-protocol)
- [MCP authentication](https://learn.microsoft.com/azure/foundry/agents/how-to/mcp-authentication)
- [Toolbox overview](https://learn.microsoft.com/azure/foundry/agents/concepts/toolbox-overview)
- [Toolbox how-to](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/toolbox)
- [Toolbox quickstart](https://learn.microsoft.com/azure/foundry/agents/quickstarts/quickstart-toolbox-agent)
- [Tool authentication](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/tool-authentication)
- [Tool Search](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/tool-search)
- [Tool catalog](https://learn.microsoft.com/azure/foundry/agents/concepts/tool-catalog)
- [Agent Framework Responses quickstart](https://learn.microsoft.com/azure/foundry/agents/quickstarts/responses-api)
- [Azure AI Search tool](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/ai-search)
- [AI Search agentic retrieval index](https://learn.microsoft.com/azure/search/agentic-retrieval-how-to-create-index)

### Hosted agent delivery

- [Hosted agents concept](https://learn.microsoft.com/azure/foundry/agents/concepts/hosted-agents)
- [Hosted-agent contract](https://learn.microsoft.com/azure/foundry/agents/concepts/hosted-agent-contract)
- [Hosted-agent permissions](https://learn.microsoft.com/azure/foundry/agents/concepts/hosted-agent-permissions)
- [Hosted-agent quickstart](https://learn.microsoft.com/azure/foundry/agents/quickstarts/quickstart-hosted-agent)
- [Deploy hosted agent](https://learn.microsoft.com/azure/foundry/agents/how-to/deploy-hosted-agent)
- [Hosted-agent code deployment](https://learn.microsoft.com/azure/foundry/agents/how-to/deploy-hosted-agent-code)
- [Hosted-agent CI/CD quickstart](https://learn.microsoft.com/azure/foundry/agents/quickstarts/set-up-cicd-hosted-agent)
- [Hosted-agent telemetry](https://learn.microsoft.com/azure/foundry/agents/how-to/configure-hosted-agent-telemetry)

### Structured outputs and webhooks

- [Structured outputs how-to](https://learn.microsoft.com/azure/foundry/openai/how-to/structured-outputs)
- [JSON mode how-to](https://learn.microsoft.com/azure/foundry/openai/how-to/json-mode)
- [Webhooks how-to](https://learn.microsoft.com/azure/foundry/openai/how-to/webhooks)
- [Enable A2A endpoint](https://learn.microsoft.com/azure/foundry/agents/how-to/enable-agent-to-agent-endpoint)
- [Development lifecycle](https://learn.microsoft.com/azure/foundry/agents/concepts/development-lifecycle)

### Azure OpenAI how-to (advanced)

- [Embeddings](https://learn.microsoft.com/azure/foundry/openai/how-to/embeddings)
- [Function calling](https://learn.microsoft.com/azure/foundry/openai/how-to/function-calling)
- [JSON mode](https://learn.microsoft.com/azure/foundry/openai/how-to/json-mode)
- [Predicted outputs](https://learn.microsoft.com/azure/foundry/openai/how-to/predicted-outputs)
- [Prompt caching](https://learn.microsoft.com/azure/foundry/openai/how-to/prompt-caching)
- [Latency](https://learn.microsoft.com/azure/foundry/openai/how-to/latency)
- [Deep research](https://learn.microsoft.com/azure/foundry/openai/how-to/deep-research)
- [Codex](https://learn.microsoft.com/azure/foundry/openai/how-to/codex)
- [ChatGPT](https://learn.microsoft.com/azure/foundry/openai/how-to/chatgpt)
- [Realtime audio](https://learn.microsoft.com/azure/foundry/openai/how-to/realtime-audio)
- [Model router for agents](https://learn.microsoft.com/azure/foundry/openai/how-to/model-router-agents)

### Azure OpenAI concepts (prompt + safety)

- [Prompt engineering](https://learn.microsoft.com/azure/foundry/openai/concepts/prompt-engineering)
- [Advanced prompt engineering](https://learn.microsoft.com/azure/foundry/openai/concepts/advanced-prompt-engineering)
- [System message](https://learn.microsoft.com/azure/foundry/openai/concepts/system-message)
- [Safety system-message templates](https://learn.microsoft.com/azure/foundry/openai/concepts/safety-system-message-templates)
- [Red teaming](https://learn.microsoft.com/azure/foundry/openai/concepts/red-teaming)
- [Abuse monitoring](https://learn.microsoft.com/azure/foundry/openai/concepts/abuse-monitoring)
- [Content streaming](https://learn.microsoft.com/azure/foundry/openai/concepts/content-streaming)
- [Prompt transformation](https://learn.microsoft.com/azure/foundry/openai/concepts/prompt-transformation)
- [Model retirements](https://learn.microsoft.com/azure/foundry/openai/concepts/model-retirements)
- [Model retirement schedule](https://learn.microsoft.com/azure/foundry/openai/concepts/model-retirement-schedule)
- [Retired models](https://learn.microsoft.com/azure/foundry/openai/concepts/retired-models)

### LangChain deep dives

- [LangChain hosted agents](https://learn.microsoft.com/azure/foundry/how-to/develop/langchain-hosted-agents)
- [LangChain memory](https://learn.microsoft.com/azure/foundry/how-to/develop/langchain-memory)
- [LangChain middleware](https://learn.microsoft.com/azure/foundry/how-to/develop/langchain-middleware)
- [LangChain models](https://learn.microsoft.com/azure/foundry/how-to/develop/langchain-models)
- [LangChain Toolbox](https://learn.microsoft.com/azure/foundry/how-to/develop/langchain-toolbox)

### Foundry dev tooling

- [Get started with projects in VS Code](https://learn.microsoft.com/azure/foundry/how-to/develop/get-started-projects-vs-code)
- [Install CLI + SDK](https://learn.microsoft.com/azure/foundry/how-to/develop/install-cli-sdk)
- [AI template get started](https://learn.microsoft.com/azure/foundry/how-to/develop/ai-template-get-started)
- [Evaluate admin connected models](https://learn.microsoft.com/azure/foundry/how-to/develop/evaluate-admin-connected-models)

### Repository assets

- [OpenAPI Function backend](azure_functions_orders/README.md)
- [MCP Function server](northwind_mcp/README.md)
- [Workflow preview assets](workflows/README.md)
- [Responses hosted-agent sample](hosted_agent_responses/README.md)
- [Domain 1 planning guide](../01-plan-and-manage/README.md)
- [Domain 5 retrieval guide](../05-information-extraction/README.md)
