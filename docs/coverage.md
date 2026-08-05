# AI-103 April 2026 coverage

Source: [`AI-103.md`](../AI-103.md), “Skills measured as of April 16, 2026.”
This matrix maps every bullet to code that exists now, not to planned work.

**Labels**

- **Runnable** — numbered Python lesson contains relevant executable behavior.
  It can still require Azure resources, permissions, feature availability, or
  billable usage; this matrix does not claim it was run in your subscription.
- **Local** — executable local/reference behavior only; it does not configure
  or prove the Azure feature.
- **Partial** — runnable evidence covers part of the bullet; limitation stated.
- **Cross-domain** — evidence lives outside the objective’s domain.
- **Gap** — no implementation in this repository covers the required behavior.

## 1. Plan and manage an Azure AI solution (25–30%)

### Choose appropriate Foundry services for generative AI and agents

| April 2026 bullet | Evidence | Status |
|---|---|---|
| Choose appropriate model for each task, including LLMs, small language models, multimodal models, and Foundry Tools | D1 `01_model_catalog_list.py` lists project deployments; `02_deployment_types.py` compares deployment types; D2 `02_model_behavior.py`, `03_reasoning.py`; D3 `01_multimodal_understanding.py` | **Partial** — no dedicated SLM or code-model selection exercise. |
| Choose appropriate Foundry services for generative tasks, grounding, vector search, agent workflows, or multimodal processing | D1 `02_deployment_types.py`, `04_model_router.py`; D2 tools/workflows; D3 multimodal; D5 Search/CU | **Cross-domain / Partial** — selection is study guidance and examples, not a service recommender. |
| Choose appropriate method for retrieval and indexing | D5 `00_search_index_setup.py`, `04_search_indexer_setup.py`, `05_search_skillset.py`, `01_search_basic_query.py`–`03_search_hybrid_semantic.py` | **Runnable** |
| Choose appropriate memory, tool, and knowledge integration services for agent solutions | D2 `06_file_search_tool.py`, `11_agent_function_tools.py`, `14_foundry_memory.py` | **Runnable** — memory is preview. |

### Set up AI solutions in Foundry

| April 2026 bullet | Evidence | Status |
|---|---|---|
| Design Azure infrastructure for AI apps and agent-based solutions | Root README and domain READMEs describe topology, endpoints, roles, and resource paths | **Conceptual** — no infrastructure-as-code or provisioning workflow. |
| Choose appropriate deployment options | D1 `02_deployment_types.py` | **Local** — prints documented comparison; does not query availability. |
| Configure model and agent deployments | D1 `03_deploy_model.py`; D2 `08_prompt_agent_create.py` | **Runnable** — model lesson writes deployment; agent lesson creates version. |
| Integrate Foundry projects with CI/CD pipelines | D1 README release workflow and official Bicep/Terraform/evaluation-pipeline references | **Conceptual / Partial** — teaches a production gate but does not ship a repository CI workflow. |

### Manage, monitor, and secure AI systems

| April 2026 bullet | Evidence | Status |
|---|---|---|
| Manage quotas, scaling, rate limits, and cost footprints for model and agent workloads | D1 `05_quotas_and_tpm.py`, `06_rate_limit_backoff.py`, deployment-type reference | **Partial** — quota inspection and retry only; no autoscaling or billing analysis. |
| Monitor model performance, drift, safety events, and grounding quality | D1 `20_groundedness_detection.py`, `22_foundry_evaluation.py`, `23_continuous_evaluation.py`, `26_foundry_tracing_setup.py` | **Partial** — evaluation/continuous-rule/tracing paths exist; drift policy, alerts, and configured live service remain subscription-dependent. |
| Monitor data ingestion quality, search index health, and relevance performance | D5 `04_search_indexer_setup.py` starts an indexer; D5 `03_search_hybrid_semantic.py` prints query results | **Partial** — no indexer-status, ingestion-quality, or relevance-evaluation monitor. |
| Configure security, including managed identity, private networking, keyless credentials, and role policies | D1 `07_managed_identity_agent.py`, `08_rbac_role_policies.py`; shared keyless clients; D1 README private-network architecture guidance | **Partial** — private-network implementation remains conceptual. |

### Implement responsible AI across generative AI and agentic systems

