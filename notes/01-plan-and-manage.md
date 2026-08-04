# Domain 1 — Plan and Manage an Azure AI Solution (25–30%)

## Syllabus sections

| Section | Topics |
|---------|--------|
| Choose Foundry services | Model selection, deployment type, retrieval method, memory/tools |
| Set up AI solutions | Infra design, deployment options, model+agent config, CI/CD |
| Manage, monitor, secure | Quotas, monitoring, index health, security |
| Responsible AI | Safety filters, evaluators, tracing, agent governance |

---

# Model Selection

## The decision tree

```
What task are you doing?
        │
        ├── Multi-step reasoning + broad knowledge? → LLM (GPT-4.1, o4)
        │
        ├── Single narrow task, cost/latency critical? → SLM (Phi-4, Llama 3.2)
        │
        ├── Image + text together? → Multimodal (GPT-4o, gpt-4.1)
        │
        ├── Translate text? → Azure Translator (Foundry Tools)
        ├── Detect entities/PII/sentiment? → Azure Language (Foundry Tools)
        ├── Voice? → Azure Speech (Foundry Tools)
        └── Route traffic across models dynamically? → Model Router deployment
```

## LLM vs SLM comparison

| Dimension | LLM | SLM |
|-----------|-----|-----|
| Knowledge breadth | Broad | Narrow |
| Reasoning depth | Deep multi-step | Single task |
| Latency | Higher | Lower |
| Cost | Higher | Lower |
| On-device / edge | No | Yes (Phi-4) |
| Examples | GPT-4.1, o4-mini, Claude Opus | Phi-4, Llama 3.2 3B |

Memory: **LLM = think broadly; SLM = act cheaply.**

## Model Router

```
deploy model-router deployment
        ↓
send any prompt
        ↓
router picks best model automatically
        ↓
check response.model to see which was chosen
```

---

# Deployment Types

> **MS Docs source:** `.context/azure-ai-docs/articles/foundry/foundry-models/concepts/deployment-types.md`

## Standard deployments — 10 types (pay-per-token OR PTU × Global/DataZone/Regional)

| Type | SKU code | Data processing | Billing | Best for |
|------|----------|----------------|---------|---------|
| **Instant (preview)** | N/A | Any region | Pay-per-token | Prototyping — no deployment needed |
| **Global Standard** | `GlobalStandard` | Any region | Pay-per-token | Default; highest quota; new models first |
| **Global Provisioned** | `GlobalProvisionedManaged` | Any region | PTU (reserved) | Predictable high-throughput, global routing |
| **Global Batch** | `GlobalBatch` | Any region | 50% off, 24hr async | Large async jobs |
| **Data Zone Standard** | `DataZoneStandard` | EU / US / APAC zone | Pay-per-token | Zone compliance + higher quota than regional |
| **Data Zone Provisioned** | `DataZoneProvisionedManaged` | EU / US / APAC zone | PTU (reserved) | Zone compliance + guaranteed throughput |
| **Data Zone Batch** | `DataZoneBatch` | EU / US / APAC zone | 50% off, 24hr async | Large async jobs within data zone |
| **Standard (Regional)** | `Standard` | Single region | Pay-per-token | Strict regional compliance, low volume |
| **Regional Provisioned** | `ProvisionedManaged` | Single region | PTU (reserved) | Regional compliance + guaranteed throughput |
| **Developer** | `DeveloperTier` | Any region | Pay-per-token | Fine-tuned model evaluation only; 24hr lifetime |

## Managed Compute (preview — separate category)

For OSS models not covered by Standard deployments (Hugging Face, NVIDIA NIMs, Databricks, industry models):

```
Billing:   Hourly per GPU SKU (A100 80GB / H100 80GB / H200 141GB / MI300X)
Scaling:   Auto-scale + scale-to-zero (billing stops when idle)
Auth:      Same Foundry endpoint, same Entra ID / API key
Route:     <endpoint>/managed-deployments/<deployment-name>/
```

## Decision tree (updated)

