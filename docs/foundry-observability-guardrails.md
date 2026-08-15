# Azure AI Foundry: Guardrails, Tracing, Monitoring & Evaluation — Complete Guide

> Written from official Foundry docs. Direct, no fluff. Every service name, SDK call, and portal path is exact.

---

## The Big Picture — 30 Seconds

```
Every request flows through this pipeline:

  USER INPUT
      ↓
  [GUARDRAILS — input scan]        ← blocks jailbreaks, hate, PII before model sees it
      ↓
  MODEL / AGENT RUNS
    ↓ agent calls a tool?
  [GUARDRAILS — tool call scan]    ← blocks misaligned tool calls (preview)
    ↓ tool returns data?
  [GUARDRAILS — tool response scan] ← blocks indirect attacks in tool responses (preview)
      ↓
  [GUARDRAILS — output scan]       ← blocks harmful/copyrighted content in final response
      ↓
  RESPONSE SENT TO USER
      ↓  (async, after)
  [TRACING]                        ← records every step as OpenTelemetry spans → App Insights
      ↓  (aggregated over time)
  [MONITORING]                     ← dashboards, alerts, token usage, latency, error rate
      ↓  (offline, on a schedule)
  [EVALUATION]                     ← quality scores on dataset: groundedness, safety, coherence
```

---

## PART 1 — GUARDRAILS

### What a Guardrail Is

A **guardrail** is a named collection of **controls**.

A **control** = (risk category) + (intervention point) + (response action).

Example control: "Detect violence at Medium severity on user input → annotate and block."

Foundry uses classification models from **Azure AI Content Safety** under the hood.

---

### Risk Categories

| Risk | Applies to Models | Applies to Agents (Preview) | What it detects |
|---|---|---|---|
| **Hate / Unfairness** | ✅ | ✅ | Language targeting social groups based on race, gender, religion, etc. |
| **Sexual** | ✅ | ✅ | Explicit sexual content |
| **Violence** | ✅ | ✅ | Physical harm, weapons, threats |
| **Self-harm** | ✅ | ✅ | Instructions or encouragement to harm oneself |
| **User Prompt Attacks** | ✅ | ✅ | Jailbreak attempts by the user ("ignore all previous instructions") |
| **Indirect Attacks (XPIA)** | ✅ | ✅ | Jailbreak injected inside a document/tool response the agent reads |
| **Spotlighting** | ✅ | ❌ | Advanced prompt injection mitigation (models only, preview) |
| **Protected Material — Text** | ✅ | ✅ | Copyrighted text (song lyrics, articles, recipes) |
| **Protected Material — Code** | ✅ | ✅ | Licensed code in model output |
| **Groundedness** | ✅ | ❌ | Response not supported by source documents (models only, preview) |
| **PII** | ✅ | ✅ | Personally identifiable information |
| **Task Adherence** | ✅ | ✅ | Agent doing something the user did NOT ask for (preview) |

---

### Severity Levels (Content Risks)

For Hate, Violence, Sexual, Self-harm:

| Level | Behavior |
|---|---|
| **Off** | Detection disabled. Requires Microsoft approval. |
| **Low** | Flags low severity and above. Least restrictive. |
| **Medium** | Flags medium severity and above. Default. |
| **High** | Flags only the most extreme content. Most restrictive. |

Severity scales are 0–7:
- 0–1 = Very Low (neutral/educational context)
- 2–3 = Low (mild, not glorified)
- 4–5 = Medium (direct insults, graphic but not extreme)
- 6–7 = High (inciting violence, illegal content, extreme abuse)

---

### Four Intervention Points

Where exactly the guardrail check fires:

| Point | Who it applies to | What it scans | Example use |
|---|---|---|---|
| **User input** | Models + Agents | The prompt the user sent | Block jailbreaks before model processes them |
| **Tool call** *(Preview)* | Agents only | What the agent is about to send TO a tool | Block a `delete_files()` call when user only asked to "list files" |
| **Tool response** *(Preview)* | Agents only | What a tool returned TO the agent | Block indirect attack payload in a web search result |
| **Output** | Models + Agents | Final response to the user | Block copyrighted lyrics in the answer |

> **Latency:** each intervention point adds ~50–100ms. With all 4 enabled, expect ~200–400ms overhead.

**Supported tools for tool call/response scanning:** Azure AI Search, Azure Functions, OpenAPI, SharePoint Grounding, Fabric Data Agent, Bing Grounding, Bing Custom Search, Browser Automation. Tools NOT in this list are not scanned at those points.

---

### Two Response Actions

| Action | Models | Agents | What happens |
|---|---|---|---|
| **Annotate** | ✅ | ❌ | Adds a flag to the API response. Does NOT block. Caller decides what to do. |
| **Annotate and block** | ✅ | ✅ | Flags AND returns an error. Agent/model stops. |

---

### Guardrail Inheritance — Important Rule

> **The agent's guardrail FULLY OVERRIDES the model's guardrail.**

If a model deployment has Violence=High and you assign an agent a guardrail with Violence=Low:
- Agent input scan: Violence Low ✓
- Tool calls: not scanned (agent guardrail has no tool call control)
- Tool responses: not scanned
- Agent output: Violence Low ✓
- The model's Violence=High has zero effect on that agent.

**Default guardrail:** `Microsoft.DefaultV2` — applied to all models automatically.

For agents: if no custom guardrail assigned → inherits model's guardrail.

---

### Task Adherence — Guardrail for Agent Misalignment

Detects when the agent is about to do something different from what the user asked.

**What it catches:**
- User asked "show me my calendar" → agent plans to call `clear_calendar_events()` → BLOCK
- User asked "check my data usage" → agent plans `change_data_plan()` → BLOCK
- User asked "write a draft email" → agent plans to call `send_email()` → BLOCK (no explicit send instruction)

**API response:**
```json
{
  "taskRiskDetected": true,
  "details": "Agent attempts to share a document externally without user request or confirmation."
}
```

**Call via REST:**
```
POST <endpoint>/contentsafety/agent:analyzeTaskAdherence?api-version=2024-12-15-preview
```

Body needs: `tools` (list of tool definitions) + `messages` (conversation history with tool calls).

**Limitation:** 100,000 character max input. English primary. Data may route to US/EU regions.

---

### Where to Configure Guardrails

**Portal:** Foundry portal → your project → **Guardrails + controls** tab

**SDK:** create a guardrail policy object, assign to model deployment or agent.

