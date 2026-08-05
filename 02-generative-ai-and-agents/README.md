---
ai-usage: ai-assisted
---

# Domain 2: Implement generative AI and agentic solutions

> Detailed study guide plus runnable labs for Azure OpenAI-compatible Responses,
> Foundry prompt and hosted agents, tools, memory, workflow migration,
> evaluation, observability, production RAG, and LangChain/LangGraph integration.
>
> Run every numbered lesson from repository root:
>
> ```bash
> uv run python 02-generative-ai-and-agents/<lesson>.py
> ```
>
> Code proves one narrow path. It is not a production deployment, authorization
> design, data-retention policy, or evaluation result.

## Learning outcomes

After this domain, you should be able to:

- choose direct Responses, a project client, a prompt agent, or a hosted agent;
- keep endpoint, SDK, Entra role, and deployment-name boundaries straight;
- distinguish model-selected tool calls from application-authorized actions;
- design retrieval, memory, conversation state, and graph state deliberately;
- recognize preview surfaces and plan migration before depending on them;
- evaluate traces rather than treating a single good answer as evidence;
- trace, deploy, secure, operate, and clean up an agentic workload.

## Lesson map

Run the lessons in order unless a row says otherwise. Lessons marked
**read-only** make no Azure request with their default command. `--apply`
always means that the command can create, invoke, upload, or delete cloud
assets; read its lesson before using that switch.

| Stage | Lessons | Outcome | Default side effect |
|---|---|---|---|
| Direct model baseline | 01–03 | Call a deployment, tune sampling, and use a reasoning deployment. | Model tokens. |
| Managed Responses tools | 04–07 | Use web search, code interpreter, file search, and strict JSON. | 04–05 and 07 use model/tools; 06 creates then cleans its files and vector store. |
| Prompt agents and state | 08–16 | Create versions, execute tools safely, use conversations/memory, and inspect workflow migration. | Agent versions and model/tool requests; memory/workflow preview state where used. |
| Orchestration and local frameworks | 17–22 | Compare local framework, router, evaluation, tracing, LangChain, and graph RAG paths. | Model/evaluator calls; optional telemetry export. |
| Governed external tools | 23–25 | Connect MCP, publish a Toolbox, and use Azure AI Search safely. | **Read-only** until `--apply`; 23/25 create temporary agent versions, 24 persists a Toolbox version. |
| Hosted agent delivery | 26–28 | Validate a Responses hosted-agent contract, keep A2A separate, and inspect OIDC delivery. | 26–28 are local/read-only; contained deployment uses explicit `--apply`. |
| Cloud quality and operations | 29–30 | Create a durable cloud evaluation run deliberately and check production telemetry/RAG prerequisites. | 29 is **read-only** until `--apply`; 30 is **read-only**. |

There are **30 numbered lessons**. The contained
[`hosted_agent_responses/`](hosted_agent_responses/README.md) project is part
of lessons 26–28, not a 31st lesson.

## Mental model

An LLM call predicts useful next content.
An agentic application adds state, tools, policy, and an execution loop.
Those layers have separate failure modes and owners.

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

A model can request a tool.
A model cannot safely be trusted to authorize a tool.
The application validates arguments, checks caller authority, performs the
least-privileged action, returns a bounded result, and records the decision.

## Service and endpoint map

### Resource, project, deployment, endpoint

| Term | Meaning | Do not confuse it with |
|---|---|---|
| **Foundry resource** | Azure resource holding account-level configuration, model deployments, access, and quota context. | A project or a callable model. |
| **Foundry project** | Workspace under a Foundry resource for project APIs, agents, connections, and collaboration. | Direct Azure OpenAI endpoint. |
| **Model family** | Capability/version label, such as `gpt-4.1-mini`. | A deployment name. |
| **Deployment** | Named configured instance of a model. | A model family label or endpoint. |
| **Direct client** | OpenAI SDK client that calls Azure OpenAI-compatible APIs. | `AIProjectClient`. |
| **Project client** | `AIProjectClient` for project and prompt-agent APIs. | Direct OpenAI SDK client. |
| **Hosted agent** | Deployed managed runtime with packaging, identity, ingress, deployment, and lifecycle. | Local `AgentFramework` process. |

| Surface | Setting | URL shape | This repository uses it for | Starting access concern |
|---|---|---|---|---|
| Direct Azure OpenAI-compatible data plane | `AZURE_OPENAI_ENDPOINT` | `https://<resource>.openai.azure.com` | Lessons 01–07, 19–22 direct clients. | Direct Azure OpenAI data action on matching resource. |
| Foundry project API | `PROJECT_ENDPOINT` | `https://<resource>.services.ai.azure.com/api/projects/<project>` | Lessons 08–18 agent/project APIs. | Foundry project access on matching project/resource. |
| Foundry account helper | `FOUNDRY_ENDPOINT` | `https://<resource>.services.ai.azure.com` | Shared configuration; not substituted into direct OpenAI client. | Depends on operation. |
| Application Insights | `APPLICATIONINSIGHTS_CONNECTION_STRING` | Connection string, not an inference endpoint. | Optional lesson 21 export. | Telemetry write/access and data governance. |

`_shared/openai_client.py` deliberately constructs
`<AZURE_OPENAI_ENDPOINT>/openai/v1`.
`_shared/foundry_client.py` deliberately constructs `AIProjectClient` with
`PROJECT_ENDPOINT`.
Do not replace either URL with the other because both contain the same resource
name.
Endpoint selection determines SDK route, API contract, and RBAC expectation.

### Authentication model

All numbered Python lessons use `DefaultAzureCredential`.
On a workstation, `az login` commonly supplies Azure CLI credentials.
In Azure, use a managed identity or workload identity.
A successful credential chain only proves some credential obtained a token.
It does not prove it has right role at right scope for called endpoint.

```bash
az login
uv sync
cp .env.example .env
```

Use deployment **names** in `DEFAULT_MODEL`, `REASONING_MODEL`, and
`EMBEDDING_MODEL`.
Do not put a model-family name there unless deployment has same name.
Do not commit `.env`, access tokens, API keys, connection strings, customer
content, or production tool outputs.

### Minimum environment contract

```dotenv
FOUNDRY_ENDPOINT=https://<resource>.services.ai.azure.com
PROJECT_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<project>
AZURE_OPENAI_ENDPOINT=https://<resource>.openai.azure.com
DEFAULT_MODEL=<chat-deployment-name>
REASONING_MODEL=<reasoning-deployment-name>
EMBEDDING_MODEL=<embedding-deployment-name>
ORDERS_FN_ENDPOINT=https://<reachable-function-app>
APPLICATIONINSIGHTS_CONNECTION_STRING=<optional-connection-string>

# Lessons 23–25: existing project connections and Search index
NORTHWIND_MCP_ENDPOINT=https://<app>.azurewebsites.net/runtime/webhooks/mcp
NORTHWIND_MCP_CONNECTION=<project-connection-id>
SEARCH_CONNECTION_NAME=<foundry-project-connection-name>
SEARCH_ENDPOINT=https://<search-service>.search.windows.net
SEARCH_INDEX=<vector-capable-index-name>

# Lesson 29: durable cloud evaluation target
AZURE_AI_PROJECT_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<project>
AZURE_AI_MODEL_DEPLOYMENT_NAME=<evaluation-target-or-judge-deployment>
```

`ORDERS_FN_ENDPOINT` has no `/api` suffix.
Lesson 12 appends `/api` while replacing OpenAPI `servers`.
`APPLICATIONINSIGHTS_CONNECTION_STRING` is optional.
Lesson 21 still runs without it but emits no Azure Monitor tracer spans.
Lessons 23–25 read project connection identifiers rather than connection
secrets. Lesson 29 uses `AZURE_AI_PROJECT_ENDPOINT` deliberately so an
evaluation target can differ from the general lesson project; set it to the
same `PROJECT_ENDPOINT` only when that is intentional.

### Create and configure resources

Use portal, CLI, or infrastructure as code (IaC) for different work:

| Method | Best use | Strength | Boundary |
|---|---|---|---|
| Foundry portal | Explore supported model/region combinations and inspect runs. | Fast discovery and visual diagnostics. | Record every production setting elsewhere; manual clicks drift. |
| Azure CLI / `azd` | Local setup, scripted deployment, hosted-agent inner loop, and CI invocation. | Repeatable command history and OIDC-friendly automation. | Validate subscription, active project, and command preview before mutation. |
| Bicep/Terraform/IaC pipeline | Resource groups, networking, private endpoints, RBAC, tags, and production promotion. | Reviewable, idempotent infrastructure and policy. | Model/tool/runtime data-plane setup still needs supported API or deployment automation. |

Create a nonproduction Foundry resource and project in a supported region,
then deploy chat, reasoning, and embedding models by deployment **name**.
Check quota and model availability before committing a region or capacity.
Use a separate Azure AI Search service/index and Function App when lessons
need them. The lessons do not provision those durable dependencies for you.

