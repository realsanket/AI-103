# Practice-question coverage map

This map covers the supplied practice-question PDF. It contains **175**
numbered questions (`Q1` through `Q175`), not 174. Read the questions after
the mapped domain's normal lesson sequence; a question with a second lesson
reference is intentionally cross-domain.

Each domain also has a `questions/` directory. `Existing` means that a lesson
already exercises the concept. `Existing; partial` means the lesson exercises
the service or pattern but not the exact setting the answer names; the text
after `partial:` says what is missing. `New` is a local, no-cloud question
supplement. `Gap` needs current-documentation validation before it can become
a runnable lesson. `Compatibility` is intentionally not a new lab because the
source uses legacy/retired surfaces outside this repository's current-scope rule.

A lesson is linked only when its code demonstrates the answer (or the service
the answer names). Lessons that demonstrate a distractor, such as a
groundedness-only check for a question whose answer is a RAG evaluator, are
not linked.

## Code traceability

Every directly mapped local lesson below now declares its question numbers in a
Practice-question coverage source marker. The Lesson file(s) column links
to that code. Adjacent only deliberately does not change a Gap or
Compatibility result into runnable coverage; it is a nearby lesson to study
while validating the missing or legacy surface. Each domain questions/README.md
repeats the same per-question file map.

## 01 - Plan and manage