**Default:** Microsoft.DefaultV2 is pre-assigned. You can create custom guardrails with different severity settings per risk.

---

### Troubleshooting Guardrails

| Symptom | Cause | Fix |
|---|---|---|
| Agent not respecting guardrail | Agent using model's guardrail, not its own | Explicitly assign guardrail to the agent |
| Preview risks not applying to agent | Spotlighting, Groundedness not yet supported for agents | Expected — those controls only run on models |
| Legitimate content blocked | Severity too restrictive | Lower severity threshold or request modified filter from MS |
| Tool calls not scanned | Tool not in supported list OR tool call/response intervention points not configured | Check supported tools list; add controls at tool call/response points |

---

## PART 2 — TRACING

### What Tracing Is

Tracing records the complete execution of ONE request as a **span tree**. Each operation is a span. Spans nest to show the full call chain.

Built on **OpenTelemetry (OTel)** semantic conventions. Data ships to **Azure Application Insights**.

---

### Key Concepts

| Concept | What it is |
|---|---|
| **Trace** | Full journey of one request — root span with all child spans |
| **Span** | One operation: start time, end time, attributes (inputs/outputs/tokens), status |
| **Attributes** | Key-value pairs on a span: model name, token count, tool arguments, etc. |
| **Semantic conventions** | Standardized attribute names across tools (OpenTelemetry GenAI conventions) |
| **Trace exporter** | Ships spans to App Insights. Async — does not block the request. |

---

### What a Trace Looks Like

```
[root] responses.create — 1.8s
  ├── [child] memory_search_call — 0.12s
  │     query: "What are my catering preferences?"
  │     result: [dairy-free, email updates]
  ├── [child] gpt-5.2 — 1.4s
  │     tokens: prompt=412 completion=92
  │     finish_reason: stop
  ├── [child] memory_command_preview_call — 0.06s
  │     action: remember
  │     content: "prefers dairy-free catering and email updates"
  └── [child] memory_command_preview_call_output — 0.01s
        status: completed
```

What every trace captures:
- User input + agent output
- Every tool call: which tool, arguments, response, latency
- Token counts (prompt + completion)
- Duration of each step
- Errors and retries

---

### Two Tracing Modes

**1. Server-side tracing (automatic, zero code change)**

Connect App Insights to your Foundry project → done. Foundry auto-traces all Prompt agents, Hosted agents, and Workflows. Available in portal → **Traces** tab within minutes.

Best for: most users, production monitoring.

**2. Client-side tracing (instrument your own code)**

Use when you need to trace custom logic around the agent call (pre/post processing, your own pipelines).

```bash
pip install azure-ai-projects azure-identity opentelemetry-sdk azure-core-tracing-opentelemetry azure-monitor-opentelemetry
```

```python
from azure.monitor.opentelemetry import configure_azure_monitor
from azure.ai.inference.tracing import AIInferenceInstrumentor

# Get connection string from your project
conn_str = project.telemetry.get_connection_string()

# Wire up App Insights
configure_azure_monitor(connection_string=conn_str)

# Instrument the Azure AI Inference SDK (model calls)
AIInferenceInstrumentor().instrument()
```

After this: every `chat_client.complete()` or `responses.create()` auto-generates spans.

**3. Local tracing (VS Code, no cloud)**

Use the **Microsoft Foundry Toolkit** VS Code extension. Sends spans to a local OTLP collector. Works with OpenAI, Anthropic, LangChain, Foundry Agent Service. No Azure account needed for local dev.

---

### Framework Integrations

Tracing works with all major agent frameworks out of the box:

| Framework | How to enable |
|---|---|
| Foundry Agent Service | Server-side: automatic. Client-side: `AIInferenceInstrumentor().instrument()` |
| LangChain | `from langchain_azure_ai.tracing import enable_azure_monitor_tracing` |
| LangGraph | Same as LangChain |
| Microsoft Agent Framework | Built-in OTel instrumentation |
| OpenAI Agents SDK | OpenTelemetry integration built in |

All use the same W3C Trace Context + OpenTelemetry GenAI semantic conventions — spans are consistent across frameworks.

---

### Multi-Agent Tracing

For multi-agent systems (agent calling another agent), Foundry captures cross-agent spans:

| Span type | What it captures |
|---|---|
| `execute_task` | Task decomposition and dispatch |
| `agent_to_agent_interaction` | One agent calling another |
| `agent.state.management` | Memory updates, context management |
| `agent_planning` | Internal planning steps |
| `agent_orchestration` | Coordinator agent directing sub-agents |
| `execute_tool` | Tool invocation + arguments + result |

---

### Conversation View

In Foundry portal → Traces tab: search by Response ID or Trace ID → click a **Conversation ID** to see:
- Full turn-by-turn conversation history
- Ordered tool calls and run steps
- Token usage per response
- Inputs and outputs at each step

---

### Permissions Required for Tracing

| What | Role needed |
|---|---|
| View traces in Foundry portal | Log Analytics Reader on App Insights resource |
| Query protected telemetry tables | Privileged Monitoring Data Reader |
| Write traces (instrument code) | No special role — uses App Insights connection string |

---

### Sensitive Content in Traces

Traces capture everything — prompts, tool arguments, model outputs. This means **PII, secrets, and user data can end up in App Insights**.

Rules:
- Never put API keys, tokens, passwords in prompts or tool arguments
- Redact personal data before it enters the telemetry pipeline
- Apply same access controls to App Insights as you do to production logs

**Restrict access to sensitive content:** Foundry routes the 7 sensitive OTel attributes (prompts, responses, tool args, system instructions) to a dedicated protected table `AppGenAIContent`. Set that table to protection level = Protected → only `Privileged Monitoring Data Reader` can query it. Full setup in Part 7 below.

---

### Logging End-User Feedback

Log thumbs up/down or star ratings alongside traces using OTel events:

```python
# Emit a gen_ai.evaluation.result event via OTel
# Binary (thumbs up/down): score = 0.0 (fail) or 1.0 (pass)
# Likert (1-5 stars): score = 1.0 to 5.0, threshold = 3.0

# Event attributes:
# gen_ai.evaluation.score.value: the score
# gen_ai.evaluation.score.label: "pass" or "fail"
# gen_ai.evaluation.name: e.g. "thumbs_up"
# microsoft.gen_ai.human_evaluation.source: "end_user" or "builder"
```