Use Microsoft Entra ID and managed or workload identities in deployed
workloads. Store exceptional API keys, connection secrets, and third-party
credentials in a project connection or Key Vault-backed connection, never in
`.env`, source, tool descriptions, or trace attributes. A Foundry connection
resolves a secret at runtime; it is not permission to use its target. Grant
the runtime identity only the data actions required by its endpoint and tool.

For private networking, create private endpoints and private DNS for each
resource independently: Foundry/Azure OpenAI, Azure AI Search, Storage, Key
Vault, Container Registry, Application Insights ingestion/query paths, and
private tool backends. Then test DNS plus ingress and egress **from the real
runner or hosted-agent network**, not only from a developer laptop. A private
endpoint does not grant RBAC, and RBAC does not create network reachability.

## Safe order and prerequisite decision tree

### Resource prerequisites

1. Complete root repository setup with `uv sync`.
2. Create/select nonproduction Foundry resource and project.
3. Deploy compatible chat model and record deployment name.
4. Deploy reasoning model before lesson 03.
5. Deploy embedding model before lesson 14 or 22.
6. Sign in with `az login` and verify endpoint-specific RBAC.
7. Fill `.env` with endpoint shapes above.
8. Start with low-cost development inputs and non-sensitive sample data.

### Run order

| Stage | Run | Why |
|---|---|---|
| Direct baseline | 01, 02, 03 | Validate direct client, behavior control, reasoning deployment. |
| Managed tools | 04, 05, 06, 07 | Learn service-executed tools and structured contract. |
| Prompt-agent basics | 08 then 09, then 10–13 | Create definition before name-only invocation; learn state and external tools. |
| Durable/preview state | 14, then 15 and 16 | Memory needs embedding model; workflow lesson 16 needs lesson 15 intake agent. |
| Orchestration/evaluation | 17, 18, 19 | Separate local framework, router pattern, and evaluator semantics. |
| Framework paths | 20, 21, 22 | Learn OpenAI-compatible endpoint behavior, metadata-only tracing, and local graph retrieval. |
| External tool boundaries | 23, 24, 25 | Run no-cloud preflights, then connect only reviewed MCP, Toolbox, and Search dependencies. |
| Hosted deployment | 26, 27, 28 | Validate Responses runtime contract, A2A boundary, and OIDC CI/CD before deployment. |
| Cloud operations | 29, 30 | Validate JSONL and lifecycle before a persistent evaluation run; check telemetry/Search readiness locally. |

### Choose a runtime

```text
Need one generated response and application owns all state/tools?
  Yes -> Direct Responses API.
  No  -> Need stored Foundry agent definition/version and Foundry tools?
           Yes -> Prompt Agent through project endpoint.
           No  -> Need local Python orchestration / framework portability?
                    Yes -> Agent Framework, LangChain, or LangGraph locally.
                    No  -> Need managed long-running deployed runtime?
                             Yes -> package and deploy a hosted agent.
                             No  -> start with direct Responses API.
```

Use a prompt agent when Foundry owns a stored, versioned definition and
service-managed tools. Use a hosted agent when Foundry must run your packaged
application and expose a managed endpoint. Use direct Responses when your
application owns tool execution and state. Do not select a runtime because its
name contains "agent"; select it for the state, protocol, identity, network,
and lifecycle boundary that you need.

Local framework code is not a hosted deployment.
A registered prompt agent is not automatically a hosted runtime.
A visual workflow is not a substitute for production deployment lifecycle.

## Glossary

| Term | Study definition |
|---|---|
| **Responses API** | Unified response-generation API that can emit messages and tool calls. |
| **Prompt agent** | Foundry stored, versioned definition containing model, instructions, and tools. |
| **Agent reference** | Request body reference selecting agent name and optional version. |
| **Conversation** | Server-managed turn history identified by `conversation.id`. |
| **Function tool** | Schema advertised to model; application executes requested call. |
| **Built-in tool** | Tool executed by service, such as web search, code interpreter, or file search. |
| **OpenAPI tool** | Service-created callable operations from an OpenAPI contract and reachable backend. |
| **MCP** | Model Context Protocol: protocol for discovering/invoking tools through an MCP server. |
| **Toolbox** | Foundry-managed reusable collection/catalogue of tools and connections; not MCP protocol. |
| **A2A** | Agent-to-agent protocol/integration for communicating with an external agent; not a generic function call. |
| **RAG** | Retrieval-augmented generation: retrieve evidence, then generate grounded answer. |
| **Vector store** | Indexed chunks plus embeddings for similarity retrieval. |
| **Embedding** | Numeric representation used for semantic comparison, not a chat response. |
| **Memory** | Managed preview long-term memory extraction/retrieval, scoped by identity/context. |
| **Workflow** | Preview visual/YAML orchestration asset; retirement is scheduled December 1, 2026. |
| **Graph state** | Explicit application-controlled state passed between LangGraph nodes. |
| **Trace** | Structured execution record containing spans, timing, attributes, and possibly content. |
| **Evaluation** | Repeatable scoring over defined inputs/outputs/traces; not a single model answer. |
| **Grounding** | Answer claims supported by retrieved/tool evidence. |
| **Human approval** | Explicit authorization checkpoint before consequential side effect. |

## Tool catalog and contracts

### Tool-selection decision table

| Need | Start with | Lifecycle owner | Key limit |
|---|---|---|---|
| Fresh public information | Web search | Managed service | Cite results; obey data/citation policy. |
| Calculation/data analysis | Code interpreter | Managed sandbox | Treat generated code/output as untrusted result. |
| Small uploaded corpus | File search | Managed vector store | Upload/index lifecycle and retrieval quality still matter. |
| Existing Python/application action | Function tool | Application | Model requests; app authorizes and executes. |
| Existing HTTP API | OpenAPI tool | Agent service plus backend | Backend must be deployed/reachable and authentication aligned. |
| Reusable protocol tool server | Remote MCP | MCP server/operator | Remote endpoint, auth, tool trust, and network policy matter. |
| Reusable governed Foundry tools | Toolbox/tool catalog | Foundry/project operator | Product surface distinct from MCP and app functions. |
| Delegate to another agent | A2A or explicit agent-as-tool pattern | Agent/operator | Identity, task boundary, and delegated authority need design. |
| Deterministic local routing | Application code/LangGraph edge | Application | Do not pretend probabilistic model routing is deterministic. |

### Function-calling lifecycle

```text
1. Define narrow JSON Schema: tool name, description, allowed fields, types.
2. Model emits zero, one, or many `function_call` items with `call_id`.
3. Application looks up only allowlisted tool name.
4. Application parses JSON and rejects malformed/non-object arguments.
5. Application rejects unexpected keys, missing required keys, and wrong types.
6. Application checks caller identity, tenant scope, authorization, and business rules.
7. Application executes bounded least-privileged operation or returns safe error.
8. Application sends `function_call_output` with original `call_id`.
9. Model receives result and may request another tool or produce final message.
10. Application stops at bounded round count and logs decisions safely.
```

Lessons 09, 11, and 18 implement this pattern.
They preserve the exact `call_id`.
They process every emitted function call in each response.
They return structured errors rather than crash on bad arguments.
They cap iterations at `MAX_TOOL_ROUNDS = 8`.

`strict=True` constrains tool arguments to supplied schema.
It does not authorize action.
It does not authenticate user.
It does not validate semantic/business constraints.
It does not make returned tool data true.

### Tool-security checklist

- Allowlist tool names; never dynamically import/execute model-selected names.
- Parse JSON; require object shape; reject unknown fields by default.
- Validate ranges, formats, ownership, tenant, and resource identifiers.
- Re-authorize against authenticated caller, not model-provided identity fields.
- Separate read from write/delete/pay/send tools.
- Require explicit confirmation/human approval before consequential actions.
- Use short-lived scoped credentials; never expose secrets in tool schema/result.
- Bound time, retries, result size, pagination, and tool rounds.
- Treat retrieved web/document/API text as untrusted indirect prompt input.
- Return minimal error detail; log correlation IDs without secrets or sensitive payloads.
- Test prompt injection and confused-deputy scenarios before enabling privileged tools.
- Review tool traces and permissions after every schema or backend change.

### OpenAPI reachability and authentication

Lesson 12 starts from `azure_functions_orders/northwind_spec.json`.
It replaces its intentionally invalid server with
`$ORDERS_FN_ENDPOINT/api` at runtime.
The local Azure Function is useful only for local contract testing:

```bash
cd 02-generative-ai-and-agents/azure_functions_orders
cp local.settings.json.example local.settings.json
func start
curl http://localhost:7071/api/orders
curl http://localhost:7071/api/orders/1002
```

Foundry Agent Service cannot reach laptop `localhost`, `127.0.0.1`, or `::1`.
Deploy backend, expose route to Agent Service, then set endpoint without `/api`:

```bash
func azure functionapp publish <your-function-app-name>
# .env
ORDERS_FN_ENDPOINT=https://<your-function-app>.azurewebsites.net
```

Lesson 12 uses `OpenApiAnonymousAuthDetails()` only for static demo orders.
Its deployed backend remains anonymous unless you change Function configuration.
Production path: protect API with API key or Microsoft Entra authentication,
select matching OpenAPI tool auth details, grant minimum backend access, and
verify agent service network egress/ingress and DNS before registering tool.
Do not claim production auth exists because sample OpenAPI schema contains
operations.

### MCP, Toolbox, and A2A distinctions

`northwind_mcp/` is independent of numbered lessons.
It exposes Azure Functions MCP triggers at `/runtime/webhooks/mcp`.
It is not automatically attached by lesson 12 and is not the OpenAPI backend.
Use local MCP endpoint only with local MCP client:

```bash
cd 02-generative-ai-and-agents/northwind_mcp
cp local.settings.json.example local.settings.json
pip install -r requirements.txt
func start
```

A remote Foundry connection needs deployed reachable endpoint:
`https://<app>.azurewebsites.net/runtime/webhooks/mcp`.
Configure Function keys or Entra authentication before non-demo use and align
connection authentication with server expectation.

MCP standardizes tool-server interaction.
Toolbox organizes managed reusable tools in Foundry.
A2A sends work to another agent and introduces delegated-agent identity/task
boundaries.
Function calling is an application-controlled request/response loop.
They can coexist but are not interchangeable labels.

## State and RAG paths

### State decision tree

```text
Need previous turns only inside one interaction?
  Yes -> conversation ID; test isolation and retention.
  No  -> Need durable user preference/fact recall across conversations?
           Yes -> preview Foundry Memory with explicit user scope and consent.
           No  -> Need deterministic workflow data/state transitions?
                    Yes -> application/graph state or database.
                    No  -> stateless Responses call.
```

Conversation state preserves interaction context.
It does not prove durable user profile memory.
Memory recalls extracted/retrieved information probabilistically.
It does not replace source-of-truth customer system or authorization database.
Graph state is explicit program state controlled by application.
Do not store secrets, credentials, payment data, or sensitive precise location
in prompts, vector stores, memory, trace attributes, or tool results.

### RAG choices

| Path | Lessons | Storage/index | Good for | Limits |
|---|---:|---|---|---|
| Managed file search | 06 | Managed uploaded files/vector store | Fast learning path, small corpus. | Creates cloud files/vector state; retrieval needs evaluation. |
| Foundry Memory | 14 | Preview memory store | Scoped durable preference recall. | Async/debounced extraction; not immediate or guaranteed recall. |
| Local FAISS | 22 | In-process index from PDFs | Graph/RAG learning. | Rebuilds every run; no production durability, ACL, or governance. |
| Azure AI Search | Domain 5 | Search service index | Production retrieval path. | Requires ingestion, schema, ACL, monitoring, and evaluation. |

For any RAG path:

1. define authoritative source and update/deletion process;
2. chunk with source metadata and evaluate retrieval before generation;
3. apply identity/tenant/document ACL before returning chunks;
4. pass bounded evidence, not entire corpus, to model;
5. require citation/uncertainty behavior when evidence is absent;
6. evaluate answer quality, groundedness, retrieval quality, and safety;
7. monitor drift, stale content, zero-hit rate, and cost.

## Preview and lifecycle boundaries

| Area | Current lesson contract | Planning consequence |
|---|---|---|
| Foundry Memory | Preview; `project.beta.memory_stores`, `MemorySearchPreviewTool`, scoped `{{$userId}}`, and `x-memory-user-id`. | Pin/test SDK behavior, design fallback/source of truth, avoid relying on immediate recall. |
| Workflows | Preview and retire December 1, 2026. | Do not begin new long-lived solution on visual workflow alone; migrate orchestration to Agent Framework/hosted agent path. |
| Agent evaluators | Preview evaluator SDK surface. | Treat output scores as measurements needing dataset, thresholds, review, and regression policy. |
| Hosted agents | Separate deployment product/lifecycle. | Local Agent Framework code needs packaging, deployment, identity, ingress, monitoring, and release process. |

Lesson 14 creates/fetches a named store, versioned agent, and two conversations.
It scopes memory through `x-memory-user-id: user-sarah-chen`.
It waits 65 seconds after first conversation because updates are asynchronous
and debounced.
Wait is demonstration, not delivery guarantee.
The answer must never claim a preference absent from retrieved memory.

Lessons 15–16 retain YAML as study artifact.
`wf_triage.yml` routes `policy_question` to Knowledge agent and other input to
Ticket agent after intake output stored as `Local.Triage`.
Lesson 16 uploads preview workflow definition and tells you to test portal
playground while preview remains.
It does not prove a hosted-agent deployment or production scheduler.

## Lesson-by-lesson guide

### How to read each walkthrough

For lessons 01–22, **Question** gives what problem is solved, **Concepts**
gives why/architecture vocabulary, **What code proves** traces code path,
**Limitations** states where not to use sample, and **Check** names expected
output or verification, pitfall, and best next practice. The run-order table
states cross-lesson dependencies and resource prerequisites. Lessons 23–30
use explicit **What and why**, **Prerequisites**, **Architecture**, **Output**,
**Use and do not use**, **Pitfalls**, and **Key takeaway** labels because they
cross deployment, network, and durable-data boundaries.

### 01 — First Responses API call

**Question:** Can direct Azure OpenAI-compatible Responses call deployed chat model?

Run:

```bash
uv run python 02-generative-ai-and-agents/01_first_api_call.py
```

**Concepts:** `OpenAI` client, `DefaultAzureCredential`, deployment name,
`responses.create`, `response.output_text`.

**What code proves:** Direct client from `_shared/openai_client.py` sends one
prompt through `AZURE_OPENAI_ENDPOINT/openai/v1`.

**Limitations:** It does not create a Foundry agent, test project endpoint, or
prove tool, evaluation, throughput, or production authorization behavior.

**Check:** A printed answer proves direct endpoint, credential, and deployment
work together for this simple request.

### 02 — Model behavior

**Question:** How does temperature alter sampling behavior?

Run:

```bash
uv run python 02-generative-ai-and-agents/02_model_behavior.py
```

**Concepts:** temperature, output variability, prompt invariance, deployment
configuration versus request parameters.

**What code proves:** Same prompt runs with `0.0`, `1.0`, and `2.0`.

**Limitations:** Temperature is not a truth, safety, grounding, determinism,
or quality guarantee. Exact support/range remains model/API dependent.

**Check:** Compare patterns across repeated runs; do not choose value by one
example.

### 03 — Reasoning

**Question:** How is a reasoning-tier request configured?

Run:

```bash
uv run python 02-generative-ai-and-agents/03_reasoning.py
```

**Concepts:** separate `REASONING_MODEL`, `reasoning={"effort": "high"}`,
reasoning cost/latency trade-off.

**What code proves:** Direct Responses request asks configured reasoning
deployment to analyze concurrency failure scenario.

**Limitations:** High effort is not proof of correctness. Reasoning models,
parameter support, price, and latency depend on deployment/model availability.

**Check:** Compare against representative problems and total latency/cost.

### 04 — Web search tool

**Question:** How can model obtain current public information?

Run:

```bash
uv run python 02-generative-ai-and-agents/04_web_search_tool.py
```

**Concepts:** built-in `web_search`, `tool_choice="auto"`, freshness,
citations, tool selection.

**What code proves:** Direct Responses call exposes managed web search and asks
for citations.

**Limitations:** `auto` can skip search. Search output can be incomplete,
wrong, malicious, or unfit for sensitive decisions. Validate citations and
follow source/data-use requirements.

**Check:** Use `tool_choice="required"` only to test invocation behavior, not
as a substitute for answer verification.

### 05 — Code interpreter

**Question:** When should model calculate rather than narrate calculation?

Run:

```bash
uv run python 02-generative-ai-and-agents/05_code_interpreter.py
```

**Concepts:** managed `code_interpreter`, auto container, generated code,
execution output, final answer.

**What code proves:** Response can contain `code_interpreter_call` items and
message item; lesson prints code and outputs.

**Limitations:** Sandbox execution does not make assumptions, data, or
conclusions correct. Never treat it as unrestricted production compute.

**Check:** Independently verify formula and input assumptions.

### 06 — File search tool

**Question:** What is smallest managed RAG path without Azure AI Search?

Run:

```bash
uv run python 02-generative-ai-and-agents/06_file_search_tool.py
```

**Concepts:** files API, `purpose="assistants"`, vector store, managed
chunking/embeddings/retrieval, file-search tool.

**What code proves:** Uploads each policy PDF, creates named vector store, and
requests answer with its ID.

**Limitations:** Every run can create files/vector-store state and charges.
No ACL, metadata filter, ingestion cleanup, citation validation, or retrieval
evaluation is implemented.

**Check:** Record IDs, test known-answer/zero-answer cases, then delete labs.