| Q | Lesson file(s) | Coverage | Status |
|---:|---|---|---|
| 3 | [`11_prompt_shields_docs.py`](../01-plan-and-manage/11_prompt_shields_docs.py), [`12_spotlighting.py`](../01-plan-and-manage/12_spotlighting.py) | L11–12 Document Prompt Shields and Spotlighting | Existing |
| 5 | [`25_foundry_tracing_setup.py`](../01-plan-and-manage/25_foundry_tracing_setup.py), [`26_agent_tracing.py`](../01-plan-and-manage/26_agent_tracing.py) | L25–26 run tracing | Existing |
| 9 | [`30_evaluation_cicd_preflight.py`](../01-plan-and-manage/30_evaluation_cicd_preflight.py) | L30 evaluation CI/CD gate | Existing |
| 10 | [`25_foundry_tracing_setup.py`](../01-plan-and-manage/25_foundry_tracing_setup.py), [`26_agent_tracing.py`](../01-plan-and-manage/26_agent_tracing.py), [`23_langchain_tracing.py`](../02-generative-ai-and-agents/23_langchain_tracing.py) | L25–26 tracing, D2 L23 telemetry | Existing |
| 17 | [`06_rate_limit_backoff.py`](../01-plan-and-manage/06_rate_limit_backoff.py) | L06 retry with exponential backoff and jitter | Existing |
| 19 | [`30_evaluation_cicd_preflight.py`](../01-plan-and-manage/30_evaluation_cicd_preflight.py), [`19_groundedness_detection.py`](../01-plan-and-manage/19_groundedness_detection.py) | L30 merge gate plus L19 groundedness detection | Existing; partial: L30 gates on coherence, not groundedness |
| 23 | [`01_access_and_metrics_preflight.py`](../01-plan-and-manage/questions/01_access_and_metrics_preflight.py), [`05_diagnostics_preflight.py`](../07-production-platform-other/05_diagnostics_preflight.py) | `questions/01_access_and_metrics_preflight.py` plus D7 L05 RequestResponse diagnostics | Existing |
| 24 | [`25_foundry_tracing_setup.py`](../01-plan-and-manage/25_foundry_tracing_setup.py), [`26_agent_tracing.py`](../01-plan-and-manage/26_agent_tracing.py), [`23_langchain_tracing.py`](../02-generative-ai-and-agents/23_langchain_tracing.py) | L25–26 distributed tracing | Existing |
| 26 | [`19_groundedness_detection.py`](../01-plan-and-manage/19_groundedness_detection.py), [`21_foundry_evaluation.py`](../01-plan-and-manage/21_foundry_evaluation.py), [`22_continuous_evaluation.py`](../01-plan-and-manage/22_continuous_evaluation.py) | L19 groundedness, L21–22 risk and safety evaluation | Existing; partial: no built-in groundedness evaluator configured |
| 34 | [`19_groundedness_detection.py`](../01-plan-and-manage/19_groundedness_detection.py), [`21_foundry_evaluation.py`](../01-plan-and-manage/21_foundry_evaluation.py) | L19 groundedness detection, L21 evaluation run | Existing; partial: no built-in groundedness evaluator configured |
| 40 | [`11_prompt_shields_docs.py`](../01-plan-and-manage/11_prompt_shields_docs.py), [`18_protected_material.py`](../01-plan-and-manage/18_protected_material.py) | L11 and L18 injection versus protected material | Existing |
| 42 | [`11_prompt_shields_docs.py`](../01-plan-and-manage/11_prompt_shields_docs.py), [`12_spotlighting.py`](../01-plan-and-manage/12_spotlighting.py), [`22_bing_grounding_preflight.py`](../08-advanced-agents-other/22_bing_grounding_preflight.py) | L11–12 plus D8 L22 web grounding | Existing |
| 47 | [`26_agent_tracing.py`](../01-plan-and-manage/26_agent_tracing.py) | L26 token diagnostics | Existing |
| 48 | [`08_rbac_role_policies.py`](../01-plan-and-manage/08_rbac_role_policies.py), [`19_blob_identity_paths.py`](../05-information-extraction/19_blob_identity_paths.py) | L08 RBAC and D5 L19 Blob identity | Existing |
| 49 | [`30_evaluation_cicd_preflight.py`](../01-plan-and-manage/30_evaluation_cicd_preflight.py), [`04_cicd_preflight.py`](../07-production-platform-other/04_cicd_preflight.py) | L30 evaluation gate plus D7 L04 OIDC workflow | Existing |
| 53 | [`07_managed_identity_agent.py`](../01-plan-and-manage/07_managed_identity_agent.py), [`01_first_api_call.py`](../02-generative-ai-and-agents/01_first_api_call.py) | L07 identity plus D2 L01 Responses | Existing |
| 56 | [`26_agent_tracing.py`](../01-plan-and-manage/26_agent_tracing.py) | L26 latency and token diagnosis | Existing |
| 58 | [`26_agent_tracing.py`](../01-plan-and-manage/26_agent_tracing.py), [`24_production_observability_preflight.py`](../02-generative-ai-and-agents/24_production_observability_preflight.py) | L26 and D2 L24 latency decomposition | Existing |
| 59 | [`20_provenance_detection.py`](../01-plan-and-manage/20_provenance_detection.py), [`08_rbac_role_policies.py`](../01-plan-and-manage/08_rbac_role_policies.py) | L20 Content Safety identity reads Blob, L08 least-privilege RBAC | Existing |
| 63 | [`09_content_safety_filters.py`](../01-plan-and-manage/09_content_safety_filters.py), [`48_hosted_agent_guardrails.py`](../02-generative-ai-and-agents/48_hosted_agent_guardrails.py), [`20_provenance_detection.py`](../01-plan-and-manage/20_provenance_detection.py) | L09 guardrail block action, D2 L48 agent guardrail, L20 Blob Data Reader identity | Existing; partial: tool-call and tool-response intervention points not configured |
| 64 | [`17_evaluator_groundedness.py`](../01-plan-and-manage/17_evaluator_groundedness.py) | L17 critique and regeneration | Existing |
| 65 | [`10_prompt_shields_user.py`](../01-plan-and-manage/10_prompt_shields_user.py) | L10 User Prompt Shields | Existing |
| 66 | [`21_foundry_evaluation.py`](../01-plan-and-manage/21_foundry_evaluation.py), [`25_foundry_tracing_setup.py`](../01-plan-and-manage/25_foundry_tracing_setup.py), [`26_agent_tracing.py`](../01-plan-and-manage/26_agent_tracing.py) | L21 evaluation and L25–26 observability | Existing; partial: no relevance evaluator configured |
| 68 | [`25_foundry_tracing_setup.py`](../01-plan-and-manage/25_foundry_tracing_setup.py), [`26_agent_tracing.py`](../01-plan-and-manage/26_agent_tracing.py) | L25–26 prompt/output token metrics | Existing |
| 69 | [`17_evaluator_groundedness.py`](../01-plan-and-manage/17_evaluator_groundedness.py), [`19_groundedness_detection.py`](../01-plan-and-manage/19_groundedness_detection.py), [`21_foundry_evaluation.py`](../01-plan-and-manage/21_foundry_evaluation.py) | L17, L19, L21 groundedness handling | Existing |
| 71 | [`07_managed_identity_agent.py`](../01-plan-and-manage/07_managed_identity_agent.py), [`08_rbac_role_policies.py`](../01-plan-and-manage/08_rbac_role_policies.py) | L08 direct Azure OpenAI RBAC | Existing |
| 75 | [`08_rbac_role_policies.py`](../01-plan-and-manage/08_rbac_role_policies.py), [`01_foundry_iq_connection_preflight.py`](../08-advanced-agents-other/01_foundry_iq_connection_preflight.py) | L08 Search Index Data Reader, D8 L01 reader versus contributor | Existing |
| 78 | [`25_foundry_tracing_setup.py`](../01-plan-and-manage/25_foundry_tracing_setup.py), [`26_agent_tracing.py`](../01-plan-and-manage/26_agent_tracing.py) | L25–26 tool latency spans | Existing |
| 80 | [`21_foundry_evaluation.py`](../01-plan-and-manage/21_foundry_evaluation.py), [`22_continuous_evaluation.py`](../01-plan-and-manage/22_continuous_evaluation.py) | L21–22 quality regression | Existing |
| 81 | [`04_model_router.py`](../01-plan-and-manage/04_model_router.py) | L04 Model Router | Existing |
| 85 | [`04_model_router.py`](../01-plan-and-manage/04_model_router.py), [`03_reasoning.py`](../02-generative-ai-and-agents/03_reasoning.py) | L04 small-versus-frontier routing, D2 L03 multi-step reasoning model | Existing; partial: no dedicated LLM-versus-SLM exercise |
| 96 | [`25_foundry_tracing_setup.py`](../01-plan-and-manage/25_foundry_tracing_setup.py), [`26_agent_tracing.py`](../01-plan-and-manage/26_agent_tracing.py) | L25–26 stage latency tracing | Existing |
| 98 | [`17_evaluator_groundedness.py`](../01-plan-and-manage/17_evaluator_groundedness.py) | L17 reflection/regeneration | Existing |
| 100 | [`17_evaluator_groundedness.py`](../01-plan-and-manage/17_evaluator_groundedness.py), [`21_foundry_evaluation.py`](../01-plan-and-manage/21_foundry_evaluation.py) | L17 corrective retry versus L21 evaluation | Existing |
| 101 | [`21_foundry_evaluation.py`](../01-plan-and-manage/21_foundry_evaluation.py), [`30_evaluation_cicd_preflight.py`](../01-plan-and-manage/30_evaluation_cicd_preflight.py) | L30 and L21 RAG CI/CD evaluation | Existing |
| 103 | [`18_protected_material.py`](../01-plan-and-manage/18_protected_material.py), [`19_groundedness_detection.py`](../01-plan-and-manage/19_groundedness_detection.py), [`21_foundry_evaluation.py`](../01-plan-and-manage/21_foundry_evaluation.py) | L18 protected material, L19 groundedness, L21 evaluation | Existing; partial: no relevance evaluator configured |
| 104 | [`21_foundry_evaluation.py`](../01-plan-and-manage/21_foundry_evaluation.py) | L21 evaluation categories | Existing |
| 111 | [`25_foundry_tracing_setup.py`](../01-plan-and-manage/25_foundry_tracing_setup.py), [`26_agent_tracing.py`](../01-plan-and-manage/26_agent_tracing.py) | L25–26 end-to-end traces | Existing |
| 112 | [`25_foundry_tracing_setup.py`](../01-plan-and-manage/25_foundry_tracing_setup.py) | L25 Application Insights setup | Existing |
| 113 | [`01_access_and_metrics_preflight.py`](../01-plan-and-manage/questions/01_access_and_metrics_preflight.py), [`08_rbac_role_policies.py`](../01-plan-and-manage/08_rbac_role_policies.py) | `questions/01_access_and_metrics_preflight.py` plus L08 role assignment | Existing; partial: Key Vault Secrets User role not named |
| 115 | [`25_foundry_tracing_setup.py`](../01-plan-and-manage/25_foundry_tracing_setup.py), [`26_agent_tracing.py`](../01-plan-and-manage/26_agent_tracing.py), [`23_langchain_tracing.py`](../02-generative-ai-and-agents/23_langchain_tracing.py) | L25–26 hierarchical spans, D2 L23 tool-call spans | Existing |
| 125 | [`06_rate_limit_backoff.py`](../01-plan-and-manage/06_rate_limit_backoff.py), [`06_file_search_tool.py`](../02-generative-ai-and-agents/06_file_search_tool.py) | L06 throttling, D2 L06 uploads | Existing |
| 130 | [`30_evaluation_cicd_preflight.py`](../01-plan-and-manage/30_evaluation_cicd_preflight.py) | L30 evaluation YAML CI/CD | Existing; partial: no evaluation-config workflow action |
| 133 | [`09_content_safety_filters.py`](../01-plan-and-manage/09_content_safety_filters.py) | L09 Content Safety severity | Existing |
| 134 | [`17_evaluator_groundedness.py`](../01-plan-and-manage/17_evaluator_groundedness.py) | L17 retry evaluation before return | Existing |
| 139 | — | Control-plane resource concepts | Gap: multi-service resource exercise |
| 140 | — | Responsible AI governance | Gap: transparency exercise |
| 142 | Adjacent only: [`07_managed_identity_agent.py`](../01-plan-and-manage/07_managed_identity_agent.py), [`08_rbac_role_policies.py`](../01-plan-and-manage/08_rbac_role_policies.py) | L07–08 endpoint/auth boundary | Compatibility: source key flow conflicts with keyless baseline |
| 166 | [`02_deployment_types.py`](../01-plan-and-manage/02_deployment_types.py), [`03_deploy_model.py`](../01-plan-and-manage/03_deploy_model.py) | L02–03 regional deployment/version pinning | Existing; partial: L03 hard-codes GlobalStandard and sets no version-upgrade option |
| 167 | [`11_prompt_shields_docs.py`](../01-plan-and-manage/11_prompt_shields_docs.py), [`11_ocr_image_injection_safety.py`](../03-computer-vision/11_ocr_image_injection_safety.py) | L11 plus D3 L11 indirect injection | Existing |
| 168 | [`21_foundry_evaluation.py`](../01-plan-and-manage/21_foundry_evaluation.py) | L21 evaluation run | Existing; partial: no RAG evaluators configured |
| 175 | [`01_access_and_metrics_preflight.py`](../01-plan-and-manage/questions/01_access_and_metrics_preflight.py), [`09_prompt_agent_invoke.py`](../02-generative-ai-and-agents/09_prompt_agent_invoke.py) | `questions/01_access_and_metrics_preflight.py` plus D2 L09 `agents.get` | Existing |

