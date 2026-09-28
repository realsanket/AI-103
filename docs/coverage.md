# AI-103 April 2026 coverage

Source: [`AI-103.md`](../AI-103.md), “Skills measured as of April 16, 2026.”
This matrix maps every exam bullet to code that exists now, not to planned
work. Supplemental Domains 6, 8, and 9 are documented after the exam-objective
matrix.

**Labels**

- **Runnable** — numbered Python lesson contains relevant executable behavior.
  It can still require Azure resources, permissions, feature availability, or
  billable usage; this matrix does not claim it was run in your subscription.
- **Preflight** — default command validates local configuration or static assets
  only; it makes no Azure request.
- **Opt-in** — an explicit remote-request or mutation path exists, but this
  repository does not provide evidence that its remote operation was run
  successfully.
- **Local** — executable local/reference behavior only; it does not configure
  or prove the Azure feature.
- **Partial** — runnable evidence covers part of the bullet; limitation stated.
- **Cross-domain** — evidence lives outside the objective’s domain.
- **Gap** — no implementation in this repository covers the required behavior.

## 1. Plan and manage an Azure AI solution (25–30%)

### Choose appropriate Foundry services for generative AI and agents

| April 2026 bullet | Evidence | Status |
|---|---|---|
| Choose appropriate model for each task, including LLMs, small language models, multimodal models, and Foundry Tools | D1 `01_model_catalog_list.py` lists project deployments; `02_deployment_types.py` compares deployment types; `36_solution_planning_choices.py` maps requirements to LLM, SLM, reasoning, multimodal, embedding, image-generation, or Foundry Tool choices; D2 `02_model_behavior.py`, `03_reasoning.py`; D3 `01_multimodal_understanding.py` | **Partial / Local** — L36 is local decision logic; no SLM or code model is deployed or called. |
| Choose appropriate Foundry services for generative tasks, grounding, vector search, agent workflows, or multimodal processing | D1 `02_deployment_types.py`, `04_model_router.py`, `36_solution_planning_choices.py` (Foundry resource versus single-service resource, ARM `PUT` body); D2 tools/workflows; D3 multimodal; D5 Search/CU | **Cross-domain / Partial / Local** — selection is study guidance and local examples, not a service recommender. |
| Choose appropriate method for retrieval and indexing | D5 `00_search_index_setup.py`, `04_search_indexer_setup.py`, `05_search_skillset.py`, `01_search_basic_query.py`–`03_search_hybrid_semantic.py` | **Runnable** |
| Choose appropriate memory, tool, and knowledge integration services for agent solutions | D2 `06_file_search_tool.py`, `11_agent_function_tools.py`, `14_foundry_memory.py` | **Runnable** — memory is preview. |

### Set up AI solutions in Foundry

| April 2026 bullet | Evidence | Status |
|---|---|---|
| Design Azure infrastructure for AI apps and agent-based solutions | D7 `07-production-platform-other`: current Bicep and Terraform regional-cell assets, VNet/private DNS/private endpoints, managed identity, Key Vault CMK, diagnostics, locks, policy, and explicit plan/apply wrappers; L11 `connections.bicep` (Key Vault and keyless model-resource connections) and `selected-networks.bicep` (VNet rules plus service endpoint) | **Preflight / Opt-in** — assets are locally tested (`bicep build`, `terraform validate`); Azure deployment and region capability remain subscription-dependent. |
| Choose appropriate deployment options | D1 `02_deployment_types.py` | **Local** — prints documented comparison; does not query availability. |
| Configure model and agent deployments | D1 `03_deploy_model.py` (SKU, capacity, version-upgrade policy); D2 `08_prompt_agent_create.py` | **Preflight / Opt-in** — model lesson prints the ARM body by default and writes the deployment only with `--apply`; agent lesson creates a version. |
| Integrate Foundry projects with CI/CD pipelines | D7 contained GitHub OIDC/self-hosted-private-runner workflow plus explicit Bicep `what-if`/Terraform `plan` and `--apply` gate; D1 `30_evaluation_cicd_preflight.py` (agent-evaluation GitHub Action workflow) and `35_rag_quality_gate.py` (non-zero exit blocks a merge) | **Local / Preflight / Opt-in** — workflows are intentionally not active and require OIDC, runner, state backend, and environment review; L35 calls judge models only with `--apply`. |

### Manage, monitor, and secure AI systems