### 07 — Structured output

**Question:** How can extraction have machine-valid schema contract?

Run:

```bash
uv run python 02-generative-ai-and-agents/07_structured_output.py
```

**Concepts:** `text.format`, JSON Schema, schema name, `strict=True`,
`additionalProperties: false`, JSON parsing.

**What code proves:** Ticket extraction parses `response.output_text` into
entities/topics after strict schema response request.

**Limitations:** Schema conformance does not prove extraction accuracy or
business validity. Validate content, missing facts, and downstream constraints.

**Check:** Add representative adversarial/ambiguous tickets to evaluation set.

### 08 — Prompt-agent creation

**Question:** What does a versioned Foundry Prompt Agent definition contain?

Run:

```bash
uv run python 02-generative-ai-and-agents/08_prompt_agent_create.py
```

**Concepts:** project client, `PromptAgentDefinition`, instructions,
`FunctionTool`, strict parameter schemas, agent name/version.

**What code proves:** Creates version for `IT-HelpDesk-Agent` with three
function-tool schemas.

**Limitations:** Registering schema never runs local Python functions. Each
run creates a new version; lifecycle/cleanup matters.

**Check:** Save printed name/version and use lesson 09 to execute calls.

### 09 — Prompt-agent invocation and safe tool loop

**Question:** How does application execute prompt-agent requested functions?

Run:

```bash
uv run python 02-generative-ai-and-agents/09_prompt_agent_invoke.py
```

**Concepts:** agent reference, server conversation, `function_call`,
`function_call_output`, call ID, JSON validation, tool loop cap.

**What code proves:** It uses latest named agent version, validates allowed and
required parameters, executes local helpdesk functions, and continues response.

**Limitations:** Demo functions are not authorization system. Production must
bind caller identity/tenant and evaluate confidential result redaction.

**Check:** Inspect printed tool name/arguments; call ID must be returned
unchanged.

### 10 — Prompt agent with web search

**Question:** How is built-in tool persisted in agent definition?

Run:

```bash
uv run python 02-generative-ai-and-agents/10_agent_web_search.py
```

**Concepts:** `WebSearchTool`, stored versioned model/instructions/tools,
citations.

**What code proves:** Creates `web-search-lab-agent`; it does not invoke it.

**Limitations:** New version costs/lifecycle apply; tool availability/results
and citation requirements remain runtime/model dependent.

**Check:** This is definition evidence only, not a completed research answer.

### 11 — End-to-end function-tool agent

**Question:** What does entire model-tool-model cycle look like in one file?

Run:

```bash
uv run python 02-generative-ai-and-agents/11_agent_function_tools.py
```

**Concepts:** create version, pin agent version in reference, conversation,
multi-call iteration, safe local executor.

**What code proves:** Model can request password and Slack installation tools;
application validates each request and returns results before final answer.

**Limitations:** No durable idempotency key, per-user authorization, timeout,
rate limit, audit sink, or human approval exists.

**Check:** Treat tool description/schema as untrusted request interface and
apply production policy outside model.

### 12 — OpenAPI tool and Function backend

**Question:** How does Foundry turn reachable OpenAPI operations into tools?

Run:

```bash
uv run python 02-generative-ai-and-agents/12_agent_openapi_tools.py
```

**Concepts:** OpenAPI 3.0, operation IDs/descriptions, runtime server override,
remote reachability, OpenAPI anonymous auth demo.

**What code proves:** Agent definition discovers operations from spec, then
queries order `1002` through deployed backend.

**Limitations:** `func start` only validates local Function. Agent Service
cannot call localhost. Sample uses anonymous static data; no production auth is
implemented.

**Check:** Curl deployed URL from suitable network, validate auth, then run.

### 13 — Conversation thread

**Question:** How is multi-turn context retained without resending messages?

Run:

```bash
uv run python 02-generative-ai-and-agents/13_conversation_thread.py
```

**Concepts:** `conversations.create`, one ID, server-managed transcript,
agent-reference name, version creation.

**What code proves:** Second request in same conversation can resolve “it” to
order `#4521` from prior turn.

**Limitations:** Conversation context is not durable profile memory. Scope,
retention, user isolation, and deletion policy need explicit design.

**Check:** Use new conversation ID to verify blank-slate behavior.

### 14 — Foundry Memory preview

**Question:** How can preview memory recall a scoped preference across conversations?

Run:

```bash
uv run python 02-generative-ai-and-agents/14_foundry_memory.py
```

**Concepts:** beta memory store, chat/embedding deployment contract,
`MemorySearchPreviewTool`, `{{$userId}}`, `x-memory-user-id`, async update.

**What code proves:** Store definition uses configured chat and embedding
models; two new conversations use same explicit memory-user header.

**Limitations:** Preview API. Memory writes are asynchronous/debounced and
extraction/retrieval is not guaranteed after 65 seconds. It is not source of
truth or consent/PII solution.

**Check:** Verify same header/user scope, then test absent, stale, and deleted
preference behavior.

### 15 — Workflow intake prerequisite

**Question:** How does intake agent emit data required for conditional route?

Run:

```bash
uv run python 02-generative-ai-and-agents/15_workflow_intake.py
```

**Concepts:** schema file, strict JSON-schema response, versioned intake
agent, `policy_question` versus `service_issue`, `refund_related`.

**What code proves:** Creates `wf-IntakeAgent`, produces JSON matching
`workflows/wf_intake_schema.json`.

**Limitations:** Classification can be wrong even with valid JSON. It is
preview preparation, not workflow deployment.

**Check:** Run before lesson 16; include ambiguous tickets in evaluation.

### 16 — Conditional workflow preview

**Question:** What does preview YAML conditional routing describe?

Run:

```bash
uv run python 02-generative-ai-and-agents/16_workflow_conditional.py
```

**Concepts:** YAML artifact, leaf agents, workflow definition, agent existence
preflight, portal playground testing.

**What code proves:** Verifies intake agent, versions Knowledge/Ticket agents,
and creates/updates `wf-Triage` preview definition.

**Limitations:** Workflows retire December 1, 2026. SDK preview surface may
vary. This is not hosted-agent deployment, CI/CD workflow, or durable job run.

**Check:** Study YAML and plan equivalent Agent Framework/hosted-agent path.

### 17 — Local Agent Framework

**Question:** What does local Agent Framework use of Foundry model look like?

Run:

```bash
uv run python 02-generative-ai-and-agents/17_hosted_agent_framework.py
```

**Concepts:** `Agent`, `FoundryChatClient`, async `run`, project endpoint,
local process.

**What code proves:** Local Python process calls configured Foundry model with
Agent Framework instructions.

**Limitations:** Filename is historical teaching label only. Code does not
package, deploy, host, invoke, monitor, or grant identity to hosted agent.

**Check:** For hosted runtime, use local Foundry hosted-agent deployment docs
and implement deployment lifecycle separately.

### 18 — Multi-agent coordination

**Question:** How can router delegate to specialists through tool loop?

Run:

```bash
uv run python 02-generative-ai-and-agents/18_multi_agent_coord.py
```

**Concepts:** router, specialists, agent-as-tool application pattern, strict
single-question schema, error propagation, tool rounds.

**What code proves:** Router selects billing or technical function; executor
invokes named specialist through agent reference and returns response.

**Limitations:** This is not Foundry A2A protocol implementation. Model routing
is probabilistic; no escalation, authorization propagation, budgeting, or
specialist trust policy is implemented.

**Check:** Measure wrong-route, multi-intent, unavailable-specialist, and loop
cases before real delegation.

### 19 — Evaluator SDK

**Question:** What is a local evaluator call versus cloud evaluation run?

Run:

```bash
uv run python 02-generative-ai-and-agents/19_evaluator_task_adherence.py
```

**Concepts:** trace shape, `TaskAdherenceEvaluator`,
`ToolCallAccuracyEvaluator`, evaluator model config, score/reasoning.

**What code proves:** Builds complete redacted in-memory agent turn, including
tool call and matching tool result, then passes it to local SDK evaluators.
`azure-ai-evaluation` is already in root manifest.

**Limitations:** It does **not** create Foundry portal/cloud evaluation, upload
dataset, persist run, or guarantee meaningful score. One synthetic trace only
demonstrates evaluator input contract; it is not representative evidence.

**Check:** Build versioned representative dataset/traces, aggregate metrics,
set thresholds, inspect failures, and gate releases separately.

### 20 — LangChain agent

**Question:** How does LangChain reuse local tools with Azure OpenAI-compatible model?

Run:

```bash
uv run python 02-generative-ai-and-agents/20_langchain_agent.py
```

**Concepts:** `create_agent`, `@tool`, `ChatOpenAI`, bearer token provider,
OpenAI-compatible `/openai/v1` base URL.

**What code proves:** LangChain local tools answer order/inventory request;
chat model uses `AZURE_OPENAI_ENDPOINT`, not project endpoint.