Query in App Insights via KQL:
```kusto
customEvents
| where name == "gen_ai.evaluation.result"
| extend score = todouble(customDimensions["gen_ai.evaluation.score.value"])
| summarize avg_score = avg(score) by bin(timestamp, 1h)
```

---

### Tracing Data Retention and Cost

- Traces store in App Insights — follows your App Insights retention setting (default 90 days in portal)
- Cost: App Insights charges per GB ingested. Token-rich traces (long prompts) cost more.
- Sampling: configure in App Insights to reduce volume for high-traffic apps.

---

### Troubleshooting Tracing

| Symptom | Cause | Fix |
|---|---|---|
| No traces in portal | App Insights not connected, or no traffic yet | Connect App Insights in project settings; generate agent traffic |
| Authorization error viewing traces | Missing Log Analytics Reader role | Add role in IAM on App Insights resource |
| Client-side traces missing | Missing SDK install or `instrument()` not called | Reinstall packages; ensure `AIInferenceInstrumentor().instrument()` runs before any model calls |
| Sensitive data in traces | Prompts contain PII or secrets | Redact before calling model; use protected table feature |

---

## PART 3 — MONITORING

### What Monitoring Is

Monitoring = aggregating traces + metrics over time to answer "is the system healthy?"

Uses **Azure Monitor** + **Application Insights** (same resource that stores traces). Foundry also has a built-in **Agent Monitoring Dashboard**.

---

### Agent Monitoring Dashboard

**Portal:** Foundry portal → Build → select an agent → **Monitor** tab.

Requires: App Insights connected, Log Analytics Reader role.

#### Dashboard sections

**Summary cards (top row):**
- Total requests
- Success rate
- Average latency
- Total tokens consumed
- Evaluation scores (if continuous eval configured)

**Charts (time-series):**
- Token usage over time — spike = unexpected cost or verbose prompts
- Latency (p50/p95) — above 10s = investigate throttling or complex tool chains
- Run success rate — below 95% = investigate failures
- Evaluation metric scores — trend up/down shows quality drift
- Red teaming results — failed scans = security risk (if red teaming enabled)

---

### Key Metrics to Watch

| Metric | Alert threshold | What it means when bad |
|---|---|---|
| **Token usage** | Spike > 2x baseline | Verbose prompts, prompt injection, runaway loops |
| **Latency p95** | > 10s | Model throttling, complex tool chains, network issues |
| **Run success rate** | < 95% | Broken tools, guardrail over-blocking, model errors |
| **Evaluation scores** | Drop > 0.5 points | Quality regression, prompt drift, data distribution shift |
| **Content filter block rate** | Spike | Abuse pattern, new attack vector |
| **Red team scan fails** | Any failure | Active security risk in agent behavior |

---

### Continuous Evaluation in Monitoring

Instead of only running evaluation offline before release, continuous evaluation runs evaluators ON LIVE TRAFFIC automatically.

Two modes:

**Scheduled evaluation** — runs on a fixed schedule (e.g. every day at 9 AM):
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

`max_hourly_runs=100` = at most 100 evaluation runs per hour. Default cap is 100.

**Permission needed:** project managed identity must have **Foundry User** role.

---

### Alerts

Configure in Monitor settings panel (gear icon on Monitor tab):

| Alert type | What triggers it |
|---|---|
| Latency alert | Latency exceeds threshold (e.g. p95 > 10s) |
| Token usage alert | Token count spikes above baseline |
| Evaluation score alert | Score drops below threshold |
| Red team alert | Red teaming scan finds a failure |

Alerts integrate with Azure Monitor Alerts → email, Teams, PagerDuty, webhook.

---

### Red Teaming (via Monitor tab)

Portal: Monitor tab → Settings → Red team scans.

Runs adversarial tests automatically on a schedule to detect:
- Data leakage
- Prohibited action execution
- Jailbreak vulnerabilities

If scan fails → shown in Monitor dashboard as a red indicator. Requires remediation before next release.

---

### Monitoring for Custom Agents (not in Foundry)

You can centralize monitoring in Foundry even for agents running elsewhere:

1. Register the agent in **Foundry Control Plane** (Assets → Register)
2. Instrument the agent to emit OTel telemetry using GenAI semantic conventions
3. Point the agent's OTel exporter at the same App Insights instance as your Foundry project
4. View traces and configure continuous eval in Foundry portal

---

### Troubleshooting Monitoring

| Symptom | Cause | Fix |
|---|---|---|
| Dashboard charts empty | No traffic in time range, or ingestion delay | Expand time range; generate traffic; wait 2–5 min |
| Authorization error | Missing RBAC on App Insights | Add Log Analytics Reader (+ Privileged Monitoring Data Reader for protected tables) |
| Continuous eval results not showing | Rule not enabled, or MI missing Foundry User role | Verify rule is enabled; assign Foundry User to project MI |
| Eval runs skipped | `max_hourly_runs` limit hit | Increase limit or wait for next hour |

---

## PART 4 — EVALUATION

### What Evaluation Is

Evaluation = run a dataset of prompts through your app → score each output on quality dimensions.

Runs **offline** — never in the request path. Run before a release, on a schedule, or against a sample of production traces.

Two run modes:
- **Local** — runs evaluators on your machine. Fast, free, limited to non-hosted evaluators.
- **Cloud** — runs evaluators in Azure Foundry evaluation service. Scalable, uses a judge model, costs tokens.

---

### Evaluator Categories

#### 1. General Purpose Evaluators (Writing Quality)

| Evaluator | `builtin` name | Measures | Score |
|---|---|---|---|
| **Coherence** | `builtin.coherence` | Logical flow, organization of ideas, argument structure | 1–5 Likert |
| **Fluency** | `builtin.fluency` | Grammar, vocabulary, readability | 1–5 Likert |

Both use LLM-as-judge. Best judge model: `gpt-5-mini` (best balance cost/accuracy).

Required inputs:
- `Coherence`: `query` + `response`
- `Fluency`: `response` only

Output example:
```json
{"metric": "coherence", "score": 4, "label": "pass", "threshold": 3, "passed": true,
 "reason": "Response directly addresses the question with clear logical connections."}
```

Conversation-level: coherence can evaluate full multi-turn conversations by setting `evaluation_level="conversation"`.

---

#### 2. RAG Evaluators (Retrieval-Augmented Generation)

Use these when your app retrieves documents and generates answers grounded in them.