## 02 - Generative AI and agents

| Q | Lesson file(s) | Coverage | Status |
|---:|---|---|---|
| 6 | [`05_code_interpreter.py`](../02-generative-ai-and-agents/05_code_interpreter.py), [`06_file_search_tool.py`](../02-generative-ai-and-agents/06_file_search_tool.py), [`22_bing_grounding_preflight.py`](../08-advanced-agents-other/22_bing_grounding_preflight.py) | L05 code interpreter, L06 file search, D8 L22 Grounding with Bing | Existing |
| 7 | [`12_agent_openapi_tools.py`](../02-generative-ai-and-agents/12_agent_openapi_tools.py) | L12 OpenAPI tools | Existing; partial: L12 uses anonymous auth, not an API-key security scheme |
| 8 | [`16_workflow_conditional.py`](../02-generative-ai-and-agents/16_workflow_conditional.py) | L16 conditional workflow | Existing |
| 12 | [`14_foundry_memory.py`](../02-generative-ai-and-agents/14_foundry_memory.py) | L14 Foundry Memory | Existing |
| 13 | [`27_agent_azure_ai_search_preflight.py`](../02-generative-ai-and-agents/27_agent_azure_ai_search_preflight.py), [`40_a2a_authentication.py`](../02-generative-ai-and-agents/40_a2a_authentication.py), [`05_gateway_publishing_preflight.py`](../08-advanced-agents-other/05_gateway_publishing_preflight.py) | L27 forced tool_choice, L40 agent-identity auth, D8 L05 publishing identity | Existing |
| 16 | [`01_few_shot_response_controls.py`](../02-generative-ai-and-agents/questions/01_few_shot_response_controls.py), [`27_agent_azure_ai_search_preflight.py`](../02-generative-ai-and-agents/27_agent_azure_ai_search_preflight.py) | `questions/01_few_shot_response_controls.py` plus L27 forced tool_choice | Existing |
| 18 | Adjacent only: [`15_foundry_toolbox_preflight.py`](../08-advanced-agents-other/15_foundry_toolbox_preflight.py) | D8 L15 project connection inventory | Gap: model-resource connection preflight |
| 25 | Adjacent only: [`09_prompt_agent_invoke.py`](../02-generative-ai-and-agents/09_prompt_agent_invoke.py), [`35_openai_function_calling.py`](../02-generative-ai-and-agents/35_openai_function_calling.py) | L09 tool loop, L35 function calling | Gap: parallel tool-execution exercise |
| 29 | [`06_file_search_tool.py`](../02-generative-ai-and-agents/06_file_search_tool.py), [`14_foundry_memory.py`](../02-generative-ai-and-agents/14_foundry_memory.py) | L14 memory and L06 File Search | Existing |
| 33 | Adjacent only: [`16_workflow_conditional.py`](../02-generative-ai-and-agents/16_workflow_conditional.py), [`43_af_declarative_workflow.py`](../02-generative-ai-and-agents/43_af_declarative_workflow.py), [`44_af_checkpoints.py`](../02-generative-ai-and-agents/44_af_checkpoints.py) | L16/L43 workflows, L44 human-in-the-loop checkpoints | Gap: exact visual-builder/Powers Fx variant |
| 43 | [`43_af_declarative_workflow.py`](../02-generative-ai-and-agents/43_af_declarative_workflow.py) | L43 Power Fx expressions in declarative YAML | Existing |
| 44 | [`13_conversation_thread.py`](../02-generative-ai-and-agents/13_conversation_thread.py) | L13 conversation continuity | Existing |
| 45 | [`13_conversation_thread.py`](../02-generative-ai-and-agents/13_conversation_thread.py) | L13 conversation continuity | Existing |
| 52 | [`06_file_search_tool.py`](../02-generative-ai-and-agents/06_file_search_tool.py), [`27_agent_azure_ai_search_preflight.py`](../02-generative-ai-and-agents/27_agent_azure_ai_search_preflight.py) | L06 File Search for uploads, L27 Azure AI Search tool for the enterprise index | Existing |
| 62 | [`13_conversation_thread.py`](../02-generative-ai-and-agents/13_conversation_thread.py) | L13 durable conversation state | Existing |
| 67 | [`12_agent_openapi_tools.py`](../02-generative-ai-and-agents/12_agent_openapi_tools.py) | L12 OpenAPI connection auth | Existing; partial: L12 uses anonymous auth, not a connection-backed key |
| 73 | [`06_file_search_tool.py`](../02-generative-ai-and-agents/06_file_search_tool.py), [`14_foundry_memory.py`](../02-generative-ai-and-agents/14_foundry_memory.py) | L14 memory and L06 File Search | Existing |
| 76 | [`05_code_interpreter.py`](../02-generative-ai-and-agents/05_code_interpreter.py), [`06_file_search_tool.py`](../02-generative-ai-and-agents/06_file_search_tool.py), [`25_computer_use_preflight.py`](../08-advanced-agents-other/25_computer_use_preflight.py) | L05 code interpreter, L06 file search, D8 L25 computer use | Existing |
| 79 | [`05_code_interpreter.py`](../02-generative-ai-and-agents/05_code_interpreter.py), [`22_bing_grounding_preflight.py`](../08-advanced-agents-other/22_bing_grounding_preflight.py) | L05 code interpreter, D8 L22 Grounding with Bing | Existing |
| 82 | [`07_structured_output.py`](../02-generative-ai-and-agents/07_structured_output.py), [`32_openai_json_mode.py`](../02-generative-ai-and-agents/32_openai_json_mode.py) | L07/L32 strict JSON schema output | Existing |
| 83 | [`05_code_interpreter.py`](../02-generative-ai-and-agents/05_code_interpreter.py), [`06_file_search_tool.py`](../02-generative-ai-and-agents/06_file_search_tool.py) | L05–06 uploaded contracts/spreadsheets | Existing |
| 86 | [`06_file_search_tool.py`](../02-generative-ai-and-agents/06_file_search_tool.py), [`22_bing_grounding_preflight.py`](../08-advanced-agents-other/22_bing_grounding_preflight.py), [`25_computer_use_preflight.py`](../08-advanced-agents-other/25_computer_use_preflight.py) | D2 L06 file search, L22 Grounding with Bing, L25 computer use | Existing |
| 93 | [`01_few_shot_response_controls.py`](../02-generative-ai-and-agents/questions/01_few_shot_response_controls.py), [`03_reasoning.py`](../02-generative-ai-and-agents/03_reasoning.py) | `questions/01_few_shot_response_controls.py` plus L03 reasoning effort | Existing |
| 97 | [`01_few_shot_response_controls.py`](../02-generative-ai-and-agents/questions/01_few_shot_response_controls.py) | `questions/01_few_shot_response_controls.py` | New |
| 99 | [`02_model_behavior.py`](../02-generative-ai-and-agents/02_model_behavior.py) | L02 temperature | Existing |
| 102 | [`13_conversation_thread.py`](../02-generative-ai-and-agents/13_conversation_thread.py) | L13 multi-session state | Existing |
| 108 | [`01_few_shot_response_controls.py`](../02-generative-ai-and-agents/questions/01_few_shot_response_controls.py), [`02_model_behavior.py`](../02-generative-ai-and-agents/02_model_behavior.py) | `questions/01_few_shot_response_controls.py` plus L02 temperature | Existing |
| 109 | Adjacent only: [`15_workflow_intake.py`](../02-generative-ai-and-agents/15_workflow_intake.py), [`16_workflow_conditional.py`](../02-generative-ai-and-agents/16_workflow_conditional.py), [`44_af_checkpoints.py`](../02-generative-ai-and-agents/44_af_checkpoints.py) | L15–16 workflows, L44 human-in-the-loop checkpoints | Gap: visual-builder approval node |
| 110 | [`01_few_shot_response_controls.py`](../02-generative-ai-and-agents/questions/01_few_shot_response_controls.py) | `questions/01_few_shot_response_controls.py` | New |
| 123 | [`14_foundry_memory.py`](../02-generative-ai-and-agents/14_foundry_memory.py), [`08_rag_client_run.py`](../05-information-extraction/08_rag_client_run.py) | L14 persistent memory, D5 L08 retrieval from approved sources | Existing |
| 131 | [`31_openai_embeddings.py`](../02-generative-ai-and-agents/31_openai_embeddings.py), [`02_search_vector.py`](../05-information-extraction/02_search_vector.py) | L31 embeddings plus D5 vector search | Existing |
| 153 | [`31_openai_embeddings.py`](../02-generative-ai-and-agents/31_openai_embeddings.py), [`02_search_vector.py`](../05-information-extraction/02_search_vector.py) | L31 semantic-similarity embeddings | Existing |
| 154 | [`08_prompt_agent_create.py`](../02-generative-ai-and-agents/08_prompt_agent_create.py) | L08 system instructions | Existing |
| 155 | [`01_first_api_call.py`](../02-generative-ai-and-agents/01_first_api_call.py) | L01 endpoint, credential, deployment | Existing |
| 169 | [`08_prompt_agent_create.py`](../02-generative-ai-and-agents/08_prompt_agent_create.py) | L08 scoped system instructions | Existing |
| 174 | [`14_foundry_memory.py`](../02-generative-ai-and-agents/14_foundry_memory.py) | L14 cross-session memory | Existing |

