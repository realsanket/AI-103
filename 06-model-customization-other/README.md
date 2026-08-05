# Domain 6: Model customization and delivery

> Supplemental current Microsoft Foundry labs. Run commands from repository root with `uv run python 06-model-customization-other/<lesson>.py`. Every remote operation is opt-in with `--apply`; default commands validate local inputs or print a preflight. A successful request proves only that request. It does not prove model quality, safety, data governance, capacity, availability, or production readiness.

This domain covers model customization and current delivery choices that affect its operational result: supervised fine-tuning (SFT), Direct Preference Optimization (DPO), reinforcement fine-tuning (RFT), distillation, datasets, graders, training, deployment, evaluation, quota, PTU, priority processing, Global Batch, instant access, model router, and cost.

## Start safely

Install project dependencies, authenticate, and configure existing endpoints:

```bash
uv sync
cp .env.example .env
az login
uv run python 06-model-customization-other/00_customization_preflight.py
```

The labs use `_shared.openai_client.openai_client()`: an OpenAI v1 client against `AZURE_OPENAI_ENDPOINT` with `DefaultAzureCredential` and scope `https://ai.azure.com/.default`. Do not use a Foundry project endpoint as this client's base URL. Use deployment names for deployed models. A model-router deployment is also a deployment name. Instant access uses a supported model name, not a deployment.

Set existing root settings before an opt-in operation:

```dotenv
AZURE_OPENAI_ENDPOINT=https://<resource>.openai.azure.com
FOUNDRY_ENDPOINT=https://<resource>.services.ai.azure.com
AZURE_SUBSCRIPTION_ID=<subscription-id>
AZURE_RESOURCE_GROUP=<resource-group>
```

Pass model names, deployment names, dataset paths, job IDs, and output paths as command arguments. This keeps data-bearing or experiment-specific values out of `.env.example`. Never put an API key, access token, customer data, SAS URL, or connection string in source control.

### Roles, boundaries, and preflight

Start with `Foundry User` to use project/model data-plane features. Training and model deployment require current permissions for the target resource; a deployment generally needs `Microsoft.CognitiveServices/accounts/deployments/write` or an equivalent role. `10_quota_ptu_preflight.py --apply` also needs management-plane read access. Confirm exact roles in the target tenant before an apply operation.

Before every `--apply`:

1. Use a disposable, nonproduction resource and a least-privilege identity.
1. Verify current model, method, region, tier, quota, and capacity support in
the Foundry portal/model catalog. Do not infer availability from this repo.
1. Remove secrets, personal data, protected content, and unlicensed material
from datasets. Confirm retention, residency, and training-use approval.
1. Establish a held-out evaluation baseline and a threshold before training.
1. Estimate training, grading, inference, hosting, evaluation, storage,
monitoring, and network cost. Set Azure budgets and tags outside this repo.
1. Review every output and persistent effect printed by the preflight.

`--apply` is never a confirmation prompt. It performs the named operation immediately. Read-only Azure inspection is also opt-in so a default run makes no cloud request.

## Learning path

| Lesson | Default action | `--apply` effect |
|---|---|---|
| `00_customization_preflight.py` | Reads local settings. | No `--apply`; remains local. |
| `01_sft_dataset.py` | Validates SFT JSONL. | Not applicable; remains local. |
| `02_dpo_dataset.py` | Validates DPO JSONL. | Not applicable; remains local. |
| `03_rft_dataset_grader.py` | Validates RFT JSONL and compiles grader source without running it. | Not applicable; remains local. |
| `04_distillation_dataset.py` | Validates teacher prompts and prints output plan. | Calls teacher once per row and creates a new local JSONL candidate file. |
| `05_submit_training.py` | Validates selected data and submission plan. | Uploads files and submits exactly one SFT, DPO, or RFT job. |
| `06_training_monitor.py` | Prints read plan. | Reads one job and its ten newest events. |
| `07_deploy_checkpoint.py` | Prints deployment payload plan. | Creates or updates one deployment. |
| `08_evaluate_candidate.py` | Validates held-out exact-match rows. | Calls candidate and optional baseline once per row. |
| `09_batch_inference.py` | Validates Global Batch Responses JSONL. | Uploads input and creates one asynchronous Global Batch job. |
| `10_quota_ptu_preflight.py` | Explains delivery-choice preflight. | Reads resource region, deployments, and quota usage. |
| `11_priority_processing.py` | Prints one priority request plan. | Sends one priority-tier Responses request. |
| `12_router_instant.py` | Prints router or instant-access plan. | Sends one router or instant model request. |
| `13_cost_review.py` | Calculates a local PTU arithmetic estimate. | Not applicable; remains local. |