```
Just prototyping / trying a model?    → Instant (no deployment required)
No data residency requirement?        → Global Standard (highest quota)
EU / US / APAC zone compliance?       → Data Zone Standard or Data Zone Provisioned
Strict single-region requirement?     → Standard (Regional) or Regional Provisioned
Predictable throughput, no 429s?      → any Provisioned type (pick by data zone need)
Large batch job, not time-sensitive?  → Global Batch or Data Zone Batch (50% cheaper)
Fine-tuned model evaluation?          → Developer (24hr lifetime, no SLA)
OSS model (Llama, HuggingFace, NIM)?  → Managed Compute (hourly GPU)
```

Memory: **Global = first + cheap; Data Zone = EU/US/APAC compliance; Regional = strict; PTU = guaranteed; Batch = async 50% off; Managed Compute = OSS hourly GPU.**

### PTU exam trap

PTU reserves *throughput* (tokens/minute capacity), NOT a fixed number of tokens. You still pay per token consumed. The benefit: no 429 rate-limit errors.

---

# Authentication + Security

## Auth ladder

```
❌ Hardcoded API key        ← never
        ↓
✅ Managed Identity          ← VM / App Service in Azure gets an Azure AD identity
        ↓
✅ DefaultAzureCredential    ← automatically picks the right credential
        ↓
✅ Bearer token via Entra   ← scope: https://cognitiveservices.azure.com/.default
```

`DefaultAzureCredential` tries credentials in this order:
1. Environment variables
2. Workload Identity (AKS)
3. Managed Identity
4. Azure CLI (`az login`)
5. Azure Developer CLI
6. Visual Studio / VS Code

For OpenAI SDK: use `get_bearer_token_provider(DefaultAzureCredential(), scope)` — never pass a raw key.

## Foundry RBAC roles (source: `foundry/concepts/rbac-foundry.md`)

| Role | Create projects | Build/develop | Assign roles | Publish agents | Interact with agents |
|------|:--------------:|:-------------:|:------------:|:--------------:|:--------------------:|
| **Foundry Agent Consumer** | ✘ | ✘ | ✘ | ✘ | ✔ |
| **Foundry User** | ✘ | ✔ | ✘ | ✘ | ✔ |
| **Foundry Project Manager** | ✘ | ✔ | ✔ (Foundry User only) | ✔ | ✔ |
| **Foundry Account Owner** | ✔ | ✘ | ✔ | ✘ | ✘ |
| **Foundry Owner** | ✔ | ✔ | ✔ | ✔ | ✔ |

Azure built-in **Owner** / **Contributor** still grant control-plane access but NOT data-plane (no build/develop, no agent endpoints). Key rule: data-plane needs a Foundry role.

### Agent-scope assignments

Assign at per-agent scope (not just project scope) to grant endpoint access to one agent only:
```
/subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.CognitiveServices/
  accounts/<account>/projects/<project>/agents/<agentName>
```

### AI Search roles (still needed for search scenarios)

| Role | What it allows |
|------|---------------|
| **Search Index Data Reader** | Query an AI Search index |
| **Search Index Data Contributor** | Write/update documents in AI Search index |

## Private networking note

Private endpoints connect an Azure AI resource to your VNet so traffic never leaves the Microsoft backbone. Configured in portal / ARM — not in application code. Pair with Managed Identity for fully keyless, network-isolated access.

---

# Quotas, Rate Limits, Cost

## Key concepts

| Term | Meaning |
|------|---------|
| **TPM** | Tokens Per Minute — rate limit on how fast you can consume tokens |
| **RPM** | Requests Per Minute — rate limit on number of API calls |
| **PTU** | Provisioned Throughput Unit — pre-reserved capacity block |
| **HTTP 429** | Too Many Requests — you hit the rate limit |

## Backoff pattern (tenacity)

```python
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from openai import RateLimitError

@retry(
    retry=retry_if_exception_type(RateLimitError),
    wait=wait_exponential(multiplier=1, min=2, max=60),
    stop=stop_after_attempt(6),
)
def call_api(): ...
```

Memory: **429 = wait and retry with exponential backoff + jitter.**

---

# Monitoring + Evaluators

## The monitoring stack

```
Application
      │
      ├── OpenTelemetry spans ─────────────────→ Application Insights
      │     └── attributes: tokens.input, tokens.output,
      │                     latency_ms, safety.*
      │
      ├── Evaluators (offline batch) ──────────→ Foundry Evaluation UI
      │     ├── Response Completeness
      │     ├── Groundedness
      │     ├── Task Adherence
      │     └── Tool Call Accuracy
      │
      └── Search index health ─────────────────→ Indexer run logs
```