## 03 - Computer vision

| Q | Lesson file(s) | Coverage | Status |
|---:|---|---|---|
| 11 | [`01_image_edit_fidelity_preflight.py`](../03-computer-vision/questions/01_image_edit_fidelity_preflight.py) | `questions/01_image_edit_fidelity_preflight.py` | New |
| 20 | [`01_image_edit_fidelity_preflight.py`](../03-computer-vision/questions/01_image_edit_fidelity_preflight.py) | `questions/01_image_edit_fidelity_preflight.py` | New current image-edit equivalent |
| 27 | [`06_image_masked_edit.py`](../03-computer-vision/06_image_masked_edit.py) | L06 mask-bounded editing | Existing |
| 30 | [`06_image_masked_edit.py`](../03-computer-vision/06_image_masked_edit.py) | L06 sky replacement with a mask | Existing |
| 32 | [`03_image_moderation.py`](../03-computer-vision/03_image_moderation.py) | L03 image moderation | Existing |
| 37 | [`10_prompt_shields_user.py`](../01-plan-and-manage/10_prompt_shields_user.py), [`11_prompt_shields_docs.py`](../01-plan-and-manage/11_prompt_shields_docs.py), [`11_ocr_image_injection_safety.py`](../03-computer-vision/11_ocr_image_injection_safety.py) | D1 L10 user-prompt shields (No) versus L11 document shields, D3 L11 OCR | Existing |
| 38 | [`11_prompt_shields_docs.py`](../01-plan-and-manage/11_prompt_shields_docs.py), [`03_image_moderation.py`](../03-computer-vision/03_image_moderation.py), [`11_ocr_image_injection_safety.py`](../03-computer-vision/11_ocr_image_injection_safety.py) | D3 L03 image moderation (No) versus D1 L11 document shields, D3 L11 OCR | Existing |
| 39 | [`11_prompt_shields_docs.py`](../01-plan-and-manage/11_prompt_shields_docs.py), [`11_ocr_image_injection_safety.py`](../03-computer-vision/11_ocr_image_injection_safety.py) | L11 OCR injection plus D1 L11–12 | Existing |
| 54 | [`06_image_masked_edit.py`](../03-computer-vision/06_image_masked_edit.py) | L06 remove a logo with a mask | Existing |
| 60 | [`01_image_edit_fidelity_preflight.py`](../03-computer-vision/questions/01_image_edit_fidelity_preflight.py), [`05_image_prompt_edit.py`](../03-computer-vision/05_image_prompt_edit.py) | `questions/01_image_edit_fidelity_preflight.py` plus L05 source-image edit | Existing |
| 72 | [`11_prompt_shields_docs.py`](../01-plan-and-manage/11_prompt_shields_docs.py), [`11_ocr_image_injection_safety.py`](../03-computer-vision/11_ocr_image_injection_safety.py) | L11 OCR content is indirect injection | Existing |
| 95 | [`06_image_masked_edit.py`](../03-computer-vision/06_image_masked_edit.py) | L06 selective object removal | Existing |
| 105 | [`14_video_analysis.py`](../03-computer-vision/14_video_analysis.py), [`12_cu_custom_analyzer.py`](../05-information-extraction/12_cu_custom_analyzer.py) | L14 video segments, D5 L12 `generate` field method | Existing; partial: no video field schema |
| 117 | Adjacent only: [`01_multimodal_understanding.py`](../03-computer-vision/01_multimodal_understanding.py) | L01 visual understanding | Compatibility: legacy Vision Brands result shape |
| 124 | Adjacent only: [`09_video_remix.py`](../03-computer-vision/09_video_remix.py) | L09 video remix | Gap: video inpainting |
| 126 | [`01_multimodal_understanding.py`](../03-computer-vision/01_multimodal_understanding.py) | L01 multimodal content input | Existing |
| 135 | — | Custom Vision defect classifier | Compatibility: legacy Custom Vision |
| 136 | [`16_image_generation_dalle.py`](../03-computer-vision/16_image_generation_dalle.py) | L16 DALL-E generation | Existing; partial: consumes a DALL-E deployment, does not deploy one |
| 143 | — | Custom Vision precision/recall | Compatibility: legacy Custom Vision |
| 148 | — | Custom Vision classifier configuration | Compatibility: legacy Custom Vision |
| 159 | — | Custom Vision defect detector | Compatibility: legacy Custom Vision |
| 164 | — | Vision `imageType` API | Compatibility: legacy Vision API |
| 165 | — | Custom Vision metrics | Compatibility: legacy Custom Vision |
| 173 | [`07_video_generation.py`](../03-computer-vision/07_video_generation.py) | L07 async create and poll (REST equivalent of `videos.create`/`retrieve`) | Existing |

