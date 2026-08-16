# Azure AI Foundry: Guardrails, Tracing, Monitoring & Evaluation

> Written from official Foundry docs. Direct, no fluff. Every service name, SDK call, and portal path is exact.
>
> **Reading order:** Big Picture → Guardrails → Tracing → Monitoring → Evaluation → How it all connects

---

## The Big Picture — 30 Seconds

```
Every request flows through this pipeline:

  USER INPUT
      ↓
  [GUARDRAILS — input scan]          ← blocks jailbreaks, hate, PII before model sees it
      ↓
  MODEL / AGENT RUNS
    ↓ agent calls a tool?
  [GUARDRAILS — tool call scan]      ← blocks misaligned tool calls (preview)
    ↓ tool returns data?
  [GUARDRAILS — tool response scan]  ← blocks indirect attacks in tool responses (preview)
      ↓
  [GUARDRAILS — output scan]         ← blocks harmful/copyrighted content in final response
      ↓
  RESPONSE SENT TO USER
      ↓  (async, after)
  [TRACING]                          ← records every step as OpenTelemetry spans → App Insights
      ↓  (aggregated over time)
  [MONITORING]                       ← dashboards, alerts, token usage, latency, error rate
      ↓  (offline, on a schedule)
  [EVALUATION]                       ← quality scores on dataset: groundedness, safety, coherence
```

| | Scope | Timing | Blocks traffic? |
|---|---|---|---|
| Guardrails | one request | real-time | **yes** |
| Tracing | one request | post-fact async | no |
| Monitoring | all requests | continuous | no |
| Evaluation | dataset | offline | no |

---

## PART 1 — GUARDRAILS

### What a Guardrail Is

A **guardrail** is a named collection of **controls**.

A **control** = (risk category) + (intervention point) + (response action).

Example: "Detect Violence at Medium severity on User input → Annotate and block."

Foundry uses classification models from **Azure AI Content Safety** under the hood.

---

### Risk Categories

| Risk | Models | Agents (Preview) | What it detects |
|---|---|---|---|
| **Hate / Unfairness** | ✅ | ✅ | Language targeting social groups (race, gender, religion) |
| **Sexual** | ✅ | ✅ | Explicit sexual content |
| **Violence** | ✅ | ✅ | Physical harm, weapons, threats |
| **Self-harm** | ✅ | ✅ | Instructions to harm oneself |
| **User Prompt Attacks** | ✅ | ✅ | Jailbreaks by the user ("ignore all previous instructions") |
| **Indirect Attacks (XPIA)** | ✅ | ✅ | Jailbreak injected inside a tool response or document |
| **Spotlighting** | ✅ | ❌ | Advanced prompt injection mitigation (models only, preview) |
| **Protected Material — Text** | ✅ | ✅ | Copyrighted text (song lyrics, articles, recipes) |
| **Protected Material — Code** | ✅ | ✅ | Licensed code in model output |
| **Groundedness** | ✅ | ❌ | Response not supported by source docs (models only, preview) |
| **PII** | ✅ | ✅ | Personally identifiable information |
| **Task Adherence** | ✅ | ✅ | Agent doing something the user did NOT ask for (preview) |

---

### Severity Levels

For Hate, Violence, Sexual, Self-harm — each has a 0–7 scale:

| Guardrail setting | Raw score that triggers block | What it allows through |
|---|---|---|
| **Off** | Nothing blocked (requires MS approval) | Everything |
| **Low** | score ≥ 2 | Only Very Low (0–1) passes |
| **Medium** *(default)* | score ≥ 4 | Low and below passes |
| **High** | score ≥ 6 | Medium and below passes |

Score meanings:
- 0–1 = Very Low (neutral/educational)
- 2–3 = Low (mild, not glorified)
- 4–5 = Medium (direct insults, graphic)
- 6–7 = High (inciting violence, illegal content)

---

### Four Intervention Points

| Point | Who | What it scans | Latency added |
|---|---|---|---|
| **User input** | Models + Agents | Prompt the user sent | ~50–100ms |
| **Tool call** *(Preview)* | Agents only | What agent sends TO a tool | ~50–100ms |
| **Tool response** *(Preview)* | Agents only | What tool returns TO agent | ~50–100ms |
| **Output** | Models + Agents | Final response to user | ~50–100ms |

> All 4 enabled = ~200–400ms overhead per request.

**Supported tools for tool call/response scanning:** Azure AI Search, Azure Functions, OpenAPI, SharePoint Grounding, Fabric Data Agent, Bing Grounding, Bing Custom Search, Browser Automation. Tools not in this list are NOT scanned at those points.

---

### Two Response Actions

| Action | Models | Agents | Effect |
|---|---|---|---|
| **Annotate** | ✅ | ❌ | Flags in API response. Does NOT block. Caller decides. |
| **Annotate and block** | ✅ | ✅ | Flags AND returns error. Request stops. |

---

### Guardrail Inheritance — Critical Rule

> **The agent's guardrail FULLY OVERRIDES the model's guardrail.**

Example: model has Violence=High, agent has Violence=Low + no tool call/response controls:
- User input: Violence Low ✓
- Tool calls: NOT scanned (no control configured)
- Tool responses: NOT scanned
- Output: Violence Low ✓
- Model's Violence=High → zero effect on that agent

**Defaults:**
- Models: `Microsoft.DefaultV2` auto-assigned
- Agents with no custom guardrail: inherits model's guardrail
- Agents with custom guardrail: uses that guardrail exclusively

---

### Task Adherence — Guardrail for Agent Misalignment

Detects when the agent is about to do something the user did NOT ask for.

**Real examples:**
- User: "show me my calendar" → agent plans `clear_calendar_events()` → **BLOCK**
- User: "check my data usage" → agent plans `change_data_plan()` → **BLOCK**
- User: "write a draft email" → agent plans `send_email()` → **BLOCK** (no explicit send instruction)

**API response:**
```json
{
  "taskRiskDetected": true,
  "details": "Agent attempts to share a document externally without user request or confirmation."
}
```

**REST call:**
```
POST <endpoint>/contentsafety/agent:analyzeTaskAdherence?api-version=2024-12-15-preview
```

Body: `tools` (tool definitions list) + `messages` (conversation + tool calls history).

Limits: 100,000 char max. English primary. Data may route to US/EU regions.

---

### Guided Guardrail Setup — Questionnaire-Based

Don't know which controls to pick? Answer 3 questions → Foundry recommends the right guardrails.

**Portal:** Build → Agents → select agent → Guardrails section → **Manage guardrail** → **Guided guardrails setup**

**Question set 1 — Who uses this agent?**
- Public users → stricter content safety, jailbreak protections
- Internal teams → lighter controls for trusted users