**Limitations:** Tools use in-memory demo data. `token_provider()` returns a
token when model is built; production must account for credential refresh
behavior, retries, tracing, and authorization.

**Check:** Do not point `ChatOpenAI` at `PROJECT_ENDPOINT` or
`FOUNDRY_ENDPOINT` in this lesson contract.

### 21 — LangChain tracing

**Question:** How can LangChain calls export OpenTelemetry trace to Azure Monitor?

Run:

```bash
uv run python 02-generative-ai-and-agents/21_langchain_tracing.py
```

**Concepts:** `AzureAIOpenTelemetryTracer`, callbacks, agent ID, Application
Insights connection string, metadata-only content-recording default.

**What code proves:** Adds tracer only if environment setting exists; otherwise
runs and reports stdout-only destination. It passes
`enable_content_recording=False`.

**Limitations:** Content recording is disabled here. Enabling it can capture
sensitive prompts, tool arguments, and outputs. Configure retention, access,
redaction, sampling, and consent before production. Trace export is not
evaluator/cloud evaluation.

**Check:** Query Application Insights by printed agent ID after propagation;
never interpret missing trace as proof request did not run.

### 22 — LangGraph local RAG agent

**Question:** How do explicit graph state and tool loop create local RAG agent?

Run:

```bash
uv run python 02-generative-ai-and-agents/22_langgraph_agent.py
```

**Concepts:** `StateGraph`, `MessagesState`, `START`, `END`, conditional edge,
`ToolNode`, `FAISS`, PDF loader, chunking, embeddings, similarity search.

**What code proves:** Rebuilds local FAISS from policy PDFs per run, binds
search tool, loops model → tool → model while model requests tool.

**Limitations:** Both `ChatOpenAI` and `OpenAIEmbeddings` use
`AZURE_OPENAI_ENDPOINT/openai/v1`; embedding `model` is configured deployment
name. Index is ephemeral local demo with no ACL, persistence, update/delete,
evaluation, citations policy, or production retrieval service.

**Check:** Use Azure AI Search in Domain 5 for production retrieval design.

### 23 — MCP tool preflight and approval

**What and why:** MCP is a protocol for an agent to discover and invoke remote
tools. It reduces custom adapter work; it does not make a server, server
output, identity, or requested action trustworthy. This lesson makes that
boundary explicit before attaching independent
[`northwind_mcp/`](northwind_mcp/README.md) Azure Function server.

**Prerequisites and dependencies:** Deploy Function, expose
`https://<app>.azurewebsites.net/runtime/webhooks/mcp`, create matching Foundry
project connection, and set `NORTHWIND_MCP_ENDPOINT` and
`NORTHWIND_MCP_CONNECTION`. Endpoint must be HTTPS and reachable from Agent
Service; `localhost` only works with local MCP client. Use Function/Entra
authentication in real service. For private server, use supported private
networking, private DNS, dedicated MCP subnet, and test route from agent
network.

Run read-only preflight:

```bash
uv run python 02-generative-ai-and-agents/23_mcp_tool_preflight.py
```

Then, only after reviewing server owner, arguments, data boundary, auth,
region, retention, logging, and cost:

```bash
uv run python 02-generative-ai-and-agents/23_mcp_tool_preflight.py --apply
uv run python 02-generative-ai-and-agents/23_mcp_tool_preflight.py --apply --approve
```

**Architecture and code path:** `MCPTool` identifies remote endpoint and
project connection, restricts discovery to `get_order_status` and
`list_customer_orders`, and sets `require_approval="always"`. Prompt agent
requests tool; application prints each `mcp_approval_request`, allowlists its
name, and returns approval response only with `--approve`. `finally` deletes
temporary agent version.

**Output and use:** Default output says `No cloud calls made.` Applied output
shows approval decision, answer, and deletion message. Use for reviewed read
tools or UI-mediated approval checkpoint. Do not use `--approve` as unattended
authorization for writes, payments, personal data, or unassessed third-party
server. Preserve independent caller authorization at tool backend; project
connection authenticates service, not end user.

**Pitfalls and takeaway:** MCP differs from function tools (application
executes them), Toolbox (managed MCP-compatible catalog), and A2A (delegated
agent protocol). Tool description and output are untrusted input. Keep
allowlist, approval, least-privilege identity, timeout, result-size limit, and
audit correlation. **Key takeaway:** remote protocol integration is external
trust boundary, not permission grant.

### 24 — Toolbox and tool catalog preflight

**What and why:** Foundry Toolbox packages curated tool collection behind one
versioned MCP-compatible endpoint. It centralizes connection management,
governance, and discovery. Tool search helps when large catalog would otherwise
consume context and input tokens; it does not validate action or replace tool
authorization.

**Prerequisites and dependencies:** Need Foundry project, compatible
region/model support, and developer/agent identity with appropriate Foundry
access. Review each included connection's identity, RBAC scope, DPA, residency,
retention, telemetry, quota, and billing. Web search sends queries to public
service, so do not include secrets or customer data. Production consumers need
migration/version plan before toolbox version removal.

Run:

```bash
uv run python 02-generative-ai-and-agents/24_toolbox_tool_catalog_preflight.py
uv run python 02-generative-ai-and-agents/24_toolbox_tool_catalog_preflight.py --apply
# After verifying no consumer still selects this version:
uv run python 02-generative-ai-and-agents/24_toolbox_tool_catalog_preflight.py --apply --delete-version <version>
```

**Architecture and code path:** Default execution prints no-cloud plan.
`catalog_tools()` declares named public-web tool and
`ToolSearchToolboxTool`; `--apply` calls
`project.toolboxes.create_version()` for `northwind-tool-catalog-lab`.
Deletion calls `delete_version()` only with both `--apply` and explicit
version. Print output records created version and cleanup command.

**Use and do not use:** Use Toolbox when several agents/frameworks share
governed catalog and need versioned rollout. Use direct function tools for
small application-owned actions. Do not call Toolbox arbitrary MCP server: it
is Foundry-managed, but can expose MCP-compatible tools. Do not delete default
or referenced version without checking consumers, rollback, and compatibility.

**Best practice and takeaway:** Pin or promote tested versions, maintain tool
owners and data classifications, and make downstream tools independently
authorize callers. **Key takeaway:** catalog discovery saves context; it does
not turn selected tool into approved operation.

### 25 — Azure AI Search agent tool preflight

**What and why:** This is production-RAG direction: Agent Service queries
vector-capable Azure AI Search index through existing Foundry project
connection. It contrasts with lesson 06 managed file search and lesson 22
ephemeral local FAISS. Search supplies durable indexing and retrieval
operations; it does not make retrieved documents tenant-authorized.

**Prerequisites and dependencies:** Create Search service, index, ingestion
pipeline, retrievable source URL/content fields, embeddings, and Foundry
connection. Set `SEARCH_CONNECTION_NAME` and `SEARCH_INDEX`. For keyless
access, grant project managed identity **Search Index Data Contributor** and
**Search Service Contributor** as required by configuration; grant
developers/agent callers Foundry access separately. Private-network Search
uses identity-based access, private endpoint/DNS, and agent-to-Search
reachability. Do not use key-based Search path for private-network scenario.

Run:

```bash
uv run python 02-generative-ai-and-agents/25_agent_azure_ai_search_preflight.py
uv run python 02-generative-ai-and-agents/25_agent_azure_ai_search_preflight.py --apply
```

**Architecture and code path:** Preflight is local. With `--apply`, lesson
resolves named connection, builds `AzureAISearchTool` with
`VECTOR_SEMANTIC_HYBRID` and `top_k=3`, creates temporary prompt-agent
version, requires tool, prints URL citations, then deletes agent in `finally`.
It never creates or deletes Search service, index, documents, or connection.
Expected output is grounded answer/citation lines followed by temporary-agent
deletion.

**Use and do not use:** Use as bounded integration smoke test after retrieval
quality and ACL behavior are tested. Do not treat it as ingestion, security
trimming, citation validation, or RAG evaluation. Do not index data without
source ownership, retention/deletion workflow, sensitivity review, and
per-document or tenant filter design.

**Pitfalls and takeaway:** Retrieved content can contain indirect prompt
injection. Apply security trimming before retrieval, pass bounded excerpts,
require evidence/citations or uncertainty, and measure retrieval hit quality,
groundedness, latency, Search/model/embedding cost, and zero-result behavior.
**Key takeaway:** RAG is retrieval plus authorization, source lifecycle, and
evaluation—not vector query alone.

### 26 — Responses hosted-agent preflight

**What and why:** Hosted agent runs packaged application code under Foundry
Agent Service. This lesson validates contained source-deployment sample
[`hosted_agent_responses/`](hosted_agent_responses/README.md), not local
`AgentFramework` process. It uses Responses protocol for OpenAI-compatible
user/application requests.

