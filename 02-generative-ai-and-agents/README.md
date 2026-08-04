# Domain 2 — Implement Generative AI and Agentic Solutions (30–35%)

> Run any lesson: `uv run python 02-generative-ai-and-agents/<file>.py`
> Prereqs: `.env` filled, `az login` completed. See root [README.md](../README.md).

Largest exam domain — most files. 22 lessons walk you from your first
Responses API call to multi-agent orchestration, workflows, and framework
integrations (LangChain, LangGraph, Agent Framework).

---

## What this domain teaches you

Everything that lives **on top of** a Foundry deployment. Domain 1 got you
to "a model is deployed and I can call it keylessly." Domain 2 takes that
raw model and turns it into a **product**: you'll learn the **Responses API**
in depth, wire the **7 tool categories** (Web Search, File Search, Code
Interpreter, Function, OpenAPI, MCP, A2A), register **Prompt Agents** in the
Foundry portal, orchestrate multi-agent workflows, add **long-term memory**
that persists across conversations, run **built-in evaluators**, and
integrate the three most common **third-party agent frameworks**
(Microsoft Agent Framework, LangChain, LangGraph). Every lesson is a small
runnable Python file plus the mental model behind it.

---

## Agents in 90 seconds

If you skipped Domain 1's runway, read this once. It unlocks every diagram.

- **Responses API** — the one API used for **everything** in this domain.
  `client.responses.create(model=..., input=..., tools=[...])`. Same call
  covers plain text prompts, tool-augmented flows, agent invocations, and
  multi-turn conversations.
- **conversation_id** — server-managed transcript. Pass the same
  `conversation.id` on two `responses.create` calls → the agent has full
  history without you resending anything. Different id = blank slate.
- **Prompt Agent** — an agent definition (model + instructions + tools)
  **registered** in the Foundry portal (or via SDK `create_version`). Called
  by name via `extra_body={"agent_reference": {"name": ...}}`. Portable
  across projects; versioned automatically.