**Question set 2 — Input and data handling:**
- Where does input come from? (user messages / files / external APIs)
- Processes sensitive data? → enables PII detection
- Handles PII specifically? → enables data protection controls

**Question set 3 — Tools and actions:**
- Calls external tools? → enables tool response validation + spotlighting (indirect attack protection)
- Takes real-world actions (send email, modify records)? → enables task adherence + action validation
- Generates or executes code? → enables protected material detection + code safety

After answering → review recommended controls per intervention point → edit if needed → **Create guardrails**.

> Each agent needs its own guardrail. Never share one guardrail across agents with different use cases.

---

### Where to Configure Guardrails

- **Portal:** Foundry portal → project → **Guardrails + controls** tab
- **Try it out:** Guardrails + controls → **Try it out** → test inputs interactively
- **Task Adherence test:** Try it out → Agentic Workflow → Task Adherence
- **SDK:** create a policy object, assign to model deployment or agent

---

### Troubleshooting Guardrails

| Symptom | Cause | Fix |
|---|---|---|
| Agent ignoring guardrail | Still using model's guardrail | Explicitly assign guardrail to the agent |
| Preview risks not working on agent | Spotlighting/Groundedness not supported for agents yet | Expected — those controls only run on models |
| Legitimate content blocked | Severity threshold too restrictive | Lower severity or apply for modified filter from Microsoft |
| Tool calls not scanned | Tool not in supported list OR no tool call control configured | Check supported tools list; add tool call/response controls |

---

## PART 2 — TRACING

### What Tracing Is

Tracing records the complete execution of ONE request as a **span tree**. Each operation = one span. Spans nest to show the full call chain.

Built on **OpenTelemetry (OTel)** semantic conventions. Data ships async to **Azure Application Insights**.

Tracing NEVER blocks a request — it fires after the response is sent.

---

### Key Concepts

| Concept | What it is |
|---|---|
| **Trace** | Full journey of one request — root span + all child spans |
| **Span** | One operation: start time, end time, attributes, status |
| **Attributes** | Key-value pairs on a span: model name, token count, tool args, etc. |
| **Semantic conventions** | Standardized OTel attribute names (GenAI conventions) — consistent across frameworks |
| **Trace exporter** | Ships spans to App Insights. Async — does not block the request. |

---

### What a Trace Looks Like

```
[root] responses.create — 1.8s
  ├── [child] memory_search_call — 0.12s
  │     query: "What are my catering preferences?"
  │     result: [dairy-free, email updates]
  ├── [child] gpt-5.2 — 1.4s
  │     tokens: prompt=412  completion=92
  │     finish_reason: stop
  ├── [child] memory_command_preview_call — 0.06s
  │     action: remember
  │     content: "prefers dairy-free catering and email updates"
  └── [child] memory_command_preview_call_output — 0.01s
        status: completed
```

Every trace captures: user input, agent output, tool calls (name + args + result + latency), token counts, errors and retries.

---

### Three Tracing Modes

**1. Server-side (automatic — zero code change)**

Connect App Insights to your project → done. Foundry auto-traces all Prompt agents, Hosted agents, and Workflows. Available in portal → Traces tab within minutes. Best starting point for everyone.

**2. Client-side (instrument your own code)**

Use when you need spans on custom logic around the agent call.

```bash
pip install azure-ai-projects azure-identity opentelemetry-sdk \
            azure-core-tracing-opentelemetry azure-monitor-opentelemetry
```

```python
from azure.monitor.opentelemetry import configure_azure_monitor
from azure.ai.inference.tracing import AIInferenceInstrumentor

conn_str = project.telemetry.get_connection_string()
configure_azure_monitor(connection_string=conn_str)
AIInferenceInstrumentor().instrument()
# every chat_client.complete() or responses.create() now auto-generates spans
```

Disable auto-instrumentation of Responses/Conversations API (keep only explicit spans):
```python
import os
os.environ["AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API"] = "false"
# set BEFORE calling AIProjectInstrumentor().instrument()
```

Disable trace context propagation (if compliance requires it):
```python
AIProjectInstrumentor().instrument(enable_trace_context_propagation=False)
```

**3. Local (VS Code, no cloud)**

Install **Microsoft Foundry Toolkit** VS Code extension → spans go to a local OTLP collector. Works with OpenAI, Anthropic, LangChain, Foundry Agent Service. No Azure account needed for local dev.

---

### Framework Integrations

| Framework | How to enable tracing |
|---|---|
| Foundry Agent Service | Server-side: automatic. Client-side: `AIInferenceInstrumentor().instrument()` |
| LangChain | `from langchain_azure_ai.tracing import enable_azure_monitor_tracing` |
| LangGraph | Same as LangChain |
| Microsoft Agent Framework | Built-in OTel instrumentation |
| OpenAI Agents SDK | OTel integration built in |

All use W3C Trace Context + OTel GenAI semantic conventions — spans consistent across frameworks.

---

### Multi-Agent Tracing

For agent-to-agent systems, Foundry captures cross-agent spans:

| Span type | What it captures |
|---|---|
| `execute_task` | Task decomposition and dispatch to sub-agents |
| `agent_to_agent_interaction` | One agent calling another |
| `agent.state.management` | Memory updates, context management |
| `agent_planning` | Internal planning steps |
| `agent_orchestration` | Coordinator directing sub-agents |
| `execute_tool` | Tool invocation + arguments + result |

---

### Conversation View

Portal: Traces tab → search by Response ID or Trace ID → click a **Conversation ID** to see:
- Full turn-by-turn conversation history
- Ordered tool calls and run steps
- Token usage per response
- Inputs and outputs at each step

---

### Trace Replay — Step Through a Conversation

Visually replay any traced conversation step-by-step.

**Access:** Traces tab → click a Conversation ID or Trace ID → Replay Panel opens.

**Two views:**

| View | Best for |
|---|---|
| **Trajectories** | Hierarchical span tree with waterfall bars (duration OR token cost). Finding bottlenecks and failures. |
| **User** | Chat-style view of what the end user saw. Span tree available as collapsible panel alongside. |

**Playback controls:**
- Play → replays spans sequentially, highlighting each
- Skip → jump ahead
- 1x / 2x / 4x speed
- Timeline scrubber → jump to any moment without replaying from start

**Filter while replaying:**

| Filter | What it shows |
|---|---|
| By type: Chat / Agent / Tool / Conversation | Only matching span types |
| Token: Low (<500) / Medium (500–2k) / High (>2k) | Spot token hotspots |
| Find in trace | Search by span name |

**Use cases:** root cause analysis, token cost optimization, audit/compliance, debugging unexpected steps.

---

### Sensitive Content in Traces — AppGenAIContent Table

Traces capture prompts, system instructions, tool arguments, model responses — all potentially containing PII or PHI. Foundry isolates this into a dedicated protected table: `AppGenAIContent`.

