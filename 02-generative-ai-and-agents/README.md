# Domain 2 — Implement Generative AI and Agentic Solutions (30-35%)

Largest exam domain — most files.

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
| 09 | `09_prompt_agent_invoke.py` | Invoke agent (Responses API + thread) |
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
| — | `azure_functions_orders/` | OpenAPI-described Function backing tool 12 |
| — | `northwind_mcp/` | Custom MCP server as Azure Function |
| — | `workflows/` | JSON + YAML workflow definitions |

## Run

```bash
uv run python 02-generative-ai-and-agents/01_first_api_call.py
```

For agent files: run `08_prompt_agent_create.py` once (creates the agent version), then `09_prompt_agent_invoke.py` to talk to it.

## Reference docs

- [Foundry Agent Service](../.context/azure-ai-docs/articles/foundry/agents/overview.md)
- [Responses API](../.context/azure-ai-docs/articles/foundry/agents/quickstarts/responses-api.md)
- [Hosted agents](../.context/azure-ai-docs/articles/foundry/agents/concepts/hosted-agents.md)
- [Memory](../.context/azure-ai-docs/articles/foundry/agents/concepts/what-is-memory.md)
- [Workflows / YAML reference](../.context/azure-ai-docs/articles/foundry/agents/concepts/agent-yaml-reference.md)
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

# Responses API

## Anatomy of a call

```python
response = client.responses.create(
    model="gpt-4.1-mini",        # deployment name
    instructions="You are ...",  # system prompt (agent instructions)
    input="User message",        # current user turn
    tools=[...],                 # list of tool configs
    conversation_id="conv-123",  # OPTIONAL: pass to continue a thread
)
print(response.output_text)      # the model's text reply
print(response.model)            # which model was actually used (important for Model Router)
```

## Key fields

| Field | Purpose |
|-------|---------|
| `instructions` | System prompt / agent persona |
| `input` | User message (string or list of content parts) |
| `tools` | List of tool definitions |
| `conversation_id` | Pass back to continue the same conversation thread |
| `output_text` | The final text response |
| `output` | Full output list (includes tool call events) |
| `usage.input_tokens` | Tokens consumed by the input |
| `usage.output_tokens` | Tokens generated in the response |

Memory: **Responses API = one call for everything; `conversation_id` keeps threads.**

---

# Tool Taxonomy

## The 7 tool types ([tool-catalog.md](../.context/azure-ai-docs/articles/foundry/agents/concepts/tool-catalog.md))

```
Agent Tools
│
├── Built-in (service executes)
│     ├── Web Search        → live internet results (Bing)
│     ├── File Search       → semantic search over uploaded files (Foundry managed)
│     ├── Code Interpreter  → isolated Python sandbox, executes code
│     └── Function          → your own Python function (YOUR app executes it)
│
└── Custom (you host)
      ├── OpenAPI           → any REST API described by an OpenAPI 3.x spec
      ├── MCP               → Model Context Protocol server (tools + resources + prompts)
      └── A2A (preview)     → Agent-to-Agent; connect to other agents via A2A endpoints
```

## Tool comparison

| Tool | Category | Who executes | Config |
|------|----------|-------------|--------|
| Web Search | Built-in | Bing API | `{"type": "bing_grounding"}` |
| File Search | Built-in | Foundry | `{"type": "file_search", "vector_store_ids": [...]}` |
| Code Interpreter | Built-in | Foundry sandbox | `{"type": "code_interpreter"}` |
| Function | Built-in | **Your app** | JSON schema describing args |
| OpenAPI | Custom | **Your backend** | OpenAPI 3.0/3.1 spec JSON |
| MCP | Custom | MCP server | Server URL + auth |
| A2A (preview) | Custom | Target agent | A2A-compatible endpoint |

## Toolbox — recommended tool management layer