**Prerequisites and dependencies:** Need Python 3.13+, `azd` 1.25.3+,
`azd auth login`, `azd ext install azure.ai.agents`, Foundry project, and model
deployment. Set non-secret azd environment values `FOUNDRY_PROJECT_ENDPOINT`
and `FOUNDRY_MODEL_NAME`; keep `.azure/` uncommitted. Deployment needs
appropriate project/control-plane roles. Platform creates agent identity;
assign it RBAC on external Storage, Search, or tool resources as needed. Use
project connections/Key Vault-backed connections for secrets.

Run local validation:

```bash
uv run python 02-generative-ai-and-agents/26_hosted_agent_responses.py
cd 02-generative-ai-and-agents/hosted_agent_responses
azd ai agent run
azd ai agent invoke --local "Give a one-line deployment status."
curl -sS http://localhost:8088/readiness
```

**Architecture and code path:** `azure.yaml` declares Linux amd64 remote
source build, Python 3.13, `protocol: responses` version 2.0.0, and 0.5
CPU/1 GiB container. `main.py` reads platform-injected
`FOUNDRY_PROJECT_ENDPOINT`, reads configured model name, and delegates HTTP
server, `GET /readiness`, `POST /responses`, SIGTERM, and formatting to
`ResponsesAgentServerHost`. Handler obtains request input, calls project
Responses client with `store=False`, then returns `TextResponse`.

**Output, use, and limits:** Expected preflight says adapter owns `:8088`,
`/readiness`, and SIGTERM. Use for managed conversational endpoint with
platform-managed conversation protocol. Do not expose it as A2A, hand-roll
adapter endpoints, redeclare `FOUNDRY_PROJECT_ENDPOINT`, or bundle
macOS/Windows/ARM wheels. Sample has no custom tools, network isolation,
approval flow, or production SLO policy.

**Best practice and takeaway:** Use `python deploy.py` to print plan; use
`--apply` only after testing and reviewing region, quota, capacity, image
build, network, identity, telemetry, and cost. **Key takeaway:** hosted agent
has runtime contract, deployment lifecycle, and identity beyond local agent
code.

### 27 — Hosted agent A2A boundary

**What and why:** Responses is user/application protocol at `POST /responses`.
A2A is separate preview agent-to-agent protocol with agent discovery, task
lifecycle, caller authentication, delegated authority, and data-sharing design.
This lesson prevents false protocol claim.

**Prerequisites and code path:** Run after lesson 26 source preflight:

```bash
uv run python 02-generative-ai-and-agents/27_hosted_agent_a2a.py
```

Wrapper calls `preflight.py --a2a`. It reads `azure.yaml`, verifies sample
does **not** declare `protocol: a2a`, and prints `POST /responses` is not A2A.
No Azure call, deployment, agent, or network connection occurs.

**When to use:** Use check when team wants to delegate to another agent but
has only Responses endpoint. To implement A2A, separately enable incoming A2A
on target, create A2A project connection with target base path and matching
authentication, select `A2APreviewTool`, and design caller/target
authorization, consent, tasks, timeout, audit, and fallback. Use Foundry
Agent Consumer or another least-privilege role for callers where appropriate;
target identity still needs its own resource RBAC.

**Do not use and takeaway:** Do not treat direct Responses invocation, lesson
18 application router, or MCP tool as A2A. Do not forward user credentials or
authority to specialist without explicit delegation policy. **Key takeaway:**
transport-compatible endpoint is not agent-delegation security model.

### 28 — Hosted-agent CI/CD reference

**What and why:** Delivery must reproduce build, identity, deployment, smoke
test, telemetry, and rollback conditions. Contained `hosted-agent-cd.yml` is
reference asset, not active repository workflow. It demonstrates GitHub OIDC
rather than long-lived client secret.

Run:

```bash
uv run python 02-generative-ai-and-agents/28_hosted_agent_cicd.py
cd 02-generative-ai-and-agents/hosted_agent_responses
python deploy.py             # plan only
python deploy.py --apply     # deploy only after environment review
```

**Architecture and code path:** Workflow uses `id-token: write`,
`Azure/setup-azd`, `azure/login` with repository variables, creates/configures
azd environment, runs local preflight, calls explicit deployment wrapper, then
invokes smoke prompt. Wrapper orders optional `azd provision` before
`azd deploy`, and never mutates without `--apply`. Expected lesson output
prints asset, dry-run, and deploy paths.

**Prerequisites and configuration:** Configure federated credential, client,
tenant, subscription, project endpoint, model deployment, project roles, and
existing azd environment. Keep values in identity/platform configuration, not
source. IaC should own resource group, network, private endpoints, DNS, ACR,
Key Vault, RBAC, tags, and monitoring connection. Pipeline must reach private
endpoints or use self-hosted/private runner with correct DNS.

**Pitfalls and takeaway:** OIDC login can succeed while deployment identity
lacks Foundry Project Manager/control-plane, ACR, or resource permissions.
Smoke test must exercise deployed endpoint, identity, required tool egress,
safe failure, and observability—not only build success. Promote pinned agent
versions with evaluation evidence and rollback plan. **Key takeaway:** CI/CD
is identity and environment contract, not `deploy` command alone.

### 29 — Durable cloud evaluation

**What and why:** Lesson 19 invokes evaluator classes locally. This lesson
optionally uploads reviewed JSONL, creates persisted evaluation definition, and
starts durable cloud run. Cloud evaluation suits shared datasets, scale,
predeployment evidence, scheduled/continuous comparison, and CI gates.

**Prerequisites and dependencies:** Need `AZURE_AI_PROJECT_ENDPOINT`,
`AZURE_AI_MODEL_DEPLOYMENT_NAME`, Foundry project access, supported
region/model/evaluator, quota, and runner egress. Create versioned reviewed
dataset; each sample row requires non-empty `query`. Specific sample is
single-turn and sends all queries to model target. For tool/multi-turn agents,
preserve complete messages, tool calls/results, and final answer in reviewed
trajectory schema rather than flattening transcript.

Run local validation first:

```bash
uv run python 02-generative-ai-and-agents/29_cloud_evaluation.py --dataset cases.jsonl
uv run python 02-generative-ai-and-agents/29_cloud_evaluation.py --dataset cases.jsonl --apply
```

**Architecture and code path:** Default output describes no Azure work.
`--apply` validates JSONL locally, uploads `evals` file with 30-day expiry,
creates Task Adherence criterion with `{{item.query}}` and complete
`{{sample.output_items}}`, then starts `evals.runs.create()`. It prints
dataset file, evaluation, and run IDs. It does not poll to completion, score
human review, or delete run records.

**Use and do not use:** Use synthetic/redacted data and record prompt, model,
agent/tool, corpus, evaluator, and dataset version. Do not upload credentials,
customer secrets, or unredacted personal data. Do not call one score release
decision: inspect distributions/failures, groundedness/safety/tool metrics,
thresholds, approval, and rollback. `--apply` incurs upload, storage,
evaluation/model-token, and retained-result cost.

**Network, RBAC, and takeaway:** Private deployments require private DNS and
runner access to Foundry, Azure OpenAI, and Azure Monitor. Restricted
telemetry results require monitoring-reader access, including protected-table
role where configured. **Key takeaway:** cloud run is durable evidence only
when data, mappings, evaluator, access, region, and release policy are
deliberate.

### 30 — Production observability preflight

**What and why:** Trace, evaluation, and retrieval data carry operational,
privacy, and cost obligations. This lesson reads local configuration and
prints production checklist before connecting telemetry, changing retention,
creating evaluation records, or sending traffic.

Run:

```bash
uv run python 02-generative-ai-and-agents/30_production_observability_preflight.py
```

**Architecture and output:** `preflight()` reads shared settings and reports
whether Application Insights, project, direct Azure OpenAI, and Search
endpoints are configured. It makes no Azure request. Output says lesson 21
records metadata-only spans—content recording is disabled—and lesson 29 owns
opt-in durable evaluation data.

**Use and do not use:** Use as configuration evidence before production review
or CI preflight. Do not treat "configured" as reachable, authorized, healthy,
compliant, or cost-approved. It does not connect Application Insights,
configure sampling/redaction, grant Monitoring Reader or Privileged Monitoring
Data Reader, create private endpoints, or verify Search index.

**Best practice and takeaway:** Set retention, sampling, redaction, access
review, alert thresholds, and cleanup owner before export. Trace correlation
IDs, latency, tool rounds, failures, token/cost estimates, and safe metadata;
record prompts/outputs/tool arguments only after explicit governance approval.
Test private DNS and egress for Foundry, Azure OpenAI, Azure Monitor, Search,
Storage, Key Vault, and tool services from production runtime. **Key
takeaway:** observability measures behavior; it is neither authorization nor
quality proof.

## Evaluation and tracing truth

### What lesson 19 is

Lesson 19 is local evaluator SDK invocation.
It has one hand-built, complete, in-memory agent-turn dictionary.
It prints evaluator result to terminal.
It does not create a portal experiment.
It does not send a dataset to Foundry cloud evaluation.
It does not store a result history automatically.
It includes one valid tool call and result, but does not prove tool quality.
It does not prove agent quality because one case is statistically meaningless.

