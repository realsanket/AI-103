# Domain 6: Model customization and delivery

> Runnable labs for Foundry model customization (SFT, DPO, RFT, distillation) plus delivery-side choices (Standard, Priority, Global Batch, PTU, Instant Access, Model Router) and cost review. Run commands from repository root: `uv run python 06-model-customization-other/<lesson>.py`.
>
> Every cloud operation is opt-in via `--apply`. Default commands validate local input or print a preflight. A successful request proves only that request under its current identity, region, quota, and preview status. It does not prove model quality, safety, data governance, capacity, availability, or production readiness.

## What this domain teaches

A customization + delivery decision is a chain of independent gates, not one API call:

```text
Baseline: prompt + RAG + structured output enough?
        ↓ no
Pick method: SFT (skill/format) · DPO (preference) · RFT (verifiable reward) · Distillation (teacher→student)
        ↓
Prepare + validate reviewed data (train / validation / held-out split)
        ↓
Submit ONE training job (persistent, billable)
        ↓
Monitor job + pick checkpoint against held-out set (not "newest")
        ↓
Deploy candidate to a disposable evaluation deployment
        ↓
Evaluate vs baseline; audit safety/subgroup/latency/cost — not just aggregate
        ↓
Choose delivery: Standard · Priority · Global Batch · PTU · Instant · Router
        ↓
Cost review + tag + monitor + retire idle deployments
```

Lessons follow that chain in six stages. They do not build a production customization pipeline or prove every training-type/region/model combination.

## Foundry customization + delivery mental model

### Customization methods

| Method | Data contract | Best for | Do not use for |
|---|---|---|---|
| **SFT** (Supervised Fine-Tuning) | JSONL rows of `messages` ending in `assistant` | Reproducing a format, extraction, or reliable answer | Ambiguous preference where no output is objectively best |
| **DPO** (Direct Preference Optimization) | `input` + `preferred_output` + `non_preferred_output` | Tone, style, safety preference over paired alternatives | Teaching a new skill (needs SFT) |
| **RFT** (Reinforcement Fine-Tuning) | Prompts ending in `user` + validation set + Python `grade()` grader | Reasoning tasks with a verifiable numeric reward | Tasks whose quality cannot be reliably graded |
| **Distillation** | Reviewed seed prompts → teacher-generated SFT candidates | Bootstrapping SFT data from a stronger teacher | Automatic trust of synthetic output (must review) |

### Delivery choices

| Choice | Residency | Billing | Best for | Watch out for |
|---|---|---|---|---|
| **Standard** | Regional / Data Zone / Global | Pay-per-token | Variable traffic, dev/test | Shared capacity; 429 under load |
| **Priority processing** | Global Standard or US Data Zone Standard | Priority per-token premium | Latency-sensitive online w/o commitment | Can fall back to Standard; not a hard SLA |
| **Global Batch** | Global / Data Zone | ~50% discount, async | Deferred bulk inference | No fine-tuned models; billable past 24h |
| **PTU** (Provisioned Throughput) | Regional / Data Zone / Global | Reserved hourly capacity | High predictable volume, latency-sensitive | Bills while idle; quota ≠ capacity |
| **Instant Access** (preview) | West US 3 project currently | Pay-per-token, global quota | Preview prototyping, no deployment | Preview scope; version pin for stability |
| **Model Router** | Follows deployment | Pay per selected model | Mixed prompt complexity | Router deploy + policy configuration required |

### Two Azure planes

```text
Control plane (CognitiveServicesManagementClient)
  Create/replace deployments, read quota/usages, get resource metadata
  Roles: Cognitive Services Contributor / Owner + subscription Reader for usages

Data plane (openai_client with AZURE_OPENAI_ENDPOINT)
  files.create · fine_tuning.jobs.create · batches.create · responses.create
  Role: Cognitive Services OpenAI User (data actions on the resource)
```

Lessons 05, 06, 08, 09, 11, 12 use the data plane. Lessons 07 and 10 use the control plane. A data-plane role does not deploy models; a control-plane role does not send inference.

## Glossary

| Term | Definition |
|---|---|
| **Base model** | Foundation model available in the catalog (e.g. `gpt-4o-mini-2024-07-18`) used as the starting point for fine-tuning. |
| **Custom model** | Fine-tuned artifact produced by a training job: `ft:<base>:<org>::<id>`. |
| **Checkpoint** | Intermediate custom model snapshot during training: `ftchkpt-...`. Can be deployed instead of final. |
| **SFT** | Supervised Fine-Tuning: model learns to reproduce reviewed input→output pairs. |
| **DPO** | Direct Preference Optimization: model shifts toward preferred over non-preferred paired responses. |
| **RFT** | Reinforcement Fine-Tuning: model rewarded for correct answers by a Python grader function. |
| **Grader** | Python function `grade(sample, item) → float` executed by the RFT service in a sandbox. |
| **Distillation** | Using a stronger teacher model to generate candidate SFT training data for a smaller student. |
| **Training type** | Standard (regional), GlobalStandard (global capacity), or Developer (idle capacity, no SLA). |
| **PTU** | Provisioned Throughput Unit: reserved hourly capacity, not a prepaid token bucket. |
| **Global Batch** | Asynchronous bulk inference at ~50% discount, targets 24h completion, separate quota. |
| **Priority processing** | Premium per-token tier with lower latency on supported Standard deployments. |
| **Instant Access** | Preview: call a supported model name without creating a deployment; global quota. |
| **Model Router** | Deployed alias that picks among allowed models per request (Balanced/Quality/Cost mode). |
| **Reward hacking** | Rising train reward with flat/falling validation reward — model gamed the grader. |
| **Held-out set** | Evaluation data never seen during training or checkpoint selection; used for release decisions. |

## Setup

### Environment variables

From repository root:

```bash
uv sync
cp .env.example .env
az login
uv run python 06-model-customization-other/00_customization_preflight.py
```

Use a nonproduction Foundry resource for every `--apply`. Never commit `.env`, keys, dataset files with personal data, or fine-tuned model IDs pointing to customer content.

```dotenv
# Foundry resource endpoints
AZURE_OPENAI_ENDPOINT=https://<resource>.openai.azure.com
FOUNDRY_ENDPOINT=https://<resource>.services.ai.azure.com

# Management plane context
AZURE_SUBSCRIPTION_ID=<subscription-id>
AZURE_RESOURCE_GROUP=<resource-group>

# Base deployment for lessons 04, 11, 12 (existing pre-fine-tuning deployment)
DEFAULT_MODEL=<deployment-name>
```

`DefaultAzureCredential` picks up `az login` locally or managed/workload identity in Azure. Data-plane calls request scope `https://ai.azure.com/.default`; the custom subdomain on the Foundry resource is required for token auth.

### Safe run order

1. Run **00** first: local env-var check, no cloud call.
2. Prepare data. Validate with **01** (SFT), **02** (DPO), or **03** (RFT + grader). All local.
3. If bootstrapping training data: **04 --apply** calls a teacher once per prompt and writes candidates. Review, filter, split before uploading.
4. **05 --apply** uploads reviewed data and submits ONE training job. Persistent + billable.
5. **06 --apply** reads job state + 10 recent events. Re-run to poll.
6. **08 --apply** with `--dataset held-out.jsonl --baseline <base> --candidate <ftmodel>` (from step 5) — exact-match score only; deploy first with a temp deployment.
7. **07 --apply** creates a deployment for a chosen `ftchkpt-...` or fine-tuned model. Use a disposable eval deployment name.
8. Choose delivery: **10** for quota/PTU planning; **11 --apply** for priority test; **12 --apply** for router or instant.
9. **09 --apply** submits a Global Batch job (async, separate quota, no fine-tuned models).
10. **13** for local PTU cost arithmetic; verify hourly rate in current pricing page.