## 04 - Text and speech

| Q | Lesson file(s) | Coverage | Status |
|---:|---|---|---|
| 1 | [`12_stt_real_time.py`](../04-text-and-speech/12_stt_real_time.py) | L12 real-time STT | Existing |
| 50 | [`19_custom_speech_model.py`](../04-text-and-speech/19_custom_speech_model.py) | L19 Custom Speech endpoint | Existing; partial: REST custom-model `project` property not shown |
| 57 | [`01_mixed_language_translation_routing.py`](../04-text-and-speech/questions/01_mixed_language_translation_routing.py) | `questions/01_mixed_language_translation_routing.py` | New |
| 61 | [`19_custom_speech_model.py`](../04-text-and-speech/19_custom_speech_model.py) | L19 Custom Speech lifecycle | Existing; partial: expiry fallback to the base model not shown |
| 91 | [`12_stt_real_time.py`](../04-text-and-speech/12_stt_real_time.py), [`14_tts_neural.py`](../04-text-and-speech/14_tts_neural.py) | L12 and L14 live STT/TTS | Existing |
| 127 | [`05_language_pii.py`](../04-text-and-speech/05_language_pii.py) | L05 PII redaction and entity audit | Existing |
| 128 | [`30_gpt_live_webrtc_preflight.py`](../04-text-and-speech/30_gpt_live_webrtc_preflight.py) | L30 GPT-Live WebRTC | Existing |
| 137 | Adjacent only: [`07_language_ner.py`](../04-text-and-speech/07_language_ner.py) | L07 NER | Gap: custom-NER label quality |
| 138 | [`15_tts_ssml_hd.py`](../04-text-and-speech/15_tts_ssml_hd.py) | L15 SSML pronunciation | Existing; partial: SSML prosody and style, no phoneme element |
| 147 | — | Immersive Reader | Compatibility: outside current lesson scope |
| 150 | [`07_language_ner.py`](../04-text-and-speech/07_language_ner.py) | L07 Named Entity Recognition | Existing |
| 151 | Adjacent only: [`07_language_ner.py`](../04-text-and-speech/07_language_ner.py) | L07 NER | Gap: entity-linking-specific exercise |
| 160 | — | Language container operations | Compatibility: no current lab |
| 161 | — | Multi-service provisioning | Gap: resource-choice exercise |
| 163 | — | On-prem Language container | Compatibility: no new legacy lab |