```
Without Toolbox:  each agent wires its own tools → duplicated auth, no governance
With Toolbox:     one MCP-compatible endpoint → agents consume approved tools centrally

Lifecycle: Build → Discover (tool search) → Consume (single endpoint) → Govern (guardrails, auth)
```

```python
toolbox = project.toolboxes.create_toolbox_version(
    name="web-search-toolbox",
    tools=[WebSearchTool()],
)
# Attach toolbox to agent as MCPTool — exposes all toolbox tools automatically
```

Memory: **Toolbox = centralized tool shelf; agents consume via MCP endpoint.**

### Function calling loop

```
User sends message
        ↓
Model generates tool_call (name + args)
        ↓
YOUR APP executes the function
        ↓
YOUR APP sends result back via conversation
        ↓
Model generates final answer
```

### MCP mental model

```
WITHOUT MCP:  M apps × N tools = M×N custom integrations
WITH MCP:     M apps + N tool servers = M+N connections

Protocol: Host → Client → Server
          (app)  (SDK)   (your tool server)
```

---

# Agent SDK Comparison

## The 4 options

```
Complexity / Control
↑
│  LangGraph          StateGraph + ToolNode; failure recovery;
│                     human-in-the-loop; complex conditional logic
│
│  LangChain          create_agent(); rich chain ecosystem;
│                     AzureChatOpenAI + tools
│
│  Hosted Agent       agent-framework SDK; FoundryChatClient;
│  Framework          runs on Foundry infrastructure; managed
│
│  Prompt Agent       PromptAgentDefinition; fully managed;
│                     Foundry creates + hosts the agent
↓
Simplicity / Managed
```

## When to use each

| SDK | Use when |
|-----|---------|
| **Prompt Agent** (Foundry native) | Simple task-focused agent; Foundry manages hosting |
| **Hosted Agent (agent-framework)** | Need `FoundryChatClient` + Azure identity; managed runtime |
| **LangChain** | Existing LangChain chains/tools to integrate; familiar ecosystem |
| **LangGraph** | Multi-step stateful graph; human-in-the-loop gates; recovery on failure |

### LangGraph must-know

```python
from langgraph.graph import StateGraph, MessagesState
from langgraph.prebuilt import ToolNode

# MessagesState is required as state type for tool-calling agents
graph = StateGraph(MessagesState)
graph.add_node("agent", agent_node)
graph.add_node("tools", ToolNode(tools))
```

---

# Memory Types

## Short-term vs long-term

```
Short-term: session conversation context → managed by orchestration framework
Long-term:  Foundry Memory (cross-session persistent, [what-is-memory.md](../.context/azure-ai-docs/articles/foundry/agents/concepts/what-is-memory.md))
```

## Foundry Memory — 3 phases

```
Extraction     → system pulls key info from conversation (preferences, facts, context)
      ↓
Consolidation  → LLM merges duplicates, resolves conflicts (e.g. new allergy overrides old)
      ↓
Retrieval      → search memory store for relevant items before/during conversation
```

## 3 long-term memory types

| Type | What it stores | When to retrieve |
|------|---------------|-----------------|
| **User Profile Memory** | Durable preferences, language, product defaults | At conversation start (stable personalization) |
| **Chat Summary Memory** | Distilled summaries of prior conversation topics | Per turn (continuity context) |
| **Procedural Memory** | Reusable how-to routines from prior interactions | When user asks for a recurring workflow |

## Usage modes

| Mode | How | When |
|------|-----|------|
| **Memory Search Tool** | Attach tool to Prompt Agent | Recommended; agent reads/writes automatically |
| **Memory Store APIs** | Low-level CRUD on memory items | Full control; direct lifecycle management |

## Quotas

Max scopes per store: 100 · Max memories per scope: 10,000 · Search/Update: 1,000 req/min

## Security

Memory stores are vulnerable to prompt injection (attacker stores malicious instructions). Mitigate with Content Safety + Prompt Shields on all memory inputs/outputs.

