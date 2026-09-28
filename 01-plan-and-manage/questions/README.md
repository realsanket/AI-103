# Domain 1 question review

Run the normal domain lessons first. This folder contains a local supplement
for questions where the existing labs did not expose the decision contract
directly.

## Per-question lesson map

| Question | Lesson file(s) | Coverage note | Status |
|---:|---|---|---|
| Q3 | [`11_prompt_shields_docs.py`](../11_prompt_shields_docs.py), [`12_spotlighting.py`](../12_spotlighting.py) | L11–12 Document Prompt Shields and Spotlighting | Existing |
| Q5 | [`25_foundry_tracing_setup.py`](../25_foundry_tracing_setup.py), [`26_agent_tracing.py`](../26_agent_tracing.py) | L25–26 run tracing | Existing |
| Q9 | [`30_evaluation_cicd_preflight.py`](../30_evaluation_cicd_preflight.py) | L30 evaluation CI/CD gate | Existing |
| Q10 | [`25_foundry_tracing_setup.py`](../25_foundry_tracing_setup.py), [`26_agent_tracing.py`](../26_agent_tracing.py), [`23_langchain_tracing.py`](../../02-generative-ai-and-agents/23_langchain_tracing.py) | L25–26 tracing, D2 L23 telemetry | Existing |
| Q17 | [`06_rate_limit_backoff.py`](../06_rate_limit_backoff.py) | L06 retry with exponential backoff and jitter | Existing |
| Q19 | [`30_evaluation_cicd_preflight.py`](../30_evaluation_cicd_preflight.py), [`19_groundedness_detection.py`](../19_groundedness_detection.py) | L30 merge gate plus L19 groundedness detection | Existing; partial: L30 gates on coherence, not groundedness |
| Q23 | [`01_access_and_metrics_preflight.py`](01_access_and_metrics_preflight.py), [`05_diagnostics_preflight.py`](../../07-production-platform-other/05_diagnostics_preflight.py) | `questions/01_access_and_metrics_preflight.py` plus D7 L05 RequestResponse diagnostics | Existing |
| Q24 | [`25_foundry_tracing_setup.py`](../25_foundry_tracing_setup.py), [`26_agent_tracing.py`](../26_agent_tracing.py), [`23_langchain_tracing.py`](../../02-generative-ai-and-agents/23_langchain_tracing.py) | L25–26 distributed tracing | Existing |
| Q26 | [`19_groundedness_detection.py`](../19_groundedness_detection.py), [`21_foundry_evaluation.py`](../21_foundry_evaluation.py), [`22_continuous_evaluation.py`](../22_continuous_evaluation.py) | L19 groundedness, L21–22 risk and safety evaluation | Existing; partial: no built-in groundedness evaluator configured |
| Q34 | [`19_groundedness_detection.py`](../19_groundedness_detection.py), [`21_foundry_evaluation.py`](../21_foundry_evaluation.py) | L19 groundedness detection, L21 evaluation run | Existing; partial: no built-in groundedness evaluator configured |
| Q40 | [`11_prompt_shields_docs.py`](../11_prompt_shields_docs.py), [`18_protected_material.py`](../18_protected_material.py) | L11 and L18 injection versus protected material | Existing |
| Q42 | [`11_prompt_shields_docs.py`](../11_prompt_shields_docs.py), [`12_spotlighting.py`](../12_spotlighting.py), [`22_bing_grounding_preflight.py`](../../08-advanced-agents-other/22_bing_grounding_preflight.py) | L11–12 plus D8 L22 web grounding | Existing |
| Q47 | [`26_agent_tracing.py`](../26_agent_tracing.py) | L26 token diagnostics | Existing |
| Q48 | [`08_rbac_role_policies.py`](../08_rbac_role_policies.py), [`19_blob_identity_paths.py`](../../05-information-extraction/19_blob_identity_paths.py) | L08 RBAC and D5 L19 Blob identity | Existing |
| Q49 | [`30_evaluation_cicd_preflight.py`](../30_evaluation_cicd_preflight.py), [`04_cicd_preflight.py`](../../07-production-platform-other/04_cicd_preflight.py) | L30 evaluation gate plus D7 L04 OIDC workflow | Existing |
| Q53 | [`07_managed_identity_agent.py`](../07_managed_identity_agent.py), [`01_first_api_call.py`](../../02-generative-ai-and-agents/01_first_api_call.py) | L07 identity plus D2 L01 Responses | Existing |
| Q56 | [`26_agent_tracing.py`](../26_agent_tracing.py) | L26 latency and token diagnosis | Existing |
| Q58 | [`26_agent_tracing.py`](../26_agent_tracing.py), [`24_production_observability_preflight.py`](../../02-generative-ai-and-agents/24_production_observability_preflight.py) | L26 and D2 L24 latency decomposition | Existing |
| Q59 | [`20_provenance_detection.py`](../20_provenance_detection.py), [`08_rbac_role_policies.py`](../08_rbac_role_policies.py) | L20 Content Safety identity reads Blob, L08 least-privilege RBAC | Existing |
| Q63 | [`09_content_safety_filters.py`](../09_content_safety_filters.py), [`48_hosted_agent_guardrails.py`](../../02-generative-ai-and-agents/48_hosted_agent_guardrails.py), [`20_provenance_detection.py`](../20_provenance_detection.py) | L09 guardrail block action, D2 L48 agent guardrail, L20 Blob Data Reader identity | Existing; partial: tool-call and tool-response intervention points not configured |
| Q64 | [`17_evaluator_groundedness.py`](../17_evaluator_groundedness.py) | L17 critique and regeneration | Existing |
| Q65 | [`10_prompt_shields_user.py`](../10_prompt_shields_user.py) | L10 User Prompt Shields | Existing |
| Q66 | [`21_foundry_evaluation.py`](../21_foundry_evaluation.py), [`25_foundry_tracing_setup.py`](../25_foundry_tracing_setup.py), [`26_agent_tracing.py`](../26_agent_tracing.py) | L21 evaluation and L25–26 observability | Existing; partial: no relevance evaluator configured |
| Q68 | [`25_foundry_tracing_setup.py`](../25_foundry_tracing_setup.py), [`26_agent_tracing.py`](../26_agent_tracing.py) | L25–26 prompt/output token metrics | Existing |
| Q69 | [`17_evaluator_groundedness.py`](../17_evaluator_groundedness.py), [`19_groundedness_detection.py`](../19_groundedness_detection.py), [`21_foundry_evaluation.py`](../21_foundry_evaluation.py) | L17, L19, L21 groundedness handling | Existing |
| Q71 | [`07_managed_identity_agent.py`](../07_managed_identity_agent.py), [`08_rbac_role_policies.py`](../08_rbac_role_policies.py) | L08 direct Azure OpenAI RBAC | Existing |
| Q75 | [`08_rbac_role_policies.py`](../08_rbac_role_policies.py), [`01_foundry_iq_connection_preflight.py`](../../08-advanced-agents-other/01_foundry_iq_connection_preflight.py) | L08 Search Index Data Reader, D8 L01 reader versus contributor | Existing |
| Q78 | [`25_foundry_tracing_setup.py`](../25_foundry_tracing_setup.py), [`26_agent_tracing.py`](../26_agent_tracing.py) | L25–26 tool latency spans | Existing |
| Q80 | [`21_foundry_evaluation.py`](../21_foundry_evaluation.py), [`22_continuous_evaluation.py`](../22_continuous_evaluation.py) | L21–22 quality regression | Existing |
| Q81 | [`04_model_router.py`](../04_model_router.py) | L04 Model Router | Existing |
| Q85 | [`04_model_router.py`](../04_model_router.py), [`03_reasoning.py`](../../02-generative-ai-and-agents/03_reasoning.py) | L04 small-versus-frontier routing, D2 L03 multi-step reasoning model | Existing; partial: no dedicated LLM-versus-SLM exercise |
| Q96 | [`25_foundry_tracing_setup.py`](../25_foundry_tracing_setup.py), [`26_agent_tracing.py`](../26_agent_tracing.py) | L25–26 stage latency tracing | Existing |
| Q98 | [`17_evaluator_groundedness.py`](../17_evaluator_groundedness.py) | L17 reflection/regeneration | Existing |
| Q100 | [`17_evaluator_groundedness.py`](../17_evaluator_groundedness.py), [`21_foundry_evaluation.py`](../21_foundry_evaluation.py) | L17 corrective retry versus L21 evaluation | Existing |
| Q101 | [`21_foundry_evaluation.py`](../21_foundry_evaluation.py), [`30_evaluation_cicd_preflight.py`](../30_evaluation_cicd_preflight.py) | L30 and L21 RAG CI/CD evaluation | Existing |
| Q103 | [`18_protected_material.py`](../18_protected_material.py), [`19_groundedness_detection.py`](../19_groundedness_detection.py), [`21_foundry_evaluation.py`](../21_foundry_evaluation.py) | L18 protected material, L19 groundedness, L21 evaluation | Existing; partial: no relevance evaluator configured |
| Q104 | [`21_foundry_evaluation.py`](../21_foundry_evaluation.py) | L21 evaluation categories | Existing |
| Q111 | [`25_foundry_tracing_setup.py`](../25_foundry_tracing_setup.py), [`26_agent_tracing.py`](../26_agent_tracing.py) | L25–26 end-to-end traces | Existing |
| Q112 | [`25_foundry_tracing_setup.py`](../25_foundry_tracing_setup.py) | L25 Application Insights setup | Existing |
| Q113 | [`01_access_and_metrics_preflight.py`](01_access_and_metrics_preflight.py), [`08_rbac_role_policies.py`](../08_rbac_role_policies.py) | `questions/01_access_and_metrics_preflight.py` plus L08 role assignment | Existing; partial: Key Vault Secrets User role not named |
| Q115 | [`25_foundry_tracing_setup.py`](../25_foundry_tracing_setup.py), [`26_agent_tracing.py`](../26_agent_tracing.py), [`23_langchain_tracing.py`](../../02-generative-ai-and-agents/23_langchain_tracing.py) | L25–26 hierarchical spans, D2 L23 tool-call spans | Existing |
| Q125 | [`06_rate_limit_backoff.py`](../06_rate_limit_backoff.py), [`06_file_search_tool.py`](../../02-generative-ai-and-agents/06_file_search_tool.py) | L06 throttling, D2 L06 uploads | Existing |
| Q130 | [`30_evaluation_cicd_preflight.py`](../30_evaluation_cicd_preflight.py) | L30 evaluation YAML CI/CD | Existing; partial: no evaluation-config workflow action |
| Q133 | [`09_content_safety_filters.py`](../09_content_safety_filters.py) | L09 Content Safety severity | Existing |
| Q134 | [`17_evaluator_groundedness.py`](../17_evaluator_groundedness.py) | L17 retry evaluation before return | Existing |
| Q139 | — | Control-plane resource concepts | Gap: multi-service resource exercise |
| Q140 | — | Responsible AI governance | Gap: transparency exercise |
| Q142 | Adjacent only: [`07_managed_identity_agent.py`](../07_managed_identity_agent.py), [`08_rbac_role_policies.py`](../08_rbac_role_policies.py) | L07–08 endpoint/auth boundary | Compatibility: source key flow conflicts with keyless baseline |
| Q166 | [`02_deployment_types.py`](../02_deployment_types.py), [`03_deploy_model.py`](../03_deploy_model.py) | L02–03 regional deployment/version pinning | Existing; partial: L03 hard-codes GlobalStandard and sets no version-upgrade option |
| Q167 | [`11_prompt_shields_docs.py`](../11_prompt_shields_docs.py), [`11_ocr_image_injection_safety.py`](../../03-computer-vision/11_ocr_image_injection_safety.py) | L11 plus D3 L11 indirect injection | Existing |
| Q168 | [`21_foundry_evaluation.py`](../21_foundry_evaluation.py) | L21 evaluation run | Existing; partial: no RAG evaluators configured |
| Q175 | [`01_access_and_metrics_preflight.py`](01_access_and_metrics_preflight.py), [`09_prompt_agent_invoke.py`](../../02-generative-ai-and-agents/09_prompt_agent_invoke.py) | `questions/01_access_and_metrics_preflight.py` plus D2 L09 `agents.get` | Existing |

See the complete, one-row-per-question map in [`../../docs/question-coverage.md`](../../docs/question-coverage.md#01---plan-and-manage).