**Migration deadline: September 30, 2026** — after this, Foundry stops writing the 7 sensitive attributes to `AppDependencies`/`AppTraces`/`AppEvents`. They exist ONLY in `AppGenAIContent`.

#### The 7 Sensitive Attributes

| OTel Attribute | Column in AppGenAIContent | Example value |
|---|---|---|
| `gen_ai.input.messages` | `InputMessages` | `[{"role":"user","content":"What is my balance?"}]` |
| `gen_ai.output.messages` | `OutputMessages` | `[{"role":"assistant","content":"$4,200"}]` |
| `gen_ai.system_instructions` | `SystemInstructions` | `"You are a banking assistant. Never reveal..."` |
| `gen_ai.tool.definitions` | `ToolDefinitions` | `[{"name":"get_balance","description":"..."}]` |
| `gen_ai.tool.call.arguments` | `ToolCallArguments` | `{"account_id":"ACC-12345"}` |
| `gen_ai.tool.call.result` | `ToolCallResult` | `{"balance":4200.00,"currency":"USD"}` |
| `gen_ai.evaluation.explanation` | `EvaluationExplanation` | `"Response correct but omits pending charges..."` |

Everything else (span names, durations, token counts, error codes) stays in regular tables — visible to `Log Analytics Reader`.

#### Step 1 — Register the Feature Flag

```bash
# Routes sensitive attrs to AppGenAIContent ONLY (not old tables)
az feature register --namespace Microsoft.Insights --name protectGenAISensitiveData

# Also propagate to provider
az provider register -n Microsoft.Insights

# Verify (takes a few minutes)
az feature show --namespace Microsoft.Insights --name protectGenAISensitiveData \
  --query "properties.state" -o tsv
# → Registered
```

Need more time after Sept 30, 2026 (buys until Sept 30, 2027 max):
```bash
az feature register --namespace Microsoft.Insights --name optOutProtectGenAISensitiveData
# Remove opt-out to re-enable protection:
az feature unregister --namespace Microsoft.Insights --name optOutProtectGenAISensitiveData
```

#### Step 2 — Set Table as Protected (Deny-by-Default)

CLI (`--protection-level` flag not available in older CLI versions — use REST):
```bash
WORKSPACE_ID=$(az monitor log-analytics workspace show \
  --resource-group <your-rg> \
  --workspace-name <your-workspace> \
  --query id -o tsv)

az rest \
  --method PATCH \
  --uri "https://management.azure.com${WORKSPACE_ID}/tables/AppGenAIContent?api-version=2023-09-01" \
  --body '{"properties":{"protectionLevel":"Protected"}}'
```

Portal: Azure portal → Log Analytics workspace → **Tables** → `AppGenAIContent` → **Manage table** → Protection level = **Protected**.

#### Step 3 — Grant Access to Authorized Users Only

```bash
# Grant to a specific user
az role assignment create \
  --role "Privileged Monitoring Data Reader" \
  --assignee <user-object-id-or-upn> \
  --scope $WORKSPACE_ID

# Prefer group assignment — manage via group membership
az role assignment create \
  --role "Privileged Monitoring Data Reader" \
  --assignee <group-object-id> \
  --scope $WORKSPACE_ID
```

Use PIM for JIT access — assign as eligible, not permanent.

#### What Each Role Sees

| Role | Span metadata (names, duration, tokens) | Prompts, responses, tool args |
|---|---|---|
| No role | ❌ | ❌ |
| `Log Analytics Reader` | ✅ | ❌ |
| `Privileged Monitoring Data Reader` | ✅ | ✅ |

#### Step 4 — Update KQL Queries Before Sept 30, 2026

**Before (breaks after migration):**
```kusto
AppDependencies
| where Data has "gen_ai.input.messages"
| extend prompt = tostring(Properties["gen_ai.input.messages"])
| project timestamp, prompt
```

**After (correct — use AppGenAIContent):**
```kusto
AppGenAIContent
| where TimeGenerated > ago(24h)
| extend
    prompt      = InputMessages,
    response    = OutputMessages,
    sys_prompt  = SystemInstructions,
    tool_args   = ToolCallArguments,
    tool_result = ToolCallResult
| project TimeGenerated, AgentName, ModelName, prompt, response, tool_args
| order by TimeGenerated desc
```

**Join sensitive content with non-sensitive span metadata:**
```kusto
let sensitive = AppGenAIContent
    | where TimeGenerated > ago(1h)
    | project TraceId, SpanId, InputMessages, OutputMessages, ToolCallArguments;
AppDependencies
| where TimeGenerated > ago(1h)
| where Type == "LLM"
| join kind=leftouter sensitive on $left.OperationId == $right.TraceId
| project TimeGenerated, Name, DurationMs, InputMessages, OutputMessages
| order by DurationMs desc
```

**Correlate prompts with user feedback scores:**
```kusto
let feedback = customEvents
    | where name == "gen_ai.evaluation.result"
    | extend
        score = todouble(customDimensions["gen_ai.evaluation.score.value"]),
        label = tostring(customDimensions["gen_ai.evaluation.score.label"]),
        traceId = tostring(operation_Id);
AppGenAIContent
| where TimeGenerated > ago(7d)
| join kind=leftouter feedback on $left.TraceId == $right.traceId
| summarize avg_score = avg(score), total = count() by bin(TimeGenerated, 1d)
| order by TimeGenerated desc
```

#### Migration Checklist (before Sept 30, 2026)

- [ ] Register `protectGenAISensitiveData` feature flag
- [ ] Run `az provider register -n Microsoft.Insights`
- [ ] Set `AppGenAIContent` protection level = Protected
- [ ] Assign `Privileged Monitoring Data Reader` to authorized users/groups only
- [ ] Audit all custom KQL queries reading 7 sensitive attrs from old tables
- [ ] Update alert rules referencing sensitive attributes
- [ ] Update workbooks/dashboards using those fields
- [ ] Verify: `Log Analytics Reader` user gets denied on `AppGenAIContent`
- [ ] Verify: `Privileged Monitoring Data Reader` user can query `AppGenAIContent`

**What does NOT change:**
- Span names, durations, token counts, error codes → still in `AppDependencies`/`AppTraces`
- Foundry portal Traces view → updated automatically
- Data ingested BEFORE Sept 30, 2026 → stays in old tables unchanged
- Retention policies → unchanged

---

### Logging End-User Feedback

Log thumbs up/down or star ratings tied to traces using OTel events:

```python
# Emit gen_ai.evaluation.result event
# Binary (thumbs): score = 0.0 (fail) or 1.0 (pass)
# Likert (stars):  score = 1.0–5.0, threshold = 3.0

# Required attributes:
# gen_ai.evaluation.score.value  → the numeric score
# gen_ai.evaluation.score.label  → "pass" or "fail"
# gen_ai.evaluation.name         → e.g. "thumbs_up"
# microsoft.gen_ai.human_evaluation.source → "end_user" or "builder"
```