Memory: **User Profile = who; Chat Summary = what happened; Procedural = how to do it.**

---

# RAG Paths

## Three approaches compared

| Path | When | Infrastructure | Lesson |
|------|------|---------------|--------|
| **File Search tool** | Prototype, small doc set, zero-infra | Foundry manages blob + vector store | `02/06_file_search_tool.py` |
| **AI Search tool** | Production, large corpus, custom indexing | AI Search service + skillset | `05/07_rag_agent_search_tool.py` |
| **Manual client RAG** | Full control, custom chunking/reranking | Your code + AI Search SDK | `05/08_rag_client_run.py` |

## RAG anatomy

```
User query
      │
  Retrieve (AI Search / File Search)
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

# Workflows

## Anatomy of a Foundry workflow

```
wf_triage.yml
│
├── Step 1: Intake Agent
│     └── collects: issue_type, severity, customer_tier
│         outputs structured JSON (wf_intake_schema.json)
│
├── Step 2: Conditional Branch
│     └── if issue_type == "billing"  → Knowledge Agent
│         else                        → Ticket Agent
│
└── Step 3: End
```

- YAML + portal designer stay in sync (edit either)
- Human checkpoint = approval step between workflow stages
- Workflow = deterministic orchestration; agents = autonomous reasoning

---

# Multi-Agent Patterns

## Agent-as-tool delegation

```
Orchestrator Agent
      │
      ├── delegate to Specialist Agent A (via agent tool)
      │         └── "Answer billing questions"
      │
      └── delegate to Specialist Agent B (via agent tool)
                └── "Handle technical support"
```

## Workflow orchestration vs agent delegation

| | Workflow (YAML) | Agent-as-tool |
|--|----------------|--------------|
| Control flow | Deterministic, predefined | Dynamic, model decides |
| Branching | Explicit conditions | Model judgment |
| Human gates | Built-in approval steps | Requires custom logic |
| Best for | Known process, compliance | Flexible routing |

---

# Evaluators

## RAG evaluators (key 3)

| Evaluator | Inputs | What it scores |
|-----------|--------|---------------|
| **Groundedness** | answer, source docs | Grounded in sources? Score 1–5 (model-based) |
| **Groundedness Pro** | answer, source docs | Binary pass/fail; no model deployment needed |
| **Response Completeness** | question, answer, ground truth | Covered required points? |

## Agent evaluators — all 11 ([built-in-evaluators.md](../.context/azure-ai-docs/articles/foundry/concepts/built-in-evaluators.md))

| Evaluator | What it scores |
|-----------|---------------|
| **Task Adherence** | Agent follows task per system instructions |
| **Task Completion** | Agent completed task end-to-end |
| **Intent Resolution** | Agent correctly identified and addressed user intent |
| **Customer Satisfaction** | Holistic satisfaction: helpfulness, clarity, tone, resolution |
| **Task Navigation Efficiency** | Steps match optimal/expected path |
| **Tool Call Accuracy** | Right tool + right args (overall quality) |
| **Tool Selection** | Most appropriate tool chosen |
| **Tool Input Accuracy** | All params correct: grounded, type, format, complete |
| **Tool Output Utilization** | Tool output correctly used in response/next calls |
| **Tool Call Success** | All tool calls executed without technical failures |
| **Quality Grader** | Multi-dimension single evaluator (relevance, abstention, completeness, groundedness, context coverage) |

Combine for comprehensive coverage: `Tool Call Accuracy + Task Adherence + Intent Resolution + Rubric + Risk&Safety`

## Self-critique loop pattern (`11_evaluator_groundedness.py`)

```
Step 1: Agent generates draft answer
        ↓
Step 2: Second call critiques draft
        → Returns COMPLETE or MISSING
        ↓
Step 3: if MISSING → regenerate with critique as context
        if COMPLETE → return draft