## Evaluators — 7 categories, 30+ built-in (source: `foundry/concepts/built-in-evaluators.md`)

### Key evaluators for AI-103 exam

| Evaluator | Category | Inputs | Measures |
|-----------|----------|--------|---------|
| **Groundedness** | RAG | answer, source docs | Grounded in sources? Score 1–5 (model-based) |
| **Groundedness Pro** | RAG | answer, source docs | Binary pass/fail; no model deployment needed |
| **Response Completeness** | RAG | question, answer, ground truth | Covered required points? |
| **Task Adherence** | Agent | agent trace, task definition | Followed task per system instructions? |
| **Tool Call Accuracy** | Agent | tool calls, expected calls | Right tool with right args? |
| **Task Completion** | Agent | agent trace, task | Completed end-to-end? |
| **Intent Resolution** | Agent | conversation, user intent | Correctly identified and addressed intent? |

### All 7 evaluator categories

```
1. General purpose      Coherence, Fluency
2. Textual similarity   F1, BLEU, GLEU, ROUGE, METEOR (translation / overlap)
3. RAG                  Groundedness, Groundedness Pro, Relevance, Retrieval, Response Completeness
4. Risk & safety        Hate/Unfairness, Sexual, Violence, Self-Harm, Protected Materials,
                        Indirect Attack (XPIA), Code Vulnerability, Prohibited Actions,
                        Sensitive Data Leakage, Ungrounded Attributes
5. Agent                Task Adherence, Task Completion, Customer Satisfaction, Intent Resolution,
                        Task Navigation Efficiency, Tool Call Accuracy, Tool Selection,
                        Tool Input Accuracy, Tool Output Utilization, Tool Call Success, Quality Grader
6. Rubric               Custom weighted criteria, LLM-as-judge, normalized 0–1 score
7. Azure OpenAI Graders Model Labeler, String Checker, Text Similarity, Model Scorer
```

Evaluation levels: `turn` (single response, default) or `conversation` (full multi-turn). Cannot mix levels in one run.

---

# Responsible AI

## The defense layers (inside-out)

```
Request arrives
      │
  ┌───▼────────────────────────────────────┐
  │  Layer 1: Prompt Shields               │
  │    User prompt attack → block          │
  │    Document indirect injection → block │
  └───────────────────────┬────────────────┘
                          │
  ┌───────────────────────▼────────────────┐
  │  Layer 2: Content Safety Filters       │
  │    Hate / Sexual / Violence / Self-harm│
  │    Input + Output                      │
  └───────────────────────┬────────────────┘
                          │
  ┌───────────────────────▼────────────────┐
  │  Layer 3: Model                        │
  │    System prompt guardrails            │
  └───────────────────────┬────────────────┘
                          │
  ┌───────────────────────▼────────────────┐
  │  Layer 4: Evaluators + Tracing         │
  │    Offline analysis, approval workflow │
  └────────────────────────────────────────┘
```

## Content Safety vs Prompt Shields

| | Content Safety | Prompt Shields |
|--|---------------|----------------|
| **Purpose** | Moderate harmful content (hate/violence/sexual/self-harm) | Detect prompt injection attacks |
| **Attack type** | User-generated harmful content | Attacker hijacking model instructions |
| **Sub-types** | Text moderation, image moderation | User prompt attack, document/indirect attack |
| **Severity scale** | 0–7 per category | Detected / Not detected |
| **Lesson file** | `01/08_content_safety_filters.py` | `01/09_prompt_shields_user.py`, `01/10_prompt_shields_docs.py` |

## Indirect prompt injection (spotlighting)

```
Attacker embeds instructions in a PDF/image/email
        ↓
OCR extracts text (including malicious instructions)
        ↓
Text fed to model as "document data"
        ↓
WITHOUT Prompt Shields: model follows attacker's instructions
WITH Prompt Shields (docs): attack detected, flagged or blocked
```

---

# Guardrails (source: `foundry/guardrails/guardrails-overview.md`)

A **guardrail** = named collection of controls applied to one or many models and/or agents in a project.

## 4 intervention points