## Choose customization method

| Need | Method | Data contract | Do not use it for |
|---|---|---|---|
| Teach reliable answers, a format, extraction, or tool behavior | SFT | High-quality `messages` input-output examples | An ambiguous preference where no output is objectively best. |
| Prefer tone, style, safety, or another subjective answer over a paired alternative | DPO | One input plus preferred and non-preferred outputs | Teaching a new skill without contrasting preference pairs. |
| Improve reasoning with a measurable reward | RFT | Prompts, validation set, and one calibrated grader | Tasks whose quality cannot be reliably graded. |
| Create candidate examples from a stronger teacher | Distillation | Reviewed seed prompts, then teacher output | Automatic trust of synthetic output. |

Fine-tuning changes weights. It does not retrieve current facts, replace authorization, repair a poor task definition, or eliminate a need for prompting and evaluation. Start with prompt/structured-output/RAG baselines. Fine-tune only when a task remains stable and a measured baseline justifies the data, operation, and lifecycle cost.

### SFT data

SFT uses UTF-8 JSONL. Each record has a nonempty `messages` array that ends with an `assistant` message:

```jsonl
{"messages":[{"role":"system","content":"Extract invoice status as JSON."},{"role":"user","content":"Invoice 100 is paid."},{"role":"assistant","content":"{\"invoice\":\"100\",\"status\":\"paid\"}"}]}
```

Validate before upload:

```bash
uv run python 06-model-customization-other/01_sft_dataset.py --dataset train.jsonl
```

Split source examples before training: train for fitting, validation for training-time selection, and held-out evaluation for the release decision. Near duplicates across splits leak answers. Preserve task diversity and edge/failure cases. Prefer accurate, representative examples over bulk collection.

### DPO data

DPO uses preference pairs, not SFT `messages` rows. Each row has `input`, `preferred_output`, and `non_preferred_output`; outputs include at least one assistant message:

```jsonl
{"input":{"messages":[{"role":"system","content":"Respond briefly."},{"role":"user","content":"Explain a retry."}]},"preferred_output":[{"role":"assistant","content":"Retry bounded transient failures with backoff and jitter."}],"non_preferred_output":[{"role":"assistant","content":"Retry forever immediately."}]}
```

```bash
uv run python 06-model-customization-other/02_dpo_dataset.py --dataset preferences.jsonl
```

Keep alternatives comparable: same user intent, one intentionally preferred response, and a documented annotation rule. Do not encode hidden discrimination, policy conflicts, or accidental style bias as preference. The submission lab exposes documented DPO `beta` and `l2_multiplier` parameters. Start with defaults unless controlled experiments show a reason to change them.

### RFT data and graders

RFT suits reasoning tasks with a verifiable result. Its JSONL records end in a `user` message and can include fields consumed by the grader:

```jsonl
{"messages":[{"role":"developer","content":"Return only the arithmetic result."},{"role":"user","content":"2 + 3"}],"answer":"5"}
```

The lab checks grader syntax, but never executes it locally:

```bash
uv run python 06-model-customization-other/03_rft_dataset_grader.py \
  --dataset rft-train.jsonl --grader grader.py
```

An RFT Python grader defines `grade(sample, item)` and returns a numeric score. Keep it deterministic where possible, bounded, adversarially tested, and independent of accidental answer shortcuts. The service executes it in a constrained environment; do not rely on network access. Use a single grader, or an explicit multigrader when one reward requires combined checks.