| Evaluator | `builtin` name | Measures | When to use |
|---|---|---|---|
| **Groundedness** | `builtin.groundedness` | Is the answer supported by the source docs? (no hallucination) | Always in RAG |
| **Relevance** | `builtin.relevance` | Is the answer relevant to the question? | Question-answering |
| **Retrieval** | `builtin.retrieval` | Are the retrieved chunks relevant to the query? (without ground truth) | When retrieval quality is a bottleneck |
| **Document Retrieval** | `builtin.document_retrieval` | Precise search quality: NDCG, Fidelity, XDCG (requires ground truth labels) | When you have labeled relevance data |
| **Response Completeness** | `builtin.response_completeness` | Does the answer cover all aspects the query asked? (recall aspect) | Multi-part questions |

**Groundedness vs Response Completeness:**
- Groundedness = precision: "everything in the answer is supported by docs"
- Response Completeness = recall: "all aspects of the question are answered"

Required inputs for most RAG evaluators: `query` + `response` + `context` (the retrieved documents).

```python
testing_criteria = [
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
]
```

---

#### 3. Risk and Safety Evaluators

These use Microsoft's hosted safety models — **no `deployment_name` needed**, they don't use your quota.

| Evaluator | `builtin` name | Scope | Severity scale |
|---|---|---|---|
| **Violence** | `builtin.violence` | Models + Agents | 0–7 |
| **Sexual** | `builtin.sexual` | Models + Agents | 0–7 |
| **Self-harm** | `builtin.self_harm` | Models + Agents | 0–7 |
| **Hate / Unfairness** | `builtin.hate_unfairness` | Models + Agents | 0–7 |
| **Protected Material** | `builtin.protected_material` | Models + Agents | pass/fail |
| **Code Vulnerability** | `builtin.code_vulnerability` | Models + Agents | pass/fail |
| **Indirect Attack (XPIA)** | `builtin.indirect_attack` | Models only | pass/fail |
| **Ungrounded Attributes** | `builtin.ungrounded_attributes` | Models + Agents | true/false |
| **Prohibited Actions** *(Preview)* | `builtin.prohibited_actions` | **Agents only** | pass/fail |
| **Sensitive Data Leakage** *(Preview)* | `builtin.sensitive_data_leakage` | **Agents only** | pass/fail |

Output for content safety (0–7 scale):
```json
{"metric": "violence", "score": 0, "label": "pass", "threshold": 3, "passed": true,
 "reason": "The response refuses to provide harmful content."}
```

**Defect rate** = % of responses that fail. Use this as the headline safety metric.

**Code vulnerability** catches: SQL injection, path injection, XSS, SSRF, hardcoded credentials, tar-slip, weak crypto, Flask debug mode, and 15+ more categories.

**Indirect attack (XPIA)** categories:
- Manipulated content — false info, formatting tricks
- Intrusion — backdoors, privilege escalation, jailbreaks
- Information gathering — unauthorized data access/exfiltration

---

#### 4. Agent Evaluators

Evaluate agent-specific behaviors: did the right tools get called in the right order?

| Evaluator | `builtin` name | Measures |
|---|---|---|
| **Tool Call Accuracy** | `builtin.tool_call_accuracy` | Did the agent call the correct tools with correct arguments? |
| **Intent Resolution** | `builtin.intent_resolution` | Did the agent correctly identify what the user wanted? |
| **Task Adherence** | `builtin.task_adherence` | Did the agent complete the task without taking unintended actions? |

These require `tool_calls` in the data mapping alongside `query` and `response`.

---

#### 5. Textual Similarity Evaluators

No LLM judge needed — pure string comparison against ground truth.

| Evaluator | `builtin` name | What it computes |
|---|---|---|
| **F1 Score** | `builtin.f1_score` | Word overlap between response and ground truth (precision + recall) |
| **BLEU** | `builtin.bleu_score` | n-gram precision vs ground truth (classic MT metric) |
| **ROUGE** | `builtin.rouge_score` | Recall-oriented n-gram overlap |
| **METEOR** | `builtin.meteor_score` | Alignment-based similarity accounting for synonyms |
| **GLEU** | `builtin.gleu_score` | Variant of BLEU with recall component |
| **String Exact Match** | `builtin.string_exact_match` | 1.0 if identical, 0.0 otherwise |

Required inputs: `response` + `ground_truth`. No judge model, no cost.

---

#### 6. Custom Evaluators

Bring your own scoring logic.

Two options:

**Python function evaluator:**
```python
# Define a custom evaluator as a Python function
def my_evaluator(response: str, ground_truth: str) -> dict:
    # your scoring logic
    score = len(set(response.split()) & set(ground_truth.split())) / len(ground_truth.split())
    return {"my_metric": score, "passed": score >= 0.5}
```

**Prompt-based evaluator (LLM judge):**
```python
# Write a prompt that acts as judge
# Input template: {{query}}, {{response}}
# Output: structured score
```

Custom evaluators can be used in continuous evaluation (Monitor tab → Settings → Continuous evaluation → Add evaluator).

---

#### 7. Rubric Evaluators

Define your own pass/fail criteria in plain English. No ground truth needed.

```python
testing_criteria = [
    {
        "type": "label_model_graded_rubric",
        "name": "is_concise",
        "input": "{{item.response}}",
        "labels": ["concise", "verbose"],
        "passing_labels": ["concise"],
        "model": "gpt-5-mini",
        "instructions": "Label as 'concise' if under 100 words, 'verbose' otherwise.",
    }
]
```

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
            "data_mapping": {"query": "{{item.query}}", "response": "{{item.response}}", "context": "{{item.context}}"},
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
    name="My Safety Eval",
    data_source_config={"type": "azure_ai_source", "scenario": "responses"},
    testing_criteria=[
        {
            "type": "azure_ai_evaluator",
            "name": "violence_check",
            "evaluator_name": "builtin.violence",
            "data_mapping": {"query": "{{item.query}}", "response": "{{item.response}}"},
        }
    ],
)
```

#### Option C: Portal

Foundry portal → **Build** → **Evaluations** tab → Create evaluation → select dataset → select evaluators → run.

View results in portal, download as CSV, compare runs over time.

---

### Dataset Format (JSONL)

```jsonl
{"query": "What is the refund policy?", "response": "Refunds are processed within 5 business days.", "context": "Northwind refund policy states 5 business days processing time.", "ground_truth": "5 business days"}
{"query": "How do I cancel my subscription?", "response": "Go to Account Settings > Subscription > Cancel.", "context": "To cancel: navigate to Account Settings, then Subscription, then Cancel.", "ground_truth": "Account Settings > Subscription > Cancel"}
```

Common columns: `query`, `response`, `context`, `ground_truth`, `tool_calls`.

---

### Human Evaluation

Foundry portal → Build → Evaluations → **Human Evaluation** tab.

Assign labelers to review agent responses. Labelers see the conversation and rate:
- Relevance (1–5)
- Accuracy (1–5)
- Thumbs up/down

Results flow into same App Insights pipeline via OTel `gen_ai.evaluation.result` events.

---

### Convert Traces to Dataset

Foundry portal → Traces → filter traces → **Export to dataset**.

Creates a JSONL file from production traces. Use this dataset for evaluation without writing test cases manually. Best practice: export a sample of production traces weekly and run evaluation against them.

---

## PART 5 — HOW EVERYTHING CONNECTS

### The Full Lifecycle

```
DEVELOPMENT
───────────
Write your agent/app
↓
Run evaluation on golden dataset (offline)
  → safety score OK?
  → groundedness above 4.0?
  → task adherence passing?