### Costs and side effects

| Lesson(s) | Side effect or cost |
|---|---|
| 00, 01, 02, 03, 13 | Local only; no cloud call ever. |
| 04 | Local by default. `--apply` calls teacher once per row (inference cost) + writes new JSONL file. |
| 05 | Local by default. `--apply` uploads files + creates one training job. Training tokens billable per method + tier. |
| 06 | Local by default. `--apply` reads one job + 10 events (read-only). |
| 07 | Local by default. `--apply` creates/replaces one deployment — hosting charges start immediately. |
| 08 | Local by default. `--apply` sends 1–2 Responses calls per row (candidate + optional baseline). |
| 09 | Local by default. `--apply` uploads file + creates 24h Global Batch job. Billable per token; completed work stays billable after cancel. |
| 10 | Local by default. `--apply` reads resource, deployments, quota (control-plane read). |
| 11 | Local by default. `--apply` sends one priority-tier Responses request. |
| 12 | Local by default. `--apply` sends one router or instant-model Responses request. |

Fine-tuned model deployments bill by hour while present. Global Batch enqueued-token quota is separate from Standard. PTU quota is a policy limit; capacity is separate — check both before committing.

## Decision tables

### When to fine-tune (vs prompt/RAG)

```text
Task well-defined + baseline measured?
  No  → Fix task definition + measure baseline first.
  Yes → Baseline passes bar?
          Yes → Ship prompt/RAG.
          No  → Baseline consistently misses in a specific way?
                  No  → Try structured output + few-shot + RAG improvements.
                  Yes → Fine-tune (pick method below).
```

### Pick a customization method

| Failure mode of baseline | Method | Data you need |
|---|---|---|
| Doesn't follow exact format | **SFT** | 100+ reviewed input/output pairs |
| Wrong tone/style/safety choice between two acceptable answers | **DPO** | Preference pairs annotated by reviewer |
| Wrong reasoning steps in tasks with verifiable answer | **RFT** | Prompts + validation + calibrated grader |
| Not enough SFT data for target task | **Distillation** first, then SFT | Seed prompts + a stronger teacher deployment |

### Pick a delivery tier

```text
Async bulk (>1M requests, latency OK ~24h)?
  Yes → Global Batch (not fine-tuned models).
  No  → Sustained high volume + latency SLO?
          Yes → PTU (verify capacity + budget for idle).
          No  → Need lower latency spikes without commitment?
                  Yes → Priority processing (Global/DZ Standard only).
                  No  → Mixed prompt complexity?
                          Yes → Model Router deployment.
                          No  → Standard.

Preview prototyping without deployment overhead?
  Yes → Instant Access (West US 3, supported model list, pin version).
```

## Lesson map

| # | Lesson | Runnable objective | Status / limitation |
|---:|---|---|---|
| 00 | [Customization preflight](00_customization_preflight.py) | Verify env vars for domain 6. | Local; no cloud call. |
| 01 | [SFT dataset](01_sft_dataset.py) | Validate SFT JSONL structure. | Local; no upload. |
| 02 | [DPO dataset](02_dpo_dataset.py) | Validate DPO preference-pair JSONL. | Local; no upload. |
| 03 | [RFT dataset + grader](03_rft_dataset_grader.py) | Validate RFT JSONL + grader syntax. | Local; grader not executed. |
| 04 | [Distillation dataset](04_distillation_dataset.py) | Generate teacher candidates from seeds. | `--apply` calls teacher per row + writes JSONL. |
| 05 | [Submit training](05_submit_training.py) | Upload + submit SFT/DPO/RFT job. | `--apply` creates one persistent billable job. |
| 06 | [Training monitor](06_training_monitor.py) | Read one job + 10 events. | `--apply` read-only; not continuous. |
| 07 | [Deploy checkpoint](07_deploy_checkpoint.py) | Create deployment for fine-tuned model/checkpoint. | `--apply` replaces existing name; hosting bill starts. |
| 08 | [Evaluate candidate](08_evaluate_candidate.py) | Exact-match candidate vs baseline. | `--apply` 1-2 inference calls per row; no eval object. |
| 09 | [Global Batch](09_batch_inference.py) | Submit 24h Global Batch Responses job. | `--apply` async job; no fine-tuned models. |
| 10 | [Quota + PTU preflight](10_quota_ptu_preflight.py) | Read region, deployments, quota. | `--apply` control-plane read only. |
| 11 | [Priority processing](11_priority_processing.py) | One priority-tier Responses request. | `--apply` billable; can fall back to Standard. |
| 12 | [Router + Instant](12_router_instant.py) | Router deployment or Instant model call. | `--apply` one billable request per invocation. |
| 13 | [Cost review](13_cost_review.py) | Local PTU × rate × hours arithmetic. | Local; not a bill or forecast. |
| 14 | [Foundry Models catalog list](14_foundry_models_list.py) | List model SKUs available in subscription. | `--apply` control-plane read; subscription Reader needed. |
| 15 | [Claude model call](15_claude_model_call.py) | Call a Claude partner model via Responses API. | `--apply --model` required; Azure Marketplace billing. |
| 16 | [Model router](16_model_router.py) | Route simple vs complex prompt; observe which backing model selected. | `--apply --model <router-deployment>` required |
| 17 | [DeepSeek R1](17_deepseek_r1.py) | Call DeepSeek R1; parse `<think>` reasoning chain. | `--apply --model <deepseek-deployment>` required |
| 18 | [HuggingFace models preflight](18_huggingface_models_preflight.py) | List HuggingFace-origin models in Foundry catalog. | `--apply` subscription-level read |
| 19 | [Fireworks models preflight](19_fireworks_models_preflight.py) | Check Fireworks AI model availability in catalog. | `--apply` subscription-level read |

---

## Stage 6 — Foundry Models catalog + partner models (lessons 14–15)

Lessons 14 and 15 cover the Foundry model catalog beyond Azure OpenAI: enumerating all model SKUs visible in the subscription and calling a Claude partner model through the same Responses API client.

### 14 — Foundry Models catalog list

**Question answered:** Which model families + SKUs are available in my subscription region?

**Background.** The Foundry model catalog surfaces Azure OpenAI models (sold directly), partner models (Claude, Mistral, etc.), and open-source. Underlying data is `resource_skus` from `CognitiveServicesManagementClient`. Use before deployment (lesson 07, 05) to confirm model IDs, supported SKU tiers, and regions.

```bash
uv run python 06-model-customization-other/14_foundry_models_list.py
uv run python 06-model-customization-other/14_foundry_models_list.py --apply --kind openai
uv run python 06-model-customization-other/14_foundry_models_list.py --apply --kind claude
```

**Code path.** `resource_skus.list()` → filter `resource_type == "accounts"` → deduplicate by (name, kind) → print table filtered by `--kind`.

**What to watch.** Table of model families, kinds, tiers, and locations. Missing Claude = Marketplace subscription not enabled for subscription/region.