| April 2026 bullet | Evidence | Status |
|---|---|---|
| Manage quotas, scaling, rate limits, and cost footprints for model and agent workloads | D1 `05_quotas_and_tpm.py`, `06_rate_limit_backoff.py`, deployment-type reference | **Partial** — quota inspection and retry only; no autoscaling or billing analysis. |
| Monitor model performance, drift, safety events, and grounding quality | D1 `19_groundedness_detection.py`, `21_foundry_evaluation.py`, `22_continuous_evaluation.py`, `25_foundry_tracing_setup.py`, `35_rag_quality_gate.py` | **Partial** — evaluation/continuous-rule/tracing paths exist and L35 gates groundedness and relevance pass rates with `--apply`; drift policy, alerts, and configured live service remain subscription-dependent. |
| Monitor data ingestion quality, search index health, and relevance performance | D5 `04_search_indexer_setup.py` starts an indexer; D5 `03_search_hybrid_semantic.py` prints query results | **Partial** — no indexer-status, ingestion-quality, or relevance-evaluation monitor. |
| Configure security, including managed identity, private networking, keyless credentials, and role policies | D1 `07_managed_identity_agent.py`, `08_rbac_role_policies.py`; D7 private regional-cell IaC, user-assigned identity, disabled local auth/public access, private DNS/endpoints, CMK Key Vault role, and reviewed Policy asset; D7 L11 managed-identity Key Vault connection, VNet rules with service endpoints, and CMK CLI sequence | **Preflight / Opt-in / Partial** — local assets do not prove subscription RBAC, private DNS resolution, CMK support, or a successful deployment. |

### Implement responsible AI across generative AI and agentic systems

| April 2026 bullet | Evidence | Status |
|---|---|---|
| Configure safety filters, guardrails, risk detection, and content moderation | D1 `09_content_safety_filters.py`–`15_blocklists.py`, `18_protected_material.py`–`20_provenance_detection.py`, `28_guardrail_policy_preflight.py` | **Runnable / Partial** — advanced features are preview and require service availability; L15 persists only with `--apply`. L28 builds a guardrail with controls at all four intervention points (tool call/response are preview) and creates it only with `--apply`. |
| Apply responsible AI instrumentation, including evaluators, safety evaluations, and explanation tooling | D1 `21_foundry_evaluation.py`, `22_continuous_evaluation.py`, `24_red_teaming.py` | **Runnable / Partial** — cloud state/billing require `--apply`; rubric/evaluator availability is region dependent. |
| Implement auditing through trace logging, provenance metadata, and approval workflows | D1 `26_agent_tracing.py`, `20_provenance_detection.py`, `23_human_feedback.py`, `25_foundry_tracing_setup.py`; D2 `50_af_approval_workflow.py` | **Runnable / Local / Partial** — telemetry/provenance paths exist; D2 L50 runs a local declarative workflow that pauses for a human approval answer. No hosted approval flow or audit store is live-tested. |
| Govern agent behavior with oversight modes, constraints, and tool-access controls | D1 `16_agent_basics.py`; D2 `09_prompt_agent_invoke.py`, `11_agent_function_tools.py`, `16_workflow_conditional.py` | **Partial** — instructions, argument validation, and routing; no explicit oversight-mode service configuration. |

## 2. Implement generative AI and agentic solutions (30–35%)

### Build generative applications by using Foundry

| April 2026 bullet | Evidence | Status |
|---|---|---|
| Deploy and consume LLMs, small models, code models, and multimodal models | D1 `03_deploy_model.py`; D2 `01_first_api_call.py`, `03_reasoning.py`; D3 `01_multimodal_understanding.py` | **Partial** — consumes LLM/reasoning/multimodal paths; no dedicated small- or code-model lesson. |
| Implement RAG in an application | D2 `06_file_search_tool.py`; D5 `07_rag_prompt_agent.py`, `08_rag_client_run.py` | **Runnable** — D5 is app-owned manual RAG; D2 `27_agent_azure_ai_search_preflight.py` is separate **Preflight / Opt-in**, not live-tested managed Search integration. |
| Design workflows, tool-augmented flows, and multistep reasoning pipelines | D2 `04_web_search_tool.py`, `05_code_interpreter.py`, `11_agent_function_tools.py`, `15_workflow_intake.py`, `16_workflow_conditional.py`, `43_af_declarative_workflow.py`, `50_af_approval_workflow.py`, `51_parallel_tool_calls.py` | **Runnable / Local / Partial** — tool paths execute; L43/L50 run declarative workflows locally and L51 times parallel versus sequential tool execution locally (its model path is `--apply`). The Foundry workflow surface is preview and does not prove production orchestration. |
| Evaluate models and apps, including detecting fabrications, relevance, quality, and safety | D1 `17_evaluator_groundedness.py`, `35_rag_quality_gate.py`; D2 `21_evaluator_task_adherence.py`; D2 `22_cloud_evaluation.py` | **Partial / Opt-in** — L21 is one local in-memory evaluator trace. L22 is **Preflight / Opt-in** for durable cloud evaluation, not a completed cloud run. D1 L35 runs groundedness, relevance, retrieval, and response-completeness evaluators only with `--apply`; no evaluation run is evidenced and safety evaluators live in D1 L21–L24. |
| Integrate generative workflows into applications by using Foundry SDKs and connectors | `_shared/openai_client.py`, `_shared/foundry_client.py`; D2 lessons 01–18 | **Runnable** |
| Configure an application to connect to a Foundry project | `_shared/config.py`, `_shared/foundry_client.py` | **Runnable** |

