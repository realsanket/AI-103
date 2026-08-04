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

## The four types

| Type | Billing | Data residency | Best for |
|------|---------|---------------|---------|
| **Global Standard** | Pay-per-token | No guarantee (Microsoft-managed) | Default; first access to new models |
| **Regional Standard** | Pay-per-token | Strict (stays in region) | Compliance, data sovereignty |
| **PTU** (Provisioned Throughput) | Reserved capacity (hourly) | Regional | Predictable throughput, no 429s |
| **Serverless (MaaS)** | Pay-per-token | Varies | Non-OpenAI models (Llama, Mistral, Phi) |

## Decision tree

```
Need data to stay in one region?     → Regional Standard or PTU
Getting too many 429 errors?         → PTU (reserved throughput)
Want the newest model first?         → Global Standard
Using Llama / Mistral / Phi?         → Serverless (MaaS)
Default / dev / testing?             → Global Standard
```

Memory: **Global = first + cheap; Regional = compliant; PTU = guaranteed; Serverless = non-OpenAI.**

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

## Key RBAC roles for AI-103

| Role | What it allows |
|------|---------------|
| **Azure AI Developer** | Create and manage AI resources, agents, deployments |
| **Cognitive Services OpenAI User** | Call Responses API / Chat Completions |
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

## Evaluators quick reference

| Evaluator | Inputs | Measures |
|-----------|--------|---------|
| **Response Completeness** | question, answer, checklist | Did answer address all required points? |
| **Groundedness** | answer, source documents | Did answer stick to provided sources? |
| **Task Adherence** | agent trace, goal | Did agent follow its defined task? |
| **Tool Call Accuracy** | tool calls made, expected tools | Did agent call the right tools correctly? |

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
| "Global Standard guarantees data stays in my region" | ❌ — Regional Standard guarantees that |
| "PTU means I pre-buy tokens" | ❌ — PTU reserves throughput capacity; tokens still billed per use |
| "Content Safety catches prompt injection" | ❌ — Prompt Shields does injection defense; Content Safety does harmful content moderation |
| "DefaultAzureCredential always uses managed identity" | ❌ — It tries a chain; in local dev it uses `az login` (Azure CLI) |
| "Response Completeness evaluator checks groundedness" | ❌ — Completeness = did it cover required points; Groundedness = did it stay within sources |

---

# 30-Second Domain 1 Trick

```
Question about CHOOSING a model?     → LLM/SLM/multimodal/Foundry Tools table
Question about DEPLOYING a model?    → Global/Regional/PTU/Serverless table
Question about CREDENTIALS?          → DefaultAzureCredential + Managed Identity
Question about RATE LIMITS?          → TPM/RPM/PTU + tenacity backoff
Question about MONITORING?           → OpenTelemetry spans + evaluators
Question about SAFETY?               → Content Safety (moderation) vs Prompt Shields (injection)
Question about GOVERNANCE?           → RBAC roles + approval workflows + tracing
```