Query feedback in App Insights:
```kusto
customEvents
| where name == "gen_ai.evaluation.result"
| extend
    eval_name  = tostring(customDimensions["gen_ai.evaluation.name"]),
    score      = todouble(customDimensions["gen_ai.evaluation.score.value"]),
    label      = tostring(customDimensions["gen_ai.evaluation.score.label"]),
    source     = tostring(customDimensions["microsoft.gen_ai.human_evaluation.source"])
| summarize
    total      = count(),
    pass_rate  = round(countif(label == "pass") * 100.0 / count(), 1),
    avg_score  = round(avg(score), 2)
  by eval_name, bin(timestamp, 1h)
| order by timestamp desc
```

---

### Permissions Required for Tracing

| What | Role needed |
|---|---|
| View traces in Foundry portal | Log Analytics Reader on App Insights resource |
| Query `AppGenAIContent` (sensitive content) | Privileged Monitoring Data Reader |
| Write traces (instrument code) | No role — uses App Insights connection string |

---

### Tracing Cost and Retention

- App Insights charges per GB ingested. Long prompts = bigger spans = higher cost.
- Default retention: 90 days (configurable per workspace)
- Reduce cost: configure sampling in App Insights for high-traffic apps

---

### Troubleshooting Tracing

| Symptom | Cause | Fix |
|---|---|---|
| No traces in portal | App Insights not connected, or no traffic | Connect App Insights in project settings; generate agent traffic |
| Auth error viewing traces | Missing Log Analytics Reader | Add role in IAM on App Insights resource |
| Client-side traces missing | `instrument()` not called before model calls | Ensure `AIInferenceInstrumentor().instrument()` runs first |
| Sensitive data in all traces | `protectGenAISensitiveData` not registered | Register feature flag + set table protection level |
| `AppGenAIContent` shows no data | Feature flag not yet registered or no traces flowed | Register flag, generate agent traffic, wait a few min |

---

## PART 3 — MONITORING

### What Monitoring Is

Monitoring = aggregating traces + metrics over time to answer "is the system healthy right now?"

Uses **Azure Monitor** + **Application Insights** (same resource as tracing). Foundry has a built-in **Agent Monitoring Dashboard**.

---

### Agent Monitoring Dashboard

**Portal:** Build → select agent → **Monitor** tab.

Requires: App Insights connected, Log Analytics Reader role.

**Summary cards (top):**
- Total requests
- Success rate
- Average latency
- Total tokens consumed
- Evaluation scores (if continuous eval configured)

**Time-series charts:**

| Chart | Alert when |
|---|---|
| Token usage | Spike > 2x baseline → unexpected cost or runaway loop |
| Latency p95 | > 10s → throttling or complex tool chains |
| Run success rate | < 95% → broken tools or guardrail over-blocking |
| Evaluation scores | Drop > 0.5 points → quality regression |
| Red team scan results | Any failure → active security risk |

---

### Ask AI on the Dashboard

Built-in natural language assistant for dashboard insights.

**Access:**
- Build → Models or Agents → Monitor → click **Ask AI** icon
- Operate → Overview → select predefined prompt from Ask AI banner

**Example questions:**
- "Give me a summary of the dashboard"
- "Analyze the performance trend"
- "What caused the latency spike on August 15?"

**What Ask AI returns:**
- Summary of current metrics for the selected time range
- Highlighted anomalies with annotated chart links (click → jumps to that chart with highlight)
- Recommended next steps

**Example recommendations Ask AI gives:**
- "Investigate latency increase on [date] — it might be recurring."
- "Optimize prompt token usage to reduce costs as usage scales."
- "Consider load testing to identify bottlenecks."

> Set the time range selector BEFORE asking — Ask AI only analyzes the currently visible range.

---

### Continuous Evaluation in Monitoring

Run evaluators on LIVE TRAFFIC automatically — not just offline before release.

**Scheduled evaluation** — fixed schedule (e.g. daily at 9 AM):
```python
from azure.ai.projects.models import RecurrenceTrigger, DailyRecurrenceSchedule, EvaluationScheduleTask

schedule = Schedule(
    display_name="Daily Agent Eval",
    enabled=True,
    trigger=RecurrenceTrigger(interval=1, schedule=DailyRecurrenceSchedule(hours=[9])),
    task=EvaluationScheduleTask(eval_id=eval_object.id, eval_run=eval_run_object),
)
project_client.beta.schedules.create_or_update(schedule_id="daily-eval", schedule=schedule)
```

**Continuous evaluation** — samples live traffic as it flows (event-driven):
```python
from azure.ai.projects.models import EvaluationRule, ContinuousEvaluationRuleAction, EvaluationRuleEventType

rule = project_client.evaluation_rules.create_or_update(
    id="my-continuous-eval",
    evaluation_rule=EvaluationRule(
        display_name="Live Traffic Eval",
        action=ContinuousEvaluationRuleAction(eval_id=eval_object.id, max_hourly_runs=100),
        event_type=EvaluationRuleEventType.RESPONSE_COMPLETED,
        filter=EvaluationRuleFilter(agent_name="my-agent"),
        enabled=True,
    ),
)
```

`max_hourly_runs=100` = caps at 100 eval runs per hour.

**Required permission:** project managed identity must have **Foundry User** role.

---

### Alerts

Configure via Monitor tab → gear icon → Alerts:

| Alert type | Triggers when |
|---|---|
| Latency | p95 exceeds threshold (e.g. > 10s) |
| Token usage | Count spikes above baseline |
| Evaluation score | Score drops below threshold |
| Red team | Red teaming scan finds a failure |

Alerts integrate with Azure Monitor → email, Teams, PagerDuty, webhook.

---

### Red Teaming (via Monitor tab)

Portal: Monitor tab → Settings → **Red team scans**.

Runs adversarial tests on a schedule to detect:
- Data leakage
- Prohibited action execution
- Jailbreak vulnerabilities

Failed scan → red indicator on Monitor dashboard. Requires remediation before next release.

---

### Monitoring for Custom Agents (not hosted in Foundry)

Centralize monitoring even for agents running outside Foundry:

1. Register agent in **Foundry Control Plane** (Operate → Assets → Register)
2. Instrument agent with OTel GenAI semantic conventions
3. Point agent's OTel exporter at the same App Insights as your Foundry project
4. View traces and configure continuous eval in Foundry portal

---

### Troubleshooting Monitoring