## 05 - Information extraction

| Q | Lesson file(s) | Coverage | Status |
|---:|---|---|---|
| 2 | [`10_cu_prebuilt_layout.py`](../05-information-extraction/10_cu_prebuilt_layout.py) | L10 CU layout | Existing |
| 4 | [`27_agent_azure_ai_search_preflight.py`](../02-generative-ai-and-agents/27_agent_azure_ai_search_preflight.py), [`20_managed_search_agent_tool.py`](../05-information-extraction/20_managed_search_agent_tool.py) | L20 managed Search tool and D2 L27 | Existing |
| 14 | [`24_agentic_knowledge_base.py`](../05-information-extraction/24_agentic_knowledge_base.py), [`25_agentic_retrieve.py`](../05-information-extraction/25_agentic_retrieve.py), [`26_agentic_answer_synthesis.py`](../05-information-extraction/26_agentic_answer_synthesis.py) | L24–26 agentic retrieval | Existing |
| 15 | Adjacent only: [`12_cu_custom_analyzer.py`](../05-information-extraction/12_cu_custom_analyzer.py), [`04_id_document.py`](../09-current-ai-services-other/04_id_document.py) | D5 L12 custom field schema, D9 L04 ID fields | Gap: validate `prebuilt-documentFieldSchema` before code |
| 21 | [`01_rag_ingestion_contract.py`](../05-information-extraction/questions/01_rag_ingestion_contract.py), [`14_cu_markdown_for_rag.py`](../05-information-extraction/14_cu_markdown_for_rag.py) | `questions/01_rag_ingestion_contract.py` plus L14 structure-aware chunks | Existing |
| 28 | [`20_managed_search_agent_tool.py`](../05-information-extraction/20_managed_search_agent_tool.py) | L20 Search tool index selection | Existing |
| 31 | [`27_agent_azure_ai_search_preflight.py`](../02-generative-ai-and-agents/27_agent_azure_ai_search_preflight.py), [`20_managed_search_agent_tool.py`](../05-information-extraction/20_managed_search_agent_tool.py) | L20 Search connection | Existing |
| 35 | [`08_rag_client_run.py`](../05-information-extraction/08_rag_client_run.py) | L08 manual RAG completeness | Existing |
| 36 | [`11_cu_invoice.py`](../05-information-extraction/11_cu_invoice.py), [`13_cu_pro_mode.py`](../05-information-extraction/13_cu_pro_mode.py) | L11/L13 CU standard versus Pro | Existing |
| 41 | [`12_cu_custom_analyzer.py`](../05-information-extraction/12_cu_custom_analyzer.py) | L12 custom analyzer | Existing |
| 46 | [`11_cu_invoice.py`](../05-information-extraction/11_cu_invoice.py), [`13_cu_pro_mode.py`](../05-information-extraction/13_cu_pro_mode.py) | L11/L13 CU standard versus Pro | Existing |
| 55 | [`09_cu_prebuilt_read.py`](../05-information-extraction/09_cu_prebuilt_read.py) | L09 CU OCR | Existing |
| 84 | [`10_cu_prebuilt_layout.py`](../05-information-extraction/10_cu_prebuilt_layout.py), [`14_cu_markdown_for_rag.py`](../05-information-extraction/14_cu_markdown_for_rag.py) | L10/L14 layout Markdown RAG | Existing |
| 87 | Adjacent only: [`12_cu_custom_analyzer.py`](../05-information-extraction/12_cu_custom_analyzer.py) | L12 custom analyzer fields | Gap: `estimateFieldSourceAndConfidence` exercise |
| 88 | [`07_rag_prompt_agent.py`](../05-information-extraction/07_rag_prompt_agent.py), [`08_rag_client_run.py`](../05-information-extraction/08_rag_client_run.py) | L07–08 retrieval-context control | Existing |
| 90 | [`09_cu_prebuilt_read.py`](../05-information-extraction/09_cu_prebuilt_read.py), [`11_cu_invoice.py`](../05-information-extraction/11_cu_invoice.py) | L09–11 CU invoice pipeline | Existing |
| 92 | [`12_cu_custom_analyzer.py`](../05-information-extraction/12_cu_custom_analyzer.py) | L12 custom CU analyzer | Existing |
| 94 | Adjacent only: [`04_search_indexer_setup.py`](../05-information-extraction/04_search_indexer_setup.py), [`05_search_skillset.py`](../05-information-extraction/05_search_skillset.py) | L04–05 indexer and skillset | Gap: `normalized_images` OCR-skill exercise |
| 114 | Adjacent only: [`14_cu_markdown_for_rag.py`](../05-information-extraction/14_cu_markdown_for_rag.py), [`16_cu_multimodal_rag.py`](../05-information-extraction/16_cu_multimodal_rag.py) | L14 layout Markdown for RAG, L16 multimodal RAG records | Gap: validate `prebuilt-documentSearch` before code |
| 116 | [`31_openai_embeddings.py`](../02-generative-ai-and-agents/31_openai_embeddings.py), [`02_search_vector.py`](../05-information-extraction/02_search_vector.py) | L02 vector search and D2 L31 | Existing |
| 118 | [`03_search_hybrid_semantic.py`](../05-information-extraction/03_search_hybrid_semantic.py) | L03 hybrid/semantic retrieval | Existing |
| 120 | [`16_cu_multimodal_rag.py`](../05-information-extraction/16_cu_multimodal_rag.py) | L16 multimodal RAG | Existing; partial: CU is not configured as a Search skill |
| 121 | Adjacent only: [`05_search_skillset.py`](../05-information-extraction/05_search_skillset.py) | L05 skillset | Gap: OCR skill for scanned images |
| 122 | [`13_cu_pro_mode.py`](../05-information-extraction/13_cu_pro_mode.py) | L13 CU Pro Mode | Existing |
| 141 | Adjacent only: [`04_search_indexer_setup.py`](../05-information-extraction/04_search_indexer_setup.py), [`05_search_skillset.py`](../05-information-extraction/05_search_skillset.py), [`06_search_custom_skill.py`](../05-information-extraction/06_search_custom_skill.py) | L04–06 Search enrichment | Gap: knowledge-store projections |
| 144 | [`28_sharepoint_indexer_acls_preflight.py`](../05-information-extraction/28_sharepoint_indexer_acls_preflight.py) | L28 ACL/security trimming | Existing |
| 145 | Adjacent only: [`18_search_monitoring.py`](../05-information-extraction/18_search_monitoring.py) | L18 monitoring | Gap: query-key rotation runbook |
| 146 | [`16_cu_multimodal_rag.py`](../05-information-extraction/16_cu_multimodal_rag.py) | L16 multimodal RAG | Existing; partial: duplicate of Q120; CU is not configured as a Search skill |
| 170 | [`11_cu_invoice.py`](../05-information-extraction/11_cu_invoice.py), [`15_cu_content_agent.py`](../05-information-extraction/15_cu_content_agent.py) | L11/L15 invoice review | Existing |
| 171 | [`05_search_skillset.py`](../05-information-extraction/05_search_skillset.py) | L05 split-and-embed skillset | Existing |
| 172 | [`04_search_indexer_setup.py`](../05-information-extraction/04_search_indexer_setup.py), [`05_search_skillset.py`](../05-information-extraction/05_search_skillset.py), [`20_managed_search_agent_tool.py`](../05-information-extraction/20_managed_search_agent_tool.py) | L04–05/L20 Search RAG | Existing |