- **Ephemeral agent** — instructions live in your code, passed inline via
  `instructions=` on each `responses.create` call. No registration. Great
  for prototypes and single-file demos (Domain 1's L10.5 / L11 used this).
- **Hosted agent** — your Python/Node code packaged in a container that
  Foundry runs for you. Best when the agent needs custom code (databases,
  business logic) beyond what a prompt + tools can express. L17 shows the
  **Microsoft Agent Framework** SDK, which is the recommended way to build
  hosted agents.
- **Tool** — a capability an agent can call. Foundry ships ~10 **built-in
  tools** (Web Search, File Search, Code Interpreter, Function, Azure AI
  Search, Bing Grounding, Fabric, SharePoint, Image Generation, Browser
  Automation, Computer Use) plus 3 **custom-plug-in tools** (OpenAPI, MCP,
  A2A). The exam and this domain focus on the first ~7.
- **Toolbox** — a managed layer that bundles multiple tools behind a single
  MCP endpoint so agents consume centrally-approved tools without each
  team re-wiring auth. Optional but useful at scale.
- **Foundry Memory** — cross-session, per-user persistent knowledge (3
  types: User Profile / Chat Summary / Procedural). Distinct from
  `conversation_id` which is only session-scoped.
- **Workflow** — deterministic YAML-defined orchestration graph (nodes:
  `InvokeAzureAgent`, `ConditionGroup`, `EndConversation`, ...). Use when
  compliance/audit demands a fixed process; use agent-as-tool when you
  want the model to decide the routing dynamically.

---

## Mental model of the 22 lessons

Five phases. Read left to right — later phases build on earlier ones.

```
┌─── Phase 1: Foundations (L01–L07) ─────────────────────────────────────┐
│  L01 First API call     — Responses API + keyless auth (single call)  │
│  L02 Temperature        — tune sampling: deterministic vs creative     │
│  L03 Reasoning effort   — o-series model with `reasoning.effort=high`  │
│  L04 Web Search tool    — built-in real-time grounding                 │
│  L05 Code Interpreter   — sandboxed Python execution                   │
│  L06 File Search tool   — RAG with Foundry-managed vector store        │
│  L07 Structured output  — json_schema + strict=True                    │
└─────────────────────────────────────────────────────────────────────────┘
        ↓ know the Responses API + all built-in tools
┌─── Phase 2: Prompt Agents in the portal (L08–L14) ─────────────────────┐
│  L08 Create agent       — register a Prompt Agent with function tools │
│  L09 Invoke agent       — call it by name; execute the function calls │
│  L10 Agent + Web Search — agent wrapping a built-in tool               │
│  L11 Agent + functions  — full create+invoke cycle in one file         │
│  L12 Agent + OpenAPI    — spec-defined tools via Azure Function        │
│  L13 Conversations      — server-managed thread history                │
│  L14 Foundry Memory     — persistent knowledge across conversations    │
└─────────────────────────────────────────────────────────────────────────┘
        ↓ can build a task-focused agent and manage state
┌─── Phase 3: Workflows & multi-agent (L15–L19) ─────────────────────────┐
│  L15 Workflow intake    — intake agent with strict structured output   │
│  L16 Workflow deploy    — YAML routing → knowledge vs ticket branches  │
│  L17 Hosted agent       — Microsoft Agent Framework (portable code)    │
│  L18 Multi-agent        — router + specialists via agent-as-tool       │
│  L19 Evaluator          — Task Adherence + Tool Call Accuracy scoring  │
└─────────────────────────────────────────────────────────────────────────┘
        ↓ can orchestrate multiple agents and measure quality
┌─── Phase 4: Framework integrations (L20–L22) ──────────────────────────┐
│  L20 LangChain agent    — Foundry as ChatOpenAI backend + tools        │
│  L21 LangChain tracing  — OpenTelemetry → Application Insights         │
│  L22 LangGraph agent    — StateGraph + ToolNode + FAISS RAG            │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 30-Second Domain 2 Cheat Sheet

Keep this open while you study — the map for every exam question in the domain.

```
Consuming a model?          → Responses API (client.responses.create)  [L01]
Tuning behavior?            → temperature/top_p [L02]; reasoning.effort [L03]
Real-time info?             → tools=[{"type":"web_search"}]  [L04, L10]
Run code / do math?         → tools=[{"type":"code_interpreter"}]  [L05]
RAG without infra?          → tools=[{"type":"file_search", "vector_store_ids":[...]}]  [L06]
Guaranteed JSON schema?     → text={"format": {"type":"json_schema", "strict":True}}  [L07, L15]
Building an agent?          → Prompt Agent → Hosted Agent → LangChain → LangGraph  [L08, L17, L20, L22]
Agent + your Python code?   → FunctionTool schema; your app executes  [L08, L09, L11]
Agent + REST backend?       → OpenApiTool + spec  [L12]
Conversation memory?        → pass conversation.id (session-scoped)  [L13]
Cross-session memory?       → Foundry Memory (3 types) — enable in portal  [L14]
Deterministic flow?         → YAML Workflow (InvokeAzureAgent + ConditionGroup)  [L15, L16]
Dynamic routing?            → Multi-agent as agent-as-tool  [L18]
Portable agent code?        → Microsoft Agent Framework (agent-framework SDK)  [L17]
Scoring an agent?           → Task Adherence + Tool Call Accuracy evaluators  [L19]
Monitoring?                 → OpenTelemetry spans → Application Insights  [L21]
Stateful multi-step graph?  → LangGraph StateGraph + ToolNode + MessagesState  [L22]
```

---

## Prereqs before you run anything

Steps 1–4 come from Domain 1. Steps 5–6 are Domain 2 additions.

1. **Azure subscription** with billing.
2. **Foundry resource + project** created.
3. **`az login`** completed. `DefaultAzureCredential` uses your CLI identity.
4. **`Foundry User` role** on the Foundry resource (portal auto-assigns if you
   created the resource; SDK/CLI creation does not — see Domain 1 L13).
5. **`.env` filled** — three subdomain URLs from Domain 1 plus:
   - `APPLICATIONINSIGHTS_CONNECTION_STRING` — optional; needed only for L21
     tracing. Without it L21 falls back to stdout.
   - `ORDERS_FN_ENDPOINT` — required only for L12 (OpenAPI agent). Points to
     the Azure Function backend in `azure_functions_orders/`. See L12 below.
6. **Azure Functions Core Tools** installed if you want to run L12 locally:
   `brew install azure-functions-core-tools@4` (macOS) or the platform
   equivalent. Optional — you can also deploy the Function to Azure.

Sanity check: `uv run python 01-plan-and-manage/07_managed_identity_agent.py`
must pass first. If it does, everything up to L11 in this domain runs cold.
L12 needs the Function; L14 memory needs the portal-side Memory toggle.

---

## Glossary — Domain 2 terms

Skim once; refer back whenever a term feels fuzzy.

| Term | Beginner definition |
|------|--------------------|
| **Responses API** | `client.responses.create(...)`. One API for text prompts, tool calls, agent invocations, multi-turn. Replaces the older Chat Completions for most agent flows. |
| **`conversation_id`** | Server-managed thread id. Pass the same id on two calls → agent has full history. Session-scoped only. |
| **`thread_id`** | OpenAI Assistants API term. Foundry Responses API uses `conversation_id` — don't confuse them. |
| **`agent_reference`** | `extra_body={"agent_reference": {"name": "...", "version": "..."}}`. Invokes a registered Prompt Agent by name. Omit `version` to get the latest. |
| **Agent version** | Each `create_version` call bumps the version. Portal keeps them all; API defaults to latest unless you pin one. |
| **Prompt Agent** | Registered agent (model + instructions + tools) stored in Foundry portal. Called by name. |
| **Ephemeral agent** | Instructions passed inline on each Responses API call via `instructions=`. No registration. |
| **Hosted agent** | Your Python/Node code packaged in a container that Foundry runs for you. Use for logic that can't be expressed as instructions + tools. |
| **Function tool** | Tool where the model requests the call but **your app** executes the function and passes the result back. `FunctionTool(...)` in the SDK. |
| **OpenAPI tool** | Tool defined by an OpenAPI 3.x spec — Foundry auto-wraps each operation into a callable tool. Backend is your REST API. |
| **MCP tool** | Model Context Protocol — external server that exposes tools + resources + prompts via a standardized protocol. |
| **A2A** | Agent-to-Agent protocol (preview). Lets one agent invoke another agent's endpoint directly. |
| **Bing Grounding** | Config key `{"type": "bing_grounding"}` for the built-in Web Search tool. |
| **Web / File / Code Interpreter** | Three most-used built-in tools: fetch web, semantic search over uploaded docs, sandboxed Python. |
| **Azure AI Search tool** | Built-in tool that plugs a full AI Search index (with skillsets) into an agent. Contrast with File Search which is Foundry-managed. |
| **Toolbox** | Managed collection of tools exposed as one MCP endpoint. Centralized auth/governance for shared tools. |
| **Vector store** | Foundry-managed embeddings index built from uploaded files. File Search tool reads from it. |
| **Foundry Memory** | Persistent, cross-session knowledge (3 types: User Profile / Chat Summary / Procedural). 3-phase pipeline: Extraction → Consolidation → Retrieval. |
| **User Profile Memory** | Durable per-user preferences (language, product defaults, allergies). Retrieved at conversation start. |
| **Chat Summary Memory** | Distilled summaries of past conversations. Retrieved per turn for continuity. |
| **Procedural Memory** | Reusable how-to routines the user has taught the agent. |
| **Workflow** | YAML-defined orchestration graph. Nodes: `InvokeAzureAgent`, `ConditionGroup`, `EndConversation`. Deterministic. |
| **Agent-as-tool** | Multi-agent pattern where one agent (router) treats other agents as callable tools via `FunctionTool`. Dynamic routing. |
| **Microsoft Agent Framework** | `agent-framework` Python SDK. Ships `Agent` + `FoundryChatClient`. Runs same code locally and inside a Foundry container. |
| **`FoundryChatClient`** | The `agent-framework` chat client pointed at a Foundry project — keyless auth via `DefaultAzureCredential`. |
| **LangChain / LangGraph** | Third-party frameworks. LangChain = chains + `create_agent()`; LangGraph = state-graph orchestration. Point them at Foundry as the model backend. |
| **`MessagesState`** | LangGraph's required state type for tool-calling agents. Holds the conversation's message list. |
| **Task Adherence / Tool Call Accuracy** | Two of the 11 built-in agent evaluators. Score how well the agent followed instructions / used the right tools. |

---

## Common first-run failures

| Symptom | Root cause | Fix |
|---------|-----------|-----|
| `Agent not found: <name>` | Prompt Agent referenced but never created | Run the lesson that creates it (L08 → L09; L15 → L16). L13/L14 now create their agents inline. |
| `Agent version mismatch` | Hardcoded version drifted | L09 no longer hardcodes version — omit `version` from `agent_reference` to get latest. |
| L12: `404 on /api/orders` | `ORDERS_FN_ENDPOINT` not set OR Function not running | Set env var; `func start` in `azure_functions_orders/`; verify with `curl $ORDERS_FN_ENDPOINT/api/orders`. |
| L14: memory doesn't recall | Memory feature not enabled on the agent (portal-only) | Foundry portal → Agents → agent → Memory → Enable. Then re-run. |
| L16: workflow deploy fails on missing agent | Old bug — fixed. L16 now creates Knowledge + Ticket agents inline. | Run L15 first (creates Intake); L16 creates the rest. |
| L21: no spans in Application Insights | `APPLICATIONINSIGHTS_CONNECTION_STRING` unset | Set it in `.env`. Without it, L21 still runs but prints only to stdout. |
| `ImportError: azure-ai-evaluation` | Optional dep missing | `pip install azure-ai-evaluation` — only L19 needs it. |
| `ImportError: agent-framework` | Optional dep missing | `pip install agent-framework agent-framework-foundry` — only L17 needs it. |

---

## Files

| # | File | Syllabus bullet |
|---|---|---|
| 01 | `01_first_api_call.py` | Deploy and consume LLMs |
| 02 | `02_model_behavior.py` | Tune generation behavior (temperature, top_p) |
| 03 | `03_reasoning.py` | Multi-step reasoning pipeline |
| 04 | `04_web_search_tool.py` | Tool-augmented flows — Web Search |
| 05 | `05_code_interpreter.py` | Tool-augmented flows — Code Interpreter |
| 06 | `06_file_search_tool.py` | Tool-augmented flows — built-in File Search (RAG) |
| 07 | `07_structured_output.py` | Structured JSON outputs (json_schema, strict) |
| 08 | `08_prompt_agent_create.py` | Define agent roles, goals, tool schemas |
| 09 | `09_prompt_agent_invoke.py` | Invoke agent (Responses API + conversation) |
| 10 | `10_agent_web_search.py` | Integrate agent tools — Web Search |
| 11 | `11_agent_function_tools.py` | Integrate agent tools — custom functions |
| 12 | `12_agent_openapi_tools.py` | Integrate agent tools — OpenAPI spec (Azure Functions) |
| 13 | `13_conversation_thread.py` | Conversation tracking |
| 14 | `14_foundry_memory.py` | Cross-session memory (Extraction → Consolidation → Retrieval) |
| 15 | `15_workflow_intake.py` | Workflow — intake agent with structured output |
| 16 | `16_workflow_conditional.py` | Workflow — conditional branching |
| 17 | `17_hosted_agent_framework.py` | Hosted agents — Microsoft Agent Framework |
| 18 | `18_multi_agent_coord.py` | Orchestrated multi-agent solutions |
| 19 | `19_evaluator_task_adherence.py` | Agent evaluators — Task Adherence + Tool Call Accuracy |
| 20 | `20_langchain_agent.py` | LangChain agent |
| 21 | `21_langchain_tracing.py` | LangChain + OpenTelemetry tracing |
| 22 | `22_langgraph_agent.py` | LangGraph stateful agent |
| — | `azure_functions_orders/` | OpenAPI-described Function backing L12 |
| — | `northwind_mcp/` | Custom MCP server as an Azure Function |
| — | `workflows/` | JSON + YAML workflow definitions |

## Reference docs

- [Foundry Agent Service overview](../.context/azure-ai-docs/articles/foundry/agents/overview.md)
- [Responses API quickstart](../.context/azure-ai-docs/articles/foundry/agents/quickstarts/responses-api.md)
- [Tool catalog](../.context/azure-ai-docs/articles/foundry/agents/concepts/tool-catalog.md)
- [Hosted agents contract](../.context/azure-ai-docs/articles/foundry/agents/concepts/hosted-agents.md)
- [Foundry Memory](../.context/azure-ai-docs/articles/foundry/agents/concepts/what-is-memory.md)
- [Workflows](../.context/azure-ai-docs/articles/foundry/agents/concepts/workflow.md)
- [Agent evaluators](../.context/azure-ai-docs/articles/foundry/concepts/evaluation-evaluators/agent-evaluators.md)
- [MCP get started](../.context/azure-ai-docs/articles/foundry/mcp/get-started.md)
- [LangChain integration](../.context/azure-ai-docs/articles/foundry/how-to/develop/langchain.md)

---

## Syllabus sections

| Section | Topics |
|---------|--------|
| Build generative apps | Deploy/consume models, RAG, workflows, evaluate, Foundry SDKs |
| Build agents | Roles/goals/tools, retrieval, function-calling, memory, multi-agent, monitoring |
| Optimize + operationalize | Prompt engineering, reflection/self-critique, observability, orchestration |

---

## Responses API — the one call you'll use everywhere

Every lesson in this domain calls `client.responses.create(...)`. Learn the
shape once; you're set.

```python
response = client.responses.create(
    model="gpt-4.1-mini",        # deployment name (Domain 1 L01 lists yours)
    instructions="You are ...",  # system prompt / agent persona
    input="User message",        # current user turn (string or list of parts)
    tools=[{"type": "web_search"}],  # optional list of tool configs
    conversation=conversation.id,     # optional — continue a thread
    text={"format": {...}},           # optional — structured output config
    temperature=0.7,                  # optional generation params
    reasoning={"effort": "high"},     # optional (o-series models only)
)
print(response.output_text)      # the final text reply
print(response.model)            # underlying model actually used (Model Router visibility)
```

| Field | Purpose |
|-------|---------|
| `instructions` | System prompt / agent persona |
| `input` | User message (string or list of content parts) |
| `tools` | List of tool definitions (see tool catalog below) |
| `conversation` | Pass `conversation.id` to continue the thread |
| `text.format` | Structured output config (`json_schema` + `strict`) |
| `output_text` | Final text response |
| `output` | Full output list — includes tool call events, code interpreter output, ... |
| `usage.input_tokens` / `usage.output_tokens` | Token counts for billing/observability |

**Exam trap:** the older Assistants API uses `thread_id`; Responses API uses
`conversation_id`. Different concept, similar name.

---

## Tool catalog — what agents can call

Foundry's tool catalog has **12 built-in tools** (Foundry executes) plus
**3 custom tool types** and **Toolbox** as the recommended packaging layer.
Source: [`agents/concepts/tool-catalog.md`](../.context/azure-ai-docs/articles/foundry/agents/concepts/tool-catalog.md).

**Built-in tools (Foundry executes):**

| Tool | Description |
|------|-------------|
| **Web Search** | Real-time public-web results with inline citations. Recommended default; for advanced tuning see [Bing tools](../.context/azure-ai-docs/articles/foundry/agents/how-to/tools/bing-tools.md). |
| **Code Interpreter** | Write + run Python in a sandbox — math, plotting, CSV crunching. |
| **Custom Code Interpreter** (preview) | Code Interpreter with custom Python packages + Container Apps environment. |
| **File Search** | Semantic search over uploaded files (Foundry-managed vector store). |
| **Azure AI Search** | Plug in an existing AI Search index (skillsets, hybrid, filters). |
| **Azure Functions** | Call your Azure Functions from an agent (distinct from OpenAPI — targets Functions specifically). |
| **Function calling** | Your JSON schema; YOUR APP executes the function. |
| **Image Generation** (preview) | Generate images (DALL·E / GPT-Image) inline in conversation. |
| **Browser Automation** (preview) | Drive a real browser via natural-language prompts. |
| **Computer Use** (preview) | Mouse / keyboard / screen automation. |
| **Microsoft Fabric** (preview) | Query a Microsoft Fabric data agent. |
| **SharePoint** (preview) | Chat with private SharePoint documents. |

**Custom tools (external execution):**

| Tool | Description |
|------|-------------|
| **MCP** | Model Context Protocol server (tools + resources + prompts). |
| **OpenAPI** | Any REST API described by an OpenAPI 3.0 or 3.1 spec. |
| **A2A** (preview) | Agent-to-Agent — connect to other agent endpoints. |

The tool types this domain covers in code: **Web Search** (L04, L10),
**Code Interpreter** (L05), **File Search** (L06), **Function calling**
(L08, L09, L11, L18), **OpenAPI** (L12), **MCP** (via `northwind_mcp/` —
optional add-on), **A2A** conceptually only.

### Toolbox — the recommended packaging layer

Per official docs: **"The recommended way to make tools available to agents
is through a Toolbox."** A Toolbox bundles multiple tools and exposes them
via a single MCP endpoint — one place for auth, versioning, governance;
tools update without touching agent code.

```
Direct-attach (fine for prototypes):  agent.tools = [WebSearchTool(), ...]
Toolbox (production path):            agent.tools = [MCPTool(toolbox_endpoint)]
```

```python
toolbox = project.toolboxes.create_toolbox_version(
    name="web-search-toolbox",
    description="Toolbox with the web search tool",
    tools=[WebSearchTool()],
)
# Toolbox exposes an MCP-compatible endpoint:
#   {PROJECT_ENDPOINT}/toolboxes/{toolbox.name}/versions/{toolbox.version}/mcp?api-version=v1
# Attach that endpoint to any agent as an MCPTool.
```

**Memory:** *Toolbox = curated bundle → one MCP endpoint → attach once, share across agents.*

### Function-calling loop (used in L09, L11, L18)

```
User sends message
        ↓
Model generates tool_call (name + args)
        ↓
YOUR APP executes the function
        ↓
YOUR APP sends result back on the same conversation
        ↓
Model generates the final answer
```

**Exam trap:** The model does NOT execute function tools. It requests the
call; your app runs the function and returns the output. Built-in tools
(Web Search, File Search, Code Interpreter) run inside Foundry — those
you don't execute.

---

## Agent SDK ladder — pick the right one

```
Complexity / Control
↑
│  LangGraph              StateGraph + ToolNode; conditional edges;
│                         human-in-the-loop; complex state routing
│
│  LangChain              create_agent(); rich chain ecosystem;
│                         AzureChatOpenAI + local tools
│
│  Microsoft Agent        agent-framework SDK; FoundryChatClient;
│  Framework (hosted)     same code local vs Foundry-managed container
│
│  Prompt Agent           PromptAgentDefinition; fully managed;
│  (Foundry native)       Foundry stores + versions the agent
↓
Simplicity / Managed
```

| SDK | Use when |
|-----|---------|
| **Prompt Agent** (Foundry native) | Simple task-focused agent; Foundry manages hosting. Default choice. |
| **Hosted Agent** (`agent-framework`) | Need portable Python code with a managed runtime; `FoundryChatClient` gives you keyless Foundry access. |
| **LangChain** | Existing LangChain chains/tools you want to reuse. Familiar ecosystem. |
| **LangGraph** | Multi-step stateful graph with conditional edges; human-in-the-loop gates; failure recovery. |

---

## Foundry Memory — cross-session knowledge

Session state (`conversation_id`) lasts one conversation. **Memory** persists
across conversations for a given user.

```
Extraction     → system pulls key info from turns (preferences, facts, context)
      ↓
Consolidation  → LLM merges duplicates, resolves conflicts (new allergy overrides old)
      ↓
Retrieval      → search memory store for relevant items before/during conversation
```

### 3 long-term memory types

| Type | What it stores | When to retrieve |
|------|---------------|-----------------|
| **User Profile Memory** | Durable preferences (language, product defaults, allergies) | At conversation start (stable personalization) |
| **Chat Summary Memory** | Distilled summaries of prior conversation topics | Per turn (continuity context) |
| **Procedural Memory** | Reusable how-to routines from prior interactions | When user asks for a recurring workflow |

**Memory:** *User Profile = who; Chat Summary = what happened; Procedural = how to do it.*

### Usage modes

| Mode | How | When |
|------|-----|------|
| **Memory Search Tool** | Attach tool to Prompt Agent | Recommended; agent reads/writes automatically |
| **Memory Store APIs** | Low-level CRUD on memory items | Full control; direct lifecycle management |

**Quotas:** 100 scopes per store · 10,000 memories per scope · 1,000 req/min.

**Security:** Memory stores are vulnerable to prompt injection (attacker
plants malicious instructions). Always run Content Safety + Prompt Shields on
memory inputs and outputs (Domain 1 L08–L10).

---

## RAG paths compared

| Path | When | Infrastructure | Where in this repo |
|------|------|---------------|--------------------|
| **File Search tool** | Prototype, small doc set, zero-infra | Foundry manages blob + vector store | L06 |
| **AI Search tool** | Production, large corpus, custom indexing | Azure AI Search + skillset | Domain 5 |
| **Manual client RAG** | Full control, custom chunking/reranking | Your code + AI Search SDK or FAISS | L22 (FAISS example) |

```
User query
      │
  Retrieve (AI Search / File Search / FAISS)
      ↓
  Top-K documents
      ↓
  Augment (inject into prompt as context)
      ↓
  Generate (model produces grounded answer)
      ↓
  Answer with citations
```

---

## Workflows — deterministic orchestration

> ⚠️ **DEPRECATION** — Microsoft Foundry is **retiring workflows on
> December 1, 2026**. For NEW work, use **Microsoft Agent Framework
> workflows** ([`/agent-framework/user-guide/workflows/`](https://learn.microsoft.com/agent-framework/user-guide/workflows/orchestrations/overview)).
> The lessons here (L15, L16) still work today; treat the YAML as
> knowledge that transfers to the Agent Framework, not the long-term
> platform. Source: [`agents/concepts/workflow.md`](../.context/azure-ai-docs/articles/foundry/agents/concepts/workflow.md).

Workflows are UI-built (or YAML-editable) graphs Foundry runs deterministically.
Use them for compliance-sensitive, repeatable, auditable orchestrations.

**Node types — portal UI names:**

| Node | Purpose |
|------|---------|
| **Agent** | Invoke an agent (registered Prompt Agent by name). |
| **Logic** | Control flow — `if/else`, `go to`, `for each`. |
| **Data transformation** | Set / parse variables (e.g. capture an agent's structured output into `Local.X`). |
| **Basic chat** | Send a message or ask the user a question mid-workflow. |

**Node types — underlying YAML kinds (what you see when editing the file):**

| YAML `kind` | Portal equivalent |
|-------------|-------------------|
| `OnConversationStart` | Trigger (workflow entry point) |
| `InvokeAzureAgent` | Agent node |
| `ConditionGroup` | Logic node (if/else branching) |
| `EndConversation` | Terminal |

**Workflow patterns (portal templates):**

| Pattern | When |
|---------|------|
| **Sequential** | Result of agent A feeds into agent B, in a fixed order. Pipelines. |
| **Group chat** | Dynamic handoff between agents based on context or rules. Escalation, fallback. |
| **Human in the loop** | Wait for user input mid-workflow. Approvals, clarifying questions. |

**Workflow vs agent-as-tool:**

| | Workflow (YAML) | Agent-as-tool (L18) |
|--|-----------------|--------------------|
| Control flow | Deterministic, predefined | Dynamic, model decides |
| Branching | Explicit conditions | Model judgment |
| Human gates | Built-in approval / basic chat | Custom logic |
| Best for | Compliance, known process | Flexible, exploratory |
| Hosted-agent support | ✘ (portal designer only supports Prompt Agents) | ✓ (any agent) |

---

## Evaluators

### RAG evaluators (key 3)

| Evaluator | Inputs | What it scores |
|-----------|--------|---------------|
| **Groundedness** | answer, source docs | Grounded in sources? Score 1–5 (model-based) |
| **Groundedness Pro** | answer, source docs | Binary pass/fail; no model deployment needed |
| **Response Completeness** | question, answer, ground truth | Covered required points? |

### 11 built-in agent evaluators

Source: [`concepts/evaluation-evaluators/agent-evaluators.md`](../.context/azure-ai-docs/articles/foundry/concepts/evaluation-evaluators/agent-evaluators.md)

| Evaluator | What it scores |
|-----------|---------------|
| **Task Adherence** | Agent follows task per system instructions |
| **Task Completion** | Agent completed the task end-to-end |
| **Intent Resolution** | Agent correctly identified + addressed user intent |
| **Customer Satisfaction** | Holistic: helpfulness, clarity, tone, resolution |
| **Task Navigation Efficiency** | Steps match optimal/expected path |
| **Tool Call Accuracy** | Right tool + right args (overall quality) |
| **Tool Selection** | Most appropriate tool chosen |
| **Tool Input Accuracy** | All params correct: grounded, type, format, complete |
| **Tool Output Utilization** | Tool output correctly used in response/next calls |
| **Tool Call Success** | All tool calls executed without technical failures |
| **Quality Grader** | Multi-dimension single evaluator (relevance, abstention, completeness, groundedness, context coverage) |

Combine for coverage: `Tool Call Accuracy + Task Adherence + Intent Resolution + Quality Grader + Risk & Safety`.

---

# Lesson 01 — First API Call

**You'll learn:** the minimum viable Responses API call — keyless auth via `DefaultAzureCredential`, one prompt, one answer.
**Prereqs:** `.env` filled, `az login`, `Foundry User` role.
**Time:** ~3 min.

**Concept:** `client.responses.create()` is the one API you'll call in almost
every lesson. This file makes one call with just a model and an input string,
prints the answer. Zero tools, zero conversations — the "hello world."

**Code:**

```python
# 01_first_api_call.py
from _shared.openai_client import openai_client
from _shared.config import settings


def main() -> None:
    client = openai_client()
    response = client.responses.create(
        model=settings().default_model,
        input="What are the three main benefits of using managed AI endpoints in the cloud?",
    )
    print("answer:", response.output_text)


if __name__ == "__main__":
    main()
```

**Expected output:**

```
answer: 1. Scalability — Azure automatically scales the endpoint to match demand...
        2. Security — managed identity and RBAC replace API keys...
        3. Compliance — regional endpoints keep data inside the required jurisdiction...
```

**Key points:**
- `openai_client()` (from `_shared/`) points at `AZURE_OPENAI_ENDPOINT/openai/v1` — the OpenAI SDK subdomain.
- `settings().default_model` = the deployment name from `.env` (`DEFAULT_MODEL`).
- If this fails with 401 → RBAC (Domain 1 L07). With 404 → deployment name mismatch (Domain 1 L06).

---

# Lesson 02 — Model Behavior (Temperature)

**You'll learn:** how temperature controls output variety; deterministic vs creative regimes; that same prompt + same model can yield very different answers.
**Prereqs:** L01 works.
**Time:** ~3 min.

**Concept:** `temperature` scales the sampling entropy. `0.0` = greedy
decoding (deterministic; same prompt → same output). `1.0` = default. `2.0`
= high entropy (creative, sometimes nonsensical). `top_p` is an alternative
knob (nucleus sampling) — use one or the other, not both.

**Code:**

```python
# 02_model_behavior.py
from _shared.openai_client import openai_client
from _shared.config import settings


def creative_tagline(temperature: float) -> str:
    client = openai_client()
    r = client.responses.create(
        model=settings().default_model,
        instructions="You are a creative copywriter.",
        input="Write a two-sentence tagline for a new AI-powered productivity app.",
        temperature=temperature,
    )
    return r.output_text


def main() -> None:
    for t in (0.0, 1.0, 2.0):
        print(f"\n--- temperature={t} ---")
        print(creative_tagline(t))


if __name__ == "__main__":
    main()
```

**Expected output:** three taglines. `t=0` is safe/predictable; `t=1` is
balanced; `t=2` is often weird or off-topic.

**Key points:**
- Use `temperature=0` for structured output, classification, math — anything you want reproducible.
- Use `temperature=0.7–1.0` for creative writing.
- Reasoning models (o-series) IGNORE `temperature` — they use `reasoning.effort` instead (see L03).

---

# Lesson 03 — Reasoning (`reasoning.effort=high`)

**You'll learn:** how to invoke a reasoning-tier model (o-series) with elevated compute budget for hard multi-step problems.
**Prereqs:** a reasoning-tier deployment exists (`REASONING_MODEL` in `.env`, e.g. `o4-mini`).
**Time:** ~5 min.

**Concept:** Reasoning models "think" internally (produce reasoning tokens
the user doesn't see) before answering. `reasoning.effort` controls how much
thinking budget the model gets: `low` / `medium` / `high`. Higher = better
answers on hard problems, higher token cost, slower response.

**Code:**

```python
# 03_reasoning.py
from _shared.openai_client import openai_client
from _shared.config import settings

_PROBLEM = """
A distributed e-commerce system is experiencing intermittent checkout failures
during peak traffic. The failures appear random, affect roughly 3 percent of the
transactions, and only occur when inventory checks and payment processing run
concurrently. Identify the most likely root cause and propose a solution.
"""


def main() -> None:
    client = openai_client()
    response = client.responses.create(
        model=settings().reasoning_model,
        instructions="You are a senior software architect.",
        input=_PROBLEM,
        reasoning={"effort": "high"},
    )
    print(response.output_text)


if __name__ == "__main__":
    main()
```

**Expected output:** a structured diagnosis pointing at a race condition
between inventory reservation and payment authorization; a solution proposal
around idempotency keys or distributed locks.

**Key points:**
- Reasoning tokens count toward billing but aren't returned in `output_text`.
- Only o-series models honor `reasoning.effort`. gpt-4.x etc. ignore it.
- Cost/latency scales with effort — don't use `high` for trivia.

---

# Lesson 04 — Web Search Tool

**You'll learn:** attach the built-in Web Search tool to a Responses API call; get real-time grounded answers with citations.
**Prereqs:** L01 works. Web Search enabled on your Foundry region (check tool catalog).
**Time:** ~5 min.

**Concept:** `{"type": "web_search"}` in `tools=` lets the model perform Bing
searches during the call. The model decides whether to search (`tool_choice="auto"`),
performs the query itself, and threads the results into its answer. You get
citations for free — no glue code.

**Code:**

```python
# 04_web_search_tool.py
from _shared.openai_client import openai_client
from _shared.config import settings


def main() -> None:
    client = openai_client()
    response = client.responses.create(
        model=settings().default_model,
        instructions="You are a helpful research assistant. Always cite your sources.",
        input="What are the latest developments in AI regulation in the European Union?",
        tools=[{"type": "web_search"}],
        tool_choice="auto",
    )
    print(response.output_text)


if __name__ == "__main__":
    main()
```

**Expected output:** a summary of recent EU AI Act developments with inline
citation URLs.

**Key points:**
- `tool_choice="auto"` → model decides. `"required"` → forces a search.
- Config type string is `"web_search"` (aka Bing Grounding under the hood).
- L10 wraps the same tool inside a registered Prompt Agent so it's reusable across apps.

---

# Lesson 05 — Code Interpreter

**You'll learn:** the model can write AND execute Python in an isolated sandbox; how to inspect both the code it wrote and the numeric result.
**Prereqs:** L01 works. Code Interpreter enabled on your Foundry region.
**Time:** ~5 min.

**Concept:** `{"type": "code_interpreter", "container": {"type": "auto"}}`
gives the model a scratch Python environment. Unlike a plain LLM answer to a
math question (which is prone to arithmetic mistakes), the model writes
Python and Foundry runs it — the answer comes from actual execution.

**Code:**

```python
# 05_code_interpreter.py
from _shared.openai_client import openai_client
from _shared.config import settings


def main() -> None:
    client = openai_client()
    response = client.responses.create(
        model=settings().default_model,
        instructions="You are a data analyst. Use Python to calculate precisely.",
        input="What is the compound interest on $10,000 at 5 percent annual rate over 10 years?",
        tools=[{"type": "code_interpreter", "container": {"type": "auto"}}],
    )
    for item in response.output:
        if item.type == "code_interpreter_call":
            print("=== Python Code the Model Wrote ===")
            print(item.code)
            print("\n=== Output from Execution ===")
            print(item.outputs)
        elif item.type == "message":
            print("\n=== Final Answer ===")
            print(response.output_text)


if __name__ == "__main__":
    main()
```

**Expected output:** the model prints a small Python snippet using the
compound-interest formula, executes it, and returns ~$16,288.95.

**Key points:**
- `response.output` is a **list** — Code Interpreter emits `code_interpreter_call` events alongside `message` events.
- Sandbox is stateless per call unless you attach files to a container.
- Perfect for: math, plotting, CSV crunching, deterministic data transforms.

---

# Lesson 06 — File Search Tool (RAG without infra)

**You'll learn:** RAG via the built-in File Search tool — Foundry handles upload, chunking, embedding, retrieval; you just attach a vector store id.
**Prereqs:** L01 works; `_shared/sample_data/northwind_policies/*.pdf` present (already in repo).
**Time:** ~10 min (first run uploads PDFs).

**Concept:** Two objects: `files` (uploaded raw docs) and `vector_stores`
(indexed embeddings). Create both, then attach `{"type": "file_search",
"vector_store_ids": [vs.id]}` to a Responses API call. The model retrieves
relevant chunks automatically, cites them in the answer.

**Code:**

```python
# 06_file_search_tool.py
from pathlib import Path
from _shared.config import SAMPLE_DATA, settings
from _shared.openai_client import openai_client


def main() -> None:
    client = openai_client()

    # Upload the Northwind policy PDFs
    files = []
    for pdf in sorted((SAMPLE_DATA / "northwind_policies").glob("*.pdf")):
        f = client.files.create(file=Path(pdf).open("rb"), purpose="assistants")
        files.append(f.id)
        print(f"uploaded: {pdf.name} → {f.id}")

    vs = client.vector_stores.create(name="northwind-policies", file_ids=files)
    print(f"vector store: {vs.id}")

    r = client.responses.create(
        model=settings().default_model,
        input="What is the refund window for the Northwind Pro plan?",
        tools=[{"type": "file_search", "vector_store_ids": [vs.id]}],
        tool_choice="auto",
    )
    print("\n=== Answer ===")
    print(r.output_text)
```

**Expected output:** upload log per PDF; final answer citing the specific
policy PDF and refund window.

**Key points:**
- Use File Search for prototyping and small corpora. For production/large corpora, use the **Azure AI Search** tool (Domain 5).
- Vector stores are reusable — you can attach the same one to many agents.
- Uploaded files persist across calls; clean them up with `client.files.delete(id)` after experiments.

---

# Lesson 07 — Structured Output (`json_schema` + `strict`)

**You'll learn:** guarantee the model's output matches a JSON schema; the difference between "advisory" JSON (asking nicely) and "strict" (mechanically enforced).
**Prereqs:** L01 works.
**Time:** ~10 min.

**Concept:** `text={"format": {"type": "json_schema", "strict": True, ...}}`
constrains the token sampler — the response is provably valid against the
schema (nested objects, enums, required fields, no extras). This is what
makes generative extraction production-grade instead of "usually right."

**Code:**

```python
# 07_structured_output.py
import json
from _shared.openai_client import openai_client
from _shared.config import settings

_TICKET = """
Subject: VPN disconnect issue - escalation needed
Hi team, this is Sarah Chen from Acme Logistics writing in again about
ticket TKT-1042. Our Gold-tier SLA promises a 4 hour response time, and
we are now at hour 6 with no update. The VPN client keeps dropping every
10 minutes on our Windows fleet since the rollout of Northwind Connect
v3.2 last Tuesday. If this isn't resolved by end of day Friday we will
be requesting the $500 SLA breach credit outlined in our contract.
"""

_SYSTEM = "You are a text analysis engine for Northwind support tickets."

_SCHEMA = {
    "type": "object",
    "properties": {
        "entities": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "category": {
                        "type": "string",
                        "enum": ["person","organization","date","product",
                                 "ticket_id","sla_tier","monetary_amount"],
                    },
                },
                "required": ["text","category"],
                "additionalProperties": False,
            },
        },
        "topics": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["entities","topics"],
    "additionalProperties": False,
}


def main() -> None:
    client = openai_client()
    r = client.responses.create(
        model=settings().default_model,
        input=[
            {"type": "message", "role": "system", "content": _SYSTEM},
            {"type": "message", "role": "user", "content": _TICKET},
        ],
        text={"format": {"type": "json_schema", "name": "ticket_extraction",
                          "schema": _SCHEMA, "strict": True}},
    )
    result = json.loads(r.output_text)
    print("=== Entities ===")
    for e in result["entities"]:
        print(f"  [{e['category']}] {e['text']}")
    print("\n=== Topics ===")
    for t in result["topics"]:
        print(f"  - {t}")
```

**Expected output:** a table of entities (Sarah Chen / Acme Logistics / TKT-1042 / Gold / $500 / …) and a list of topics.

**Key points:**
- `strict: True` requires the schema to have `additionalProperties: false` and every property in `required`.
- Enums narrow the model's choices dramatically — use them liberally.
- Non-strict schemas are hints, not guarantees. Strict = production.

---

# Lesson 08 — Create a Prompt Agent

**You'll learn:** register a Prompt Agent in Foundry (model + instructions + tool schemas) and get an `agent_reference`-callable name.
**Prereqs:** L01 works. Domain 1 L07 auth passing.
**Time:** ~5 min.

**Concept:** `client.agents.create_version(agent_name=..., definition=PromptAgentDefinition(...))`
registers (or bumps the version of) a named agent. The agent lives in your
Foundry project; any other lesson (or any other app) can invoke it via
`extra_body={"agent_reference": {"name": AGENT_NAME}}`. Run this once,
consume from anywhere.

**Code:**

```python
# 08_prompt_agent_create.py
from azure.ai.projects.models import FunctionTool, PromptAgentDefinition
from _shared.foundry_client import project_client
from _shared.config import settings

AGENT_NAME = "IT-HelpDesk-Agent"

_TOOLS = [
    FunctionTool(
        name="get_password_reset_steps",
        description="Get the company password reset steps.",
        parameters={"type": "object", "properties": {}, "required": [],
                     "additionalProperties": False},
        strict=True,
    ),
    FunctionTool(
        name="get_vpn_troubleshooting_steps",
        description="Get troubleshooting steps for VPN connection issues.",
        parameters={"type": "object", "properties": {}, "required": [],
                     "additionalProperties": False},
        strict=True,
    ),
    FunctionTool(
        name="get_software_install_guide",
        description="Get installation instructions for a supported software package.",
        parameters={
            "type": "object",
            "properties": {"software_name": {"type": "string"}},
            "required": ["software_name"],
            "additionalProperties": False,
        },
        strict=True,
    ),
]


def main() -> None:
    client = project_client()
    agent = client.agents.create_version(
        agent_name=AGENT_NAME,
        definition=PromptAgentDefinition(
            model=settings().default_model,
            instructions=(
                "You are an IT support assistant for Northwind. "
                "Help users with password resets, VPN issues, and software installation. "
                "Call your tools when you need company-specific information."
            ),
            tools=_TOOLS,
        ),
    )
    print(f"Agent created: id={agent.id} name={agent.name} version={agent.version}")
```

**Expected output:** `Agent created: id=... name=IT-HelpDesk-Agent version=1`
(or higher if you've run before).

**Key points:**
- `create_version` is idempotent-ish: running twice bumps the version, doesn't error.
- `FunctionTool` describes the function schema; you'll implement the actual Python in L09.
- `strict=True` on the tool schema makes the model's arguments provably valid.

---

# Lesson 09 — Invoke a Prompt Agent + Execute its Functions

**You'll learn:** call the registered agent, receive function-call requests, execute your local Python, feed results back, get the final answer.
**Prereqs:** L08 has been run (agent exists).
**Time:** ~10 min.

**Concept:** The full agentic loop with an external function tool:

```
user → agent → function_call event → YOUR APP runs the function →
function_call_output → agent → final answer
```

The agent's version is fetched dynamically (no more hardcoded `v1` — omitting
`version` from `agent_reference` gets the latest).

**Code:**

```python
# 09_prompt_agent_invoke.py
import json
from _shared.foundry_client import project_client
from _shared.helpdesk_functions import (
    get_password_reset_steps, get_software_install_guide, get_vpn_troubleshooting_steps,
)

AGENT_NAME = "IT-HelpDesk-Agent"

_LOCAL_FUNCTIONS = {
    "get_password_reset_steps": lambda **_: get_password_reset_steps(),
    "get_vpn_troubleshooting_steps": lambda **_: get_vpn_troubleshooting_steps(),
    "get_software_install_guide": lambda software_name: get_software_install_guide(software_name),
}


def _run_local(name: str, arguments: dict) -> str:
    fn = _LOCAL_FUNCTIONS.get(name)
    return fn(**arguments) if fn else f"Unknown function: {name}"


def _agent_ref() -> dict:
    return {"type": "agent_reference", "name": AGENT_NAME}


def main() -> None:
    project = project_client()
    openai = project.get_openai_client()

    conversation = openai.conversations.create()
    print(f"conversation: {conversation.id}")

    first = openai.responses.create(
        conversation=conversation.id,
        input="My VPN keeps disconnecting. What should I do?",
        extra_body={"agent_reference": _agent_ref()},
    )

    tool_outputs = []
    for item in first.output:
        if item.type == "function_call":
            args = json.loads(item.arguments)
            print(f"→ tool: {item.name}({args})")
            tool_outputs.append({
                "type": "function_call_output",
                "call_id": item.call_id,
                "output": _run_local(item.name, args),
            })

    if tool_outputs:
        final = openai.responses.create(
            conversation=conversation.id,
            input=tool_outputs,
            extra_body={"agent_reference": _agent_ref()},
        )
        print("\n=== Final Answer ===")
        print(final.output_text)
    else:
        print(first.output_text)
```

**Expected output:** conversation id, a `→ tool:` line for
`get_vpn_troubleshooting_steps`, then a grounded final answer using the
returned steps.

**Key points:**
- The `conversation.id` is what threads the tool output back into the same context.
- **The model does NOT execute the function.** It emits a `function_call` event; your app runs the Python and returns the output.
- Omitting `version` = get latest. Domain 1 L11 fix pattern applied here.

---

# Lesson 10 — Prompt Agent with Web Search

**You'll learn:** register an agent whose tool is Web Search — the whole capability is now callable by name from any app.
**Prereqs:** L08 pattern understood; Web Search enabled on your region.
**Time:** ~5 min.

**Concept:** Same Web Search tool as L04, but bundled inside a registered
Prompt Agent instead of attached ad-hoc per call. Trade-off: register once,
call from anywhere, but you lose per-call flexibility.

**Code:**

```python
# 10_agent_web_search.py
from azure.ai.projects.models import PromptAgentDefinition, WebSearchTool
from _shared.foundry_client import project_client
from _shared.config import settings

AGENT_NAME = "web-search-lab-agent"


def main() -> None:
    client = project_client()
    agent = client.agents.create_version(
        agent_name=AGENT_NAME,
        definition=PromptAgentDefinition(
            model=settings().default_model,
            instructions=(
                "You are a helpful assistant. Use web search to answer questions "
                "that require current information. Always cite sources."
            ),
            tools=[WebSearchTool()],
        ),
    )
    print(f"Agent created: id={agent.id} name={agent.name} version={agent.version}")
```

**Expected output:** `Agent created: ... name=web-search-lab-agent version=1`.

**Key points:**
- `WebSearchTool()` is the SDK convenience wrapper around `{"type": "web_search"}`.
- No invocation in this file — see L18 multi-agent for how to consume a registered agent from another agent.
- Compare tool syntax: L04 uses the raw dict; L10 uses the typed helper. Same result.

---

# Lesson 11 — Full Agent + Function Tools (end-to-end)

**You'll learn:** the whole agentic loop in one file — create + invoke + execute functions. Same as L08+L09 combined.
**Prereqs:** L01 works.
**Time:** ~10 min.

**Concept:** This is what a production agent invocation looks like:
setup + tool schema + call + tool loop + final answer, all wired together.
If you understand this file end-to-end you understand every agent lesson
in this domain.

**Code:**

```python
# 11_agent_function_tools.py
import json
from azure.ai.projects.models import FunctionTool, PromptAgentDefinition
from _shared.config import settings
from _shared.foundry_client import project_client
from _shared.helpdesk_functions import (
    get_password_reset_steps, get_software_install_guide, get_vpn_troubleshooting_steps,
)

AGENT_NAME = "IT-HelpDesk-Agent-Demo"

_TOOLS = [
    FunctionTool(name="get_password_reset_steps", description="Company password reset steps.",
                 parameters={"type": "object", "properties": {}, "required": [], "additionalProperties": False}, strict=True),
    FunctionTool(name="get_vpn_troubleshooting_steps", description="VPN troubleshooting steps.",
                 parameters={"type": "object", "properties": {}, "required": [], "additionalProperties": False}, strict=True),
    FunctionTool(name="get_software_install_guide", description="Install guide for a supported software package.",
                 parameters={"type": "object", "properties": {"software_name": {"type": "string"}},
                              "required": ["software_name"], "additionalProperties": False}, strict=True),
]

_LOCAL = {
    "get_password_reset_steps": lambda **_: get_password_reset_steps(),
    "get_vpn_troubleshooting_steps": lambda **_: get_vpn_troubleshooting_steps(),
    "get_software_install_guide": lambda software_name: get_software_install_guide(software_name),
}


def main() -> None:
    project = project_client()
    agent = project.agents.create_version(
        agent_name=AGENT_NAME,
        definition=PromptAgentDefinition(
            model=settings().default_model,
            instructions=("You are the Northwind IT support assistant. "
                           "Call tools when you need company-specific information."),
            tools=_TOOLS,
        ),
    )
    ref = {"type": "agent_reference", "name": agent.name, "version": agent.version}
    openai = project.get_openai_client()
    conv = openai.conversations.create()

    first = openai.responses.create(
        conversation=conv.id,
        input="I need to install Slack and I forgot my password.",
        extra_body={"agent_reference": ref},
    )

    tool_outputs = []
    for item in first.output:
        if item.type == "function_call":
            args = json.loads(item.arguments)
            print(f"→ tool: {item.name}({args})")
            tool_outputs.append({
                "type": "function_call_output",
                "call_id": item.call_id,
                "output": _LOCAL[item.name](**args),
            })

    if tool_outputs:
        final = openai.responses.create(
            conversation=conv.id, input=tool_outputs,
            extra_body={"agent_reference": ref},
        )
        print("\n=== Final Answer ===")
        print(final.output_text)
    else:
        print(first.output_text)
```

**Expected output:** two `→ tool:` lines (Slack install + password reset), then a final answer combining both.

**Key points:**
- The model can call MULTIPLE tools in one turn — iterate `first.output` for all `function_call` events.
- `call_id` matches the request to the output — never guess or reorder.
- L18 extends this to agent-as-tool (multi-agent) using the same mechanic.

---

# Lesson 12 — OpenAPI Tool (Azure Function backend)

**You'll learn:** define an agent tool with an OpenAPI 3.x spec — Foundry auto-wraps each REST operation into a callable tool. No glue code.
**Prereqs:** `ORDERS_FN_ENDPOINT` set in `.env`; the Northwind Orders Function running locally or deployed.
**Time:** ~15 min (includes starting the Function).

**Concept:** Instead of writing `FunctionTool` schemas by hand, hand the
Foundry Agent Service an OpenAPI 3.0 spec. Every operation becomes a tool
whose description/parameters/response schema all come from the spec. The
model reads the operation descriptions to decide which endpoint to call.

**Setup (one-time):**

```bash
cd 02-generative-ai-and-agents/azure_functions_orders
func start                             # local; produces http://localhost:7071
# then in .env:
ORDERS_FN_ENDPOINT=http://localhost:7071
```

Deployed alternative: publish the Function to Azure and set
`ORDERS_FN_ENDPOINT=https://<your-func>.azurewebsites.net`.

**Code:**

```python
# 12_agent_openapi_tools.py (excerpt)
import json, os
from pathlib import Path
from azure.ai.projects.models import OpenApiAnonymousAuthDetails, OpenApiTool, PromptAgentDefinition
from _shared.config import settings
from _shared.foundry_client import project_client

AGENT_NAME = "northwind-orders-agent"
SPEC_PATH = Path(__file__).parent / "azure_functions_orders" / "northwind_spec.json"


def _load_spec_with_backend() -> dict:
    backend = os.environ.get("ORDERS_FN_ENDPOINT", "").rstrip("/")
    if not backend:
        raise SystemExit(
            "ORDERS_FN_ENDPOINT is not set in .env.\n"
            "  Local:    cd 02-generative-ai-and-agents/azure_functions_orders && func start\n"
            "            then set ORDERS_FN_ENDPOINT=http://localhost:7071 in .env"
        )
    spec = json.loads(SPEC_PATH.read_text())
    spec["servers"] = [{"url": f"{backend}/api"}]
    return spec


def main() -> None:
    spec = _load_spec_with_backend()
    tool = OpenApiTool(name="northwind_orders", spec=spec,
                       description="Read Northwind customer orders.",
                       auth=OpenApiAnonymousAuthDetails())
    client = project_client()
    agent = client.agents.create_version(
        agent_name=AGENT_NAME,
        definition=PromptAgentDefinition(
            model=settings().default_model,
            instructions=(
                "You are a Northwind operations assistant. Use the northwind_orders "
                "tools to answer questions about order status. If asked about an order "
                "you cannot find, say so — do not invent data."
            ),
            tools=[tool],
        ),
    )
    print(f"Agent {agent.name} v{agent.version} created — tools discovered from OpenAPI spec.")

    openai = client.get_openai_client()
    r = openai.responses.create(
        input="What is the status of order 1002?",
        extra_body={"agent_reference": {"type": "agent_reference",
                                          "name": agent.name, "version": agent.version}},
    )
    print(r.output_text)
```

**Expected output:** `Agent created` line, then the answer for order 1002
(status returned from the Function).

**Key points:**
- Backend URL is now read from `ORDERS_FN_ENDPOINT` — no more hardcoded stale URL in the spec.
- `OpenApiAnonymousAuthDetails()` = no auth. For production use `OpenApiConnectionAuthDetails` with an API key or managed identity.
- The `description` field on each spec operation is what the model uses to decide when to call it — write it for the model, not for humans.

---

# Lesson 13 — Conversation Threads

**You'll learn:** how server-managed conversations preserve context; passing the same `conversation.id` = agent remembers previous turns.
**Prereqs:** L01 works. (Agent is now created inline — no separate setup step.)
**Time:** ~5 min.

**Concept:** `openai.conversations.create()` returns a conversation object.
Pass its `.id` on `responses.create(conversation=...)` and Foundry threads
turns for you — you don't resend history. New id → blank slate. Compare
with Memory (L14) which is cross-conversation.

**Code:**

```python
# 13_conversation_thread.py
from azure.ai.projects.models import PromptAgentDefinition
from _shared.config import settings
from _shared.foundry_client import project_client

AGENT_NAME = "northwind-support-agent-conv"

_INSTRUCTIONS = (
    "You are Northwind customer support. Answer briefly and professionally. "
    "If asked about a specific order, remember the order id across turns."
)


def _ref() -> dict:
    return {"type": "agent_reference", "name": AGENT_NAME}


def _ensure_agent(project) -> None:
    project.agents.create_version(
        agent_name=AGENT_NAME,
        definition=PromptAgentDefinition(
            model=settings().default_model, instructions=_INSTRUCTIONS,
        ),
    )


def main() -> None:
    project = project_client()
    _ensure_agent(project)
    openai = project.get_openai_client()

    sara = openai.conversations.create()
    print(f"conversation.id: {sara.id}")

    first = openai.responses.create(
        conversation=sara.id,
        input="My order #4521 is late.",
        extra_body={"agent_reference": _ref()},
    )
    print("\nturn 1:", first.output_text)

    followup = openai.responses.create(
        conversation=sara.id,
        input="Any update on it?",  # server-side history knows which order
        extra_body={"agent_reference": _ref()},
    )
    print("\nturn 2:", followup.output_text)
```

**Expected output:** turn 1 acknowledges order #4521. Turn 2's answer knows
"it" = #4521 without you re-sending the id.

**Key points:**
- `_ensure_agent()` creates-or-versions the agent so this file runs cold. Same fix pattern as Domain 1 L11.
- Conversation state is server-side — you can't inspect the raw transcript, just the ids.
- `conversation_id` ≠ `thread_id` (Assistants API). Don't mix up.

---

# Lesson 14 — Foundry Memory (Cross-Session)

**You'll learn:** persistent knowledge that survives across conversations for a given user; the 3-phase pipeline (Extraction → Consolidation → Retrieval).
**Prereqs:** L13 works. **Memory feature enabled on the agent via portal** (see below).
**Time:** ~10 min.

**Concept:** Two conversations, same `user_id`. Turn 1 tells the agent
something durable ("I'm allergic to dairy"). Turn 2, in a fresh conversation,
asks a question that should recall the fact if Memory extraction and
retrieval fired. Contrast with L13's conversation thread — that only
remembers within one session.

**Portal step (one-time, required):** Foundry portal → your project →
Agents → this agent → Memory tab → **Enable**. Without the portal toggle,
this script runs but Memory won't persist. There is no SDK-only path
today (Memory is preview).

**Code:**

```python
# 14_foundry_memory.py
from azure.ai.projects.models import PromptAgentDefinition
from _shared.config import settings
from _shared.foundry_client import project_client

AGENT_NAME = "northwind-support-with-memory"

_INSTRUCTIONS = (
    "You are Northwind customer support. Remember relevant user facts "
    "(dietary restrictions, preferences, contact preferences) so you can "
    "reference them in later conversations for the same user."
)

_USER_ID = "user-sarah-chen"
_TURN_1 = "For the record: I'm allergic to dairy. Please note it on my account."
_TURN_2 = "In a NEW conversation: what dietary restrictions should our on-site team know about?"


def _ref() -> dict:
    return {"type": "agent_reference", "name": AGENT_NAME}


def _ensure_agent(project) -> None:
    project.agents.create_version(
        agent_name=AGENT_NAME,
        definition=PromptAgentDefinition(
            model=settings().default_model, instructions=_INSTRUCTIONS,
        ),
    )


def main() -> None:
    project = project_client()
    _ensure_agent(project)
    openai = project.get_openai_client()

    # --- Conversation 1: teach the agent something durable ---
    conv1 = openai.conversations.create(metadata={"user_id": _USER_ID})
    r1 = openai.responses.create(
        conversation=conv1.id, input=_TURN_1,
        extra_body={"agent_reference": _ref(), "user_id": _USER_ID},
    )
    print("[conv 1]", r1.output_text)

    # --- Conversation 2: brand new thread; memory retrieval should surface the fact ---
    conv2 = openai.conversations.create(metadata={"user_id": _USER_ID})
    r2 = openai.responses.create(
        conversation=conv2.id, input=_TURN_2,
        extra_body={"agent_reference": _ref(), "user_id": _USER_ID},
    )
    print("\n[conv 2]", r2.output_text)
```

**Expected output:** turn 1 acknowledges the allergy. Turn 2 (fresh
conversation, same user) mentions the dairy allergy — IF Memory is enabled.

**Key points:**
- Memory is per-USER, not per-conversation. `user_id` is the join key.
- 3-phase pipeline: extraction pulls facts → consolidation merges duplicates → retrieval surfaces them at the right moment.
- 3 memory types: **User Profile** (durable facts), **Chat Summary** (past conversations), **Procedural** (how-to routines).
- Quotas: 100 scopes/store · 10K memories/scope · 1K req/min.
- Security: memory stores are prompt-injection targets. Always pair with Content Safety + Prompt Shields (Domain 1 L08–L10).

---

# Lesson 15 — Workflow Intake Agent (Structured Output)

**You'll learn:** build the intake node of a Foundry Workflow — an agent whose Responses API call is bound to a strict JSON schema so downstream nodes can route deterministically.
**Prereqs:** L07 (structured output) understood. `workflows/wf_intake_schema.json` present.
**Time:** ~10 min.

**Concept:** A workflow needs its intake step to output STRUCTURED data
(category, boolean flags, ids) that later nodes can pattern-match on. This
is L07's `json_schema` pattern wrapped inside a registered agent — the
schema comes from `wf_intake_schema.json` so the workflow's YAML can
reference `Local.Triage.category`.

**Code:**

```python
# 15_workflow_intake.py
import json
from pathlib import Path
from azure.ai.projects.models import PromptAgentDefinition
from _shared.config import settings
from _shared.foundry_client import project_client

AGENT_NAME = "wf-IntakeAgent"
SCHEMA_FILE = Path(__file__).parent / "workflows" / "wf_intake_schema.json"

_SAMPLE_TICKET = (
    "Hi Northwind, I signed up for the Pro plan yesterday but I want to cancel "
    "and get my $99 back. The dashboard is much slower than the demo showed."
)


def main() -> None:
    schema_wrapper = json.loads(SCHEMA_FILE.read_text())
    project = project_client()
    agent = project.agents.create_version(
        agent_name=AGENT_NAME,
        definition=PromptAgentDefinition(
            model=settings().default_model,
            instructions=(
                "You are the Northwind support intake agent. Classify the customer's "
                "message into one triage result. Only output the JSON schema requested."
            ),
        ),
    )
    ref = {"type": "agent_reference", "name": agent.name, "version": agent.version}
    openai = project.get_openai_client()
    r = openai.responses.create(
        input=_SAMPLE_TICKET,
        extra_body={"agent_reference": ref},
        text={"format": {"type": "json_schema", **schema_wrapper}},
    )
    triage = json.loads(r.output_text)
    print("Triage result:", json.dumps(triage, indent=2))
```

**Expected output:** `{"category": "policy_question", "refund_related": true}`
(or `"service_issue"` depending on the sample).

**Key points:**
- The schema file is the CONTRACT between this agent and the workflow YAML.
- `text.format.type = "json_schema"` + the wrapper (name + strict) enforces compliance.
- L16 deploys the workflow that consumes this agent.

---

# Lesson 16 — Workflow Deploy (Conditional Routing)

**You'll learn:** deploy a Foundry Workflow (YAML) that routes based on the intake agent's structured output; auto-creates the two leaf agents (Knowledge + Ticket) so it runs cold.
**Prereqs:** L15 has been run (creates `wf-IntakeAgent`).
**Time:** ~10 min.

> ⚠️ Foundry workflows retire **December 1, 2026**. The pattern still holds
> and the code still works — just knowing you'll want to migrate to
> Microsoft Agent Framework workflows for anything long-lived.

**Concept:** Workflows are node graphs Foundry executes deterministically:

```
OnConversationStart
    → InvokeAzureAgent(wf-IntakeAgent) → Local.Triage
    → ConditionGroup:
          Local.Triage.category == "policy_question" → wf-KnowledgeAgent
          else                                        → wf-TicketAgent
    → EndConversation
```

Use workflows when the routing must be auditable + reproducible; use
multi-agent (L18) when you want the model to decide.

**Code:**

```python
# 16_workflow_conditional.py
from pathlib import Path
from azure.ai.projects.models import PromptAgentDefinition
from _shared.config import settings
from _shared.foundry_client import project_client

WORKFLOW_NAME = "wf-Triage"
WORKFLOW_FILE = Path(__file__).parent / "workflows" / "wf_triage.yml"

INTAKE = "wf-IntakeAgent"           # created by L15
KNOWLEDGE = "wf-KnowledgeAgent"
TICKET = "wf-TicketAgent"


def _ensure_leaf_agents(project) -> None:
    project.agents.create_version(
        agent_name=KNOWLEDGE,
        definition=PromptAgentDefinition(
            model=settings().default_model,
            instructions=("You are the Northwind Knowledge Base agent. "
                          "Answer product/policy questions concisely. "
                          "If the answer isn't in the general knowledge base, "
                          "say so and suggest opening a ticket."),
        ),
    )
    project.agents.create_version(
        agent_name=TICKET,
        definition=PromptAgentDefinition(
            model=settings().default_model,
            instructions=("You are the Northwind Ticket Intake agent. "
                          "Acknowledge the issue, collect any missing details you need, "
                          "then confirm that a ticket has been created."),
        ),
    )


def _verify_intake_exists(project) -> None:
    names = [a.name for a in project.agents.list()]
    if INTAKE not in names:
        raise SystemExit(f"{INTAKE} not found. Run L15 first.")


def main() -> None:
    client = project_client()
    _verify_intake_exists(client)
    _ensure_leaf_agents(client)

    yaml_text = WORKFLOW_FILE.read_text()
    workflow = client.agents.create_version(
        agent_name=WORKFLOW_NAME,
        definition={"kind": "workflow", "definition": yaml_text},
    )
    print(f"Workflow {workflow.name} v{workflow.version} deployed.")
    print("Test in the portal → Agents playground → wf-Triage.")
```

**Expected output:** `Workflow wf-Triage v1 deployed.` Test in the Foundry
portal Agents playground.

**Key points:**
- **Cold-boot fix:** L16 now creates `wf-KnowledgeAgent` + `wf-TicketAgent` inline; earlier versions crashed here.
- Workflow YAML node types (current): `OnConversationStart`, `InvokeAzureAgent`, `ConditionGroup`, `EndConversation`. See `agents/concepts/workflow.md`.
- Workflow SDK surface is preview; the `{"kind": "workflow", "definition": yaml_text}` shape matches `azure-ai-projects >= 1.0.0b10`.
- Portal designer + YAML stay in sync — edit either.

---

# Lesson 17 — Hosted Agent (Microsoft Agent Framework)

**You'll learn:** build an agent with the `agent-framework-foundry` SDK using `FoundryChatClient` — the same code runs locally and inside a Foundry-managed container.
**Prereqs:** `pip install agent-framework-foundry aiohttp`; `PROJECT_ENDPOINT` set in `.env`.
**Time:** ~10 min.

**Concept:** Hosted agents = your Python code, Foundry-managed runtime. Per
official docs this is the **recommended** path for anything beyond a Prompt
Agent (including the workflow replacement — see Workflows deprecation note
above). The SDK gives you `Agent` and chat clients (`FoundryChatClient` uses
`DefaultAzureCredential` under the hood). Same code portable across local dev
and Foundry container hosting — that's the value prop. `agent_framework`
itself is pulled in as a dependency of `agent-framework-foundry`.

**Code:**

```python
# 17_hosted_agent_framework.py
import asyncio
from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from azure.identity import DefaultAzureCredential
from _shared.config import settings


async def _run() -> None:
    chat_client = FoundryChatClient(
        project_endpoint=settings().project_endpoint,
        model=settings().default_model,
        credential=DefaultAzureCredential(),
    )
    agent = Agent(
        chat_client=chat_client,
        instructions=(
            "You are Northwind operations assistant. Be concise. "
            "If you need current info, ask the user for it — you have no tools yet."
        ),
    )
    result = await agent.run("Give me a one-line summary of Northwind's mission.")
    print(result.messages[-1].content)


def main() -> None:
    asyncio.run(_run())
```

**Expected output:** one sentence about Northwind's mission.

**Key points:**
- `FoundryChatClient` targets the project endpoint (services.ai.azure.com/api/projects/...) — same path as `project_client().get_openai_client()`.
- Agent Framework has its own tool + workflow APIs — the SDK's docs on Microsoft Learn are the source of truth.
- Use this over Prompt Agents when you need real code (databases, retries, custom logic) that instructions + tools can't express.

---

# Lesson 18 — Multi-Agent Coordination (Agent-as-Tool)

**You'll learn:** the router-plus-specialists pattern where a router agent treats other agents as callable tools; dynamic delegation without hardcoded routing.
**Prereqs:** L11 (function-tool loop) understood.
**Time:** ~15 min.

**Concept:** Wrap each specialist agent as a `FunctionTool` on the router.
The router decides which specialist to invoke per turn (model judgment).
Contrast with L16's YAML workflow where routing is defined explicitly. Use
this when the routing decision needs the flexibility of an LLM.

```
Router Agent
      │
      ├── ask_billing_specialist(question)  → invokes billing Prompt Agent
      └── ask_tech_specialist(question)     → invokes tech Prompt Agent
```

**Code (excerpt):**

```python
# 18_multi_agent_coord.py (main flow)
def _ensure_specialists(project) -> None:
    project.agents.create_version(
        agent_name=BILLING,
        definition=PromptAgentDefinition(
            model=settings().default_model,
            instructions="You are a Northwind billing specialist. Answer billing / refund questions only.",
        ),
    )
    project.agents.create_version(
        agent_name=TECHNICAL,
        definition=PromptAgentDefinition(
            model=settings().default_model,
            instructions="You are a Northwind technical specialist. Answer product / troubleshooting questions only.",
        ),
    )


def _delegate(project, target_agent: str, question: str) -> str:
    openai = project.get_openai_client()
    r = openai.responses.create(
        extra_body={"agent_reference": {"type": "agent_reference", "name": target_agent}},
        input=question,
    )
    return r.output_text


def main() -> None:
    project = project_client()
    _ensure_specialists(project)

    router = project.agents.create_version(
        agent_name=ROUTER,
        definition=PromptAgentDefinition(
            model=settings().default_model,
            instructions=("You are the Northwind support router. Read the customer's message and delegate "
                           "to the correct specialist via a tool call. Do not answer directly."),
            tools=_router_tools(),
        ),
    )
    # ... invoke router, capture function_call events, execute _delegate() for each,
    # pass function_call_output back on the same conversation, get final answer.
```

**Expected output:** `router → ask_billing_specialist({"question": "..."})`
line, then a final answer synthesized from the specialist's response.

**Key points:**
- Same function-tool loop as L09/L11 — the specialists are just wrapped in `FunctionTool` shells.
- Router shouldn't answer directly; enforce it in the system prompt.
- Compare with L16 workflow — L18 = dynamic; L16 = deterministic.

---

# Lesson 19 — Evaluators (Task Adherence + Tool Call Accuracy)

**You'll learn:** run built-in agent evaluators from `azure-ai-evaluation` on a real agent trace; interpret the returned scores.
**Prereqs:** `pip install azure-ai-evaluation`.
**Time:** ~10 min.

**Concept:** Foundry ships 11 agent evaluators (Task Adherence, Task
Completion, Intent Resolution, Customer Satisfaction, Task Navigation
Efficiency, Tool Call Accuracy, Tool Selection, Tool Input Accuracy, Tool
Output Utilization, Tool Call Success, Quality Grader). This lesson runs
two: Task Adherence (did the agent follow the system instructions?) and
Tool Call Accuracy (did it use the right tools with the right args?).

**Code:**

```python
# 19_evaluator_task_adherence.py
import json
from _shared.config import settings
from _shared.foundry_client import project_client
from _shared.openai_client import openai_client


def _run_agent_trace() -> dict:
    client = openai_client()
    r = client.responses.create(
        model=settings().default_model,
        instructions="You are a Northwind support agent. Answer briefly.",
        input="What is the refund window for a Pro plan? If you don't know, say so.",
    )
    return {
        "query": "What is the refund window for a Pro plan?",
        "response": r.output_text,
        "tool_calls": [],
        "system_message": "You are a Northwind support agent. Answer briefly.",
    }


def main() -> None:
    trace = _run_agent_trace()
    print("=== Trace ===")
    print(json.dumps(trace, indent=2))

    try:
        from azure.ai.evaluation import TaskAdherenceEvaluator, ToolCallAccuracyEvaluator
    except ImportError:
        raise SystemExit("pip install azure-ai-evaluation to run this lesson.")

    model_config = {
        "azure_endpoint": settings().foundry_endpoint,
        "azure_deployment": settings().default_model,
        "api_version": "2024-10-21",
    }
    task_adh = TaskAdherenceEvaluator(model_config=model_config)
    tool_acc = ToolCallAccuracyEvaluator(model_config=model_config)

    print("\n=== Task Adherence ===")
    print(task_adh(query=trace["query"], response=trace["response"]))

    print("\n=== Tool Call Accuracy ===")
    print(tool_acc(query=trace["query"], response=trace["response"], tool_calls=trace["tool_calls"]))
```

**Expected output:** the trace as JSON, then scored evaluations with
scores + reasoning per evaluator.

**Key points:**
- Evaluators use a **judge model** — `model_config` is the deployment they call.
- Combine 3–4 evaluators for full agent coverage: Task Adherence + Tool Call Accuracy + Intent Resolution + Quality Grader.
- Evaluators can be attached to CI/CD gates — Domain 1 L11 shows the inline self-critique variant.

---

# Lesson 20 — LangChain Agent (Foundry as Backend)

**You'll learn:** use LangChain's `create_agent()` with `ChatOpenAI` pointed at Foundry — same tool-calling pattern, familiar LangChain surface.
**Prereqs:** `pip install langchain langchain-openai`.
**Time:** ~10 min.

**Concept:** LangChain doesn't care that Foundry is on the other end — it's
just an OpenAI-compatible endpoint. `ChatOpenAI(base_url=<foundry>/openai/v1,
api_key=<token>)` gets you the model; `create_agent()` wires tools and the
reasoning loop. Use when your team already has LangChain chains/utilities.

**Code:**

```python
# 20_langchain_agent.py
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from _shared.config import settings

_SCOPE = "https://cognitiveservices.azure.com/.default"


@tool
def get_order_status(order_id: str) -> str:
    """Get the current status of a Northwind order by order ID."""
    orders = {"ORD-001": "Dispatched.", "ORD-002": "Processing.", "ORD-003": "Delivered."}
    return orders.get(order_id, f"Order {order_id} not found.")


@tool
def get_inventory(product_id: str) -> str:
    """Check the available inventory for a Northwind product by product ID."""
    return {"PRD-A1": "142 units.", "PRD-B2": "0 units.", "PRD-C3": "37 units."}.get(
        product_id, f"Product {product_id} not found.")


def main() -> None:
    s = settings()
    token_provider = get_bearer_token_provider(DefaultAzureCredential(), _SCOPE)
    model = ChatOpenAI(
        base_url=f"{s.foundry_endpoint}/openai/v1",
        api_key=token_provider(),
        model=s.default_model,
    )
    agent = create_agent(
        model=model, tools=[get_order_status, get_inventory],
        system_prompt=("You are a helpful Northwind operations assistant. "
                        "Use the available tools to answer questions accurately."),
    )
    response = agent.invoke(
        {"messages": [{"role": "user", "content":
            "What is the status of order ORD-002 and how many units of PRD-A1 do we have?"}]}
    )
    print(response["messages"][-1].content)
```

**Expected output:** the agent answers with both order status and stock level, invoking each tool.

**Key points:**
- Token is fetched fresh each run — if it expires, restart the process.
- LangChain's `@tool` decorator supersedes Foundry's `FunctionTool` in this stack — pick one convention per app.
- No Foundry-managed persistence — the agent lives in-process only.

---

# Lesson 21 — LangChain Tracing (App Insights)

**You'll learn:** attach `AzureAIOpenTelemetryTracer` to a LangChain agent so every model call + tool call ships as a span to Application Insights.
**Prereqs:** L20 works. `APPLICATIONINSIGHTS_CONNECTION_STRING` in `.env` (optional — script falls back to stdout without it).
**Time:** ~10 min.

**Concept:** Every LangChain callback is an observability hook. The
`AzureAIOpenTelemetryTracer` (from `langchain-azure-ai`) implements that
callback interface — attach it once and every step of the agent shows up
in Transaction Search tagged with `agent_id`. Without the connection
string, the script prints an explicit "stdout only" line and runs anyway.

**Code:**

```python
# 21_langchain_tracing.py (main flow)
def _build_tracer(connection_string: str):
    from langchain_azure_ai.callbacks.tracers import AzureAIOpenTelemetryTracer
    return AzureAIOpenTelemetryTracer(
        connection_string=connection_string,
        name="Northwind LangChain Ops Agent",
        agent_id="northwind-langchain-ops-agent",
        enable_content_recording=True,
    )


def main() -> None:
    s = settings()
    token_provider = get_bearer_token_provider(DefaultAzureCredential(), _SCOPE)
    model = ChatOpenAI(base_url=f"{s.foundry_endpoint}/openai/v1",
                        api_key=token_provider(), model=s.default_model)

    agent = create_agent(
        model=model, tools=[get_order_status, get_inventory],
        system_prompt="You are a helpful Northwind operations assistant. Use tools when needed.",
    )

    if s.app_insights_connection_string:
        agent = agent.with_config({"callbacks": [_build_tracer(s.app_insights_connection_string)]})
        destination = "Application Insights → Transaction Search (agent_id=northwind-langchain-ops-agent)"
    else:
        destination = "stdout only — set APPLICATIONINSIGHTS_CONNECTION_STRING in .env to ship spans"

    r = agent.invoke({"messages": [{"role": "user",
                                     "content": "Status of ORD-002 and stock of PRD-A1?"}]})
    print(r["messages"][-1].content)
    print(f"\n→ Traces: {destination}")
```

**Expected output:** the agent's answer, then a `→ Traces:` line pointing
either at App Insights or telling you to configure the env var.

**Key points:**
- `enable_content_recording=True` includes prompt + response text in spans — turn off in prod if you're worried about PII exposure in App Insights.
- Fallback to stdout matches Domain 1 L12's tracing pattern. No `SystemExit` for missing telemetry config.
- Traces show every LangChain step (retriever, tool call, model call) as its own span with parent/child relationships.

---

# Lesson 22 — LangGraph Stateful Agent (FAISS RAG)

**You'll learn:** LangGraph's `StateGraph` + `ToolNode` + `MessagesState` for stateful agents with conditional edges; a working RAG pattern using a local FAISS index over PDFs.
**Prereqs:** `pip install langgraph langchain-community faiss-cpu pypdf`.
**Time:** ~15 min.

**Concept:** LangGraph models an agent as a directed graph of nodes with
conditional edges. `MessagesState` is the required state type for
tool-calling agents (it holds the message list). Use this when the flow
needs conditional branches, retries, or human-in-the-loop gates that a
linear `create_agent()` can't express.

Not production RAG — for production, index into Azure AI Search (Domain 5).
This lesson is about the **graph orchestration** pattern.

**Code:**

```python
# 22_langgraph_agent.py (core structure)
def main() -> None:
    model, embeddings = _clients()
    vector_store = _build_vector_store(embeddings)

    @tool
    def search_northwind_policies(query: str) -> str:
        """Search Northwind policy documents (AUP, refund, SLA)."""
        hits = vector_store.similarity_search(query, k=3)
        if not hits:
            return "No relevant policy information found."
        return "\n\n".join(
            f"[Excerpt {i} from {d.metadata.get('source', 'policy')}]\n{d.page_content}"
            for i, d in enumerate(hits, 1)
        )

    tools = [search_northwind_policies]
    model_with_tools = model.bind_tools(tools)

    def call_model(state: MessagesState) -> dict:
        system = {"role": "system", "content": (
            "You are the Northwind policy assistant. Answer using search_northwind_policies. "
            "Ground answers in retrieved excerpts. Say so if you cannot find the answer.")}
        return {"messages": [model_with_tools.invoke([system] + state["messages"])]}

    def should_continue(state: MessagesState) -> str:
        return "tools" if state["messages"][-1].tool_calls else END

    graph = (
        StateGraph(MessagesState)
        .add_node("call_model", call_model)
        .add_node("tools", ToolNode(tools))
        .add_edge(START, "call_model")
        .add_conditional_edges("call_model", should_continue)
        .add_edge("tools", "call_model")
        .compile()
    )

    for question in [
        "What is the refund window for a Northwind Pro subscription?",
        "What uptime does Northwind guarantee for Enterprise customers?",
        "Can I mine cryptocurrency on Northwind compute resources?",
    ]:
        result = graph.invoke({"messages": [{"role": "user", "content": question}]})
        print(f"Q: {question}\nA: {result['messages'][-1].content}")
```

**Expected output:** three Q/A pairs. First two ground in policy PDFs; third
(crypto mining) grounds in the AUP.

**Key points:**
- `MessagesState` is REQUIRED for tool-calling — custom state schemas won't work with `ToolNode`.
- Conditional edge (`should_continue`) is what makes it a graph — it routes to `tools` or `END` based on model output.
- The `tools → call_model` back-edge is what creates the tool-loop pattern.
- FAISS index is in-process; for production use AI Search + persisted embeddings.

---

# Common Exam Traps

| Trap | Truth |
|------|-------|
| "File Search is the same as AI Search" | ❌ — File Search = Foundry-managed blob + vector store; AI Search = full pipeline with skillsets |
| "Use `thread_id` to continue a conversation" | ❌ — Responses API uses `conversation_id`. `thread_id` is Assistants API |
| "The model executes function tools" | ❌ — Model *requests* the call; YOUR APP executes it and returns the result |
| "LangGraph works without MessagesState" | ❌ — `MessagesState` is required for tool-calling agents |
| "MCP connects M×N apps and tools" | ❌ — MCP reduces to M+N (that's the point) |
| "Model Router always uses the cheapest model" | ❌ — It selects the *best* model per prompt; may pick expensive one |
| "Toolbox is just another MCP server" | ❌ — Toolbox is a managed layer that groups tools and exposes them via one MCP endpoint |
| "A2A is the same as OpenAPI tool" | ❌ — A2A = agent-to-agent protocol; OpenAPI = REST API |
| "Foundry Memory stores conversation history" | ❌ — Memory stores distilled long-term knowledge (profile / summaries / procedures). Raw history = conversation |
| "Prompt Agent version is stable" | ❌ — Every `create_version` bumps it. Omit `version` in `agent_reference` to get latest |
| "There are only 7 built-in tools" | ❌ — **12 built-in tools** today (Web Search, Code Interpreter, Custom Code Interpreter, File Search, Azure AI Search, Azure Functions, Function calling, Image Generation, Browser Automation, Computer Use, Fabric, SharePoint) plus **3 custom** (MCP, OpenAPI, A2A) plus **Toolbox** as the recommended packaging layer |
| "Workflow YAML uses `step` and `end`" | ❌ — Portal node model: Agent / Logic / Data transformation / Basic chat. YAML kinds: `OnConversationStart`, `InvokeAzureAgent`, `ConditionGroup`, `EndConversation` |
| "Foundry workflows are the recommended long-term orchestration" | ❌ — **Retiring December 1, 2026.** New work → Microsoft Agent Framework workflows |
| "Tools attach directly to agents in production" | ❌ — Direct-attach is fine for prototypes; **Toolbox is the recommended path** for production (one MCP endpoint, centralized auth) |

---

> The 30-second cheat sheet lives at the [top of this README](#30-second-domain-2-cheat-sheet)
> — scroll up any time an exam question makes you second-guess which lesson covers it.