```

Memory: **Generate → Critique → Regenerate. Stop when COMPLETE.**

---

# Structured Output

```python
response = client.responses.create(
    model=model,
    input=prompt,
    text={
        "format": {
            "type": "json_schema",
            "name": "ticket",
            "strict": True,          # ← guarantees schema compliance
            "schema": {
                "type": "object",
                "properties": {
                    "ticket_id": {"type": "string"},
                    "priority": {"type": "string", "enum": ["low","medium","high"]},
                },
                "required": ["ticket_id", "priority"],
                "additionalProperties": False,
            },
        }
    },
)
```

`strict: True` = schema is mechanically enforced (not advisory). Model WILL match the schema.

---

# Observability

## Span attributes to set

```python
with tracer.start_as_current_span("agent.call") as span:
    span.set_attribute("model", model_name)
    # ... make the call ...
    span.set_attribute("tokens.input",  usage.input_tokens)
    span.set_attribute("tokens.output", usage.output_tokens)
    span.set_attribute("tokens.total",  usage.input_tokens + usage.output_tokens)
    span.set_attribute("latency_ms",    round(elapsed * 1000, 1))
    span.set_attribute("safety.hate",   safety_scores["hate"])
    span.set_attribute("safety.violence", safety_scores["violence"])
```

## Exporter setup

```python
from azure.monitor.opentelemetry import configure_azure_monitor
configure_azure_monitor()   # reads APPLICATIONINSIGHTS_CONNECTION_STRING from env
```

Without it: spans go to stdout. With it: spans appear in Application Insights → Transaction Search.

---

# Prompt Engineering Cheat Sheet

| Technique | When |
|-----------|------|
| **System prompt** (`instructions`) | Set persona, constraints, format |
| **Few-shot examples** | Improve consistency for specific output format |
| **Temperature 0** | Deterministic, factual, structured output |
| **Temperature 0.7–1.0** | Creative, varied responses |
| **top_p** | Alternative to temperature; nucleus sampling |
| **Chain-of-thought** | "Think step by step" for reasoning tasks |
| **Structured output** (`json_schema`) | When schema compliance is required |

---

# Common Exam Traps

| Trap | Truth |
|------|-------|
| "File Search is the same as AI Search" | ❌ — File Search = Foundry-managed blob; AI Search = full pipeline with skillsets |
| "Use `thread_id` to continue a conversation" | ❌ — Responses API uses `conversation_id` |
| "The model executes function tools" | ❌ — Model *requests* the call; YOUR APP executes it |
| "LangGraph works without MessagesState" | ❌ — `MessagesState` is required as state schema for tool-calling |
| "MCP connects M×N apps and tools" | ❌ — MCP reduces to M+N (that's the benefit) |
| "Model Router always uses the cheapest model" | ❌ — It selects the *best* model for each prompt; may use expensive one |
| "Toolbox is just another MCP server" | ❌ — Toolbox is a managed layer on top of MCP; exposes multiple tools via one endpoint with centralized auth/governance |
| "A2A is the same as OpenAPI tool" | ❌ — A2A = agent-to-agent communication; OpenAPI = external REST API |
| "Foundry Memory stores conversation history" | ❌ — Memory stores distilled long-term knowledge (user profile, summaries, procedures); raw history = conversation thread |

---

# 30-Second Domain 2 Trick

```
Consuming a model?          → Responses API (client.responses.create)
Building an agent?          → Prompt Agent → agent-framework → LangChain → LangGraph
Adding tools?               → Web Search / File Search / Code Interpreter / Function / OpenAPI / MCP
Need conversation memory?   → pass conversation_id (session) or Foundry Memory (persistent)
Grounding in documents?     → File Search (small) or AI Search (production)
Multi-agent?                → agent-as-tool (dynamic) or YAML workflow (deterministic)
Evaluating quality?         → Groundedness / Completeness / Task Adherence / Tool Call Accuracy
Monitoring?                 → OpenTelemetry spans → Application Insights
```