## 06 - Model customization and delivery

| Q | Lesson file(s) | Coverage | Status |
|---:|---|---|---|
| 107 | [`18_protected_material.py`](../01-plan-and-manage/18_protected_material.py), [`21_foundry_evaluation.py`](../01-plan-and-manage/21_foundry_evaluation.py), [`05_submit_training.py`](../06-model-customization-other/05_submit_training.py) | L05 validated fine-tuning submission plus D1 L18/L21 safety evaluation | Existing; partial: fine-tuning RAI data checks not shown |
| 132 | [`14_foundry_models_list.py`](../06-model-customization-other/14_foundry_models_list.py), [`18_huggingface_models_preflight.py`](../06-model-customization-other/18_huggingface_models_preflight.py) | L14 catalog, L18 serverless endpoints | Existing; partial: vCPU quota and key auth not shown |
| 152 | [`14_foundry_models_list.py`](../06-model-customization-other/14_foundry_models_list.py), [`18_huggingface_models_preflight.py`](../06-model-customization-other/18_huggingface_models_preflight.py) | L14 catalog, L18 serverless endpoints | Existing; partial: leaderboards and model cards not shown |

## 07 - Production platform

| Q | Lesson file(s) | Coverage | Status |
|---:|---|---|---|
| 70 | [`01_security_operations_preflight.py`](../07-production-platform-other/questions/01_security_operations_preflight.py) | `questions/01_security_operations_preflight.py` | New |
| 89 | [`04_cicd_preflight.py`](../07-production-platform-other/04_cicd_preflight.py) | L04 CI/CD OIDC | Existing |
| 119 | Adjacent only: [`01_bicep_preflight.py`](../07-production-platform-other/01_bicep_preflight.py) | L01 Key Vault CMK infrastructure | Gap: Key Vault project-connection Bicep |
| 129 | [`01_bicep_preflight.py`](../07-production-platform-other/01_bicep_preflight.py) | L01 customer-managed keys | Existing; partial: Bicep CMK, not the az CLI flag |
| 156 | Adjacent only: [`01_bicep_preflight.py`](../07-production-platform-other/01_bicep_preflight.py), [`07_network_perimeter_preflight.py`](../07-production-platform-other/07_network_perimeter_preflight.py) | L01/L07 private networking | Gap: service-endpoint mechanics |
| 157 | Adjacent only: [`01_bicep_preflight.py`](../07-production-platform-other/01_bicep_preflight.py), [`07_network_perimeter_preflight.py`](../07-production-platform-other/07_network_perimeter_preflight.py) | L01/L07 public-access boundary | Gap: service-endpoint mechanics |