RFT requires training and validation data. Calibrate the grader against baseline responses before training. Monitor train and validation reward, reasoning-token behavior, and failure cases. A rising training reward with a weak validation reward is not success; it can signal reward hacking. The current RFT service has a cost stop at $5,000 for training plus grading; resuming continues billing. Do not treat that safety stop as a budget.

### Distillation and synthetic data

`04_distillation_dataset.py` is a deliberately narrow, inspectable teacher-generation lab. Input rows contain only `messages`; with `--apply`, it calls the named teacher once per row and writes a new SFT-shaped JSONL:

```bash
uv run python 06-model-customization-other/04_distillation_dataset.py \
  --source prompts.jsonl --output distilled-candidates.jsonl \
  --teacher <teacher-deployment> --apply
```

The output file must not exist, preventing overwrite. Generated output is a candidate dataset, not approved training data. Sample and grade it, remove duplicates and unsupported claims, red-team safety behavior, split it from the prompts used to create it, and retain lineage to seed, teacher, model version, time, and review decision.

Foundry's current synthetic-data preview is a portal workflow. It supports Simple Q&A from one PDF/Markdown/text reference file or Tool use from one OpenAPI 3.0.x/3.1.x JSON file, each under 20 MB. It supports 50–1,000 samples and an optional 80/20 train-validation split. It is preview, has region limits, and automatically deploying a generator can create cost. Use it only after reviewing its current portal availability and data rules.

## Submit, monitor, deploy, and evaluate

### Submit a job

Validate data first, then explicitly submit. SFT can omit `--validation` for the API, but a validation set is strongly recommended. RFT requires it.

```bash
# Preview only: validates local data; no upload or job.
uv run python 06-model-customization-other/05_submit_training.py \
  --kind sft --train train.jsonl --validation validation.jsonl \
  --model <supported-base-model>

# Uploads each file and submits one persistent, billable job.
uv run python 06-model-customization-other/05_submit_training.py \
  --kind sft --train train.jsonl --validation validation.jsonl \
  --model <supported-base-model> --suffix northwind-v1 \
  --training-type GlobalStandard --apply
```

`--training-type` is intentionally opt-in. Current SFT training choices have different residency, queueing, and price behavior:

| Training type | Intended trade-off |
|---|---|
| `Standard` | Regional processing and data-residency guarantees, when supported. |
| `GlobalStandard` | Uses global capacity; lower cost/faster queueing can require data and weights outside resource region. |
| `Developer` | Idle-capacity savings for experiments; no latency/SLA or residency guarantee, and a job can preempt/resume. |

Model/method/tier availability changes. Verify current catalog support before submission; the lab does not choose an unsupported combination for you.

```bash
# DPO
uv run python 06-model-customization-other/05_submit_training.py \
  --kind dpo --train dpo-train.jsonl --validation dpo-validation.jsonl \
  --model <dpo-model-version> --apply

# RFT
uv run python 06-model-customization-other/05_submit_training.py \
  --kind rft --train rft-train.jsonl --validation rft-validation.jsonl \
  --grader grader.py --model <rft-model-version> --apply
```

The apply path uploads supplied data with purpose `fine-tune`, then submits one job. It does not poll, deploy, or delete uploaded files. Record job and file IDs in your experiment system. Delete data and unused custom models under your approved retention process.

### Monitor and choose a checkpoint

```bash
uv run python 06-model-customization-other/06_training_monitor.py --job-id ftjob-... --apply
```

This is read-only and prints job state plus ten recent events. It does not poll continuously, select a checkpoint, or resume/cancel a job. Compare checkpoints and final model on the untouched held-out set. Select a candidate because it meets predeclared quality, safety, latency, and cost thresholds, not because it is newest.

### Deploy one candidate