| Symptom | Cause | Fix |
|---|---|---|
| Dashboard charts empty | No traffic in range, or ingestion delay (2–5 min) | Expand time range; generate traffic; refresh |
| Auth error | Missing RBAC on App Insights | Add Log Analytics Reader (+ Privileged Monitoring Data Reader for protected tables) |
| Continuous eval not showing | Rule disabled or MI missing Foundry User role | Enable rule; assign Foundry User to project MI |
| Eval runs skipped | `max_hourly_runs` limit hit | Increase limit or wait for next hour |

---

## PART 4 — EVALUATION

### What Evaluation Is

Evaluation = run a dataset of prompts → score each output on quality/safety dimensions.

Runs **offline** — never in the request path. Run it:
- Before a release (quality gate)
- On a schedule against production traces (drift detection)
- After a model or prompt change (regression check)

**Two run modes:**
- **Local** — runs on your machine. Free, fast, no cloud needed.
- **Cloud** — runs in Foundry evaluation service. Uses judge model, costs tokens, scales to large datasets.

---

### Evaluator 1 — General Purpose (Writing Quality)

Measures writing quality independent of factual correctness.

| Evaluator | `builtin` name | Measures | Inputs needed | Score |
|---|---|---|---|---|
| **Coherence** | `builtin.coherence` | Logical flow, argument structure | `query` + `response` | 1–5 Likert |
| **Fluency** | `builtin.fluency` | Grammar, vocabulary, readability | `response` only | 1–5 Likert |

Both use LLM-as-judge. Recommended judge: `gpt-5-mini`.

```python
testing_criteria = [
    {
        "type": "azure_ai_evaluator",
        "name": "coherence",
        "evaluator_name": "builtin.coherence",
        "initialization_parameters": {"deployment_name": "gpt-5-mini"},
        "data_mapping": {"query": "{{item.query}}", "response": "{{item.response}}"},
    },
    {
        "type": "azure_ai_evaluator",
        "name": "fluency",
        "evaluator_name": "builtin.fluency",
        "initialization_parameters": {"deployment_name": "gpt-5-mini"},
        "data_mapping": {"response": "{{item.response}}"},
    },
]
```

Output:
```json
{"metric": "coherence", "score": 4, "label": "pass", "threshold": 3, "passed": true,
 "reason": "Response directly addresses the question with clear logical connections."}
```

Conversation-level coherence: set `evaluation_level="conversation"` to score across full multi-turn conversations.

---

### Evaluator 2 — RAG (Retrieval-Augmented Generation)

Use when your app retrieves documents and generates answers from them.

| Evaluator | `builtin` name | Measures | When to use |
|---|---|---|---|
| **Groundedness** | `builtin.groundedness` | Answer supported by source docs (no hallucination) | Always in RAG |
| **Relevance** | `builtin.relevance` | Answer relevant to the question | Q&A systems |
| **Retrieval** | `builtin.retrieval` | Retrieved chunks relevant to query (no ground truth needed) | When retrieval is a bottleneck |
| **Document Retrieval** | `builtin.document_retrieval` | NDCG, Fidelity, XDCG (requires labeled relevance data) | When you have labeled data |
| **Response Completeness** | `builtin.response_completeness` | Answer covers all aspects of query (recall) | Multi-part questions |

**Groundedness vs Response Completeness:**
- Groundedness = precision: "everything stated is supported by docs"
- Response Completeness = recall: "all aspects of the question are answered"

Required inputs: `query` + `response` + `context` (the retrieved documents).

```python
{
    "type": "azure_ai_evaluator",
    "name": "groundedness",
    "evaluator_name": "builtin.groundedness",
    "initialization_parameters": {"deployment_name": "gpt-5-mini"},
    "data_mapping": {
        "query": "{{item.query}}",
        "response": "{{item.response}}",
        "context": "{{item.context}}",
    },
}
```

---

### Evaluator 3 — Risk and Safety

Use Microsoft's hosted safety models. **No `deployment_name` needed** — does not use your model quota.

| Evaluator | `builtin` name | Scope | Scale |
|---|---|---|---|
| **Violence** | `builtin.violence` | Models + Agents | 0–7 severity |
| **Sexual** | `builtin.sexual` | Models + Agents | 0–7 severity |
| **Self-harm** | `builtin.self_harm` | Models + Agents | 0–7 severity |
| **Hate / Unfairness** | `builtin.hate_unfairness` | Models + Agents | 0–7 severity |
| **Protected Material** | `builtin.protected_material` | Models + Agents | pass/fail |
| **Code Vulnerability** | `builtin.code_vulnerability` | Models + Agents | pass/fail |
| **Indirect Attack (XPIA)** | `builtin.indirect_attack` | Models only | pass/fail |
| **Ungrounded Attributes** | `builtin.ungrounded_attributes` | Models + Agents | true/false |
| **Prohibited Actions** *(Preview)* | `builtin.prohibited_actions` | **Agents only** | pass/fail |
| **Sensitive Data Leakage** *(Preview)* | `builtin.sensitive_data_leakage` | **Agents only** | pass/fail |

Output (0–7 scale; default threshold = 3 → blocks medium+):
```json
{"metric": "violence", "score": 0, "label": "pass", "threshold": 3, "passed": true,
 "reason": "The response refuses to provide harmful content."}
```

**Defect rate** = % of responses that fail. Use as the headline safety metric.

**Code vulnerability** catches: SQL injection, path injection, XSS, SSRF, hardcoded credentials, tar-slip, weak crypto, Flask debug mode, reflected XSS, and 10+ more.

**Indirect attack (XPIA)** categories:
- Manipulated content — false info, formatting tricks
- Intrusion — backdoors, privilege escalation, jailbreaks
- Information gathering — unauthorized data access/exfiltration

Agent-specific evaluators need `tool_calls` in the data mapping:
```python
{
    "type": "azure_ai_evaluator",
    "name": "prohibited_actions",
    "evaluator_name": "builtin.prohibited_actions",
    "data_mapping": {
        "query": "{{item.query}}",
        "response": "{{item.response}}",
        "tool_calls": "{{sample.tool_calls}}",
    },
}
```

---

### Evaluator 4 — Agent Evaluators

Evaluate agent-specific quality: did the right tools get called in the right order?

| Evaluator | `builtin` name | Measures |
|---|---|---|
| **Tool Call Accuracy** | `builtin.tool_call_accuracy` | Correct tools called with correct arguments? |
| **Intent Resolution** | `builtin.intent_resolution` | Agent correctly identified what the user wanted? |
| **Task Adherence** | `builtin.task_adherence` | Agent completed task without unintended actions? |

Requires `tool_calls` + `query` + `response` in data mapping.

---

### Evaluator 5 — Textual Similarity

No LLM judge. Pure string/token comparison against ground truth. Free to run.