| Point | Applies to | Notes |
|-------|-----------|-------|
| **User input** | Models + Agents | Prompt sent to model/agent |
| **Tool call** (preview) | Agents only | Action + data agent proposes to send to tool |
| **Tool response** (preview) | Agents only | Content returned from tool to agent |
| **Output** | Models + Agents | Final completion returned to user |

## Risk categories (12 total)

```
Content risks (severity Off/Low/Medium/High):
  Hate | Sexual | Self-harm | Violence

Injection / attack:
  User prompt attacks | Indirect attacks | Spotlighting (preview, models only)

Compliance:
  Protected material (code) | Protected material (text)
  Groundedness (preview, models only)
  PII (preview)
  Task Adherence (preview)
```

## Severity levels — NOT the same as Content Safety 0–7

| Level | Behavior |
|-------|---------|
| **Off** | Disabled (approved customers only) |
| **Low** | Flag low severity and above |
| **Medium** | Flag medium severity and above |
| **High** | Flag only most severe |

## Guardrails vs Content Safety (exam trap)

| | Guardrails | Content Safety (direct API) |
|--|-----------|---------------------------|
| Scope | Applied at model/agent deployment level | Called directly in app code |
| Intervention points | 4 (input, tool call, tool response, output) | Input + output only |
| Severity scale | Off / Low / Medium / High | 0–7 per category |
| Agent-specific controls | Yes (tool call/response, network egress) | No |
| Network egress | Yes (hosted agents, preview) | No |

Memory: **Guardrails = deployment-level policy; Content Safety = API-level call.**

---

# CI/CD for Foundry Projects

```
Code change → GitHub Actions / Azure DevOps
        ↓
Run evaluators on golden test set
        ↓
Gate: groundedness score ≥ threshold?
        ↓ yes
Deploy new agent version (workflow YAML + portal sync)
        ↓
Approval workflow (human gate) for high-risk changes
```

Workflow YAML lives in `02-generative-ai-and-agents/workflows/wf_triage.yml`. Portal designer and YAML stay in sync — edit either.

---

# Common Exam Traps

| Trap | Truth |
|------|-------|
| "Global Standard guarantees data stays in my region" | ❌ — Data Zone Standard stays in EU/US/APAC zone; Regional Standard stays in one region |
| "PTU means I pre-buy tokens" | ❌ — PTU reserves throughput capacity; tokens still billed per use |
| "Content Safety catches prompt injection" | ❌ — Prompt Shields does injection defense; Content Safety does harmful content moderation |
| "DefaultAzureCredential always uses managed identity" | ❌ — It tries a chain; in local dev it uses `az login` (Azure CLI) |
| "Response Completeness evaluator checks groundedness" | ❌ — Completeness = did it cover required points; Groundedness = did it stay within sources |
| "Foundry User = Azure AI Developer role" | ❌ — Foundry now uses its own 5-role hierarchy; Azure AI Developer is old terminology |
| "Guardrails severity is 0–7 like Content Safety" | ❌ — Guardrails severity = Off/Low/Medium/High; Content Safety uses 0–7 |
| "Data Zone = single region" | ❌ — Data Zone = EU or US or APAC zone (multiple regions within the zone) |
| "Managed Compute deployment bills per token" | ❌ — Managed Compute bills hourly per GPU SKU, not per token |

---

# 30-Second Domain 1 Trick

```
Question about CHOOSING a model?     → LLM/SLM/multimodal/Foundry Tools table
Question about DEPLOYING a model?    → 10-type table: Global/DataZone/Regional × pay-per-token/PTU/Batch
Question about OSS models?           → Managed Compute (hourly GPU, not pay-per-token)
Question about CREDENTIALS?          → DefaultAzureCredential + Managed Identity
Question about RATE LIMITS?          → TPM/RPM/PTU + tenacity backoff
Question about MONITORING?           → OpenTelemetry spans + 7-category evaluators
Question about SAFETY filters?       → Content Safety API (0-7) vs Guardrails (Off/Low/Medium/High)
Question about INJECTION defense?    → Prompt Shields (user prompt) / Prompt Shields (docs/indirect)
Question about RBAC?                 → 5 Foundry roles: Consumer < User < Project Manager < Account Owner < Owner
```