```bash
uv run python 06-model-customization-other/07_deploy_checkpoint.py \
  --model-id ftchkpt-... --name northwind-ft-eval --sku Standard --capacity 1

uv run python 06-model-customization-other/07_deploy_checkpoint.py \
  --model-id ftchkpt-... --name northwind-ft-eval --sku Standard --capacity 1 --apply
```

`--apply` creates or updates the named deployment. That can replace an existing deployment and begins hosting charges. Preflight model/SKU support, quota, and capacity in the target region first. Fine-tuned models can use Standard, Global Standard preview, or Provisioned Throughput preview only where currently supported. Use a separate evaluation deployment, tag it, and delete it after the decision.

### Evaluate candidate versus baseline

`08_evaluate_candidate.py` makes a small, transparent exact-match comparison for tasks that really have one exact answer:

```jsonl
{"query":"2 + 3","expected":"5"}
```

```bash
uv run python 06-model-customization-other/08_evaluate_candidate.py \
  --dataset held-out.jsonl --candidate northwind-ft-eval \
  --baseline <base-deployment> --apply
```

It makes one Responses call per model per row, prints score only, and creates no cloud evaluation object. Exact match is unsuitable for open-ended quality. For those tasks, define an evaluation dataset and use a reviewed deterministic, similarity, label, score, or safety grader. Keep task graders separate from the RFT reward when measuring release quality. Audit representative outputs, subgroups, safety failures, latency, tokens, and cost alongside aggregate scores.

## Delivery and cost labs

### Global Batch

Global Batch is for asynchronous bulk work, not low-latency inference. It uses a Global Batch deployment and separate enqueued-token quota. It targets 24-hour processing but jobs can run longer until cancelled; completed work is still billable. Current documentation states that Batch does not support fine-tuned models.

Each JSONL row must have a unique `custom_id`, `POST`, `/v1/responses`, and the same Global Batch deployment in `body.model`:

```jsonl
{"custom_id":"case-1","method":"POST","url":"/v1/responses","body":{"model":"<global-batch-deployment>","input":"Classify: paid invoice"}}
```

```bash
uv run python 06-model-customization-other/09_batch_inference.py --input batch.jsonl
uv run python 06-model-customization-other/09_batch_inference.py --input batch.jsonl --apply
```

Apply uploads a file with purpose `batch` and creates one `24h` Batch job. It does not poll results, read output/error files, or cancel the job. Include file expiry and output retention in production automation.

### Quota, PTU, and capacity

```bash
uv run python 06-model-customization-other/10_quota_ptu_preflight.py
uv run python 06-model-customization-other/10_quota_ptu_preflight.py --apply
```

The default command is a local decision aid. Apply reads resource location, deployments, and quota usage only. It does not query live PTU model capacity, request quota, create a deployment, or guarantee a SKU/model is available.

Quota is a policy limit; capacity is currently deployable supply. PTU quota and capacity are both region and deployment-type scoped, and quota does not reserve capacity. Check capacity in the current Foundry deployment experience or model capacities API immediately before deployment. PTU sizing depends on request rate, input/output shape, cache rate, model-specific parameters, and minimum size. Use the Foundry PTU calculator/current sizing guidance rather than a fixed TPM conversion.

| Delivery choice | Use it when | Cost/operational constraint |
|---|---|---|
| Standard | Traffic varies or you are developing/testing. | Pay per token; shared capacity. |
| Priority processing | A supported online workload needs lower latency without commitment. | Priority per-token price; can fall back to Standard. |
| Provisioned Throughput | High, predictable, latency-sensitive production volume. | PTU hourly/reservation cost even when idle; capacity must exist. |
| Global Batch | Large deferred processing. | Asynchronous; separate quota; no fine-tuned model support. |
| Instant access | Preview prototyping with a supported model. | Current preview scope, global quota, and model list apply. |
| Model router | Model selection can trade quality/cost/latency per prompt. | Deploy and monitor router policy; inspect selected model. |

### Priority processing

```bash
uv run python 06-model-customization-other/11_priority_processing.py --model <deployment>
uv run python 06-model-customization-other/11_priority_processing.py --model <deployment> --apply
```

