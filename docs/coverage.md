# AI-103 Syllabus Coverage Matrix

Cross-check: every syllabus bullet in `../AI-103.md` maps to at least one file
in this repo. Files listed relative to the repo root.

## Domain 1 — Plan and manage an Azure AI solution (25-30%)

### Choose the appropriate Foundry services for generative AI and agents
- Choose an appropriate model for each task (LLM/SLM/multimodal/tools) → `01-plan-and-manage/01_model_catalog_list.py`, `02-generative-ai-and-agents/02_model_behavior.py`, `02-generative-ai-and-agents/03_reasoning.py`
- Choose Foundry services for generative / grounding / vector search / agents / multimodal → `01-plan-and-manage/02_deployment_types.py`, `01-plan-and-manage/04_model_router.py`
- Choose retrieval / indexing method → `05-information-extraction/01_search_basic_query.py`, `05-information-extraction/02_search_vector.py`, `05-information-extraction/03_search_hybrid_semantic.py`
- Choose memory / tool / knowledge integration for agents → `02-generative-ai-and-agents/14_foundry_memory.py`, `02-generative-ai-and-agents/06_file_search_tool.py`

### Set up AI solutions in Foundry
- Design Azure infra → `README.md`, `_shared/config.py`
- Choose deployment options → `01-plan-and-manage/02_deployment_types.py`
- Configure model + agent deployments → `01-plan-and-manage/03_deploy_model.py`, `02-generative-ai-and-agents/08_prompt_agent_create.py`
- CI/CD integration → workflow YAML in `02-generative-ai-and-agents/workflows/`

### Manage, monitor, secure
- Quotas / scaling / rate limits / cost → `01-plan-and-manage/05_quotas_and_tpm.py`, `01-plan-and-manage/06_rate_limit_backoff.py`
- Monitor model performance / drift / safety / grounding → `01-plan-and-manage/11_evaluator_groundedness.py`, `01-plan-and-manage/12_agent_tracing.py` (tokens + latency + safety signals), `02-generative-ai-and-agents/19_evaluator_task_adherence.py`
- Monitor data ingestion / search index health → `05-information-extraction/04_search_indexer_setup.py`
- Security: managed identity / private networking / keyless / RBAC → `01-plan-and-manage/07_managed_identity_agent.py`, `_shared/openai_client.py` (bearer-token pattern), `01-plan-and-manage/13_rbac_role_policies.py` (role assignments)

### Responsible AI
- Safety filters / guardrails / risk detection / moderation → `01-plan-and-manage/08_content_safety_filters.py`, `01-plan-and-manage/09_prompt_shields_user.py`, `01-plan-and-manage/10_prompt_shields_docs.py`
- Evaluators / safety evals / explanation tooling → `01-plan-and-manage/11_evaluator_groundedness.py`, `02-generative-ai-and-agents/19_evaluator_task_adherence.py`
- Trace logging / provenance / approval workflows → `01-plan-and-manage/12_agent_tracing.py`, workflow YAML
- Govern agent behavior (oversight modes / constraints / tool-access) → `02-generative-ai-and-agents/16_workflow_conditional.py`

## Domain 2 — Implement generative AI and agentic solutions (30-35%)

### Build generative apps
- Deploy + consume LLM / SLM / code / multimodal → `02-generative-ai-and-agents/01_first_api_call.py` (LLM), `02-generative-ai-and-agents/03_reasoning.py` (reasoning), `03-computer-vision/01_multimodal_understanding.py`
- Implement RAG → `02-generative-ai-and-agents/06_file_search_tool.py`, `05-information-extraction/07_rag_agent_search_tool.py`, `05-information-extraction/08_rag_client_run.py`
- Workflows / tool-augmented / multistep reasoning → `02-generative-ai-and-agents/04_web_search_tool.py`, `02-generative-ai-and-agents/05_code_interpreter.py`, `02-generative-ai-and-agents/15_workflow_intake.py`, `02-generative-ai-and-agents/16_workflow_conditional.py`
- Evaluate models + apps (fabrication / relevance / quality / safety) → `01-plan-and-manage/11_evaluator_groundedness.py`
- Foundry SDKs + connectors → `_shared/openai_client.py`, `_shared/foundry_client.py`
- Configure app connection to Foundry project → `_shared/config.py`