↓ (if yes)
Deploy

PRODUCTION
──────────
Every request:
  → Guardrails check input [real-time, blocking]
  → Agent/model runs
  → Guardrails check output [real-time, blocking]
  → Trace written to App Insights [async, non-blocking]
  
Continuous (background):
  → Monitoring dashboard shows latency, tokens, errors [2–5 min lag]
  → Continuous evaluation samples live traffic [every response or hourly schedule]
  → Red teaming scans run on schedule [daily/weekly]
  → Alerts fire if metrics cross thresholds

RELEASE GATE
────────────
Before next version:
  → Run evaluation on new dataset
  → Compare scores to previous version
  → Pass gate: deploy
  → Fail gate: fix prompt/model, re-evaluate
```

---

## Portal Locations Cheat Sheet

| Feature | Where |
|---|---|
| Create / edit guardrail policy | Project → **Guardrails + controls** |
| Test guardrail (try it out) | Project → Guardrails + controls → **Try it out** |
| Task Adherence test | Guardrails + controls → Try it out → Agentic Workflow → Task Adherence |
| Connect App Insights | Project → **Settings** → Tracing |
| View traces (per request) | Project → **Traces** tab |
| View conversation history | Traces → click a Conversation ID |
| Agent monitoring dashboard | Build → select agent → **Monitor** tab |
| Configure continuous eval | Monitor tab → gear icon → Continuous evaluation |
| Run evaluation | Build → **Evaluations** tab → Create |
| Human evaluation | Evaluations → **Human Evaluation** subtab |
| Recurring eval configs | Evaluations → **Recurring Configs** subtab |
| Export traces to dataset | Traces → filter → Export to dataset |
| Red teaming | Monitor tab → Settings → Red team scans |

---

## Common Confusion Points — Cleared Up

**"Guardrails vs evaluation — both check for harmful content. Same thing?"**
No. Guardrails: real-time, blocks the response before user sees it. Evaluation: offline, scores a batch of responses AFTER the fact. You need both — guardrails prevent harm in production, evaluation measures how often harm is attempted so you can tune.

**"Groundedness is a guardrail filter AND an evaluator. Which is which?"**
`builtin.groundedness` evaluator = offline scoring, runs on a dataset, does NOT block anything.
The Groundedness risk in guardrails = real-time filter on model output that can BLOCK responses. Two different features with similar goals. Groundedness guardrail is models-only (not agents) in current preview.

**"Task Adherence is a guardrail AND an evaluator. Which is which?"**
Task Adherence in guardrails = calls Content Safety API at runtime, blocks misaligned tool calls.
`builtin.task_adherence` evaluator = offline scoring of agent step quality. Same concept, different execution path.

**"Tracing = logging?"**
Tracing is structured, hierarchical, tied to a specific request. Logging is flat text. Tracing shows the SPAN TREE of one request. Logs are good for errors; traces are essential for AI because a single response spawns dozens of sub-calls.

**"Monitoring tells me if answers are good?"**
No. Monitoring tells you latency, error rate, and token count — operational health. Whether answers are CORRECT is evaluation — completely separate pipeline.

**"If I have guardrails, do I need evaluation?"**
Yes. Guardrails block known bad patterns. Evaluation reveals whether your app produces good-quality, grounded, coherent answers — things guardrails don't measure. Guardrails = safety floor. Evaluation = quality ceiling.

**"The severity scale for content safety is 0–7 for evaluation but Off/Low/Medium/High for guardrails. How do they map?"**
Guardrail severity threshold = minimum severity level that triggers blocking:
- Low threshold ≈ score ≥ 2 triggers block
- Medium threshold ≈ score ≥ 4 triggers block
- High threshold ≈ score ≥ 6 triggers block

Evaluation outputs the raw 0–7 score and compares to a threshold you set (default 3 = blocks medium+).

---

---

## PART 6 — ADDITIONAL EVALUATION TOOLS

### Rubric Evaluators — Custom Scoring Criteria

Define exactly what "good" means for your specific use case. Instead of using generic quality metrics, you write a rubric with weighted dimensions and an LLM judges each response against it.

**How it works:**
- You define criteria (dimensions) — each with a `description` and a `weight`
- LLM judge scores each dimension 1–5 on each response
- Overall score = weighted average of applicable dimensions, normalized to 0–1
- Pass if score ≥ threshold (default 0.5)

**Dimension fields:**

| Field | What it is |
|---|---|
| `id` | Stable slug, e.g. `"intent_recognition"` |
| `description` | What to measure and what counts as good/bad |
| `weight` | Importance (1–10). Generation pipeline assigns exactly ONE dimension weight 8–10. |
| `always_applicable` | If true, scored for EVERY response without checking relevance first. Use for general quality. |

**Auto-generate a rubric (recommended):**

In portal: Evaluations → Create → select rubric evaluator → provide one of:
- Foundry agent (pulls instructions automatically)
- Agent system prompt (paste instructions)
- Reference files (domain docs, knowledge base)

Optionally add production traces on top for grounding in real usage.

Best judge models: `gpt-5.4-mini` (best cost/performance), `gpt-5.2`, `gpt-5-mini`.

**Example rubric (restaurant reservation agent):**
```json
[
  {"id": "intent_recognition", "description": "Correctly identifies booking intent and pursues the right workflow.", "weight": 9},
  {"id": "tool_usage_accuracy", "description": "Calls correct tool with correct params. No unnecessary calls.", "weight": 6},
  {"id": "policy_enforcement", "description": "Enforces: dinner 17:00-22:00, max party 8, 30-day window.", "weight": 5},
  {"id": "information_gathering", "description": "Collects date/time/party/contact before booking. No re-asking.", "weight": 4},
  {"id": "communication_clarity", "description": "Clear, concise, professional tone. Confirms before finalizing.", "weight": 2},
  {"id": "general_quality", "description": "Other quality factors not covered above.", "weight": 5, "always_applicable": true}
]
```

**Pass example output:**
```json
{
  "score": 0.94, "label": "pass", "threshold": 0.5, "passed": true,
  "reason": "intent_recognition(5), tool_usage_accuracy(5), policy_enforcement(5) — correct booking, valid params, within constraints.",
  "properties": {"dimension_scores": [{"id": "intent_recognition", "score": 5, "applicable": true, "weight": 9, "reason": "..."}]}
}
```

**Fail example:** party of 12 when max is 8 → `policy_enforcement` score 1 → overall 0.35 → fail.

Rubric evaluators work in continuous evaluation (Monitor tab → Settings → Continuous evaluation → Add evaluator).

---

### Azure OpenAI Graders — Alternative Evaluation API

Different API surface from built-in evaluators. Uses the OpenAI Evals API directly (`openai_client.evals.create`). Use when you need full prompt control or deterministic string checks.

| Grader type | Uses LLM? | What it does |
|---|---|---|
| `label_model` | Yes | Classifies text into your predefined categories (sentiment, topic, etc.) |
| `score_model` | Yes | Assigns numeric score 0–1 based on your custom scoring prompt |
| `string_check` | No | Exact/pattern string comparison against ground truth |
| `text_similarity` | No | Similarity metrics (BLEU, ROUGE, cosine, fuzzy) against ground truth |

**Label grader (classify sentiment/topic):**
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
    "passing_labels": ["positive", "neutral"],  # fail if negative
}
```