Apply sends exactly one billable Responses request with `service_tier="priority"`. Priority processing currently applies to supported Global Standard and US Data Zone Standard deployment configurations, shares quota with Standard, and can return a Standard-tier response under documented ramp/peak/long-context conditions. Inspect returned `service_tier`, Azure Monitor request/latency/usage metrics, and Cost Management tags. Do not assume priority is a hard guarantee; PTU is the dedicated-capacity choice.

### Model router and instant access

```bash
# Existing model-router deployment
uv run python 06-model-customization-other/12_router_instant.py \
  --mode router --model model-router --apply

# Current supported instant model name, not a deployment
uv run python 06-model-customization-other/12_router_instant.py \
  --mode instant --model <instant-model-name> --apply
```

Router apply calls its deployed alias and prints requested versus returned model. Router routing modes are Balanced, Quality, and Cost; select mode and model subset in deployment configuration, then validate quality, safety, latency, selected-model distribution, and cost with your workload.

Instant access is current preview behavior, not a replacement for deployments. At this repository's documentation snapshot it requires a West US 3 project, Foundry User access, a supported instant model, and global quota. It uses the same client/API but requires no deployment. Pin a version when stability matters. Use a deployment for fine-tuned models, PTU, custom content filters, data residency, endpoint-specific policy, or team quota partitioning.

### Cost review

```bash
uv run python 06-model-customization-other/13_cost_review.py \
  --ptu 50 --hourly-rate <current-price-per-ptu-hour>
```

This local calculator performs only `PTU × current hourly rate × hours`. It does not fetch prices or report Azure charges. Supply a current price verified for target model/SKU/region and compare estimates with actual Cost Management data. Include training tokens, RFT grading, distillation teacher calls, deployment hosting, candidate evaluation, priority/batch price, storage, monitoring, egress, and reservation terms. Delete idle evaluation deployments and expired datasets under your retention policy.

## Local official documentation used

This domain uses current material in `.context/azure-ai-docs/`; it does not reproduce retired SDK samples or legacy endpoint workflows. Recheck these local files before changing a lab:

| Topic | Local official source |
|---|---|
| SFT workflow, JSONL, tiers, checkpoints | `.context/azure-ai-docs/articles/foundry/openai/how-to/fine-tuning.md` and `includes/fine-tuning-oai-sdk.md` |
| DPO format and supported models | `.context/azure-ai-docs/articles/foundry/openai/how-to/fine-tuning-direct-preference-optimization.md` and its includes |
| RFT, rewards, graders, metrics | `.context/azure-ai-docs/articles/foundry/openai/how-to/reinforcement-fine-tuning.md` and its include |
| Synthetic data generation | `.context/azure-ai-docs/articles/foundry/fine-tuning/data-generation.md` |
| Fine-tuned deployment | `.context/azure-ai-docs/articles/foundry/openai/how-to/fine-tuning-deploy.md` |
| Evaluation graders | `.context/azure-ai-docs/articles/foundry/concepts/evaluation-evaluators/azure-openai-graders.md` |
| Global Batch | `.context/azure-ai-docs/articles/foundry/openai/how-to/batch.md` and `includes/how-to-batch-content.md` |
| PTU | `.context/azure-ai-docs/articles/foundry/openai/concepts/provisioned-throughput.md` |
| Priority | `.context/azure-ai-docs/articles/foundry/openai/concepts/priority-processing.md` |
| Router | `.context/azure-ai-docs/articles/foundry/openai/concepts/model-router.md` |
| Instant access | `.context/azure-ai-docs/articles/foundry/concepts/instant-models.md` |
| Fine-tuning cost | `.context/azure-ai-docs/articles/foundry/openai/how-to/fine-tuning-cost-management.md` |

Feature, model, region, quota, capacity, pricing, API, and preview status change independently. Local documentation supports this curriculum; the target subscription and current Microsoft Learn documentation decide whether an opt-in operation is available.