## 08 - Advanced agents

| Q | Lesson file(s) | Coverage | Status |
|---:|---|---|---|
| 22 | [`05_code_interpreter.py`](../02-generative-ai-and-agents/05_code_interpreter.py), [`25_computer_use_preflight.py`](../08-advanced-agents-other/25_computer_use_preflight.py) | L25 Computer Use plus D2 L05 | Existing |
| 77 | [`09_mcp_get_started.py`](../08-advanced-agents-other/09_mcp_get_started.py), [`27_agent_azure_ai_search_preflight.py`](../02-generative-ai-and-agents/27_agent_azure_ai_search_preflight.py) | L09 MCP tool, D2 L27 forced tool_choice | Existing; partial: tool_choice does not target the MCP tool type |
| 106 | Adjacent only: [`22_bing_grounding_preflight.py`](../08-advanced-agents-other/22_bing_grounding_preflight.py) | L22 Bing grounding | Gap: verify current forced-tool payload |
| 149 | [`09_mcp_get_started.py`](../08-advanced-agents-other/09_mcp_get_started.py), [`25_mcp_tool_preflight.py`](../02-generative-ai-and-agents/25_mcp_tool_preflight.py), [`27_agent_azure_ai_search_preflight.py`](../02-generative-ai-and-agents/27_agent_azure_ai_search_preflight.py) | L09 MCP tool, D2 L25 MCP agent, D2 L27 forced tool_choice | Existing |

## 09 - Document Intelligence

| Q | Lesson file(s) | Coverage | Status |
|---:|---|---|---|
| 51 | [`02_layout_markdown_tables.py`](../09-current-ai-services-other/02_layout_markdown_tables.py) | L02 Layout Markdown and tables | Existing |
| 74 | [`02_layout_markdown_tables.py`](../09-current-ai-services-other/02_layout_markdown_tables.py) | L02 Layout Markdown and tables | Existing |
| 158 | [`20_language_sentiment.py`](../04-text-and-speech/20_language_sentiment.py), [`01_read_ocr.py`](../09-current-ai-services-other/01_read_ocr.py) | L01 Read OCR plus D4 L20 sentiment | Existing |
| 162 | [`01_read_ocr.py`](../09-current-ai-services-other/01_read_ocr.py) | L01 DI Read OCR | Existing current equivalent to legacy Vision Read |

## Study rules

1. Run the mapped lesson's preflight before any `--apply` or `--run` path.
2. Use the question supplement only to understand a request or design contract; it does not prove cloud authorization or feature availability.
3. Treat `Gap` rows as documentation work, not successful feature coverage.
4. Treat `Compatibility` rows as exam-history review. Do not add a retired API as a new runnable lab.
