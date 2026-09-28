# Domain 2 question review

## Per-question lesson map

| Question | Lesson file(s) | Coverage note | Status |
|---:|---|---|---|
| Q6 | [`05_code_interpreter.py`](../05_code_interpreter.py), [`06_file_search_tool.py`](../06_file_search_tool.py), [`22_bing_grounding_preflight.py`](../../08-advanced-agents-other/22_bing_grounding_preflight.py) | L05 code interpreter, L06 file search, D8 L22 Grounding with Bing | Existing |
| Q7 | [`12_agent_openapi_tools.py`](../12_agent_openapi_tools.py) | L12 OpenAPI tools | Existing; partial: L12 uses anonymous auth, not an API-key security scheme |
| Q8 | [`16_workflow_conditional.py`](../16_workflow_conditional.py) | L16 conditional workflow | Existing |
| Q12 | [`14_foundry_memory.py`](../14_foundry_memory.py) | L14 Foundry Memory | Existing |
| Q13 | [`27_agent_azure_ai_search_preflight.py`](../27_agent_azure_ai_search_preflight.py), [`40_a2a_authentication.py`](../40_a2a_authentication.py), [`05_gateway_publishing_preflight.py`](../../08-advanced-agents-other/05_gateway_publishing_preflight.py) | L27 forced tool_choice, L40 agent-identity auth, D8 L05 publishing identity | Existing |
| Q16 | [`01_few_shot_response_controls.py`](01_few_shot_response_controls.py), [`27_agent_azure_ai_search_preflight.py`](../27_agent_azure_ai_search_preflight.py) | `questions/01_few_shot_response_controls.py` plus L27 forced tool_choice | Existing |
| Q18 | Adjacent only: [`15_foundry_toolbox_preflight.py`](../../08-advanced-agents-other/15_foundry_toolbox_preflight.py) | D8 L15 project connection inventory | Gap: model-resource connection preflight |
| Q25 | Adjacent only: [`09_prompt_agent_invoke.py`](../09_prompt_agent_invoke.py), [`35_openai_function_calling.py`](../35_openai_function_calling.py) | L09 tool loop, L35 function calling | Gap: parallel tool-execution exercise |
| Q29 | [`06_file_search_tool.py`](../06_file_search_tool.py), [`14_foundry_memory.py`](../14_foundry_memory.py) | L14 memory and L06 File Search | Existing |
| Q33 | Adjacent only: [`16_workflow_conditional.py`](../16_workflow_conditional.py), [`43_af_declarative_workflow.py`](../43_af_declarative_workflow.py), [`44_af_checkpoints.py`](../44_af_checkpoints.py) | L16/L43 workflows, L44 human-in-the-loop checkpoints | Gap: exact visual-builder/Powers Fx variant |
| Q43 | [`43_af_declarative_workflow.py`](../43_af_declarative_workflow.py) | L43 Power Fx expressions in declarative YAML | Existing |
| Q44 | [`13_conversation_thread.py`](../13_conversation_thread.py) | L13 conversation continuity | Existing |
| Q45 | [`13_conversation_thread.py`](../13_conversation_thread.py) | L13 conversation continuity | Existing |
| Q52 | [`06_file_search_tool.py`](../06_file_search_tool.py), [`27_agent_azure_ai_search_preflight.py`](../27_agent_azure_ai_search_preflight.py) | L06 File Search for uploads, L27 Azure AI Search tool for the enterprise index | Existing |
| Q62 | [`13_conversation_thread.py`](../13_conversation_thread.py) | L13 durable conversation state | Existing |
| Q67 | [`12_agent_openapi_tools.py`](../12_agent_openapi_tools.py) | L12 OpenAPI connection auth | Existing; partial: L12 uses anonymous auth, not a connection-backed key |
| Q73 | [`06_file_search_tool.py`](../06_file_search_tool.py), [`14_foundry_memory.py`](../14_foundry_memory.py) | L14 memory and L06 File Search | Existing |
| Q76 | [`05_code_interpreter.py`](../05_code_interpreter.py), [`06_file_search_tool.py`](../06_file_search_tool.py), [`25_computer_use_preflight.py`](../../08-advanced-agents-other/25_computer_use_preflight.py) | L05 code interpreter, L06 file search, D8 L25 computer use | Existing |
| Q79 | [`05_code_interpreter.py`](../05_code_interpreter.py), [`22_bing_grounding_preflight.py`](../../08-advanced-agents-other/22_bing_grounding_preflight.py) | L05 code interpreter, D8 L22 Grounding with Bing | Existing |
| Q82 | [`07_structured_output.py`](../07_structured_output.py), [`32_openai_json_mode.py`](../32_openai_json_mode.py) | L07/L32 strict JSON schema output | Existing |
| Q83 | [`05_code_interpreter.py`](../05_code_interpreter.py), [`06_file_search_tool.py`](../06_file_search_tool.py) | L05–06 uploaded contracts/spreadsheets | Existing |
| Q86 | [`06_file_search_tool.py`](../06_file_search_tool.py), [`22_bing_grounding_preflight.py`](../../08-advanced-agents-other/22_bing_grounding_preflight.py), [`25_computer_use_preflight.py`](../../08-advanced-agents-other/25_computer_use_preflight.py) | D2 L06 file search, L22 Grounding with Bing, L25 computer use | Existing |
| Q93 | [`01_few_shot_response_controls.py`](01_few_shot_response_controls.py), [`03_reasoning.py`](../03_reasoning.py) | `questions/01_few_shot_response_controls.py` plus L03 reasoning effort | Existing |
| Q97 | [`01_few_shot_response_controls.py`](01_few_shot_response_controls.py) | `questions/01_few_shot_response_controls.py` | New |
| Q99 | [`02_model_behavior.py`](../02_model_behavior.py) | L02 temperature | Existing |
| Q102 | [`13_conversation_thread.py`](../13_conversation_thread.py) | L13 multi-session state | Existing |
| Q108 | [`01_few_shot_response_controls.py`](01_few_shot_response_controls.py), [`02_model_behavior.py`](../02_model_behavior.py) | `questions/01_few_shot_response_controls.py` plus L02 temperature | Existing |
| Q109 | Adjacent only: [`15_workflow_intake.py`](../15_workflow_intake.py), [`16_workflow_conditional.py`](../16_workflow_conditional.py), [`44_af_checkpoints.py`](../44_af_checkpoints.py) | L15–16 workflows, L44 human-in-the-loop checkpoints | Gap: visual-builder approval node |
| Q110 | [`01_few_shot_response_controls.py`](01_few_shot_response_controls.py) | `questions/01_few_shot_response_controls.py` | New |
| Q123 | [`14_foundry_memory.py`](../14_foundry_memory.py), [`08_rag_client_run.py`](../../05-information-extraction/08_rag_client_run.py) | L14 persistent memory, D5 L08 retrieval from approved sources | Existing |
| Q131 | [`31_openai_embeddings.py`](../31_openai_embeddings.py), [`02_search_vector.py`](../../05-information-extraction/02_search_vector.py) | L31 embeddings plus D5 vector search | Existing |
| Q153 | [`31_openai_embeddings.py`](../31_openai_embeddings.py), [`02_search_vector.py`](../../05-information-extraction/02_search_vector.py) | L31 semantic-similarity embeddings | Existing |
| Q154 | [`08_prompt_agent_create.py`](../08_prompt_agent_create.py) | L08 system instructions | Existing |
| Q155 | [`01_first_api_call.py`](../01_first_api_call.py) | L01 endpoint, credential, deployment | Existing |
| Q169 | [`08_prompt_agent_create.py`](../08_prompt_agent_create.py) | L08 scoped system instructions | Existing |
| Q174 | [`14_foundry_memory.py`](../14_foundry_memory.py) | L14 cross-session memory | Existing |

The supplement makes no inference call; it only constructs reviewed request fragments. See the complete map in [`../../docs/question-coverage.md`](../../docs/question-coverage.md#02---generative-ai-and-agents).