**References:** [Models sold directly by Azure](https://learn.microsoft.com/azure/foundry/foundry-models/concepts/models-sold-directly-by-azure) · [Models from partners](https://learn.microsoft.com/azure/foundry/foundry-models/concepts/models-from-partners) · [Deploy Foundry Models](https://learn.microsoft.com/azure/foundry/foundry-models/how-to/deploy-foundry-models)

### 15 — Claude partner model call

**Question answered:** Does the Responses API client work identically for Claude partner model deployments?

**Background.** Claude models (Anthropic) in Foundry use the same `responses.create()` API as Azure OpenAI — only the deployment name differs. Billing is Azure Marketplace terms. This lesson proves API shape parity and surfaces `response.model` to identify which Claude variant served the request.

```bash
uv run python 06-model-customization-other/15_claude_model_call.py
uv run python 06-model-customization-other/15_claude_model_call.py --apply --model <claude-deployment>
```

**Code path.** `openai_client().responses.create(model=claude_deployment, input=prompt)` → print `response.model` + `output_text`.

**What to watch.** `model: claude-opus-4-*` or similar. Same response shape as Azure OpenAI. Billing differs — check Marketplace meters, not Azure OpenAI usage.

**References:** [Claude models](https://learn.microsoft.com/azure/foundry/foundry-models/concepts/claude-models) · [Claude models billing](https://learn.microsoft.com/azure/foundry/foundry-models/concepts/claude-models-billing) · [Claude models hosting comparison](https://learn.microsoft.com/azure/foundry/foundry-models/concepts/claude-models-hosting-comparison)

---

## Stage 7 — Model router + partner models catalog (lessons 16–19)

Stage 7 extends the Foundry Models catalog beyond Azure OpenAI: model routing across a pool, reasoning chains from DeepSeek R1, and discovering HuggingFace and Fireworks AI models in the same catalog surface.

### 16 — Model router

**Question answered:** Which backing model did the router select for a simple vs complex prompt?

**Background.** The Model Router is a Foundry deployment type that automatically selects from a configured pool of backing models. Simple prompts route to fast/cheap models; complex ones to more capable models. The selection is visible in `response.model`. Router configuration (pool, policy) is managed in the Foundry portal or via Bicep — this lesson only observes the routing decision.

```bash
uv run python 06-model-customization-other/16_model_router.py
uv run python 06-model-customization-other/16_model_router.py --apply --model <router-deployment>
```

**Code path.** `openai_client().responses.create(model=ROUTER_MODEL, input=prompt)` × 2 → print `response.model` per request.

**What to watch.** `response.model` differs between simple and complex prompts when the router has multiple backing models. Same model for both = single backing model or router not yet enabled.

**References:** [Model router concepts](https://learn.microsoft.com/azure/foundry/openai/concepts/model-router) · [Model router how-to](https://learn.microsoft.com/azure/foundry/openai/how-to/model-router) · [Responses with model routing](https://learn.microsoft.com/azure/foundry/openai/how-to/responses-model-routing) · [Model choice guide](https://learn.microsoft.com/azure/foundry/foundry-models/how-to/model-choice-guide)

---

### 17 — DeepSeek R1 reasoning chain

**Question answered:** How does DeepSeek R1's `<think>` reasoning chain appear in the Responses API output?

**Background.** DeepSeek R1 is a partner reasoning model in the Foundry catalog. It generates an internal chain of thought surfaced in `<think>...</think>` tags in `output_text`. It uses the identical Responses API client as Azure OpenAI — only the deployment name differs. Billing flows through Azure Marketplace.

```bash
uv run python 06-model-customization-other/17_deepseek_r1.py
uv run python 06-model-customization-other/17_deepseek_r1.py --apply --model <deepseek-deployment>
```

**Code path.** `openai_client().responses.create(model=DEEPSEEK_MODEL, input=prompt)` → `re.search(r"<think>(.*?)</think>", output_text)` → print thinking block + answer.

**What to watch.** Non-empty `<think>` block = reasoning chain exposed. Text after `</think>` = final answer. Empty = deployment does not expose reasoning tags.

**References:** [DeepSeek R1 tutorial](https://learn.microsoft.com/azure/foundry/foundry-models/tutorials/get-started-deepseek-r1) · [Foundry Models catalog](https://learn.microsoft.com/azure/foundry/foundry-models/concepts/models) · [Generate responses](https://learn.microsoft.com/azure/foundry/foundry-models/how-to/generate-responses)

---

### 18 — HuggingFace models preflight

**Question answered:** Which HuggingFace-origin open-source models are available in the Foundry catalog for my subscription?

**Background.** Foundry's Models catalog includes Phi, Mistral, Llama, Qwen, Gemma, and other HuggingFace-origin models as serverless or managed compute endpoints. They appear in `resource_skus.list()` alongside Azure OpenAI and partner models. Once deployed, they use the same Responses API — only the deployment name differs.

```bash
uv run python 06-model-customization-other/18_huggingface_models_preflight.py
uv run python 06-model-customization-other/18_huggingface_models_preflight.py --apply
```

**Code path.** `CognitiveServicesManagementClient.resource_skus.list()` → filter `resource_type=="accounts"` + name contains HF family keyword → print name, kind, locations.

**What to watch.** Phi, Mistral, Llama, Qwen entries = HuggingFace-origin available. Zero results = catalog not loaded for subscription region.

**References:** [Foundry Models catalog](https://learn.microsoft.com/azure/foundry/foundry-models/concepts/models) · [HuggingFace models](https://learn.microsoft.com/azure/foundry/foundry-models/how-to/hugging-face-models) · [Model choice guide](https://learn.microsoft.com/azure/foundry/foundry-models/how-to/model-choice-guide)

---

### 19 — Fireworks AI models preflight

**Question answered:** Are Fireworks AI partner models available in my Foundry catalog?

**Background.** Fireworks.ai provides optimized inference for open-source models (Llama, Mixtral variants) via Azure Marketplace partnership. They appear in the Foundry Models catalog as marketplace deployments; billing flows through Azure Marketplace separately from Azure OpenAI quota. Enable them in the Foundry portal before deploying.

```bash
uv run python 06-model-customization-other/19_fireworks_models_preflight.py
uv run python 06-model-customization-other/19_fireworks_models_preflight.py --apply
```

**Code path.** `CognitiveServicesManagementClient.resource_skus.list()` → filter name/kind containing "fireworks" → print model name, kind, locations.

**What to watch.** Zero results = Fireworks not enabled. Enable via Foundry portal → Model Catalog → Fireworks.ai → Enable partner.

**References:** [Enable Fireworks models](https://learn.microsoft.com/azure/foundry/how-to/fireworks/enable-fireworks-models) · [Import custom models (Fireworks)](https://learn.microsoft.com/azure/foundry/how-to/fireworks/import-custom-models) · [Foundry Models catalog](https://learn.microsoft.com/azure/foundry/foundry-models/concepts/models)

---

## Stage 1 — Preflight and data validation (lessons 00–03)

Start here. Every training job downstream depends on reviewed data. These four lessons make zero cloud calls and cannot cost money. They exist so a bad row does not survive until upload.

### 00 — Customization preflight

**Question answered:** Are the env vars for this domain configured?

**Background.** Every lesson from 04 onward reads at least one of `AZURE_OPENAI_ENDPOINT`, `FOUNDRY_ENDPOINT`, `AZURE_SUBSCRIPTION_ID`, `AZURE_RESOURCE_GROUP`, or `DEFAULT_MODEL`. This lesson checks all five in one place. It proves configuration is present — not that permissions, quota, or capacity exist.

```bash
uv run python 06-model-customization-other/00_customization_preflight.py
```

**Code path.**
1. `settings()` reads `.env` via the shared config helper.
2. Print each of the five keys as `configured` or `missing`.
3. Print reminder about nonproduction resource + model/method/region/quota + data governance review before any `--apply`.

**What to watch.** All five should print `configured`. Any `missing` must be filled in `.env` before running lessons 05, 07, 09, 10, 11, or 12 with `--apply`.

**Study points.**
- The check is naive: it does NOT verify the endpoint responds, that the identity has any role, or that `DEFAULT_MODEL` maps to a real deployment.
- `az login` is a separate step — this lesson doesn't test the token.

**References:** [Fine-tuning considerations](https://learn.microsoft.com/azure/foundry/openai/concepts/fine-tuning-considerations) · [Authentication and authorization](https://learn.microsoft.com/azure/foundry/concepts/authentication-authorization-foundry)

### 01 — Validate SFT JSONL

**Question answered:** Does my SFT dataset conform to the API contract before I upload it?

**Background.** SFT teaches a model to reproduce reviewed input→output pairs. Each JSONL row is `{"messages": [...]}` where the array is nonempty and ends with an `assistant` message. Bad rows only surface after upload — this lab catches them locally.

```bash
uv run python 06-model-customization-other/01_sft_dataset.py --dataset train.jsonl
```

**Code path.**
1. `jsonl_rows()` reads nonblank lines, parses each as an object.
2. Per row: `messages()` asserts nonempty list with string roles.
3. Assert last message role == `"assistant"`.
4. Print validated count.

**What to watch.** `Validated N SFT record(s)`. A `ValueError` names the failing row (e.g. `row 42 must end with an assistant message for SFT.`).

**Data hygiene.**
- Split into train/validation/held-out BEFORE running this. Near duplicates across splits leak answers.
- Preserve edge and failure cases; prefer accurate, representative examples over bulk.
- Remove secrets, personal data, protected content, and unlicensed material before validation.

**References:** [Fine-tuning](https://learn.microsoft.com/azure/foundry/openai/how-to/fine-tuning) · [Fine-tuning considerations](https://learn.microsoft.com/azure/foundry/openai/concepts/fine-tuning-considerations)

### 02 — Validate DPO JSONL

**Question answered:** Does my preference-pair dataset match the DPO contract?

**Background.** DPO shifts a model toward a preferred response over a rejected alternative. Row shape: `{"input": {"messages": [...]}, "preferred_output": [...], "non_preferred_output": [...]}` where each output list contains at least one assistant message. DPO teaches subjective preference (tone, style, safety), NOT new capability.

```bash
uv run python 06-model-customization-other/02_dpo_dataset.py --dataset preferences.jsonl
```

**Code path.**
1. Per row: assert `input` is object with valid `messages`.
2. Assert `preferred_output` and `non_preferred_output` are valid message arrays.
3. Assert at least one assistant message in each output.

**What to watch.** `Validated N DPO preference pair(s)`. Errors name row + field.

**Preference design rules.**
- Same user intent in both outputs, one intentional difference.
- Do not encode hidden discrimination or accidental style bias as preference.
- Documented annotation rule per reviewer.
- Start with default `beta=0.1` and `l2_multiplier=0.1` in lesson 05 unless a controlled experiment justifies a change.

**References:** [DPO](https://learn.microsoft.com/azure/foundry/openai/how-to/fine-tuning-direct-preference-optimization) · [Fine-tuning considerations](https://learn.microsoft.com/azure/foundry/openai/concepts/fine-tuning-considerations)

### 03 — Validate RFT dataset + grader

**Question answered:** Does my RFT data end in a user message, and does my grader compile?

**Background.** RFT rewards correct answers on tasks with a verifiable outcome. JSONL rows end in a `user` message (the model generates the answer during training). Extra fields feed the grader. The Python grader defines `grade(sample, item) → float`. Foundry runs it sandboxed; this lab only compiles the source locally.

```bash
uv run python 06-model-customization-other/03_rft_dataset_grader.py \
  --dataset rft-train.jsonl --grader grader.py
```

**Code path.**
1. Per row: assert last message role == `"user"`.
2. `grader.read_text()` → assert `def grade(sample, item):` substring present.
3. `compile(source, path, "exec")` — syntax check only, does not execute.

**What to watch.** `Validated N RFT prompt(s) and compiled <grader>`.

**Reward-hacking discipline.**
- Rising train reward + flat validation reward = reward hacking, not progress.
- Keep grader deterministic, bounded, adversarially tested.
- No network calls in grader (sandbox blocks it).
- Current RFT $5,000 safety stop is a stop, not a budget.
- Calibrate grader on baseline responses BEFORE training.

**References:** [Reinforcement fine-tuning](https://learn.microsoft.com/azure/foundry/openai/how-to/reinforcement-fine-tuning) · [Azure OpenAI graders](https://learn.microsoft.com/azure/foundry/concepts/evaluation-evaluators/azure-openai-graders)

---

## Stage 2 — Bootstrap training data (lesson 04)

When you have seed prompts but not enough labelled outputs, use a stronger teacher to generate candidate outputs. This is the one lesson in stages 1–3 that can cost money by default.

### 04 — Distillation dataset from teacher model

**Question answered:** How do I generate SFT candidates from a stronger teacher?

**Background.** Distillation uses a teacher model to create input→output pairs a smaller student can be fine-tuned on. Default validates source rows locally. `--apply` sends each row's messages to the teacher and writes an SFT-shaped JSONL. Output path must not exist — this prevents overwriting reviewed data.

```bash
# preflight: local validation only
uv run python 06-model-customization-other/04_distillation_dataset.py \
  --source prompts.jsonl --output distilled-candidates.jsonl

# apply: teacher inference per row + write output file
uv run python 06-model-customization-other/04_distillation_dataset.py \
  --source prompts.jsonl --output distilled-candidates.jsonl \
  --teacher <teacher-deployment> --apply
```

**Code path.**
1. `validate_source()` — jsonl_rows + messages check per row.
2. If `--apply`: refuse if output exists; `openai_client().responses.create(model=teacher, input=messages)` per row.
3. Append `{"role": "assistant", "content": response.output_text}` to each row, write as SFT JSONL line.

**What to watch.** Preflight: `Validated N distillation prompt(s)`. With `--apply`: `Created <output> from N teacher response(s)`.

**Never trust the output as training data.** It is a candidate dataset. Before training:
- Sample and grade a representative fraction.
- Remove duplicates and hallucinated claims.
- Red-team safety behavior.
- Split from the seed prompts used to generate it.
- Retain lineage (seed source, teacher name + version, timestamp, reviewer).

Foundry also has a portal-only synthetic-data preview supporting one PDF/Markdown/text file or one OpenAPI 3.x JSON file under 20 MB, 50–1,000 samples, optional 80/20 split. Check its current region availability before using.

**References:** [Data generation](https://learn.microsoft.com/azure/foundry/fine-tuning/data-generation) · [Fine-tuning](https://learn.microsoft.com/azure/foundry/openai/how-to/fine-tuning)

---

## Stage 3 — Submit, monitor, deploy, evaluate (lessons 05–08)

The training lifecycle in four lessons. Each is opt-in — no default run costs money. Never `--apply` without reviewing datasets, region, quota, capacity, and the disposable deployment name you'll target.

### 05 — Submit one SFT / DPO / RFT job

**Question answered:** How do I upload reviewed data and submit exactly one training job?

**Background.** Single entrypoint for all three methods. Reuses validators from lessons 01/02/03 so bad data is caught before upload. `--apply` uploads each file with purpose `fine-tune` and submits one job.

```bash
# SFT — preflight
uv run python 06-model-customization-other/05_submit_training.py \
  --kind sft --train train.jsonl --validation validation.jsonl \
  --model <supported-base-model>

# SFT — apply, GlobalStandard training type
uv run python 06-model-customization-other/05_submit_training.py \
  --kind sft --train train.jsonl --validation validation.jsonl \
  --model <supported-base-model> --suffix northwind-v1 \
  --training-type GlobalStandard --apply

# DPO — requires preference-pair JSONL
uv run python 06-model-customization-other/05_submit_training.py \
  --kind dpo --train dpo-train.jsonl --validation dpo-validation.jsonl \
  --model <dpo-supported-base> --apply

# RFT — requires validation + grader
uv run python 06-model-customization-other/05_submit_training.py \
  --kind rft --train rft-train.jsonl --validation rft-validation.jsonl \
  --grader grader.py --model <rft-supported-base> --apply
```

**Code path.**
1. Validate all files per method (SFT last=assistant, DPO pair contract, RFT last=user + grader compiles).
2. If `--apply`: `files.create(file=..., purpose="fine-tune")` for train + optional validation.
3. `fine_tuning.jobs.create(model=, training_file=, validation_file=, suffix=, method={...})`.
4. Method payload: `{"type": "supervised"}` for SFT; `{"type": "dpo", "dpo": {"beta", "l2_multiplier"}}` for DPO; `{"type": "reinforcement", "reinforcement": {"grader": {"type": "python", "name": ..., "source": ...}}}` for RFT.
5. `--training-type` sent via `extra_body={"trainingType": value}`.

**Training type trade-offs.**

| Type | Trade-off |
|---|---|
| `Standard` | Regional processing + data-residency guarantees where supported. |
| `GlobalStandard` | Global capacity; lower cost, faster queue; data + weights may leave resource region. |
| `Developer` | Idle-capacity savings for experiments; no SLA/residency; job can preempt/resume. |

**What to watch.** Preflight: `Validated <KIND> input locally.` With `--apply`: `Uploaded training file: file-...` and `Submitted <KIND> job: ftjob-... (validating)`. Record both IDs.

**Study points.**
- SFT can omit `--validation` for the API, but you should always supply one.
- RFT requires both `--validation` and `--grader`.
- Model + method + tier availability changes; verify catalog before submission.

**References:** [Fine-tuning](https://learn.microsoft.com/azure/foundry/openai/how-to/fine-tuning) · [DPO](https://learn.microsoft.com/azure/foundry/openai/how-to/fine-tuning-direct-preference-optimization) · [Reinforcement fine-tuning](https://learn.microsoft.com/azure/foundry/openai/how-to/reinforcement-fine-tuning)

### 06 — Monitor one training job

**Question answered:** What is the state of my running job and its recent events?

**Background.** Read-only diagnostic. `--apply` retrieves one job + 10 most-recent events. Snapshot only — re-run to refresh. Does not select checkpoints, resume, or cancel.

```bash
uv run python 06-model-customization-other/06_training_monitor.py --job-id ftjob-... --apply
```

**Code path.**
1. `fine_tuning.jobs.retrieve(job_id)` → print id, status, `fine_tuned_model`.
2. `fine_tuning.jobs.list_events(fine_tuning_job_id=..., limit=10)` → print `- <created_at>: <message>` per event.

**What to watch.** `Status: succeeded` with `Fine-tuned model: ft:...` — model is ready for lesson 07 deployment. Event stream shows checkpoints (`ftchkpt-...`), validation metrics, warnings.

**Checkpoint selection rule.** Never pick "newest." Pick because a candidate meets predeclared quality, safety, latency, and cost thresholds on the untouched held-out set. Compare all `ftchkpt-...` values against baseline in lesson 08 before deploying.

**References:** [Fine-tuning](https://learn.microsoft.com/azure/foundry/openai/how-to/fine-tuning)

### 07 — Deploy a chosen candidate

**Question answered:** How do I put a fine-tuned model or checkpoint behind an inference endpoint?

**Background.** Control-plane operation via `CognitiveServicesManagementClient`. Default preflight prints intended payload; `--apply` creates or replaces one deployment. Hosting bill starts immediately.

```bash
# preflight
uv run python 06-model-customization-other/07_deploy_checkpoint.py \
  --model-id ftchkpt-... --name northwind-ft-eval --sku Standard --capacity 1

# apply
uv run python 06-model-customization-other/07_deploy_checkpoint.py \
  --model-id ftchkpt-... --name northwind-ft-eval --sku Standard --capacity 1 --apply
```

**Code path.**
1. `settings()` + `foundry_account_name()` derive account name from endpoint.
2. `CognitiveServicesManagementClient(DefaultAzureCredential, sub).deployments.begin_create_or_update(rg, account, name, Deployment(sku=Sku(name, capacity), properties=DeploymentProperties(model=DeploymentModel(format="OpenAI", name=model_id, version="1")))).result()`.
3. Print result name + provisioning state.

**What to watch.** Preflight: `Would create/update deployment <name>`. With `--apply`: `Deployment: <name>` and `State: Succeeded`. Errors: unsupported SKU for model, no capacity in region, missing control-plane role.

**Production discipline.**
- Use a separate evaluation deployment name (`northwind-ft-eval`); do not overwrite production.
- Tag deployment for cost attribution.
- Delete after evaluation decision; fine-tuned deployments bill by hour while present.
- Fine-tuned deployments support Standard, Global Standard preview, and Provisioned Throughput preview only where currently supported for the base model.

**References:** [Fine-tuning deployment](https://learn.microsoft.com/azure/foundry/openai/how-to/fine-tuning-deploy) · [Fine-tuning cost management](https://learn.microsoft.com/azure/foundry/openai/how-to/fine-tuning-cost-management)

### 08 — Evaluate candidate vs baseline

**Question answered:** Does my candidate actually beat the baseline on my held-out set?

**Background.** Small transparent exact-match scorer. Row schema: `{"query": str, "expected": str}`. Default validates rows; `--apply` sends one Responses call per model per row and prints a single score. NOT a Foundry evaluation object — no dataset, run, or portal record is created.

```bash
uv run python 06-model-customization-other/08_evaluate_candidate.py \
  --dataset held-out.jsonl --candidate northwind-ft-eval \
  --baseline <base-deployment> --apply
```

**Code path.**
1. Per row: assert `query` and `expected` are nonempty strings.
2. `score(model, rows)` → per row: `responses.create(model, input=query).output_text.strip().casefold()` vs `expected.strip().casefold()`.
3. Print `<label>: matches/total (pct%)` per model.

**What to watch.** `candidate: 42/50 exact matches (84.0%)`. Compare candidate and baseline lines.

**Exact-match is narrow.** Only meaningful for single-token classification, extraction, or arithmetic. For open-ended quality use:
- Foundry cloud evaluation (see domain 01 lesson 21).
- Reviewed deterministic, similarity, label, score, or safety graders.
- Human audit of representative outputs.
- Subgroup + safety failure + latency + token + cost review.

Never treat one aggregate score as a release decision.

**References:** [Azure OpenAI graders](https://learn.microsoft.com/azure/foundry/concepts/evaluation-evaluators/azure-openai-graders) · [Fine-tuning safety evaluation](https://learn.microsoft.com/azure/foundry/openai/how-to/fine-tuning-safety-evaluation)

---

## Stage 4 — Delivery choices (lessons 09–12)

Once a candidate is deployed, decide how requests reach it. Four delivery patterns each with a different trade-off between cost, latency, capacity guarantee, and preview scope.

### 09 — Global Batch

**Question answered:** How do I submit an async bulk inference job?

**Background.** Global Batch is async, discounted (~50%), targets 24h completion, uses a separate enqueued-token quota. Each JSONL row is a self-contained request. Batch does NOT support fine-tuned models per current docs.

```bash
# preflight
uv run python 06-model-customization-other/09_batch_inference.py --input batch.jsonl

# apply
uv run python 06-model-customization-other/09_batch_inference.py --input batch.jsonl --apply
```

Row shape:

```jsonl
{"custom_id":"case-1","method":"POST","url":"/v1/responses","body":{"model":"<global-batch-deployment>","input":"Classify: paid invoice"}}
```

**Code path.**
1. Per row: `method==POST`, `url==/v1/responses`, unique `custom_id`, `body.model` is string.
2. Assert all rows target the same deployment (batch scope).
3. If `--apply`: `files.create(purpose="batch")` → `batches.create(input_file_id=, endpoint="/v1/responses", completion_window="24h")`.

**What to watch.** Preflight: `Validated N Global Batch request(s)`. With `--apply`: `Batch: batch-... (validating|in_progress)`. Retrieve results later with `batches.retrieve()` + `files.content(output_file_id)` (not in this lab).

**Batch operational rules.**
- Not for fine-tuned models — use Standard/PTU deployment instead.
- Completed work billable after cancellation.
- Include file expiry + output retention in production automation.
- Separate quota from Standard — check `10_quota_ptu_preflight.py` for current enqueued-token allocation.

**References:** [Batch](https://learn.microsoft.com/azure/foundry/openai/how-to/batch) · [Deployment types](https://learn.microsoft.com/azure/foundry/foundry-models/concepts/deployment-types)

### 10 — Quota + PTU preflight

**Question answered:** Which quota is available and which deployments already exist in this region?

**Background.** Default is a local decision aid comparing Standard vs Priority vs Batch vs PTU vs Instant. `--apply` performs control-plane reads: resource region, deployments, and location quota usage. Inspection only, no writes.

```bash
# local decision aid
uv run python 06-model-customization-other/10_quota_ptu_preflight.py

# read cloud state
uv run python 06-model-customization-other/10_quota_ptu_preflight.py --apply
```

**Code path.**
1. `--apply`: `CognitiveServicesManagementClient.accounts.get(rg, account)` → region.
2. `deployments.list(rg, account)` → per deployment print name + model + sku + capacity.
3. `usages.list(location)` → per bucket print name + current/limit/unit (skip zero entries).

**What to watch.** Region, per-deployment SKU + capacity, per-quota-bucket usage. A limit close to `current_value` signals imminent 429s.

**Quota vs capacity.** Two separate things:
- **Quota** is a policy limit assigned per subscription + region + model + type.
- **Capacity** is currently deployable supply.
- PTU quota does NOT reserve capacity. Verify capacity in Foundry portal or Model Capacities API immediately before deployment.
- PTU sizing depends on request rate, I/O shape, cache rate, model params, minimum size — use the PTU calculator, not a fixed TPM conversion.

**References:** [Provisioned throughput](https://learn.microsoft.com/azure/foundry/openai/concepts/provisioned-throughput) · [Provisioned throughput sizing](https://learn.microsoft.com/azure/foundry/openai/how-to/provisioned-throughput-sizing) · [Provisioned throughput billing](https://learn.microsoft.com/azure/foundry/openai/concepts/provisioned-throughput-billing)

### 11 — Priority processing

**Question answered:** How do I opt one request into the priority tier and confirm it was honored?

**Background.** Priority charges a per-token premium for lower latency on supported Global Standard or US Data Zone Standard deployments. Shares quota with Standard. Under ramp/peak/long-context conditions requests can fall back to Standard tier — always inspect returned `service_tier`.

```bash
# preflight
uv run python 06-model-customization-other/11_priority_processing.py --model <deployment>

# apply
uv run python 06-model-customization-other/11_priority_processing.py --model <deployment> --apply
```

**Code path.**
1. `--apply`: `responses.create(model=deployment, input=text, service_tier="priority")`.
2. Print response model, `service_tier`, `output_text`.

**What to watch.** `Service tier: priority` confirms tier honored. Falls back to `standard` under contention.

**Priority ≠ PTU.**
- Priority = premium per-token for latency; can fall back.
- PTU = reserved hourly capacity; dedicated but bills while idle.
- For a hard latency SLA, PTU is the choice. Priority is for latency-sensitive workloads that don't need capacity guarantee.
- Monitor via Azure Monitor request latency + service_tier dimensions to see fallback rate.

**References:** [Priority processing](https://learn.microsoft.com/azure/foundry/openai/concepts/priority-processing) · [Provisioned throughput](https://learn.microsoft.com/azure/foundry/openai/concepts/provisioned-throughput)

### 12 — Model Router + Instant Access

**Question answered:** How do I call a deployed router or a supported instant model?

**Background.** Two patterns in one lab. Router picks between allowed models per request (Balanced/Quality/Cost mode configured on the deployment). Instant Access calls a supported preview model name directly with no deployment — uses global quota, currently requires West US 3 project + Foundry User + supported instant model.

```bash
# router — call deployed alias
uv run python 06-model-customization-other/12_router_instant.py \
  --mode router --model model-router --apply

# instant — call supported model name (no deployment)
uv run python 06-model-customization-other/12_router_instant.py \
  --mode instant --model <instant-model-name> --apply
```

**Code path.**
1. `--apply`: `openai_client().responses.create(model=name, input=text)`.
2. Print `Requested: <name>` and `Handled by: <response.model>`.

**What to watch.** Router: `Handled by:` shows per-request selection (often differs from `Requested:`). Instant: same client/API but no deployment created.

**When each fits.**
- **Router** — mixed prompt complexity where hard-coding one model wastes cost or quality. Configure allowed subset in deployment.
- **Instant** — preview prototyping without deployment overhead. Pin version when stability matters.
- **Neither** — replaces PTU for dedicated capacity, custom filters, data-residency requirements, endpoint-specific policy, or team quota partitioning. Use a deployment for those.

**References:** [Model router](https://learn.microsoft.com/azure/foundry/openai/concepts/model-router) · [Model router how it works](https://learn.microsoft.com/azure/foundry/openai/concepts/model-router-how-it-works) · [Instant models](https://learn.microsoft.com/azure/foundry/concepts/instant-models)

---

## Stage 5 — Cost planning (lesson 13)

Local arithmetic for PTU commitment planning. Zero cloud calls.

### 13 — PTU cost review

**Question answered:** What is a lower-bound monthly cost estimate for N PTUs at rate R?

**Background.** Pure arithmetic: `PTU × hourly_rate × hours` (default 730 h/month). Supply your verified current price from the Foundry pricing page for the exact model + region + SKU. Not a bill and not a forecast.

```bash
uv run python 06-model-customization-other/13_cost_review.py \
  --ptu 50 --hourly-rate <current-price-per-ptu-hour>
```

**Code path.**
1. `ptu_monthly_cost(ptu, hourly_rate, hours=730)` → validate positive → return product.
2. Print formula and result.

**What to watch.** `PTU hourly estimate: 50 × 1.23 × 730 = 44895.00`.

**Not included in the estimate.** Training tokens, RFT grader calls, distillation teacher calls, evaluation deployment hosting, Priority premium, Global Batch spend, storage, monitoring, network egress, reservation terms. Result is a lower bound — add these categories from current pricing.

**Cost discipline.**
- Compare estimate against actual Cost Management data with resource + deployment tags.
- Delete idle evaluation deployments and expired datasets under retention policy.
- Re-verify hourly rate in current pricing page before commitment.

**References:** [Fine-tuning cost management](https://learn.microsoft.com/azure/foundry/openai/how-to/fine-tuning-cost-management) · [Provisioned throughput billing](https://learn.microsoft.com/azure/foundry/openai/concepts/provisioned-throughput-billing)

---

## Feature status and hard limits

| Feature | Status | Practical boundary |
|---|---|---|
| SFT | GA for supported base models | JSONL last message = assistant; verify base model + region + tier support. |
| DPO | Supported for listed models | Preference-pair contract; supported model list narrower than SFT. |
| RFT | Available for listed models | $5,000 safety stop on training + grading; grader sandboxed (no network). |
| Distillation via lab 04 | Local pattern | Not a Foundry preview service; teacher choice is manual. |
| Synthetic data generation | **Preview** portal | 1 PDF/MD/text or 1 OpenAPI 3.x JSON <20 MB; 50–1,000 samples; region-limited. |
| Global Batch | GA | No fine-tuned models; separate enqueued-token quota; 24h completion target. |
| Priority processing | GA on supported Global/DZ Standard | Falls back to Standard under contention; premium per-token. |
| PTU | GA for listed models | Quota ≠ capacity; hourly billing while present including idle. |
| Instant Access | **Preview** | Currently West US 3 project + supported models + global quota. |
| Model Router | Supported | Deployed alias required; router mode + allowed subset configured on deployment. |
| Fine-tuned model deployments | GA for Standard; Global Standard + PTU **preview** where supported | Availability model + region dependent; hosting bills hourly. |

## Troubleshooting

| Symptom | Likely cause | Resolution |
|---|---|---|
| `ValueError: row N must end with an assistant message` (SFT) | Row has trailing user or system message | Fix that row before upload; lesson 05 refuses to submit. |
| `ValueError: row N needs an assistant message` (DPO) | preferred_output or non_preferred_output missing assistant role | Add assistant message to that output list. |
| `RFT Python grader must define def grade(sample, item):` | Grader missing required signature | Add exact signature; other functions can exist alongside. |
| `--output already exists` (lesson 04) | Trying to overwrite distillation output | Rename output or delete prior file after review. |
| Training job `failed` with data error | Row failed API validation post-upload | Compare failing row against SDK validator output; re-run lesson 01/02/03. |
| Job status stuck `validating` for hours | Queue depth for chosen tier | Try `--training-type GlobalStandard` for faster queue; verify tier availability. |
| Reward hacking (train high, val flat) | Grader gameable | Re-calibrate grader; add adversarial cases; consider multi-grader. |
| Deployment fails: `SKU not available for model` | Fine-tuned deployment SKU + model + region combination unsupported | Check current base-model support matrix; try different region or SKU. |
| Deployment succeeds but inference returns 404 | Deployment name mismatch or propagation delay | Verify deployment name in Foundry portal; wait a few minutes. |
| Batch job `failed` on all rows | Wrong deployment name in row bodies, or targeting fine-tuned model | Batch does not support fine-tuned models; use base Global Batch deployment. |
| Priority request returns `service_tier: standard` | Fallback under contention or unsupported deployment | Check current supported deployment types; monitor fallback rate. |
| Router returns same model every time | Router policy misconfigured or single model in allowed subset | Reconfigure router policy in Foundry portal. |
| PTU deployment fails despite quota approved | Capacity not currently deployable in region | Quota ≠ capacity; check Model Capacities API immediately before deployment. |
| Instant Access `403` or `not found` | Wrong region or unsupported model name | Confirm current supported regions + model list; Instant currently requires West US 3. |
| Cost estimate wildly off | Missing categories | Result is lower bound; add training tokens, grader calls, evaluation, batch, storage, monitoring separately. |

## CI/CD and operational release

Treat customization as a release system: reviewed datasets, one training job at a time, evaluated candidate, staged deployment, monitored production.

```text
Reviewed dataset (pinned + versioned)
  → lesson 01/02/03 local validation in CI
  → lesson 05 --apply in nonprod (record job + file IDs)
  → lesson 06 --apply to observe until Succeeded
  → lesson 07 --apply to disposable eval deployment
  → lesson 08 --apply for exact-match vs baseline
  → domain 01 lesson 21 cloud evaluation for open-ended quality
  → human audit of representative outputs + subgroups + safety
  → approval gate: quality + safety + latency + cost thresholds
  → lesson 07 --apply to production deployment name (staged)
  → canary traffic where supported; monitor via Azure Monitor + Cost Management
  → delete disposable eval deployment
```

### What to version

- Dataset content + splits (train/validation/held-out) as immutable artifacts with SHAs.
- Base model + version pin + method + training-type + hyperparameters.
- Grader source + calibration notes for RFT.
- Deployment name + SKU + capacity + region as IaC.
- Evaluation dataset + thresholds + human-review sign-off.
- Cost budget + tags for training, distillation, hosting, evaluation.

### Release gates

| Change | Minimum gate |
|---|---|
| New dataset | Lesson 01/02/03 pass; reviewer sign-off; PII/protected-content sweep. |
| New training job | Job succeeded; validation metrics acceptable; held-out score beats baseline. |
| New deployment (fine-tuned) | SKU + region supported; capacity available; hosting budget approved; retention plan set. |
| Delivery tier change (Standard→Priority/PTU/Batch) | Cost delta + latency benefit measured; fallback behavior confirmed. |
| Router policy change | Selected-model distribution + cost + quality regression review. |
| Instant Access adoption | Preview scope acknowledged; version pinned; fallback plan if preview scope changes. |

Avoid using one aggregate quality score as a release decision. A higher score can hide safety, subgroup, latency, cost, or fallback failures.

## Security, networking, and IaC

| Decision | Recommendation | Common pitfall |
|---|---|---|
| Identity for training | Least-privilege service principal or managed identity with data-plane role only; separate control-plane identity for deployments | Owner-on-subscription for training scripts blurs blast radius. |
| Dataset storage | Blob with private endpoint + customer-managed key; retention + purge policy | Datasets in repo or unversioned bucket = uncontrolled training input. |
| Fine-tuned model access | Endpoint-only role (`Cognitive Services OpenAI User` scoped to deployment) | Broad account-level access grants inference on every deployment. |
| PTU commitment | Verify capacity in target region + budget for idle + tag for cost attribution | Committing quota without capacity → deployment fails at scale time. |
| Global Batch data | File retention + output cleanup automation; separate quota accounting | Files linger after job completes; enqueued-token quota surprises. |
| Distillation teacher IP | Confirm teacher licensing permits generating training data | Teacher terms may restrict downstream student training. |
| IaC | Bicep/Terraform for deployments + role assignments; keep training jobs procedural | Portal + IaC + CLI as competing sources of truth for deployment state. |

## Common exam traps

| Claim | Correct interpretation |
|---|---|
| "Fine-tuning teaches the model facts." | False. Fine-tuning changes weights for behavior/format/preference. RAG teaches facts. |
| "DPO can teach a new task." | False. DPO refines preference between two acceptable answers. Use SFT for new skills. |
| "RFT rising train reward means training works." | False. Only rising VALIDATION reward with train matters — otherwise reward hacking. |
| "Global Batch is a fast serving tier." | False. Async 24h target; not for latency-sensitive traffic. |
| "Global Batch supports fine-tuned models." | False per current docs. Use Standard/PTU deployment. |
| "PTU quota reserves capacity." | False. Quota is policy limit; capacity is separate supply. Verify both. |
| "Priority processing is guaranteed low latency." | False. Falls back to Standard under contention. PTU is the guarantee. |
| "Instant Access replaces deployments." | False. Preview convenience; use deployments for fine-tuned models, PTU, custom filters, residency, endpoint policy. |
| "Model Router optimizes cost automatically." | Partly. Router picks per-request from allowed models per configured mode; you configure and validate. |
| "Distillation output is training data." | False. It is a candidate dataset. Review, filter, split, red-team first. |
| "Newest checkpoint = best checkpoint." | False. Pick against held-out thresholds. |
| "GlobalStandard training keeps my data regional." | False. Data + weights may leave resource region for global capacity. Use Standard for regional residency. |
| "RFT $5,000 cost stop is my budget." | False. It's a safety stop. Resuming continues billing. Set your own budget. |
| "Exact-match evaluation covers open-ended tasks." | False. Only for single-token classification/extraction. Use graders + human audit for open-ended. |
| "Fine-tuned deployment behaves same as base." | False. Behavior + safety + latency + token count can differ. Re-run safety evaluation. |

## Objective coverage and limits

Runnable evidence in this folder covers dataset validation for SFT/DPO/RFT, distillation candidate generation, single training job submission per method, job monitoring, fine-tuned model deployment, exact-match evaluation, Global Batch submission, control-plane quota reads, priority-tier request, router + Instant Access invocation, and local PTU cost arithmetic.

It does **not** prove production readiness, current region/model availability, complete safety evaluation of a fine-tuned candidate, capacity guarantees for PTU/Batch/Instant, correctness of an RFT grader against adversarial inputs, or cost accuracy beyond a lower-bound PTU arithmetic. Preview features (Instant Access, RFT scope, fine-tuned PTU/Global Standard) can change independently.

## References

### Fine-tuning methods

- [Fine-tuning (SFT overview)](https://learn.microsoft.com/azure/foundry/openai/how-to/fine-tuning)
- [Direct Preference Optimization](https://learn.microsoft.com/azure/foundry/openai/how-to/fine-tuning-direct-preference-optimization)
- [Reinforcement fine-tuning](https://learn.microsoft.com/azure/foundry/openai/how-to/reinforcement-fine-tuning)
- [Fine-tuning considerations](https://learn.microsoft.com/azure/foundry/openai/concepts/fine-tuning-considerations)
- [Fine-tuning safety evaluation](https://learn.microsoft.com/azure/foundry/openai/how-to/fine-tuning-safety-evaluation)
- [Fine-tuning functions](https://learn.microsoft.com/azure/foundry/openai/how-to/fine-tuning-functions)
- [Fine-tuning vision](https://learn.microsoft.com/azure/foundry/openai/how-to/fine-tuning-vision)

### Data + graders

- [Data generation (preview synthetic data)](https://learn.microsoft.com/azure/foundry/fine-tuning/data-generation)
- [Azure OpenAI graders](https://learn.microsoft.com/azure/foundry/concepts/evaluation-evaluators/azure-openai-graders)
- [Fine-tune CLI](https://learn.microsoft.com/azure/foundry/fine-tuning/fine-tune-cli)

### Deployment + cost

- [Fine-tuning deployment](https://learn.microsoft.com/azure/foundry/openai/how-to/fine-tuning-deploy)
- [Fine-tuning cost management](https://learn.microsoft.com/azure/foundry/openai/how-to/fine-tuning-cost-management)
- [Deployment types](https://learn.microsoft.com/azure/foundry/foundry-models/concepts/deployment-types)
- [Automate quota and deployments](https://learn.microsoft.com/azure/foundry/openai/how-to/automate-quota-deployments)

### Delivery tiers

- [Global Batch](https://learn.microsoft.com/azure/foundry/openai/how-to/batch)
- [Priority processing](https://learn.microsoft.com/azure/foundry/openai/concepts/priority-processing)
- [Provisioned throughput](https://learn.microsoft.com/azure/foundry/openai/concepts/provisioned-throughput)
- [Provisioned throughput sizing](https://learn.microsoft.com/azure/foundry/openai/how-to/provisioned-throughput-sizing)
- [Provisioned throughput billing](https://learn.microsoft.com/azure/foundry/openai/concepts/provisioned-throughput-billing)
- [Provisioned get started](https://learn.microsoft.com/azure/foundry/openai/how-to/provisioned-get-started)
- [Model router](https://learn.microsoft.com/azure/foundry/openai/concepts/model-router)
- [Model router how it works](https://learn.microsoft.com/azure/foundry/openai/concepts/model-router-how-it-works)
- [Model router policy](https://learn.microsoft.com/azure/foundry/how-to/model-router-policy)
- [Instant models](https://learn.microsoft.com/azure/foundry/concepts/instant-models)

### Migration

- [Model inference to OpenAI API migration](https://learn.microsoft.com/azure/foundry/how-to/model-inference-to-openai-migration)

### Foundry Models catalog

- [Endpoints (model catalog)](https://learn.microsoft.com/azure/foundry/foundry-models/concepts/endpoints)
- [Model versions](https://learn.microsoft.com/azure/foundry/foundry-models/concepts/model-versions)
- [Models sold directly by Azure](https://learn.microsoft.com/azure/foundry/foundry-models/concepts/models-sold-directly-by-azure)
- [Models from partners](https://learn.microsoft.com/azure/foundry/foundry-models/concepts/models-from-partners)
- [Deployment types (gov)](https://learn.microsoft.com/azure/foundry/foundry-models/concepts/deployment-types-gov)
- [Deploy Foundry Models](https://learn.microsoft.com/azure/foundry/foundry-models/how-to/deploy-foundry-models)
- [Configure Entra ID for Foundry Models](https://learn.microsoft.com/azure/foundry/foundry-models/how-to/configure-entra-id)

### Claude models (partner)

- [Claude models](https://learn.microsoft.com/azure/foundry/foundry-models/concepts/claude-models)
- [Claude models billing](https://learn.microsoft.com/azure/foundry/foundry-models/concepts/claude-models-billing)
- [Claude models hosting comparison](https://learn.microsoft.com/azure/foundry/foundry-models/concepts/claude-models-hosting-comparison)
- [Configure Claude Code](https://learn.microsoft.com/azure/foundry/foundry-models/how-to/configure-claude-code)
- [Configure Claude Desktop](https://learn.microsoft.com/azure/foundry/foundry-models/how-to/configure-claude-desktop)
- [Claude models data privacy](https://learn.microsoft.com/azure/foundry/responsible-ai/claude-models/data-privacy)

### Related domains

- [Domain 1: Plan and manage Foundry](../01-plan-and-manage/README.md)
- [Domain 2: Generative AI and agents](../02-generative-ai-and-agents/README.md)