| April 2026 bullet | Evidence | Status |
|---|---|---|
| Configure safety filters, guardrails, risk detection, and content moderation | D1 `09_content_safety_filters.py`–`15_blocklists.py`, `19_protected_material.py`–`21_provenance_detection.py` | **Runnable / Partial** — advanced features are preview and require service availability; L15 persists only with `--apply`. |
| Apply responsible AI instrumentation, including evaluators, safety evaluations, and explanation tooling | D1 `22_foundry_evaluation.py`, `23_continuous_evaluation.py`, `25_red_teaming.py` | **Runnable / Partial** — cloud state/billing require `--apply`; rubric/evaluator availability is region dependent. |
| Implement auditing through trace logging, provenance metadata, and approval workflows | D1 `18_agent_tracing.py`, `21_provenance_detection.py`, `24_human_feedback.py`, `26_foundry_tracing_setup.py` | **Runnable / Partial** — telemetry/provenance paths exist; approval workflow remains application architecture. |
| Govern agent behavior with oversight modes, constraints, and tool-access controls | D1 `16_agent_basics.py`; D2 `09_prompt_agent_invoke.py`, `11_agent_function_tools.py`, `16_workflow_conditional.py` | **Partial** — instructions, argument validation, and routing; no explicit oversight-mode service configuration. |

## 2. Implement generative AI and agentic solutions (30–35%)

### Build generative applications by using Foundry

| April 2026 bullet | Evidence | Status |
|---|---|---|
| Deploy and consume LLMs, small models, code models, and multimodal models | D1 `03_deploy_model.py`; D2 `01_first_api_call.py`, `03_reasoning.py`; D3 `01_multimodal_understanding.py` | **Partial** — consumes LLM/reasoning/multimodal paths; no dedicated small- or code-model lesson. |
| Implement RAG in an application | D2 `06_file_search_tool.py`; D5 `07_rag_prompt_agent.py`, `08_rag_client_run.py` | **Runnable** — D5 is app-owned manual RAG, not a managed Search agent tool. |
| Design workflows, tool-augmented flows, and multistep reasoning pipelines | D2 `04_web_search_tool.py`, `05_code_interpreter.py`, `11_agent_function_tools.py`, `15_workflow_intake.py`, `16_workflow_conditional.py` | **Runnable** — workflow surface is preview. |
| Evaluate models and apps, including detecting fabrications, relevance, quality, and safety | D1 `17_evaluator_groundedness.py`; D2 `19_evaluator_task_adherence.py` | **Partial** — self-critique and local task-adherence example; no complete fabrication/relevance/safety evaluation suite. |
| Integrate generative workflows into applications by using Foundry SDKs and connectors | `_shared/openai_client.py`, `_shared/foundry_client.py`; D2 lessons 01–18 | **Runnable** |
| Configure an application to connect to a Foundry project | `_shared/config.py`, `_shared/foundry_client.py` | **Runnable** |

### Build agents by using Foundry

| April 2026 bullet | Evidence | Status |
|---|---|---|
| Define agent roles, goals, conversation-tracking approach, and tool schemas | D2 `08_prompt_agent_create.py`, `09_prompt_agent_invoke.py`, `13_conversation_thread.py` | **Runnable** |
| Build agents that integrate retrieval, function-calling, and conversation memory | D2 `06_file_search_tool.py`, `11_agent_function_tools.py`, `14_foundry_memory.py` | **Runnable** — memory is preview and asynchronous. |
| Integrate agent tools, including APIs, knowledge stores, search, content understanding, and custom functions | D2 `10_agent_web_search.py`, `11_agent_function_tools.py`, `12_agent_openapi_tools.py`; D5 `15_cu_content_agent.py` | **Partial** — no documented managed Azure AI Search tool is configured. |
| Implement orchestrated multi-agent solutions | D2 `18_multi_agent_coord.py` | **Runnable** |
| Build autonomous or semiautonomous workflows with safeguards and approval flow controls | D2 `15_workflow_intake.py`, `16_workflow_conditional.py` | **Partial** — conditional preview workflow; no human approval flow. |
| Integrate monitoring into deployed agents, evaluate agent behavior, and perform error analysis | D1 `22_foundry_evaluation.py`–`26_foundry_tracing_setup.py`; D2 `19_evaluator_task_adherence.py`, `21_langchain_tracing.py` | **Partial** — evaluation, feedback, continuous-rule, and tracing setup paths exist; live deployed-agent monitoring remains resource-dependent. |

### Optimize and operationalize generative AI systems