### Build agents
- Agent roles / goals / conversation tracking / tool schemas → `02-generative-ai-and-agents/08_prompt_agent_create.py`, `02-generative-ai-and-agents/13_conversation_thread.py`
- Retrieval + function-calling + conversation memory → `02-generative-ai-and-agents/11_agent_function_tools.py`, `02-generative-ai-and-agents/14_foundry_memory.py`
- Integrate tools (APIs / KBs / search / CU / custom fns) → `02-generative-ai-and-agents/10_agent_web_search.py`, `02-generative-ai-and-agents/12_agent_openapi_tools.py`, `05-information-extraction/07_rag_agent_search_tool.py`, `05-information-extraction/15_cu_content_agent.py`
- Multi-agent orchestration → `02-generative-ai-and-agents/18_multi_agent_coord.py`
- Autonomous/semi-autonomous + safeguards + approvals → `02-generative-ai-and-agents/16_workflow_conditional.py`
- Monitoring / evaluation / error analysis → `02-generative-ai-and-agents/19_evaluator_task_adherence.py`, `02-generative-ai-and-agents/21_langchain_tracing.py`

### Optimize + operationalize
- Prompt engineering + params → `02-generative-ai-and-agents/02_model_behavior.py`, `02-generative-ai-and-agents/07_structured_output.py`
- Reflection / chain-of-thought / self-critique → `01-plan-and-manage/11_evaluator_groundedness.py`
- Observability (tracing / tokens / safety / latency) → `01-plan-and-manage/12_agent_tracing.py`, `02-generative-ai-and-agents/21_langchain_tracing.py`
- Orchestrate multiple models / hybrid → `02-generative-ai-and-agents/18_multi_agent_coord.py`, `02-generative-ai-and-agents/22_langgraph_agent.py`

## Domain 3 — Implement computer vision solutions (10-15%)

### Image + video generation
- Generate images from text + reference media → `03-computer-vision/02_image_generation.py`
- Generate videos from text + reference media → `03-computer-vision/05_video_generation.py`
- Image editing (inpainting / masks / prompt) → `03-computer-vision/03_image_prompt_edit.py`, `03-computer-vision/04_image_masked_edit.py`
- Edit generated videos → `03-computer-vision/09_video_analysis.py` (segment output feeds edit pipelines)
- Platform generation/editing controls → covered by 02 / 03 / 04

### Multimodal understanding
- Visual context via multimodal model → `03-computer-vision/01_multimodal_understanding.py`
- Concise + detailed captions (single + multi image) → `03-computer-vision/07_alt_text_captions.py`
- Question-answering grounded in visual evidence → `03-computer-vision/01_multimodal_understanding.py`
- Alt-text + extended descriptions → `03-computer-vision/07_alt_text_captions.py`
- Visual characteristics via Content Understanding → `03-computer-vision/08_content_understanding_image.py`
- Video analysis / segment interpretation → `03-computer-vision/09_video_analysis.py`
- Standard + pro-mode CU pipelines → `05-information-extraction/13_cu_pro_mode.py`
- Identify objects / components / regions → `03-computer-vision/08_content_understanding_image.py`

### Responsible AI for multimodal
- Classify unsafe visual content → `03-computer-vision/06_image_moderation.py`, `01-plan-and-manage/08_content_safety_filters.py`
- Indirect prompt injection via embedded text → `01-plan-and-manage/10_prompt_shields_docs.py`
- Watermarks / prohibited symbols / brand rules → `01-plan-and-manage/08_content_safety_filters.py` (Content Safety custom categories)