### What a credible evaluation loop needs

1. Define task, user population, harm boundary, and success metric.
2. Build versioned representative dataset with expected outcomes or rubrics.
3. Include normal, edge, ambiguous, multilingual, adversarial, and zero-evidence cases.
4. Capture exact model/deployment, prompt/agent version, tool schema, and corpus version.
5. Evaluate response quality, groundedness, tool selection/arguments, latency, cost, and safety.
6. Inspect distributions and failures, not only average score.
7. Establish release thresholds, human review, rollback, and regression comparisons.
8. Run predeployment and periodically against production-like traces under governance.

### Cloud evaluation distinction

Cloud evaluation is managed experiment/run workflow with dataset, configuration,
persisted results, comparison, and service-side visibility subject to current
Foundry contract.
It is larger than calling evaluator class in process.
Use local SDK for quick iterative checks.
Use cloud evaluation when you need repeatable shared datasets, persisted runs,
comparisons, and release evidence.
Verify current region, quota, networking, identity, and preview support from
local Foundry documentation before adopting it.

### Tracing distinction

A trace records what happened in execution.
An evaluator judges aspects of output/trace against rule/model/rubric.
Observability helps find latency, retry, tool-loop, and failure patterns.
Observability is not a correctness score.
A high evaluator score is not authorization evidence.
Record content only after data-governance approval.

## Operations, security, and CI/CD

### Production readiness checklist

| Concern | Minimum evidence |
|---|---|
| Identity | Workload identity selected; roles scoped to endpoint/action; no user shared credentials. |
| Network | Tool backends and remote MCP endpoints reachable from runtime; DNS/egress/ingress tested. |
| Secrets | Secret store/managed identity; no keys in repository, prompts, tool schema, or logs. |
| Input safety | Size/type/rate limits; injection handling; user and document trust boundaries defined. |
| Tool safety | Allowlist, strict schema, semantic validation, caller authorization, timeout, idempotency, approval. |
| State | Conversation/user/tenant isolation; retention/deletion; source-of-truth decision documented. |
| RAG | ACL filtering, source versioning, ingestion/deletion, retrieval and groundedness evaluation. |
| Output | Schema/content validation, citations where required, escalation/human review for consequential results. |
| Telemetry | Correlation IDs, latency/errors/cost estimates, redaction, sampling, retention, access review. |
| Evaluation | Versioned dataset, thresholds, regression comparison, failure triage, release decision owner. |
| Resilience | Rate limit policy, bounded retry, timeout, circuit/queue/fallback behavior, rollback. |
| Cost | Token/tool/storage/telemetry budget, quotas, alerts, cleanup owner. |

### CI/CD sequence

```text
Commit code, prompts, schemas, infrastructure, and evaluation fixtures
    -> lint/type/test deterministic application code
    -> run schema and contract tests against mock/isolated backend
    -> provision/update least-privileged nonproduction resources through IaC
    -> deploy versioned agent/hosted runtime/tool backend
    -> smoke test endpoint, identity, tool reachability, and safe failure paths
    -> run evaluation dataset and policy checks
    -> approve promotion with model/prompt/tool/corpus version evidence
    -> canary or staged release with traces, alerts, rollback
    -> evaluate production-like failures and remove stale versions/resources
```

Do not deploy mutable prompts/tool definitions manually without version record.
Do not make production tool mutation enabled merely because dev read tool works.
Do not use model output as CI approval decision by itself.

### Hosted-agent boundary

Lesson 17 only demonstrates local Agent Framework. Lessons 26–28 add a
contained Responses hosted-agent source sample, static contract validation, and
an OIDC CI/CD reference. They still do not prove a production deployment.
Before promotion, verify deployed endpoint, version `active` state, project and
agent identity RBAC, external-tool/network reachability, private DNS, session
policy, telemetry access/data handling, scaling, cost, health behavior,
rollback, and cleanup in your target environment.

### Cost and cleanup

| Asset | Lessons | Cleanup concern |
|---|---:|---|
| Model tokens/reasoning | 01–05, 07, 09, 11–22, 23, 25, 29 | Input/output/reasoning, managed tools, evaluators, and retries accrue usage. |
| File/vector store | 06 | Normal completion deletes lesson-created vector store and uploaded files; interrupted runs still need inventory. |
| Agent versions | 08, 10–18, 23, 25 | Re-runs create versions; 23/25 delete their temporary version in `finally`; review/remove stale lab versions after interrupted runs. |
| Memory store/items | 14 | Preview data, retention, consent, and deletion need owner. |
| Function Apps and hosted runtime | 12, 23, 26–28 | Hosting, storage, remote build/image, telemetry, egress, auth, and container capacity cost. |
| Toolbox and Search | 24–25 | Toolbox versions persist; Search service/index/embedding/query costs exist even though lesson 25 does not create them. |
| Evaluation and telemetry | 19, 21, 29–30 | Local evaluator tokens, App Insights ingestion/retention, uploaded evaluation data, runs, and results need budget and deletion owner. |

Use disposable study names/projects when possible.
Inventory after experiments.
Delete agents/versions, files, vector stores, memory stores, Function Apps,
telemetry data/resources, and test deployments according to policy.

## Troubleshooting decision table

| Symptom | Diagnose | Correct action |
|---|---|---|
| `401`/`403` direct call | Endpoint, effective identity, direct role/scope. | Use `AZURE_OPENAI_ENDPOINT`; assign matching data-plane role. |
| `401`/`403` project agent call | Project URL, identity, Foundry project access. | Use `PROJECT_ENDPOINT`; verify project/resource role. |
| `404 DeploymentNotFound` | Deployment name/endpoint mismatch. | List deployments; set configured deployment name. Do not retry blindly. |
| Lesson 03 fails | Reasoning deployment absent/incompatible. | Set/deploy supported `REASONING_MODEL`; review model support. |
| Function result rejected | Missing/mismatched `call_id` or invalid result loop. | Preserve each `call_id`; submit all outputs in same conversation. |
| Tool loops forever | Ambiguous instructions/tool result or repeated failure. | Keep cap, return bounded errors, inspect trace; never remove cap. |
| Lesson 12 rejects endpoint | `ORDERS_FN_ENDPOINT` empty/local host. | Deploy backend; use reachable HTTPS base URL without `/api`. |
| Lesson 12 backend fails | Route/auth/network/spec mismatch. | Curl deployed `/api/orders`; align OpenAPI auth and Function auth. |
| MCP connection fails | Local endpoint, auth, network, protocol server issue. | Deploy `/runtime/webhooks/mcp`; configure matching auth. |
| Lesson 23 denies tool | `--approve` absent, tool not allowlisted, or malformed approval request. | Inspect printed name/arguments; approve only reviewed allowlisted read action. |
| Lesson 24 version removal breaks agent | Consumer references deleted Toolbox version. | Inventory consumers, promote/test replacement, then delete during controlled change. |
| Lesson 25 fails | Connection/index/RBAC/private DNS mismatch. | Verify named project connection, vector-capable index, identity role, and agent-to-Search route. |
| Memory misses preference | Different header/scope, async update, extraction/retrieval miss. | Use same user ID, wait/retry per contract, never invent recall. |
| Lesson 16 fails | Lesson 15 not run or workflow preview SDK/service changed. | Create intake agent first; inspect supported preview surface. |
| Lesson 19 import failure | Environment not synced. | Run `uv sync`; package exists in root manifest. |
| Low evaluator score | Single case, weak trace, or out-of-scope rubric. | Inspect result, improve dataset/trace and regression process. |
| No lesson 21 traces | Missing/invalid connection string or telemetry delay. | Set connection string; inspect governance/export configuration. |
| Lesson 26 preflight fails | Runtime contract/dependency drift. | Run contained preflight; preserve Responses adapter, port 8088, and remote Linux amd64 build contract. |
| Hosted deploy succeeds but invoke fails | Version inactive, wrong protocol, RBAC, private DNS, or egress issue. | Poll status; invoke correct protocol; test identity and route from deployed runtime. |
| Lesson 29 `--apply` fails | Missing dataset/env/RBAC/region/quota. | Validate JSONL and both environment values; inspect project role, evaluator support, quota, and runner network. |
| LangChain/LangGraph error | Wrong endpoint/deployment/token scope. | Use OpenAI-compatible endpoint `/openai/v1`, deployment names. |
| Embedding failure in 22 | Chat model used as embedding deployment or unsupported endpoint. | Set compatible `EMBEDDING_MODEL`; use same OpenAI-compatible base URL. |
| FAISS answer is unsupported | Retrieval miss or model skipped evidence. | Evaluate chunks/retrieval, require grounded behavior, return uncertainty. |
| High cost/latency | Reasoning, output length, tools, retrieval, retries, telemetry. | Trace path; cap output/tools; choose model and budget deliberately. |