**Score grader (0–1 quality score):**
```python
{
    "type": "score_model",
    "name": "quality_score",
    "model": "gpt-5-mini",
    "input": [
        {"role": "system", "content": "Rate response quality 0 to 1. 1=perfect, 0=wrong."},
        {"role": "user", "content": "Response: {{item.response}}\nGround Truth: {{item.ground_truth}}"},
    ],
    "pass_threshold": 0.7,
}
```

**String check (exact match):**
```python
{
    "type": "string_check",
    "name": "exact_match",
    "input": "{{item.response}}",
    "reference": "{{item.ground_truth}}",
    "operation": "eq",  # also: ne, like, ilike
}
```

**Text similarity (BLEU/ROUGE/cosine):**
```python
{
    "type": "text_similarity",
    "name": "similarity_check",
    "input": "{{item.response}}",
    "reference": "{{item.ground_truth}}",
    "evaluation_metric": "bleu",  # also: rouge_1-5, rouge_l, meteor, cosine, fuzzy_match, gleu
    "pass_threshold": 0.8,
}
```

**When to use graders vs built-in evaluators:**
- Graders: need custom LLM prompt, custom classification labels, or deterministic comparison
- Built-in evaluators (`builtin.groundedness`, etc.): need standardized safety/quality scoring against Foundry benchmarks

---

### Benchmark Evaluations — Industry Standard Datasets

Run your model or agent against pre-built benchmark datasets without creating your own test data.

**Portal:** Build → Evaluations → Create → select target → Data step → choose **Benchmarks**.

Available benchmarks:

| Benchmark | Task | Examples | What it measures |
|---|---|---|---|
| **AIME 2025** | Reasoning, Math | 30 | Competition math problems |
| **BBEH** | Reasoning, Quality | 4,520 | Broad evaluation harness |
| **BIG-Bench Hard** | Reasoning, Quality | 934 | Hard reasoning tasks (regex_match scoring) |
| **ChemBench** | Reasoning, Sciences | 2,785 | Chemistry knowledge |
| **FrontierScience** | Reasoning, Quality | 160 | Scientific frontier questions (needs judge model) |
| **GPQA Diamond** | Reasoning, Quality | 198 | Expert-level science questions |
| **MuSR** | Reasoning, Quality | 756 | Multi-step reasoning |
| **TruthfulQA** | Truthfulness, Quality | 790 | Factual accuracy / hallucination rate |