| Evaluator | `builtin` name | What it computes |
|---|---|---|
| **F1 Score** | `builtin.f1_score` | Word overlap — precision + recall |
| **BLEU** | `builtin.bleu_score` | n-gram precision (classic MT metric) |
| **ROUGE** | `builtin.rouge_score` | n-gram recall |
| **METEOR** | `builtin.meteor_score` | Alignment-based, accounts for synonyms |
| **GLEU** | `builtin.gleu_score` | BLEU variant with recall component |
| **String Exact Match** | `builtin.string_exact_match` | 1.0 if identical, 0.0 otherwise |

Required: `response` + `ground_truth`.

---

### Evaluator 6 — Custom Evaluators

Bring your own scoring logic.

**Python function:**
```python
def my_evaluator(response: str, ground_truth: str) -> dict:
    score = len(set(response.split()) & set(ground_truth.split())) / len(ground_truth.split())
    return {"my_metric": score, "passed": score >= 0.5}
```

**Prompt-based (LLM judge with your own prompt):**
```python
# Define a prompt template that takes {{query}} and {{response}}
# Returns a structured score
# Register in Foundry portal → Evaluations → Custom evaluators
```

Custom evaluators work in continuous evaluation (Monitor tab → Settings → Continuous evaluation → Add evaluator).

---

### Evaluator 7 — Rubric Evaluators

Define exactly what "good" means for your domain. LLM judges each response against weighted criteria.

**How it works:**
- Define dimensions — each with `description` + `weight`
- LLM scores each dimension 1–5 per response
- Overall score = weighted average of applicable dimensions, normalized to 0–1
- Pass if score ≥ threshold (default 0.5)

**Dimension fields:**

| Field | What it is |
|---|---|
| `id` | Stable slug, e.g. `"intent_recognition"` |
| `description` | Exactly what to measure — specific and unambiguous |
| `weight` | Importance (1–10). ONE dimension should be 8–10 (most decisive). |
| `always_applicable` | If true, scored for EVERY response. Use for general quality dimension. |

**Auto-generate a rubric (recommended):**

Portal: Evaluations → Create → Rubric evaluator → provide:
- Foundry agent (pulls instructions automatically)
- Agent system prompt (paste it)
- Reference files (domain docs, knowledge base)
- Optional: production traces on top for real-usage grounding

Best judge models: `gpt-5.4-mini`, `gpt-5.2`, `gpt-5-mini`.

**Example rubric — restaurant reservation agent:**
```json
[
  {
    "id": "intent_recognition",
    "description": "Correctly identifies booking intent (book/modify/cancel) and pursues the right workflow without unnecessary clarification.",
    "weight": 9
  },
  {
    "id": "tool_usage_accuracy",
    "description": "Calls the correct tool with correct parameters. No unnecessary calls. No skipped calls.",
    "weight": 6
  },
  {
    "id": "policy_enforcement",
    "description": "Enforces business rules: dinner service 17:00–22:00, max party 8, 30-day booking window.",
    "weight": 5
  },
  {
    "id": "information_gathering",
    "description": "Collects date/time/party size/contact before booking. Does not re-ask for info already given.",
    "weight": 4
  },
  {
    "id": "communication_clarity",
    "description": "Clear, concise, professional tone. Confirms reservation details before finalizing.",
    "weight": 2
  },
  {
    "id": "general_quality",
    "description": "Other important quality factors not covered above.",
    "weight": 5,
    "always_applicable": true
  }
]
```

**Pass output (party of 4, valid booking):**
```json
{
  "score": 0.94, "label": "pass", "threshold": 0.5, "passed": true,
  "reason": "intent_recognition(5), tool_usage_accuracy(5), policy_enforcement(5) — correct booking, valid params, within all constraints.",
  "properties": {
    "dimension_scores": [
      {"id": "intent_recognition", "score": 5, "weight": 9, "applicable": true},
      {"id": "tool_usage_accuracy", "score": 5, "weight": 6, "applicable": true},
      {"id": "policy_enforcement", "score": 5, "weight": 5, "applicable": true}
    ]
  }
}
```

**Fail output (party of 12, max is 8):**
```json
{
  "score": 0.35, "label": "fail", "threshold": 0.5, "passed": false,
  "reason": "policy_enforcement(1) — agent booked party of 12 despite max party size of 8."
}
```

Rubric evaluators work in continuous evaluation — wire via Monitor tab → Settings → Continuous evaluation → Add evaluator.

---

### Evaluator 8 — Azure OpenAI Graders

Different API surface (OpenAI Evals API directly). Use when you need full prompt control or deterministic checks.

| Grader | Uses LLM? | What it does |
|---|---|---|
| `label_model` | Yes | Classifies into your predefined labels |
| `score_model` | Yes | Assigns 0–1 numeric score via your prompt |
| `string_check` | No | Exact/pattern string comparison |
| `text_similarity` | No | BLEU/ROUGE/cosine/fuzzy similarity |

**Label grader — classify sentiment or topic:**
```python
{
    "type": "label_model",
    "name": "sentiment_check",
    "model": "gpt-5-mini",
    "input": [
        {"role": "developer", "content": "Classify as 'positive', 'neutral', or 'negative'"},
        {"role": "user", "content": "Statement: {{item.query}}"},
    ],
    "labels": ["positive", "neutral", "negative"],
    "passing_labels": ["positive", "neutral"],
}
```

**Score grader — 0 to 1 quality score with your own criteria:**
```python
{
    "type": "score_model",
    "name": "quality_score",
    "model": "gpt-5-mini",
    "input": [
        {"role": "system", "content": "Rate response quality 0 to 1. 1=perfect, 0=completely wrong."},
        {"role": "user", "content": "Response: {{item.response}}\nGround Truth: {{item.ground_truth}}"},
    ],
    "pass_threshold": 0.7,
}
```

**String check — exact match:**
```python
{
    "type": "string_check",
    "name": "exact_match",
    "input": "{{item.response}}",
    "reference": "{{item.ground_truth}}",
    "operation": "eq",   # also: ne, like (wildcard), ilike (case-insensitive)
}
```

**Text similarity — BLEU / ROUGE / cosine / fuzzy:**
```python
{
    "type": "text_similarity",
    "name": "similarity_check",
    "input": "{{item.response}}",
    "reference": "{{item.ground_truth}}",
    "evaluation_metric": "bleu",  # rouge_1–5, rouge_l, meteor, cosine, fuzzy_match, gleu
    "pass_threshold": 0.8,
}
```

**When graders vs built-in evaluators:**
- Graders: custom LLM prompt, custom labels, or deterministic comparison
- `builtin.*` evaluators: standardized safety/quality scoring via Foundry hosted models

---

### Benchmark Evaluations — Industry Standard Datasets

Run model or agent against curated benchmarks without building your own test data.

**Portal:** Build → Evaluations → Create → Data step → select **Benchmarks**