## Common traps

1. **Same resource name, wrong endpoint.** `services.ai.azure.com` project URL is
not direct `openai.azure.com` base URL in this repository's OpenAI SDK path.
2. **Model family versus deployment.** `model=` normally needs configured
 deployment name.
3. **Tool schema equals permission.** It does not; application authorizes.
4. **Strict JSON equals true content.** It only constrains structure.
5. **Local curl equals agent reachability.** It does not; Agent Service cannot
 reach laptop localhost.
6. **Anonymous demo equals production OpenAPI auth.** It does not.
7. **MCP equals OpenAPI/Toolbox/A2A.** They solve different integration layers.
8. **Conversation equals memory.** Conversation is turn context; memory is
preview durable extraction/retrieval.
9. **Waiting 65 seconds equals guaranteed memory.** It does not.
10. **Workflow YAML equals supported long-term runtime.** Workflows retire
December 1, 2026.
11. **Local Agent Framework equals hosted agent.** It does not deploy anything.
12. **One evaluator printout equals cloud evaluation.** It does not.
13. **Trace equals evaluation.** Trace observes execution; evaluator scores it.
14. **Application Insights content recording is harmless.** It can retain
sensitive data.
15. **LangChain accepts project endpoint.** Lessons 20–22 configure direct
Azure OpenAI-compatible `/openai/v1` base URL.
16. **Embedding model can be chat deployment.** Use compatible embedding
deployment name.
17. **FAISS demo is production RAG.** It rebuilds local index and has no ACL.
18. **Agent version re-run is free/no state.** New versions and cloud state
accumulate.
19. **`--apply` means harmless preview.** It can upload, create, invoke, or
delete durable cloud assets.
20. **MCP approval is backend authorization.** It is one client-side
decision; backend still enforces identity and business policy.
21. **Toolbox is MCP server you operate yourself.** It is Foundry-managed,
versioned catalog with an MCP-compatible endpoint.
22. **Search citations prove permission or truth.** Citations expose source;
ACL, source quality, and groundedness still need validation.
23. **Responses hosted agent is A2A.** It is not unless separately declared
and configured for A2A.
24. **Private endpoint proves private runtime path.** DNS, egress, ingress,
and every identity/action still need verification.
25. **Cloud evaluation run equals release approval.** It is evidence to
review against thresholds and policy.
26. **Metadata-only tracing is free of governance.** Metadata can still be
sensitive and incur ingestion/retention cost.

## Coverage limits and high-value next lessons

This domain intentionally demonstrates narrow runnable paths. Lessons 23–30
add preflight and minimal, explicitly gated examples for MCP approval,
Toolbox/versioning, Azure AI Search integration, hosted Responses runtime,
hosted A2A boundary, OIDC CI/CD, cloud evaluation, and observability.

It does not fully implement following production requirements:

- remote MCP OAuth/Entra setup, credential rotation, server lifecycle, or
  backend authorization;
- incoming A2A endpoint deployment, delegated-identity policy, task lifecycle,
  or cross-agent audit;
- Azure AI Search ingestion, ACL/security trimming, reranking, index lifecycle,
  and RAG quality/safety evaluation;
- hosted-agent private networking, supply-chain policy, scaling, incident
  operations, session strategy, or promotion gate;
- cloud-evaluation completion polling, results analysis, continuous evaluation,
  safety/RAG evaluator selection, or CI release approval;
- human approval workflows for write tools, idempotent writes, durable queues,
  or transaction reconciliation.

Treat these as deliberate curriculum boundaries, not implied support.

## Local references

### Core contracts

- [Responses API quickstart](../.context/azure-ai-docs/articles/foundry/agents/quickstarts/responses-api.md)
- [Prompt agent quickstart](../.context/azure-ai-docs/articles/foundry/agents/quickstarts/prompt-agent.md)
- [Function calling](../.context/azure-ai-docs/articles/foundry/agents/how-to/tools/function-calling.md)
- [Tool best practices](../.context/azure-ai-docs/articles/foundry/agents/concepts/tool-best-practice.md)
- [Tool catalog](../.context/azure-ai-docs/articles/foundry/agents/concepts/tool-catalog.md)
- [Toolbox overview](../.context/azure-ai-docs/articles/foundry/agents/concepts/toolbox-overview.md)
- [Create and use a Toolbox](../.context/azure-ai-docs/articles/foundry/agents/how-to/tools/toolbox.md)
- [MCP tools](../.context/azure-ai-docs/articles/foundry/agents/how-to/tools/model-context-protocol.md)
- [MCP authentication](../.context/azure-ai-docs/articles/foundry/agents/how-to/mcp-authentication.md)
- [Agent-to-agent tools](../.context/azure-ai-docs/articles/foundry/agents/how-to/tools/agent-to-agent.md)
- [Agent-to-agent authentication](../.context/azure-ai-docs/articles/foundry/agents/concepts/agent-to-agent-authentication.md)
- [OpenAPI tools](../.context/azure-ai-docs/articles/foundry/agents/how-to/tools/openapi.md)
- [Tool authentication](../.context/azure-ai-docs/articles/foundry/agents/how-to/tools/tool-authentication.md)

### State, runtime, and operations

- [Memory usage](../.context/azure-ai-docs/articles/foundry/agents/how-to/memory-usage.md)
- [Memory concept](../.context/azure-ai-docs/articles/foundry/agents/concepts/what-is-memory.md)
- [Workflow concept](../.context/azure-ai-docs/articles/foundry/agents/concepts/workflow.md)
- [Hosted agents](../.context/azure-ai-docs/articles/foundry/agents/concepts/hosted-agents.md)
- [Hosted-agent runtime contract](../.context/azure-ai-docs/articles/foundry/agents/concepts/hosted-agent-contract.md)
- [Hosted-agent deployment](../.context/azure-ai-docs/articles/foundry/agents/how-to/deploy-hosted-agent.md)
- [Hosted-agent code deployment](../.context/azure-ai-docs/articles/foundry/agents/how-to/deploy-hosted-agent-code.md)
- [Hosted-agent permissions](../.context/azure-ai-docs/articles/foundry/agents/concepts/hosted-agent-permissions.md)
- [Hosted-agent CI/CD](../.context/azure-ai-docs/articles/foundry/agents/quickstarts/set-up-cicd-hosted-agent.md)
- [Hosted-agent telemetry](../.context/azure-ai-docs/articles/foundry/agents/how-to/configure-hosted-agent-telemetry.md)
- [Development lifecycle](../.context/azure-ai-docs/articles/foundry/agents/concepts/development-lifecycle.md)

### Evaluation and frameworks

- [Agent evaluators](../.context/azure-ai-docs/articles/foundry/concepts/evaluation-evaluators/agent-evaluators.md)
- [Cloud evaluation](../.context/azure-ai-docs/articles/foundry/how-to/develop/cloud-evaluation.md)
- [Foundry observability](../.context/azure-ai-docs/articles/foundry/concepts/observability.md)
- [Trace data](../.context/azure-ai-docs/articles/foundry/observability/concepts/trace-data.md)
- [RAG evaluators](../.context/azure-ai-docs/articles/foundry/concepts/evaluation-evaluators/rag-evaluators.md)
- [Risk and safety evaluators](../.context/azure-ai-docs/articles/foundry/concepts/evaluation-evaluators/risk-safety-evaluators.md)
- [LangChain agents](../.context/azure-ai-docs/articles/foundry/how-to/develop/langchain-agents.md)
- [LangChain hosted agents](../.context/azure-ai-docs/articles/foundry/how-to/develop/langchain-hosted-agents.md)

### Repository assets

- [OpenAPI Function asset](azure_functions_orders/README.md)
- [MCP Function asset](northwind_mcp/README.md)
- [Workflow preview assets](workflows/README.md)
- [Responses hosted-agent asset](hosted_agent_responses/README.md)
- [Domain 1 planning guide](../01-plan-and-manage/README.md)
- [Domain 5 retrieval guide](../05-information-extraction/README.md)

## Before declaring a lab complete

- [ ] Command ran from repository root or documented nested asset directory.
- [ ] Endpoint used matches selected client.
- [ ] Deployment names exist and match required capability.
- [ ] Identity/role failure, if any, was diagnosed without adding secrets.
- [ ] Created agent/file/vector/memory/workflow/Toolbox/evaluation IDs and versions were recorded.
- [ ] Tool request/response path preserved call IDs and rejected bad arguments.
- [ ] External API/MCP backend was tested from actual runtime reachability path.
- [ ] Preview limitation and migration path were recorded.
- [ ] Costs, stored data, traces, and cleanup owner were reviewed.
- [ ] Evaluation claims distinguish local sample from persisted cloud evidence.
- [ ] Hosted deployment, if used, passed readiness, protocol, identity, network, and smoke-test checks.
- [ ] Private DNS, endpoint reachability, RBAC, quota, region, cost, retention, and cleanup were reviewed from runtime network.