### Build agents by using Foundry

| April 2026 bullet | Evidence | Status |
|---|---|---|
| Define agent roles, goals, conversation-tracking approach, and tool schemas | D2 `08_prompt_agent_create.py`, `09_prompt_agent_invoke.py`, `13_conversation_thread.py` | **Runnable** |
| Build agents that integrate retrieval, function-calling, and conversation memory | D2 `06_file_search_tool.py`, `11_agent_function_tools.py`, `14_foundry_memory.py` | **Runnable** — memory is preview and asynchronous. |
| Integrate agent tools, including APIs, knowledge stores, search, content understanding, and custom functions | D2 `10_agent_web_search.py`, `11_agent_function_tools.py`, `12_agent_openapi_tools.py`; D2 `25_mcp_tool_preflight.py`–`27_agent_azure_ai_search_preflight.py`; D5 `15_cu_content_agent.py` | **Partial** — L25–L27 default to **Preflight**; their `--apply`/`--invoke` paths are **Opt-in** and not live-tested. Toolbox publication and local Agent Framework consumption are implemented but require a configured version; MCP server deployment and managed Search-agent integration are not proven by default. |
| Implement orchestrated multi-agent solutions | D2 `18_multi_agent_coord.py` | **Runnable** |
| Build autonomous or semiautonomous workflows with safeguards and approval flow controls | D2 `15_workflow_intake.py`, `16_workflow_conditional.py`, `25_mcp_tool_preflight.py`, `50_af_approval_workflow.py` | **Partial / Local** — conditional preview workflow; L25 has approval code only in **Opt-in** remote path; L50 pauses a local declarative workflow at a `Question` checkpoint and resumes with the approver's answer. No hosted human approval flow is live-tested. |
| Integrate monitoring into deployed agents, evaluate agent behavior, and perform error analysis | D1 `21_foundry_evaluation.py`–`26_agent_tracing.py`; D2 `21_evaluator_task_adherence.py`, `23_langchain_tracing.py`, `22_cloud_evaluation.py`, `24_production_observability_preflight.py`; D8 `28_cross_domain_observability.py` | **Partial** — local/opt-in evaluation and tracing paths exist, and D8 adds a read-only non-content health query. No deployed-agent monitoring or cloud evaluation run is live-tested. |

### Optimize and operationalize generative AI systems

| April 2026 bullet | Evidence | Status |
|---|---|---|
| Tune generation behavior, such as prompt engineering and adjusting model parameters | D2 `02_model_behavior.py`, `07_structured_output.py` | **Runnable** |
| Implement model reflection, chain-of-thought evaluations, and self-critique loops | D1 `17_evaluator_groundedness.py`; D2 `21_evaluator_task_adherence.py`, `22_cloud_evaluation.py` | **Partial** — self-critique/local evaluator example; no chain-of-thought storage. L22's durable evaluator is **Preflight / Opt-in**, not a completed run. |
| Set up observability by implementing tracing, token analytics, safety signals, and latency breakdowns | D1 `22_continuous_evaluation.py`, `23_human_feedback.py`, `25_foundry_tracing_setup.py`, `26_agent_tracing.py`, `35_rag_quality_gate.py` (completion-token budget report); D2 `23_langchain_tracing.py`, `24_production_observability_preflight.py`; D8 `28_cross_domain_observability.py` | **Partial** — tracing, local token analytics over recorded usage, and a read-only non-content health query are implemented, but no live portal telemetry, alerts, or production retention setup is tested. |
| Orchestrate multiple models, flows, or hybrid LLM and rules engines | D2 `18_multi_agent_coord.py`, `20_langgraph_agent.py`; D2 `28_hosted_agent_responses.py`–`30_hosted_agent_cicd.py` | **Runnable / Partial** — L18/L20 provide application-local orchestration. L28–L30 are **Local / Preflight** hosted-agent contract, A2A-boundary, and CI/CD reference assets; hosted deployment is not live-tested, while D8 L03 covers the current opt-in A2A card path. |