| April 2026 bullet | Evidence | Status |
|---|---|---|
| Tune generation behavior, such as prompt engineering and adjusting model parameters | D2 `02_model_behavior.py`, `07_structured_output.py` | **Runnable** |
| Implement model reflection, chain-of-thought evaluations, and self-critique loops | D1 `17_evaluator_groundedness.py` | **Partial** — self-critique/regeneration; no chain-of-thought evaluation storage or evaluator run. |
| Set up observability by implementing tracing, token analytics, safety signals, and latency breakdowns | D1 `18_agent_tracing.py`, `23_continuous_evaluation.py`, `24_human_feedback.py`, `26_foundry_tracing_setup.py`; D2 `21_langchain_tracing.py` | **Partial** — manual and native-tracing setup paths are taught; live portal telemetry remains resource-dependent. |
| Orchestrate multiple models, flows, or hybrid LLM and rules engines | D2 `18_multi_agent_coord.py`, `22_langgraph_agent.py` | **Runnable** |

## 3. Implement computer vision solutions (10–15%)

### Design and implement image- and video-generation solutions

| April 2026 bullet | Evidence | Status |
|---|---|---|
| Implement a solution that generates images from text prompts and reference media | D3 `02_image_generation.py` | **Partial** — text generation; no reference-media input flow. |
| Implement a solution that generates videos from text prompts and reference media | D3 `05_video_generation.py` | **Partial** — text-to-video only. |
| Configure image-editing workflows, including inpainting, mask-based edits, and prompt-driven modifications | D3 `03_image_prompt_edit.py`, `04_image_masked_edit.py` | **Runnable** |
| Implement workflows to edit generated videos | None; D3 `09_video_analysis.py` only analyzes video segments | **Gap** |
| Select and apply appropriate generation and editing controls provided by platform | None | **Gap** — lessons generate/edit but do not configure platform controls. |

### Design and implement multimodal understanding workflows

| April 2026 bullet | Evidence | Status |
|---|---|---|
| Build a solution that analyzes visual context by using multimodal models | D3 `01_multimodal_understanding.py` | **Runnable** |
| Configure apps to produce concise or detailed captions for single or multiple images | D3 `07_alt_text_captions.py` | **Runnable** |
| Implement a solution that enables question-answering grounded in visual evidence | D3 `01_multimodal_understanding.py` | **Partial** — image summary prompt, not a dedicated visual-Q&A interaction. |
| Configure generation of alt-text and extended image descriptions aligned to accessibility guidelines | D3 `07_alt_text_captions.py` | **Runnable** |
| Implement visual understanding by configuring Azure Content Understanding in Foundry Tools to extract visual characteristics | D3 `08_content_understanding_image.py` | **Runnable** — requires reachable image URL/SAS. |
| Implement video analysis workflows to process and interpret video segments | D3 `09_video_analysis.py` | **Runnable** — prints segment time range and summary. |
| Configure single-task and pro-mode Content Understanding pipelines | D5 CU lessons 09–13 | **Runnable / Cross-domain** — lesson 13 creates a Pro analyzer and submits comma-separated document URLs as multi-input `inputs`; Pro mode remains preview and input-type constrained. |
| Implement solutions that identify objects, components, or regions within images or video | D3 `08_content_understanding_image.py` | **Partial** — prints returned Markdown and `Summary`; no object/component/region extraction contract. |

### Implement responsible AI for multimodal content

| April 2026 bullet | Evidence | Status |
|---|---|---|
| Implement filters to classify unsafe or disallowed visual content | D3 `06_image_moderation.py` | **Runnable** |
| Detect and mitigate indirect prompt injection by using embedded text in images | D1 `11_prompt_shields_docs.py` tests local OCR text | **Partial / Cross-domain** — no image-embedded-text input path. |
| Enforce visual policy rules, such as applying watermarks, flagging prohibited symbols, upholding brand usage requirements, and detecting potentially inappropriate content | D3 `06_image_moderation.py` detects inappropriate image categories | **Partial** — no watermark, symbol, or brand-rule enforcement. |

## 4. Implement text analysis solutions (10–15%)

### Apply language model text analysis

| April 2026 bullet | Evidence | Status |
|---|---|---|
| Implement solutions to extract entities, topics, summaries, and structured JSON outputs by using generative prompting and Foundry Tools | D4 `01_llm_ner.py`; D2 `07_structured_output.py` | **Partial** — entities/topics and strict JSON; no dedicated summary lesson. |
| Configure detection of sentiment, tone, safety issues, and sensitive content | D4 `02_llm_sentiment.py`, `05_language_pii.py`, `20_language_sentiment.py`; D1 `09_content_safety_filters.py` | **Runnable / Cross-domain** |
| Build solutions that translate text by using Azure Translator in Foundry Tools or LLM-powered translation flows | D4 `03_llm_translation.py`, `04_translator_rest.py` | **Runnable** |
| Customize language model outputs for domain tasks, such as compliance summarization and domain extraction | D4 `01_llm_ner.py`, `10_health_text_analytics.py` | **Partial** — domain extraction; no compliance-summarization lesson. |