## Domain 4 — Implement text analysis solutions (10-15%)

### Language model text analysis
- Entities / topics / summaries / structured JSON → `04-text-and-speech/01_llm_ner.py`, `02-generative-ai-and-agents/07_structured_output.py`
- Sentiment / tone / safety / sensitive content → `04-text-and-speech/02_llm_sentiment.py`, `04-text-and-speech/05_language_pii.py`, `01-plan-and-manage/08_content_safety_filters.py`
- Translation (Translator + LLM) → `04-text-and-speech/03_llm_translation.py`, `04-text-and-speech/04_translator_rest.py`
- Domain customization → `04-text-and-speech/10_health_text_analytics.py`

### Speech solutions
- STT + TTS for agentic interactions → `04-text-and-speech/11_stt_fast_file.py`, `04-text-and-speech/12_stt_real_time.py`, `04-text-and-speech/13_stt_batch.py`, `04-text-and-speech/14_tts_neural.py`, `04-text-and-speech/15_tts_ssml_hd.py`
- Speech as an agent modality (incl. custom models) → `04-text-and-speech/18_voice_live_prompt_agent.py`, `04-text-and-speech/17_llm_speech_preview.py`, `04-text-and-speech/19_custom_speech_model.py`
- Multimodal reasoning from audio input → `04-text-and-speech/17_llm_speech_preview.py`, `04-text-and-speech/18_voice_live_prompt_agent.py`
- Translate speech → `04-text-and-speech/16_speech_translation.py`

### Additional Language & MCP
- Azure Language MCP tools + agent use → `04-text-and-speech/08_language_mcp_tools.py`, `04-text-and-speech/09_language_mcp_agent.py`

## Domain 5 — Implement information extraction solutions (10-15%)

### Retrieval + grounding pipelines
- Ingest + index (docs / images / audio / video) → `05-information-extraction/04_search_indexer_setup.py`, `05-information-extraction/14_cu_markdown_for_rag.py`
- Semantic / hybrid / vector search grounding → `05-information-extraction/02_search_vector.py`, `05-information-extraction/03_search_hybrid_semantic.py`
- Enrichment (custom + built-in skills) → `05-information-extraction/05_search_skillset.py`, `05-information-extraction/06_search_custom_skill.py`
- Configure RAG ingestion + OCR → `05-information-extraction/05_search_skillset.py`, `05-information-extraction/09_cu_prebuilt_read.py`
- Connect retrieval to workflows + agent tools → `05-information-extraction/07_rag_agent_search_tool.py`, `05-information-extraction/08_rag_client_run.py`

### Extract content from documents
- Multimodal pipelines (OCR + layout + field extraction) → `05-information-extraction/09_cu_prebuilt_read.py`, `05-information-extraction/10_cu_prebuilt_layout.py`, `05-information-extraction/11_cu_invoice.py`, `05-information-extraction/12_cu_custom_analyzer.py`
- Clean grounded representations for agents + RAG → `05-information-extraction/14_cu_markdown_for_rag.py`
- Analyzers → structured / markdown outputs → `05-information-extraction/10_cu_prebuilt_layout.py`, `05-information-extraction/13_cu_pro_mode.py`, `05-information-extraction/15_cu_content_agent.py`

---

## Coverage summary

| Domain | Bullets in AI-103.md | Files behind them |
|---|---|---|
| 1 — Plan & manage | ~20 | 13 lessons |
| 2 — GenAI + agents | ~18 | 22 lessons |
| 3 — Computer vision | ~12 | 9 lessons |
| 4 — Text + speech | ~12 | 19 lessons |
| 5 — Info extraction | ~10 | 15 lessons |
| **Total** | ~72 bullets | **78 files** |

Every bullet has ≥1 file. Where multiple files cover the same bullet, they
compare approaches (e.g. discriminative vs generative, or manual RAG vs
agent-tool RAG) that the exam explicitly asks about.