## 3. Implement computer vision solutions (10–15%)

Evidence below inventories source code and local checks, not successful remote
execution. A **Runnable** lesson can require configured Azure access; an
**Opt-in** path has no live-success claim.

### Design and implement image- and video-generation solutions

| April 2026 bullet | Evidence | Status |
|---|---|---|
| Implement a solution that generates images from text prompts and reference media | D3 `04_image_generation.py`, `05_image_prompt_edit.py`, `16_image_model_deployment.py` | **Partial** — text-to-image (L04) and image-input edits (L05) exist; L16 deploys a GPT-image model only with `--apply`. No separate multi-reference composition flow. |
| Implement a solution that generates videos from text prompts and reference media | D3 `07_video_generation.py`, `08_reference_media_preflight.py` | **Preflight / Opt-in** — L07 previews by default and, with `--apply`, runs Sora 2 `videos.create` → `videos.retrieve` → `download_content`; L08 validates one reference image and submits only with `--apply`. No successful remote run is evidenced. |
| Configure image-editing workflows, including inpainting, mask-based edits, and prompt-driven modifications | D3 `05_image_prompt_edit.py`, `06_image_masked_edit.py` | **Runnable** |
| Implement workflows to edit generated videos | D3 `09_video_remix.py` | **Preflight / Opt-in / Partial** — default is local guidance; `--apply` has one fixed-prompt remix path for completed `video_` IDs, not a general video editor or a live-tested workflow. |
| Select and apply appropriate generation and editing controls provided by platform | D3 `04_image_generation.py`–`07_video_generation.py`, `08_reference_media_preflight.py` | **Partial** — code fixes image size/quality/output format and video dimensions/duration; reference-media dimensions are locally checked only on opt-in apply. It does not expose or evaluate broader platform controls. |

### Design and implement multimodal understanding workflows

| April 2026 bullet | Evidence | Status |
|---|---|---|
| Build a solution that analyzes visual context by using multimodal models | D3 `01_multimodal_understanding.py` | **Runnable** |
| Configure apps to produce concise or detailed captions for single or multiple images | D3 `02_alt_text_captions.py` | **Runnable** |
| Implement a solution that enables question-answering grounded in visual evidence | D3 `01_multimodal_understanding.py` | **Partial** — image summary prompt, not a dedicated visual-Q&A interaction. |
| Configure generation of alt-text and extended image descriptions aligned to accessibility guidelines | D3 `02_alt_text_captions.py` | **Runnable** |
| Implement visual understanding by configuring Azure Content Understanding in Foundry Tools to extract visual characteristics | D3 `13_content_understanding_image.py`, `12_cu_blob_preflight.py`, `15_cu_visual_handoff.py`, `17_cu_custom_video_analyzer.py` | **Runnable / Local / Preflight / Opt-in** — L13 has CU image-analysis code; L12 is local SAS/configuration inspection; L15 bounds a CU result only with `--apply`; L17 validates a custom video field schema locally and creates the analyzer only with `--apply`. CU request paths are not live-tested. |
| Implement video analysis workflows to process and interpret video segments | D3 `14_video_analysis.py`, `15_cu_visual_handoff.py`, `17_cu_custom_video_analyzer.py` | **Runnable / Opt-in** — L14 prints returned segment ranges/summaries; L15 can normalize bounded video segments with `--apply`; L17 segments a video and generates per-segment fields only with `--apply`. No successful CU operation is evidenced. |
| Configure single-task and pro-mode Content Understanding pipelines | D5 CU lessons 09–13 | **Runnable / Partial** — lessons 09–12 are single-task GA analyzers. Pro mode's only API (`2025-05-01-preview`) was retired on July 15, 2026; lesson 13 shows the current replacement (one analyze per document plus app-side comparison) and preflights locally by default. |
| Implement solutions that identify objects, components, or regions within images or video | D3 `13_content_understanding_image.py`, `14_video_analysis.py`, `15_cu_visual_handoff.py` | **Partial** — output is Markdown, summary, or bounded time segments; no object/component/region extraction contract. |

### Implement responsible AI for multimodal content