| Benchmark | Task | Examples | Scoring |
|---|---|---|---|
| **AIME 2025** | Math/Reasoning | 30 | Competition math |
| **BBEH** | Reasoning/Quality | 4,520 | Broad harness |
| **BIG-Bench Hard** | Reasoning/Quality | 934 | regex_match |
| **ChemBench** | Sciences | 2,785 | Chemistry knowledge |
| **FrontierScience** | Reasoning/Quality | 160 | Needs judge model |
| **GPQA Diamond** | Expert Science | 198 | regex_match |
| **MuSR** | Multi-step Reasoning | 756 | regex_match |
| **TruthfulQA** | Truthfulness | 790 | TruthfulQA metric |

**Target vs judge model:**
- Target = the model/agent being evaluated
- Judge model = the model scoring answers (FrontierScience needs one; TruthfulQA doesn't)

**REST API:**
```http
POST {project-endpoint}/openai/evals?api-version=2025-11-15-preview
Content-Type: application/json

{
  "name": "truthfulqa-eval",
  "data_source_config": {
    "type": "azure_ai_source",
    "scenario": "benchmark_preview",
    "benchmark_name": "builtin.truthful_qa",
    "benchmark_version": "3"
  }
}
```

For benchmarks needing a judge model, add `"grader_model": "{connection-name}/{deployment}"`.

Then add a run per target:
```http
POST {project-endpoint}/openai/evals/{eval-id}/runs?api-version=2025-11-15-preview

{
  "name": "run-gpt-5-2",
  "data_source": {
    "type": "azure_ai_benchmark_preview",
    "target": {"type": "azure_ai_model", "model": "{connection}/{deployment}"}
  }
}
```

Result shows as: `82%` = `645/790 examples passing`.

---

### Running Evaluations

#### Option A: Local (Python SDK)
```python
from azure.ai.evaluation import evaluate

result = evaluate(
    data="test_dataset.jsonl",
    evaluators={
        "groundedness": {
            "type": "azure_ai_evaluator",
            "evaluator_name": "builtin.groundedness",
            "initialization_parameters": {"deployment_name": "gpt-5-mini"},
            "data_mapping": {
                "query": "{{item.query}}",
                "response": "{{item.response}}",
                "context": "{{item.context}}",
            },
        }
    },
    output_path="results.json",
)
print(result["metrics"])
# {"groundedness.groundedness": 4.2}
```

#### Option B: Cloud (Foundry Evaluation Service)
```python
eval_object = openai_client.evals.create(
    name="Safety Eval",
    data_source_config={"type": "azure_ai_source", "scenario": "responses"},
    testing_criteria=[
        {
            "type": "azure_ai_evaluator",
            "name": "violence_check",
            "evaluator_name": "builtin.violence",
            "data_mapping": {
                "query": "{{item.query}}",
                "response": "{{item.response}}",
            },
        }
    ],
)
```

#### Option C: Portal
Build → **Evaluations** tab → Create → select dataset → select evaluators → Run.

View results, download CSV, compare runs over time in the portal.

---

### Dataset Format (JSONL)

```jsonl
{"query": "What is the refund policy?", "response": "Refunds processed in 5 business days.", "context": "Policy: 5 business days.", "ground_truth": "5 business days"}
{"query": "How do I cancel?", "response": "Go to Account Settings > Subscription > Cancel.", "context": "Cancel via Account Settings > Subscription > Cancel.", "ground_truth": "Account Settings > Subscription > Cancel"}
```

Common columns: `query`, `response`, `context`, `ground_truth`, `tool_calls`.

Data mapping syntax:
- `{{item.field_name}}` — field from your dataset
- `{{sample.output_text}}` — response generated during eval (for model/agent targets)
- `{{sample.output_items}}` — agent responses (for agent targets)

---

### Human Evaluation

Portal: Build → Evaluations → **Human Evaluation** tab.

Assign labelers to review agent responses. Labelers rate:
- Relevance (1–5)
- Accuracy (1–5)
- Thumbs up/down

Results flow into App Insights via OTel `gen_ai.evaluation.result` events — same pipeline as automated evals.

---

### Cluster Analysis — Find Patterns in Failures

After running evaluation, group similar failures to find WHAT is going wrong and WHY.

**Portal:** Evaluations → select completed runs → **Cluster analysis** button.

> Results are NOT saved. Download before navigating away.

**What the cluster map shows:**
- Each dot = one evaluated response
- Color = cluster assignment
- Position = semantic similarity — similar failures are close together
- Click a cluster → diagnostic description + recommended fix
- Click a subcluster → entry-level score breakdown
- Click a dot → full conversation + metadata + trace ID

**Filter the map:**

| Filter | What it narrows to |
|---|---|
| Chat / Agent / Tool / Conversation | Specific span types |
| Low / Medium / High token | Responses by token cost |
| Advanced (score, evaluator, timestamp) | Custom subsets |

**Typical cluster names:** `inadequate_final_answer`, `incorrect_response`, `invalid_api_key`, etc.

Each cluster provides: error pattern description + specific recommendations (e.g. "Update prompt to enforce constraint X", "Add validation for Y").

**After cluster analysis:**
- Refine agent instructions to address recurring failure patterns
- Curate fine-tuning data from identified failure categories
- Re-run evaluation after fixing and compare new cluster map

---

### Convert Traces to Dataset

Portal: Traces → filter to relevant traces → **Export to dataset**.

Creates JSONL from production traces — no manual test-case writing. Best practice: export weekly sample of production traces and run evaluation against them to catch quality drift early.

---

## PART 5 — HOW EVERYTHING CONNECTS

### The Full Lifecycle

```
BEFORE RELEASE
──────────────
Write your agent/app
↓
Run evaluation on golden dataset (offline):
  → Safety defect rate OK?
  → Groundedness ≥ 4.0 / 5?
  → Task Adherence passing?
  → Rubric score ≥ threshold?
↓ (pass)
Deploy to production

IN PRODUCTION (every request)
──────────────────────────────
Guardrails scan input        [real-time, blocking, ~50–100ms per point]
Agent/model runs
Guardrails scan output       [real-time, blocking]
Response sent to user
Trace written to App Insights [async, non-blocking]

CONTINUOUS (background, every response or on schedule)
──────────────────────────────────────────────────────
Monitoring dashboard shows latency/tokens/errors  [2–5 min lag]
Continuous evaluation scores sampled live traffic
Red teaming scans run on schedule (daily/weekly)
Alerts fire when metrics cross thresholds

BEFORE NEXT RELEASE
───────────────────
Run evaluation on new dataset
Compare scores to previous version baseline
Pass gate → deploy
Fail gate → fix prompt/model → re-evaluate
```

---

## Portal Locations Cheat Sheet

| Feature | Portal path |
|---|---|
| Create / edit guardrail | Project → **Guardrails + controls** |
| Test guardrail interactively | Guardrails + controls → **Try it out** |
| Test Task Adherence | Try it out → Agentic Workflow → Task Adherence |
| Guided guardrail setup | Build → Agents → agent → Guardrails → **Managed guardrail** → Guided setup |
| Connect App Insights | Project → **Settings** → Tracing |
| View traces (per request) | Project → **Traces** tab |
| View conversation history | Traces → click a Conversation ID |
| Trace Replay | Traces → click Conversation/Trace ID → Replay Panel |
| Agent monitoring dashboard | Build → select agent → **Monitor** tab |
| Ask AI on dashboard | Monitor tab → **Ask AI** icon |
| Configure continuous eval | Monitor tab → gear icon → Continuous evaluation |
| Run evaluation | Build → **Evaluations** tab → Create |
| Benchmark evaluation | Evaluations → Create → Data step → Benchmarks |
| Human evaluation | Evaluations → **Human Evaluation** subtab |
| Recurring eval configs | Evaluations → **Recurring Configs** subtab |
| Cluster analysis | Evaluations → select run → **Cluster analysis** |
| Export traces to dataset | Traces → filter → **Export to dataset** |
| Red teaming | Monitor tab → Settings → Red team scans |
| AppGenAIContent table protection | Azure portal → Log Analytics workspace → Tables → AppGenAIContent → Manage table |

---

## Common Confusion Points

**"Guardrails vs evaluation — both check for harmful content. Same thing?"**
No. Guardrails: real-time, blocks before user sees it. Evaluation: offline batch scoring after the fact. You need both — guardrails prevent harm in production; evaluation measures how often harm is attempted so you can tune the guardrails and prompts.

**"Groundedness is a guardrail filter AND an evaluator. Which is which?"**
`builtin.groundedness` = offline evaluator, scores on a dataset, never blocks anything.
Groundedness risk in guardrails = real-time filter on model output that CAN block. Same goal, two different execution paths. Groundedness guardrail is models-only (not agents) in current preview.

**"Task Adherence is a guardrail AND an evaluator. Which is which?"**
Task Adherence guardrail = calls Content Safety API at runtime, blocks misaligned tool calls before they execute.
`builtin.task_adherence` evaluator = offline scoring of whether agent stayed on task. Same concept, different path.

**"Tracing = logging?"**
Tracing is structured, hierarchical, and tied to ONE specific request. Logging is flat text. Tracing shows the SPAN TREE of a request including all sub-calls. A single agent response spawns dozens of sub-calls — flat logs can't show the call hierarchy; traces can.

**"Monitoring tells me if answers are good?"**
No. Monitoring = latency, error rate, token count — operational health. Whether answers are CORRECT is evaluation — completely separate pipeline. Both are needed; neither replaces the other.

**"If I have guardrails, do I need evaluation?"**
Yes. Guardrails block known harmful patterns at runtime. Evaluation tells you whether your app produces quality, grounded, coherent answers — things guardrails don't measure. Guardrails = safety floor. Evaluation = quality ceiling.

**"Severity 0–7 in evaluation vs Off/Low/Medium/High in guardrails — how do they map?"**
- Guardrail threshold "Low" → blocks score ≥ 2
- Guardrail threshold "Medium" → blocks score ≥ 4 (default)
- Guardrail threshold "High" → blocks score ≥ 6
- Evaluation default threshold = 3 (fail if score > 3, i.e. blocks medium severity)

**"What's the difference between Rubric evaluators and Custom evaluators?"**
Custom evaluators: bring your own Python function or judge prompt — full freedom, no structure imposed.
Rubric evaluators: structured format with weighted dimensions, auto-generated from agent context, dimension-level scores in output. Rubric is a specific TYPE of custom evaluator with more scaffolding.

---

## References

- [Guardrails overview](https://learn.microsoft.com/azure/foundry/guardrails/guardrails-overview)
- [Intervention points](https://learn.microsoft.com/azure/foundry/guardrails/intervention-points)
- [Task Adherence](https://learn.microsoft.com/azure/foundry/guardrails/task-adherence)
- [How to create guardrails](https://learn.microsoft.com/azure/foundry/guardrails/how-to-create-guardrails)
- [Guided guardrail setup](https://learn.microsoft.com/azure/foundry/guardrails/guided-set-up)
- [Agent tracing overview](https://learn.microsoft.com/azure/foundry/observability/concepts/trace-agent-concept)
- [Set up tracing](https://learn.microsoft.com/azure/foundry/observability/how-to/trace-agent-setup)
- [Trace replay](https://learn.microsoft.com/azure/foundry/observability/how-to/trace-agent-replay)
- [Sensitive content in traces](https://learn.microsoft.com/azure/foundry/observability/how-to/traces-sensitive-content)
- [Log end-user feedback](https://learn.microsoft.com/azure/foundry/observability/how-to/log-end-user-feedback)
- [Monitor agents dashboard](https://learn.microsoft.com/azure/foundry/observability/how-to/how-to-monitor-agents-dashboard)
- [Monitoring dashboard Ask AI](https://learn.microsoft.com/azure/foundry/observability/how-to/optimization-dashboard)
- [General purpose evaluators](https://learn.microsoft.com/azure/foundry/concepts/evaluation-evaluators/general-purpose-evaluators)
- [RAG evaluators](https://learn.microsoft.com/azure/foundry/concepts/evaluation-evaluators/rag-evaluators)
- [Risk and safety evaluators](https://learn.microsoft.com/azure/foundry/concepts/evaluation-evaluators/risk-safety-evaluators)
- [Agent evaluators](https://learn.microsoft.com/azure/foundry/concepts/evaluation-evaluators/agent-evaluators)
- [Textual similarity evaluators](https://learn.microsoft.com/azure/foundry/concepts/evaluation-evaluators/textual-similarity-evaluators)
- [Custom evaluators](https://learn.microsoft.com/azure/foundry/concepts/evaluation-evaluators/custom-evaluators)
- [Rubric evaluators](https://learn.microsoft.com/azure/foundry/concepts/evaluation-evaluators/rubric-evaluators)
- [Azure OpenAI graders](https://learn.microsoft.com/azure/foundry/concepts/evaluation-evaluators/azure-openai-graders)
- [Benchmark evaluations](https://learn.microsoft.com/azure/foundry/observability/how-to/benchmark-evaluations)
- [Evaluate an agent](https://learn.microsoft.com/azure/foundry/observability/how-to/evaluate-agent)
- [Human evaluation](https://learn.microsoft.com/azure/foundry/observability/how-to/human-evaluation)
- [Cluster analysis](https://learn.microsoft.com/azure/foundry/observability/how-to/cluster-analysis)
- [Traces to dataset](https://learn.microsoft.com/azure/foundry/observability/how-to/traces-to-dataset)
