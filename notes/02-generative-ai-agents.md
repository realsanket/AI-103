# Domain 2 — Implement Generative AI and Agentic Solutions (30–35%)

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

## The 6 tool types

```
Agent Tools
│
├── 🌐 Web Search        → live internet results (Bing)
├── 📁 File Search       → semantic search over uploaded files (Foundry managed)
├── 🐍 Code Interpreter  → isolated Python sandbox, executes code
├── ⚙️  Function          → your own Python function (app executes it)
├── 📋 OpenAPI           → any REST API described by an OpenAPI 3.x spec
└── 🔌 MCP               → Model Context Protocol server (tools + resources + prompts)
```

## Tool comparison

| Tool | Who executes | Data lives | Config |
|------|-------------|-----------|--------|
| Web Search | Bing API | Internet | `{"type": "bing_grounding"}` |
| File Search | Foundry | Managed blob | `{"type": "file_search", "vector_store_ids": [...]}` |
| Code Interpreter | Foundry sandbox | Ephemeral | `{"type": "code_interpreter"}` |
| Function | **Your app** | Anywhere | JSON schema describing args |
| OpenAPI | **Your backend** | Your service | OpenAPI 3.0/3.1 spec JSON |
| MCP | MCP server | MCP server | Server URL + auth |

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

## The three layers

```
Agent Memory
│
├── Conversation Thread (session-scoped)
│     └── pass conversation_id to Responses API
│         lost when session ends
│
├── Session Context (in-memory RAM)
│     └── variables in your running process
│         lost when process restarts
│
└── Foundry Memory (cross-session persistent)
      └── enable on AIProjectClient
          stored in Foundry project
          survives restarts and new sessions
          use: extract → consolidate → retrieve
```

## Foundry Memory API pattern

```python
client = AIProjectClient(...)
# enable memory on the project
# memory.extract()    → pull key facts from conversation
# memory.consolidate() → deduplicate + summarize stored facts
# memory.retrieve()   → fetch relevant memories for current query
```

Memory: **Thread = RAM; Foundry Memory = disk.**

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

## Quick reference table

| Evaluator | Required inputs | What it scores |
|-----------|----------------|---------------|
| **Response Completeness** | question, answer, checklist | Coverage of required points |
| **Groundedness** | answer, source docs | Answer stays within sources |
| **Task Adherence** | agent trace, task definition | Agent followed its goal |
| **Tool Call Accuracy** | tool calls, expected calls | Right tool called with right args |

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