| April 2026 bullet | Evidence | Status |
|---|---|---|
| Implement filters to classify unsafe or disallowed visual content | D3 `03_image_moderation.py` | **Runnable** |
| Detect and mitigate indirect prompt injection by using embedded text in images | D3 `11_ocr_image_injection_safety.py`; D1 `11_prompt_shields_docs.py` | **Preflight / Opt-in / Partial / Cross-domain** — D3 treats supplied OCR text as untrusted and scans it only with `--run`; it neither performs OCR nor proves an image-embedded-text path ran. |
| Enforce visual policy rules, such as applying watermarks, flagging prohibited symbols, upholding brand usage requirements, and detecting potentially inappropriate content | D3 `03_image_moderation.py`, `10_visual_provenance_policy.py` | **Partial / Preflight / Opt-in** — L03 classifies image-harm categories; L10 defaults to policy guidance and has an opt-in provenance-marker detection path. No watermark application, symbol/brand enforcement, or live provenance result is evidenced. |

## 4. Implement text analysis solutions (10–15%)

The D4 advanced lessons are deliberately bounded: L21 and L22 default to
**Preflight** and require `--run` for remote discovery or reviewed-text
translation; L23 requires `--apply` for a Document Translation operation;
L24 requires `--run` for Voice Live; L25 is **Local** configuration review.
None is evidence of a successful remote operation.

### Apply language model text analysis

| April 2026 bullet | Evidence | Status |
|---|---|---|
| Implement solutions to extract entities, topics, summaries, and structured JSON outputs by using generative prompting and Foundry Tools | D4 `01_llm_ner.py`; D2 `07_structured_output.py` | **Partial** — entities/topics and strict JSON; no dedicated summary lesson. |
| Configure detection of sentiment, tone, safety issues, and sensitive content | D4 `02_llm_sentiment.py`, `05_language_pii.py`, `20_language_sentiment.py`; D1 `09_content_safety_filters.py` | **Runnable / Cross-domain** |
| Build solutions that translate text by using Azure Translator in Foundry Tools or LLM-powered translation flows | D4 `03_llm_translation.py`, `04_translator_rest.py`, `22_translator_secure_config.py`, `23_translator_batch_operations.py` | **Runnable / Preflight / Opt-in / Partial** — L04 is Text Translation v3; L22 sends reviewed text only with `--run`; L23 submits, inspects, or cancels a Document Translation batch only with `--apply`. No remote operation is live-tested. |
| Customize language model outputs for domain tasks, such as compliance summarization and domain extraction | D4 `01_llm_ner.py`, `10_health_text_analytics.py` | **Partial** — domain extraction; no compliance-summarization lesson. |

### Implement speech solutions

| April 2026 bullet | Evidence | Status |
|---|---|---|
| Implement workflows to convert speech to text and text to speech for agentic interactions | D4 `11_stt_fast_file.py`–`15_tts_ssml_hd.py`, `24_voice_live_audio_flow.py` | **Runnable / Preflight / Opt-in / Partial** — STT/TTS calls exist. L24 has a `--run` PCM file-to-file path, but no complete agentic turn, playback, or live-success evidence. |
| Integrate speech as an agent modality, including custom speech models | D4 `18_voice_live_prompt_agent.py`, `19_custom_speech_model.py`, `21_speech_mcp_preflight.py`, `24_voice_live_audio_flow.py` | **Runnable / Preflight / Opt-in / Partial** — L18 sends prerecorded audio and logs events; L19 consumes an existing Custom Speech deployment; L21 lists tools only with `--run`; L24 writes raw PCM only with `--run`. No end-to-end voice client or successful remote run is evidenced. |
| Enable multimodal reasoning from audio inputs | D4 `17_llm_speech_preview.py`, `18_voice_live_prompt_agent.py`, `24_voice_live_audio_flow.py` | **Runnable / Preflight / Opt-in / Partial** — transcription and Voice Live protocol/file flows exist, but no explicit audio-reasoning workflow or live-success evidence. |
| Translate speech into other languages by using language models and Foundry Tools | D4 `16_speech_translation.py` | **Runnable** |

## 5. Implement information extraction solutions (10–15%)

Domain 5 has **31** numbered lessons (`00`–`30`). L12–L13 and L16–L30
default to **Preflight** and make no cloud call. Their explicit remote paths
are **Opt-in** and have no successful live-operation evidence. L00–L05,
L07–L11, and L14–L15 contain remote code paths; L06 is **Local**. This matrix
does not claim any remote path was run successfully.

### Build retrieval and grounding pipelines