**Key distinction: target vs judge model**
- **Target** = the model/agent you're evaluating
- **Judge model** = the model used to score answers (e.g. FrontierScience needs a judge; TruthfulQA uses regex_match and doesn't)

**REST API:**
```http
POST {project-endpoint}/openai/evals?api-version=2025-11-15-preview
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

For benchmarks needing a judge model, add `"grader_model": "{connection}/{deployment}"`.

Result format: `82%` = `645/790 examples passing`.

---

### Cluster Analysis — Find Patterns in Failures

After running evaluation, cluster analysis groups similar failures together to show you WHAT IS GOING WRONG and WHY.

**Portal:** Evaluations → select completed runs → **Cluster analysis** button.

> Warning: results are NOT saved. Download before navigating away.

**What you see:**
- Dot map where each dot = one evaluated response, color = cluster assignment
- Dots positioned by semantic similarity — similar failures cluster together
- Click a cluster → diagnostic description + recommended fix
- Click a subcluster → entry-level scores breakdown
- Click a dot → full conversation + metadata + trace ID

**Filter options:**
- By span type: Chat, Agent, Tool, Conversation
- By token level: Low (<500), Medium (500–2k), High (>2k)
- Advanced: filter by score, evaluator type, timestamp

**Typical cluster names:** `inadequate_final_answer`, `invalid_or_missing_api_key`, `incorrect_response`, etc.

Each cluster gives: description of the pattern + recommendations for fixes (e.g. "Update prompt to enforce constraint X").

**Use cluster results to:**
- Refine agent instructions to address recurring failure patterns
- Build fine-tuning data from identified failure categories
- Re-run evaluation after fixes and compare cluster maps

---

### Guided Guardrail Setup — Questionnaire-Based

Instead of manually selecting controls, answer questions about your agent → Foundry picks the right guardrails.

**Portal:** Build → Agents → select agent → expand Guardrails section → Manage guardrail → **Guided guardrails setup**.

**Three question sets:**

**1. Who uses the agent?**
- Public users → stricter content safety, jailbreak protections
- Internal teams → lighter controls for trusted users

**2. Input and data:**
- Where does input come from? (user messages / uploaded files / external APIs)
- Does it process sensitive data? → enables PII detection
- Does it handle PII specifically? → enables data protection controls

**3. Tools and actions:**
- Calls external tools? → enables tool response validation, spotlighting (indirect attack protection)
- Takes real-world actions (send email, modify records)? → enables task adherence + action validation
- Generates or executes code? → enables protected material detection + code safety

After answering → Foundry shows recommended controls per intervention point → you can edit individual controls → **Create guardrails**.

> Each agent needs its own guardrail setup — don't share one guardrail across agents with different use cases.

---

## PART 7 — ADVANCED TRACING FEATURES

### Trace Replay — Step Through a Conversation

Visually replay any traced agent conversation step-by-step.

**Access:** Traces tab → click a Conversation ID or Trace ID → Replay Panel opens.

**Two views:**

| View | What it shows |
|---|---|
| **Trajectories** | Hierarchical span tree with waterfall bars (duration OR token cost). Best for finding bottlenecks and failures. |
| **User** | Chat-style view of what the end user saw. Span tree available as collapsible panel alongside. |

**Playback controls:**
- Play button → replays spans sequentially, highlighting each step
- Skip → jump ahead
- 1x / 2x / 4x speed
- Timeline scrubber → jump to any moment

**Filter while replaying:**
- By type: Chat, Agent, Tool, Conversation
- By token level: Low (<500 tokens), Medium (500–2k), High (>2k)
- Find in trace: search by span name

**Useful for:** Root cause analysis, token optimization (spot expensive spans), audits, debugging unexpected agent behavior.

---

### Sensitive Content Protection — AppGenAIContent Table

Foundry traces capture prompts, model responses, tool arguments — all potentially containing PII or PHI. The `AppGenAIContent` table is a dedicated protected table that isolates this sensitive content from the rest of trace telemetry.

**Migration deadline: September 30, 2026** — after this date Foundry stops writing the 7 sensitive attributes to `AppDependencies`/`AppTraces`/`AppEvents`. They only exist in `AppGenAIContent`.

---

#### The 7 Sensitive Attributes

| OTel Attribute | What it contains | Example value |
|---|---|---|
| `gen_ai.input.messages` | User prompts sent to model | `[{"role":"user","content":"What is my account balance?"}]` |
| `gen_ai.output.messages` | Model responses | `[{"role":"assistant","content":"Your balance is $4,200."}]` |
| `gen_ai.system_instructions` | System prompt / agent instructions | `"You are a banking assistant. Never reveal..."` |
| `gen_ai.tool.definitions` | Tool schemas available to agent | `[{"name":"get_balance","description":"...","parameters":{...}}]` |
| `gen_ai.tool.call.arguments` | Arguments sent to a tool call | `{"account_id":"ACC-12345","include_pending":true}` |
| `gen_ai.tool.call.result` | What the tool returned | `{"balance":4200.00,"currency":"USD","last_txn":"2026-08-15"}` |
| `gen_ai.evaluation.explanation` | LLM judge's reasoning on eval | `"Response correctly identifies the amount but omits pending..."` |

Everything else (span names, durations, token counts, latency, error codes) stays in the regular tables — visible to anyone with `Log Analytics Reader`.

---

#### Step 1 — Register the Feature Flag

```bash
# Enable early — routes sensitive attrs to AppGenAIContent ONLY
az feature register --namespace Microsoft.Insights --name protectGenAISensitiveData

# Verify registration propagated (can take a few minutes)
az feature show --namespace Microsoft.Insights --name protectGenAISensitiveData --query "properties.state"
# → "Registered"
```

**If you need more time after Sept 30, 2026** (buys until Sept 30, 2027 max):
```bash
az feature register --namespace Microsoft.Insights --name optOutProtectGenAISensitiveData
# To re-enable early: unregister the opt-out flag
az feature unregister --namespace Microsoft.Insights --name optOutProtectGenAISensitiveData
```

---

#### Step 2 — Set the Table as Protected (Deny-by-Default)

Via Azure CLI:
```bash
# Get your Log Analytics workspace resource ID first
WORKSPACE_ID=$(az monitor log-analytics workspace show \
  --resource-group <your-rg> \
  --workspace-name <your-workspace> \
  --query id -o tsv)

# Set AppGenAIContent table protection level to Protected
az monitor log-analytics workspace table update \
  --resource-group <your-rg> \
  --workspace-name <your-workspace> \
  --name AppGenAIContent \
  --protection-level Protected
```

Via portal: Azure portal → Log Analytics workspace → **Tables** → find `AppGenAIContent` → **Manage table** → set **Protection level** = `Protected`.

After this: any user with only `Log Analytics Reader` gets a permission denied when querying `AppGenAIContent`. They still see all other trace tables normally.

---

#### Step 3 — Grant Access to Authorized Users Only

```bash
# Assign Privileged Monitoring Data Reader to a specific user
az role assignment create \
  --role "Privileged Monitoring Data Reader" \
  --assignee <user-object-id-or-upn> \
  --scope $WORKSPACE_ID

# Assign to a group (preferred — manage via group membership)
az role assignment create \
  --role "Privileged Monitoring Data Reader" \
  --assignee <group-object-id> \
  --scope $WORKSPACE_ID
```

With PIM (recommended): assign as eligible rather than permanent — users activate JIT for incident review only.

---

#### What Each Role Sees

| Role | Span names, durations, token counts | Prompts, responses, tool args |
|---|---|---|
| No role | ❌ | ❌ |
| `Log Analytics Reader` | ✅ | ❌ (table protected) |
| `Privileged Monitoring Data Reader` | ✅ | ✅ |

---

#### Step 4 — Update KQL Queries (Before Sept 30, 2026)

After migration, attribute keys still appear in old tables but values become a pointer — not the actual content. Any query reading those 7 fields from `AppDependencies`/`AppTraces`/`AppEvents` silently gets empty values.

**Before (breaks after migration):**
```kusto
AppDependencies
| where Data has "gen_ai.input.messages"
| extend prompt = tostring(Properties["gen_ai.input.messages"])
| project timestamp, prompt
```

**After (correct query targeting AppGenAIContent):**
```kusto
AppGenAIContent
| where TimeGenerated > ago(24h)
| extend
    prompt     = tostring(Properties["gen_ai.input.messages"]),
    response   = tostring(Properties["gen_ai.output.messages"]),
    sys_prompt = tostring(Properties["gen_ai.system_instructions"]),
    tool_args  = tostring(Properties["gen_ai.tool.call.arguments"]),
    tool_result = tostring(Properties["gen_ai.tool.call.result"])
| project TimeGenerated, prompt, response, tool_args, tool_result
| order by TimeGenerated desc
```

**Correlate sensitive content with non-sensitive spans** (join on operation ID):
```kusto
let sensitive = AppGenAIContent
    | where TimeGenerated > ago(1h)
    | extend
        opId    = tostring(Properties["operation_id"]),
        prompt  = tostring(Properties["gen_ai.input.messages"]),
        response = tostring(Properties["gen_ai.output.messages"]);
AppDependencies
| where TimeGenerated > ago(1h)
| where DependencyType == "LLM"
| join kind=leftouter sensitive on $left.OperationId == $right.opId
| project TimeGenerated, Name, DurationMs, prompt, response
| order by DurationMs desc
```

**Check user feedback pass rate alongside prompts:**
```kusto
let feedback = customEvents
    | where name == "gen_ai.evaluation.result"
    | extend
        score = todouble(customDimensions["gen_ai.evaluation.score.value"]),
        label = tostring(customDimensions["gen_ai.evaluation.score.label"]),
        opId  = tostring(operation_Id);
AppGenAIContent
| where TimeGenerated > ago(7d)
| extend
    opId   = tostring(Properties["operation_id"]),
    prompt = tostring(Properties["gen_ai.input.messages"])
| join kind=leftouter feedback on $left.opId == $right.opId
| summarize avg_score = avg(score), total = count() by bin(TimeGenerated, 1d)
```

---

#### Checklist — Before Sept 30, 2026

- [ ] Register `protectGenAISensitiveData` feature flag
- [ ] Set `AppGenAIContent` table protection level to Protected
- [ ] Assign `Privileged Monitoring Data Reader` to authorized users/groups only
- [ ] Audit all custom KQL queries — update any reading the 7 sensitive attributes from old tables
- [ ] Update alert rules that reference sensitive attributes
- [ ] Update workbooks/dashboards using those fields
- [ ] Verify: `Log Analytics Reader` user cannot see content in `AppGenAIContent`
- [ ] Verify: `Privileged Monitoring Data Reader` user CAN query `AppGenAIContent`

---

#### What Does NOT Change

- Span names, durations, token counts, error codes, operation IDs → still in `AppDependencies`/`AppTraces`
- Built-in Foundry portal Traces view → updated automatically, continues working
- Data ingested BEFORE Sept 30, 2026 → stays in old tables, queryable as before
- Retention policies → unchanged, follows your Log Analytics workspace settings

---

### Ask AI on the Monitoring Dashboard

Built-in chat assistant on the monitoring dashboard for natural language insights.

**Portal:** 
- Build → Models or Agents → Monitor → click **Ask AI** icon
- Operate → Overview → select predefined prompt from Ask AI banner

**Example questions:**
- "Give me a summary of the dashboard"
- "Analyze the performance trend"
- "What caused the latency spike on [date]?"

Ask AI returns:
- Summary of current metrics
- Highlighted anomalies for the selected time range
- Annotated links to specific charts (click to scroll to chart with highlight)
- Recommended next steps

Example recommendations:
- "Investigate latency increase on [date] — it might be recurring."
- "Optimize prompt token usage to reduce costs as usage scales."
- "Consider load testing to identify bottlenecks."

> Tip: Adjust the time range selector BEFORE asking for insights — Ask AI only analyzes the currently selected range.

---

## References

- [Guardrails overview](https://learn.microsoft.com/azure/foundry/guardrails/guardrails-overview)
- [Intervention points](https://learn.microsoft.com/azure/foundry/guardrails/intervention-points)
- [Task Adherence](https://learn.microsoft.com/azure/foundry/guardrails/task-adherence)
- [How to create guardrails](https://learn.microsoft.com/azure/foundry/guardrails/how-to-create-guardrails)
- [Agent tracing overview](https://learn.microsoft.com/azure/foundry/observability/concepts/trace-agent-concept)
- [Set up tracing](https://learn.microsoft.com/azure/foundry/observability/how-to/trace-agent-setup)
- [Monitor agents dashboard](https://learn.microsoft.com/azure/foundry/observability/how-to/how-to-monitor-agents-dashboard)
- [Log end-user feedback](https://learn.microsoft.com/azure/foundry/observability/how-to/log-end-user-feedback)
- [General purpose evaluators](https://learn.microsoft.com/azure/foundry/concepts/evaluation-evaluators/general-purpose-evaluators)
- [RAG evaluators](https://learn.microsoft.com/azure/foundry/concepts/evaluation-evaluators/rag-evaluators)
- [Risk and safety evaluators](https://learn.microsoft.com/azure/foundry/concepts/evaluation-evaluators/risk-safety-evaluators)
- [Agent evaluators](https://learn.microsoft.com/azure/foundry/concepts/evaluation-evaluators/agent-evaluators)
- [Custom evaluators](https://learn.microsoft.com/azure/foundry/concepts/evaluation-evaluators/custom-evaluators)
- [Textual similarity evaluators](https://learn.microsoft.com/azure/foundry/concepts/evaluation-evaluators/textual-similarity-evaluators)
- [Evaluate an agent](https://learn.microsoft.com/azure/foundry/observability/how-to/evaluate-agent)
- [Human evaluation](https://learn.microsoft.com/azure/foundry/observability/how-to/human-evaluation)
- [Traces to dataset](https://learn.microsoft.com/azure/foundry/observability/how-to/traces-to-dataset)
- [Benchmark evaluations](https://learn.microsoft.com/azure/foundry/observability/how-to/benchmark-evaluations)
- [Trace replay](https://learn.microsoft.com/azure/foundry/observability/how-to/trace-agent-replay)
- [Cluster analysis](https://learn.microsoft.com/azure/foundry/observability/how-to/cluster-analysis)
- [Rubric evaluators](https://learn.microsoft.com/azure/foundry/concepts/evaluation-evaluators/rubric-evaluators)
- [Azure OpenAI graders](https://learn.microsoft.com/azure/foundry/concepts/evaluation-evaluators/azure-openai-graders)
- [Guided guardrail setup](https://learn.microsoft.com/azure/foundry/guardrails/guided-set-up)
- [Sensitive content in traces](https://learn.microsoft.com/azure/foundry/observability/how-to/traces-sensitive-content)
- [Monitoring dashboard Ask AI](https://learn.microsoft.com/azure/foundry/observability/how-to/optimization-dashboard)
