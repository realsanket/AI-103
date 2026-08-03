# Domain 1 — Plan and Manage an Azure AI Solution (25-30%)

## Files

| # | File | Syllabus bullet |
|---|---|---|
| 01 | `01_model_catalog_list.py` | Choose an appropriate model for each task (LLM/SLM/multimodal) |
| 02 | `02_deployment_types.py` | Choose appropriate deployment options (Global / Regional / PTU / Serverless) |
| 03 | `03_deploy_model.py` | Configure model and agent deployments |
| 04 | `04_model_router.py` | Choose appropriate Foundry services — Model Router |
| 05 | `05_quotas_and_tpm.py` | Manage quotas, scaling, rate limits, cost footprints |
| 06 | `06_rate_limit_backoff.py` | Handle 429 with exponential backoff + jitter |
| 07 | `07_managed_identity_agent.py` | Configure security — managed identity, keyless credentials |
| 08 | `08_content_safety_filters.py` | Configure safety filters, guardrails, content moderation |
| 09 | `09_prompt_shields_user.py` | Prompt Shields — user prompt attacks |
| 10 | `10_prompt_shields_docs.py` | Prompt Shields — indirect (document) prompt injection |
| 11 | `11_evaluator_groundedness.py` | Responsible AI instrumentation — evaluators + self-critique |
| 12 | `12_agent_tracing.py` | Observability — tracing, token analytics, safety signals, latency |
| 13 | `13_rbac_role_policies.py` | Security — RBAC role assignments (list + assign) |

## Run

```bash
python 01-plan-and-manage/07_managed_identity_agent.py
```

Prereqs: `.env` filled, `az login` completed. See root [README.md](../README.md).

## Reference docs (in-repo)

- Deployment types: `.context/azure-ai-docs/articles/foundry/concepts/deployments-overview.md`
- Model Router: `.context/azure-ai-docs/articles/foundry/openai/concepts/model-router.md`
- Provisioned Throughput: `.context/azure-ai-docs/articles/foundry/openai/provisioned-quickstart.md`
- Content Filter / Prompt Shields: `.context/azure-ai-docs/articles/foundry/openai/concepts/content-filter-prompt-shields.md`
- Guardrails: `.context/azure-ai-docs/articles/foundry/guardrails/`
- Evaluators: `.context/azure-ai-docs/articles/foundry/concepts/built-in-evaluators.md`
- Tracing: `.context/azure-ai-docs/articles/foundry/observability/how-to/trace-agent-framework.md`