| April 2026 bullet | Evidence | Status |
|---|---|---|
| Ingest and index content, such as documents, images, audio, and video | D5 `00_search_index_setup.py`, `04_search_indexer_setup.py`, `05_search_skillset.py`, `29_search_ocr_knowledge_store.py`, `30_search_cu_skill_citations.py` | **Partial / Preflight / Opt-in** — Blob document pipeline; L29 indexes text read from images (OCR) and L30 indexes Content Understanding chunks and images, both only with `--apply`. Audio and video are not indexed; D3/CU analyzes video without indexing it. |
| Configure semantic search, hybrid search, and vector search for grounding | D5 `02_search_vector.py`, `03_search_hybrid_semantic.py` | **Runnable** |
| Implement enrichment by using custom or built-in skills for text, images, and layout | D5 `05_search_skillset.py`, `06_search_custom_skill.py`, `17_search_custom_skill_deploy.py`, `29_search_ocr_knowledge_store.py`, `30_search_cu_skill_citations.py` | **Runnable / Local / Preflight / Opt-in / Partial** — L05 has split/embedding code; L06 is local Web API contract; L17 only deploys/wires derived custom skillset after `--apply` (and starts it only with `--run`); L29 (OCR, Text Merge, Shaper, knowledge-store projections) and L30 (Content Understanding layout and image skill) validate locally and deploy only with `--apply`. No live deployment is evidenced. |
| Configure RAG ingestion flow, including documents and using OCR | D5 Search pipeline plus `09_cu_prebuilt_read.py`, `10_cu_prebuilt_layout.py`, `16_cu_multimodal_rag.py`, `29_search_ocr_knowledge_store.py`, `30_search_cu_skill_citations.py` | **Partial / Preflight / Opt-in** — Search splits extracted Blob text; L29 adds OCR of normalized images to the indexer pipeline and L30 chunks with page and polygon metadata, both only with `--apply`. L16 converts one CU result to bounded local records only with `--apply`, then does not index them. |
| Connect retrieval pipelines directly to workflows and agent tools | D5 `07_rag_prompt_agent.py`, `08_rag_client_run.py`, `20_managed_search_agent_tool.py` | **Partial / Preflight / Opt-in** — L07/L08 are manual app-owned retrieval. L20 defaults to local preflight; `--enable` plus `--apply`/`--run` creates or invokes a managed Search agent, with no live-success evidence. No retrieval workflow is implemented. |

### Extract content from documents

| April 2026 bullet | Evidence | Status |
|---|---|---|
| Extract information by using multimodal pipelines that combine OCR, layout analysis, and field extraction | D5 `09_cu_prebuilt_read.py`, `10_cu_prebuilt_layout.py`, `11_cu_invoice.py`, `12_cu_custom_analyzer.py`, `16_cu_multimodal_rag.py` | **Runnable / Preflight / Opt-in / Partial** — each is a separate CU path. L16 selects a media analyzer and emits bounded records only with `--apply`; no single composed OCR/layout/field pipeline or live result is evidenced. |
| Produce clean, grounded representations to use with agents and RAG by using Content Understanding | D5 `14_cu_markdown_for_rag.py`, `15_cu_content_agent.py`, `16_cu_multimodal_rag.py`, `30_search_cu_skill_citations.py` | **Partial / Preflight / Opt-in** — L14 inspects markdown, L15 sends invoice fields to a model, and L16 emits bounded records after explicit CU submission; L30 indexes Content Understanding Markdown chunks with page-level citations only with `--apply`. |
| Implement analyzers for generating structured or markdown outputs for downstream reasoning by using Content Understanding | D5 `10_cu_prebuilt_layout.py`, `12_cu_custom_analyzer.py` (confidence/grounding, `prebuilt-documentFieldSchema` proposal), `13_cu_cross_document_validation.py`, `14_cu_markdown_for_rag.py` (`prebuilt-layout` or `prebuilt-documentSearch`) | **Runnable / Opt-in** — lessons 12–13 preflight locally and create analyzers only with `--apply`. |
| Monitor data ingestion quality, index health, and relevance performance | D5 `18_search_monitoring.py`, `03_search_hybrid_semantic.py` | **Preflight / Opt-in / Partial** — L18 defaults to local configuration checks and `--run` reads one redacted indexer-status/document-count snapshot. It has no alerts, relevance evaluation, or live-success evidence. |

## Inventory summary