### Implement speech solutions

| April 2026 bullet | Evidence | Status |
|---|---|---|
| Implement workflows to convert speech to text and text to speech for agentic interactions | D4 `11_stt_fast_file.py`–`15_tts_ssml_hd.py` | **Partial** — STT/TTS calls exist, but no complete agentic turn joining them. |
| Integrate speech as an agent modality, including custom speech models | D4 `18_voice_live_prompt_agent.py`, `19_custom_speech_model.py` | **Partial** — Voice Live demo sends prerecorded audio and logs events only. |
| Enable multimodal reasoning from audio inputs | D4 `17_llm_speech_preview.py`, `18_voice_live_prompt_agent.py` | **Partial** — transcription and Voice Live protocol demo; no explicit audio-reasoning workflow. |
| Translate speech into other languages by using language models and Foundry Tools | D4 `16_speech_translation.py` | **Runnable** |

## 5. Implement information extraction solutions (10–15%)

### Build retrieval and grounding pipelines

| April 2026 bullet | Evidence | Status |
|---|---|---|
| Ingest and index content, such as documents, images, audio, and video | D5 `00_search_index_setup.py`, `04_search_indexer_setup.py`, `05_search_skillset.py` | **Partial** — Blob document pipeline; images/audio/video are not indexed. D3/CU analyzes image/video without indexing them. |
| Configure semantic search, hybrid search, and vector search for grounding | D5 `02_search_vector.py`, `03_search_hybrid_semantic.py` | **Runnable** |
| Implement enrichment by using custom or built-in skills for text, images, and layout | D5 `05_search_skillset.py`, `06_search_custom_skill.py` | **Partial** — built-in split/embedding skillset is deployable; custom skill only runs local Web API contract and is not wired to a skillset; no image/layout enrichment. |
| Configure RAG ingestion flow, including documents and using OCR | D5 Search pipeline plus `09_cu_prebuilt_read.py`, `10_cu_prebuilt_layout.py` | **Partial** — Search skillset splits extracted Blob text; CU performs OCR/layout separately and its output is not fed into indexer. |
| Connect retrieval pipelines directly to workflows and agent tools | D5 `07_rag_prompt_agent.py`, `08_rag_client_run.py` | **Partial** — manual app-owned retrieval injects chunks into prompt; no retrieval workflow or managed Search agent tool. |

### Extract content from documents

| April 2026 bullet | Evidence | Status |
|---|---|---|
| Extract information by using multimodal pipelines that combine OCR, layout analysis, and field extraction | D5 `09_cu_prebuilt_read.py`, `10_cu_prebuilt_layout.py`, `11_cu_invoice.py`, `12_cu_custom_analyzer.py` | **Runnable** — each is a separate CU call; no single composed pipeline. |
| Produce clean, grounded representations to use with agents and RAG by using Content Understanding | D5 `14_cu_markdown_for_rag.py`, `15_cu_content_agent.py` | **Partial** — reads/inspects markdown and sends invoice fields to model; does not index markdown. |
| Implement analyzers for generating structured or markdown outputs for downstream reasoning by using Content Understanding | D5 `10_cu_prebuilt_layout.py`, `12_cu_custom_analyzer.py`, `13_cu_pro_mode.py` | **Runnable** — Pro mode is preview and requires compatible multi-input documents. |

## Inventory summary

| Domain | Numbered lessons present | Notes |
|---|---:|---|
| 1 — Plan and manage | 26 | Sequence is `01`–`26`; advanced Content Safety is `19`–`21`, evaluations `22`–`25`, tracing setup `26`. |
| 2 — Generative AI and agents | 22 | `01`–`22`. |
| 3 — Computer vision | 9 | `01`–`09`. |
| 4 — Text and speech | 20 | `01`–`20`; `20_language_sentiment.py` is included. |
| 5 — Information extraction | 16 | `00`–`15`; `00_search_index_setup.py` is included. |
| **Total** | **93** | Numbered Python lessons only; excludes shared modules, Function assets, tests, and JSON/YAML. |

Gaps and partial labels are intentional. They prevent a local study repository
from claiming implementation of private networking, CI/CD, video editing,
platform generation controls, managed Search agent tools, or other behavior
that its current code does not perform.