| Domain | Numbered lessons present | Notes |
|---|---:|---|
| 1 — Plan and manage | 37 | `01`–`36` plus `04b`; advanced evaluation, tracing, control-plane, CI/CD, guardrail, red-team, and RAG quality-gate lessons remain preflight/opt-in where documented; L36 is local planning logic. |
| 2 — Generative AI and agents | 51 | `01`–`51`; external tools are L25–L27, hosted-agent contracts L28–L30, direct advanced OpenAI patterns L31–L39, A2A/external agents L40–L42, Agent Framework workflows L43–L45, preview tool/hosted-agent operations L46–L49, a local approval workflow L50, and parallel tool calls L51. |
| 3 — Computer vision | 17 | `01`–`17`; advanced paths remain preflight/local by default except explicit remote flags. |
| 4 — Text and speech | 30 | `01`–`30`; Language, Speech, Translator, Voice, Realtime, and GPT-Live paths retain separate endpoint/auth contracts. |
| 5 — Information extraction | 31 | `00`–`30`; `00_search_index_setup.py` is included. L12–L13 and L16–L30 default to local preflight; remote work is explicit **Opt-in**. L21–L27 cover agentic retrieval (knowledge sources, knowledge base, retrieve); L29–L30 cover OCR, knowledge-store, and Content Understanding skill enrichment. |
| 6 — Model customization and delivery | 20 | Supplemental curriculum; local validation/preflight first, every cloud request remains explicit. |
| 7 — Production platform | 11 | Cross-domain infrastructure preflights; L11 adds connection and selected-network templates. Apply remains explicit and no live deployment is claimed. |
| 8 — Advanced agents and current Foundry operations | 28 | `01`–`28`; remote mutations are explicit, L22–L27 are local typed/safety preflights, and L28 is a local/opt-in read-only telemetry view. |
| 9 — Current AI services | 7 | `01`–`07`; Document Intelligence calls/builds remain opt-in and evidence-bounded. |
| **Total** | **232** | Numbered Python lessons only; excludes shared modules, Function assets, tests, and JSON/YAML. |

Gaps and partial labels are intentional. They prevent a local study repository
from claiming live implementation of hosted deployment, A2A, MCP, Toolbox,
cloud evaluation, private networking, CI/CD, video editing, platform generation
controls, managed Search agent tools, or other behavior that its default local
commands do not perform. D5 L20 is an opt-in implementation path, not a
successful managed-Search-agent run.

## Supplemental domain 6: model customization and delivery

Domain 6 is not an additional AI-103 objective. It provides current,
evidence-bounded labs for customization and delivery decisions that cut across
the five exam domains.

| Topic | Evidence | Status |
|---|---|---|
| SFT, DPO, and RFT dataset contracts | D6 `01_sft_dataset.py`, `02_dpo_dataset.py`, `03_rft_dataset_grader.py` | **Local** — validates JSONL/grader syntax; no upload or job. |
| Distillation and synthetic-data review | D6 `04_distillation_dataset.py` | **Preflight / Opt-in** — default validates prompts; `--apply` calls teacher once per prompt and writes a new local candidate dataset. |
| SFT, DPO, and RFT training | D6 `05_submit_training.py`, `06_training_monitor.py` | **Preflight / Opt-in** — `--apply` uploads/submits one job or reads one job; no live-success claim. |
| Fine-tuned checkpoint deployment and evaluation | D6 `07_deploy_checkpoint.py`, `08_evaluate_candidate.py` | **Preflight / Opt-in** — deployment mutation and inference comparison require `--apply`. |
| Batch, quota, PTU, Priority, Instant, router, and cost | D6 `09_batch_inference.py`–`13_cost_review.py` | **Local / Preflight / Opt-in** — cloud calls/mutations require `--apply`; cost calculator is local arithmetic only. |

## Supplemental domain 7: production platform

Domain 7 is not an additional AI-103 objective. It supplies a current,
locally validated production-platform baseline; it does not claim an Azure
deployment succeeded.

| Topic | Evidence | Status |
|---|---|---|
| Bicep and Terraform Foundry regional cell | D7 `bicep/main.bicep`, `terraform/` | **Preflight / Opt-in** — alternatives create private, keyless `AIServices` account/project cells only after explicit apply. |
| VNet, private endpoints, and private DNS | D7 regional-cell templates and offline tests | **Preflight / Opt-in** — assets include account, Key Vault, and Blob private paths; no subscription DNS/reachability proof. |
| CMK, Key Vault RBAC, Policy, diagnostics, and locks | D7 templates and `policy/deny-unapproved-foundry-connections.json` | **Preflight / Opt-in** — CMK follows key rotation (no pinned `keyVersion`) and names the user-assigned identity with `identityClientId`; CMK availability, roles, policy category selection, and diagnostic category availability remain tenant and region dependent. |
| CI/CD, HA, and DR | D7 contained OIDC/self-hosted runner workflow and README runbook | **Local / Preflight** — no active workflow, traffic failover, agent-state migration, or live recovery drill is claimed. |
| Connections, selected networks, and CMK by CLI | D7 `11_connections_network_rules_preflight.py`, `bicep/connections.bicep`, `bicep/selected-networks.bicep` | **Preflight / Opt-in** — default checks both templates and prints CLI sequences; `--what-if` previews and `--apply` deploys one template. No connection, network rule, or CMK change is claimed. |

## Supplemental domain 8: advanced agents and current Foundry operations

Domain 8 is not an AI-103 objective. It provides bounded, current-platform
practice for capabilities adjacent to agent delivery and operations.

| Topic | Evidence | Status |
|---|---|---|
| Foundry IQ keyless connection | D8 `01_foundry_iq_connection_preflight.py` | **Preflight / Opt-in** — validates current MCP URL locally; `--apply` creates or updates a project connection. |
| Toolbox version and endpoints | D8 `02_toolbox_publish_preflight.py` | **Preflight / Opt-in** — validates a credential-free manifest; `--apply` creates a Toolbox version. |
| A2A v1.0 card and endpoint | D8 `03_a2a_agent_card_preflight.py` | **Preflight / Opt-in** — default prints endpoints; `--apply` patches one agent. |
| Routines | D8 `04_routines_preflight.py` | **Preflight / Opt-in** — default validates local manifest; `--apply` creates and optionally dispatches a routine. |
| Gateway, endpoint release, and channel distribution | D8 `05_gateway_publishing_preflight.py` | **Preflight / Opt-in / Partial** — `--apply` pins a stable endpoint; AI Gateway and M365/Teams distribution retain explicit portal steps. |
| Agent Optimizer | D8 `06_agent_optimizer_preflight.py` | **Preflight / Opt-in** — checks hosted-agent assets; `--apply` starts a job or applies a reviewed candidate locally, never deploys. |
| Toolbox lifecycle, guardrail policy, and Skills | D8 `20_toolbox_lifecycle_governance.py`, `21_skills_private_catalog_preflight.py` | **Preflight / Opt-in** — typed policy/Skill paths and lifecycle operations exist; API Center catalogs and private-network Skills remain external prerequisites. |
| Grounding with Bing and Microsoft IQ | D8 `22_bing_grounding_preflight.py`, `23_microsoft_iq_tools_preflight.py` | **Local / Cross-domain** — typed current tools plus identity/network decisions; no Bing/Fabric/M365 request is made. |
| Reminder, Computer Use, enterprise data, and image tool | D8 `24_reminder_tool_preflight.py`–`27_image_generation_tool_preflight.py` | **Local / Preview** — request and safety contracts only; no reminder, UI action, enterprise query, or media generation. |
| Cross-domain operational observability | D8 `28_cross_domain_observability.py` | **Local / Read-only Opt-in** — maps Domain 01–09 signals and can query non-content App* health tables; no live-ingestion claim. |

## Supplemental domain 9: current Document Intelligence

Domain 9 is not an AI-103 objective. It provides current Document Intelligence
v4.0 (2024-11-30 GA) exercises and a local choice between Document Intelligence
and Content Understanding. Each default command is local. Remote analysis or
custom-model training requires explicit `--apply`; no successful Azure
operation is claimed.

| Topic | Evidence | Status |
|---|---|---|
| Read OCR | D9 `01_read_ocr.py` | **Preflight / Opt-in** — default validates local input presence; `--apply` analyzes one document. |
| Layout Markdown and tables | D9 `02_layout_markdown_tables.py` | **Preflight / Opt-in** — `--apply` requests Layout Markdown and reports structural counts. |
| Invoice and ID extraction | D9 `03_invoice.py`, `04_id_document.py` | **Preflight / Opt-in** — `--apply` invokes one prebuilt model; values remain suppressed until an explicit display flag. |
| Custom neural model | D9 `05_custom_neural_preflight.py` | **Preflight / Opt-in** — validates local model, Blob, and training-hour inputs; `--apply` starts and waits for a persistent, potentially billable build. |
| DI versus CU decision | D9 `06_di_vs_cu_decision.py` | **Local** — applies current documented scenario defaults; it doesn't measure quality, cost, availability, or performance. |
