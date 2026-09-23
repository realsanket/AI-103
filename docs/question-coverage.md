# Practice-question coverage map

This map covers the supplied practice-question PDF. It contains **175**
numbered questions (`Q1` through `Q175`), not 174. Read the questions after
the mapped domain's normal lesson sequence; a question with a second lesson
reference is intentionally cross-domain.

Each domain also has a `questions/` directory. `Existing` means that a lesson
already exercises the concept. `New` is a local, no-cloud question supplement.
`Gap` needs current-documentation validation before it can become a runnable
lesson. `Compatibility` is intentionally not a new lab because the source
uses legacy/retired surfaces outside this repository's current-scope rule.

## 01 - Plan and manage

| Q | Coverage | Status |
|---:|---|---|
| 3 | L11–12 Document Prompt Shields and Spotlighting | Existing |
| 5 | L25–26 run tracing | Existing |
| 9 | L30 evaluation CI/CD gate | Existing |
| 10 | L25–26 tracing, D2 L23 telemetry | Existing |
| 17 | L06 retry with exponential backoff and jitter | Existing |
| 19 | L30 groundedness merge gate | Existing |
| 23 | `questions/01_access_and_metrics_preflight.py` | New |
| 24 | L25–26 distributed tracing | Existing |
| 26 | L09, L21–22 groundedness and safety evaluation | Existing |
| 34 | L21 RAG quality evaluation | Existing |
| 40 | L11 and L18 injection versus protected material | Existing |
| 42 | L11–12 plus D8 L22 web grounding | Existing |
| 47 | L26 token diagnostics | Existing |
| 48 | L08 RBAC and D5 L19 Blob identity | Existing |
| 49 | L30 pull-request quality gate | Existing |
| 53 | L07 identity plus D2 L01 Responses | Existing |
| 56 | L26 latency and token diagnosis | Existing |
| 58 | L26 and D2 L24 latency decomposition | Existing |
| 59 | L08 RBAC plus D3 L03 image safety | Existing |
| 63 | L08–09 access and safety boundaries | Existing |
| 64 | L17 critique and regeneration | Existing |
| 65 | L10 User Prompt Shields | Existing |
| 66 | L21 evaluation and L25–26 observability | Existing |
| 68 | L25–26 prompt/output token metrics | Existing |
| 69 | L17, L19, L21 groundedness handling | Existing |
| 71 | L08 direct Azure OpenAI RBAC | Existing |
| 78 | L25–26 tool latency spans | Existing |
| 80 | L21–22 quality regression | Existing |
| 81 | L04 Model Router | Existing |
| 96 | L25–26 stage latency tracing | Existing |
| 98 | L17 reflection/regeneration | Existing |
| 100 | L17 corrective retry versus L21 evaluation | Existing |
| 101 | L30 and L21 RAG CI/CD evaluation | Existing |
| 103 | L18 and L21 quality/safety evaluation | Existing |
| 104 | L21 evaluation categories | Existing |
| 111 | L25–26 end-to-end traces | Existing |
| 112 | L25 Application Insights setup | Existing |
| 113 | `questions/01_access_and_metrics_preflight.py` | New |
| 115 | L25–26 hierarchical audit spans | Existing |
| 125 | L06 throttling, D2 L06 uploads | Existing |
| 130 | L30 evaluation YAML CI/CD | Existing |
| 133 | L09 Content Safety severity | Existing |
| 134 | L17 and L21 completeness | Existing |
| 139 | Control-plane resource concepts | Gap: multi-service resource exercise |
| 140 | Responsible AI governance | Gap: transparency exercise |
| 142 | L07–08 endpoint/auth boundary | Compatibility: source key flow conflicts with keyless baseline |
| 166 | L02–03 regional deployment/version pinning | Existing |
| 167 | L11 plus D3 L11 indirect injection | Existing |
| 168 | L19 and L21 RAG evaluation | Existing |
| 175 | `questions/01_access_and_metrics_preflight.py` | New |

## 02 - Generative AI and agents

| Q | Coverage | Status |
|---:|---|---|
| 6 | L04–06 web, code interpreter, file search | Existing |
| 7 | L12 OpenAPI tools | Existing |
| 8 | L16 conditional workflow | Existing |
| 12 | L14 Foundry Memory | Existing |
| 13 | L35 function calling and L40 auth | Existing |
| 16 | `questions/01_few_shot_response_controls.py` | New |
| 18 | Project connection concepts | Gap: model-resource connection preflight |
| 25 | `questions/01_few_shot_response_controls.py` | New |
| 29 | L14 memory and L06 File Search | Existing |
| 33 | L16/L43 approval workflow | Gap: exact visual-builder/Powers Fx variant |
| 43 | L43 declarative workflow | Gap: Power Fx exercise |
| 44 | L13 conversation continuity | Existing |
| 45 | L13 conversation continuity | Existing |
| 52 | L06 File Search versus D5 Search | Existing |
| 62 | L13 durable conversation state | Existing |
| 67 | L12 OpenAPI connection auth | Existing |
| 73 | L14 memory and L06 File Search | Existing |
| 76 | L05/L06 plus D8 L25 | Existing |
| 79 | L05 and L04/L10 tools | Existing |
| 82 | `questions/01_few_shot_response_controls.py` | New |
| 83 | L05–06 uploaded contracts/spreadsheets | Existing |
| 86 | L04/L06 plus D8 L25 | Existing |
| 93 | `questions/01_few_shot_response_controls.py` | New |
| 97 | `questions/01_few_shot_response_controls.py` | New |
| 99 | L02 temperature | Existing |
| 102 | L13 multi-session state | Existing |
| 108 | `questions/01_few_shot_response_controls.py` | New |
| 109 | L15–16 workflows | Gap: visual-builder approval node |
| 110 | `questions/01_few_shot_response_controls.py` | New |
| 123 | L14 plus D5 knowledge sources | Existing |
| 131 | L31 embeddings plus D5 vector search | Existing |
| 153 | L31 semantic-similarity embeddings | Existing |
| 154 | L08 system instructions | Existing |
| 155 | L01 endpoint, credential, deployment | Existing |
| 169 | L08 scoped system instructions | Existing |
| 174 | L14 cross-session memory | Existing |

## 03 - Computer vision

| Q | Coverage | Status |
|---:|---|---|
| 11 | `questions/01_image_edit_fidelity_preflight.py` | New |
| 20 | `questions/01_image_edit_fidelity_preflight.py` | New current image-edit equivalent |
| 27 | L06 mask-bounded editing | Existing |
| 30 | L06 sky replacement with a mask | Existing |
| 32 | L03 image moderation | Existing |
| 37 | L11 OCR injection plus D1 L11–12 | Existing |
| 38 | L11 OCR injection plus D1 L11–12 | Existing |
| 39 | L11 OCR injection plus D1 L11–12 | Existing |
| 54 | L06 remove a logo with a mask | Existing |
| 60 | `questions/01_image_edit_fidelity_preflight.py` | New |
| 72 | L11 OCR content is indirect injection | Existing |
| 95 | L06 selective object removal | Existing |
| 105 | L14 video segments | Gap: generated field schema |
| 117 | L01 visual understanding | Compatibility: legacy Vision Brands result shape |
| 124 | L09 video remix | Gap: video inpainting |
| 126 | L01 multimodal content input | Existing |
| 135 | Custom Vision defect classifier | Compatibility: legacy Custom Vision |
| 136 | L16 DALL-E generation | Existing |
| 143 | Custom Vision precision/recall | Compatibility: legacy Custom Vision |
| 148 | Custom Vision classifier configuration | Compatibility: legacy Custom Vision |
| 159 | Custom Vision defect detector | Compatibility: legacy Custom Vision |
| 164 | Vision `imageType` API | Compatibility: legacy Vision API |
| 165 | Custom Vision metrics | Compatibility: legacy Custom Vision |
| 173 | L07 asynchronous video lifecycle | Existing |

## 04 - Text and speech

| Q | Coverage | Status |
|---:|---|---|
| 1 | L12 real-time STT | Existing |
| 50 | L19 Custom Speech endpoint | Existing |
| 57 | `questions/01_mixed_language_translation_routing.py` | New |
| 61 | L19 Custom Speech lifecycle | Existing |
| 91 | L12 and L14 live STT/TTS | Existing |
| 127 | L05 PII plus D1 L13 | Existing |
| 128 | L30 GPT-Live WebRTC | Existing |
| 137 | L07 NER | Gap: custom-NER label quality |
| 138 | L15 SSML pronunciation | Existing |
| 147 | Immersive Reader | Compatibility: outside current lesson scope |
| 150 | L07 Named Entity Recognition | Existing |
| 151 | L07 NER | Gap: entity-linking-specific exercise |
| 160 | Language container operations | Compatibility: no current lab |
| 161 | Multi-service provisioning | Gap: resource-choice exercise |
| 163 | On-prem Language container | Compatibility: no new legacy lab |

## 05 - Information extraction

| Q | Coverage | Status |
|---:|---|---|
| 2 | L10 CU layout | Existing |
| 4 | L20 managed Search tool and D2 L27 | Existing |
| 14 | L24–26 agentic retrieval | Existing |
| 15 | CU analyzer map | Gap: validate `prebuilt-documentFieldSchema` before code |
| 21 | `questions/01_rag_ingestion_contract.py` | New |
| 28 | L20 Search tool index selection | Existing |
| 31 | L20 Search connection | Existing |
| 35 | L08 manual RAG completeness | Existing |
| 36 | L11/L13 CU standard versus Pro | Existing |
| 41 | L12 custom analyzer | Existing |
| 46 | L11/L13 CU standard versus Pro | Existing |
| 55 | L09 CU OCR | Existing |
| 75 | L20 and D1 L08 Search RBAC | Existing |
| 77 | D8 L09 MCP knowledge tool | Existing |
| 84 | L10/L14 layout Markdown RAG | Existing |
| 87 | `questions/01_rag_ingestion_contract.py` | New |
| 88 | L07–08 retrieval-context control | Existing |
| 90 | L09–11 CU invoice pipeline | Existing |
| 92 | L12 custom CU analyzer | Existing |
| 94 | `questions/01_rag_ingestion_contract.py` | New |
| 114 | CU analyzer map | Gap: validate `prebuilt-documentSearch` before code |
| 116 | L02 vector search and D2 L31 | Existing |
| 118 | L03 hybrid/semantic retrieval | Existing |
| 120 | L16 multimodal RAG | Existing |
| 121 | `questions/01_rag_ingestion_contract.py` | New |
| 122 | L13 CU Pro Mode | Existing |
| 141 | L04–06 Search enrichment | Gap: knowledge-store projections |
| 144 | L28 ACL/security trimming | Existing |
| 145 | L18 monitoring | Gap: query-key rotation runbook |
| 146 | L16 multimodal RAG | Existing; duplicate of Q120 |
| 170 | L11/L15 invoice review | Existing |
| 171 | L05 split-and-embed skillset | Existing |
| 172 | L04–05/L20 Search RAG | Existing |

## 06 - Model customization and delivery

| Q | Coverage | Status |
|---:|---|---|
| 85 | D1 L02 and D2 L03 capability selection | Existing |
| 107 | L00/L03 dataset and grader preflight plus D1 L18/L21 | Existing |
| 132 | L14 Foundry Models catalog | Existing |
| 152 | L14 catalog/serverless selection | Existing |

## 07 - Production platform

| Q | Coverage | Status |
|---:|---|---|
| 70 | `questions/01_security_operations_preflight.py` | New |
| 89 | L04 CI/CD OIDC | Existing |
| 119 | L01/L03 Key Vault connection infrastructure | Existing |
| 129 | L01 customer-managed keys | Existing |
| 156 | L01/L07 private networking | Gap: service-endpoint mechanics |
| 157 | L01/L07 public-access boundary | Gap: service-endpoint mechanics |

## 08 - Advanced agents

| Q | Coverage | Status |
|---:|---|---|
| 22 | L25 Computer Use plus D2 L05 | Existing |
| 106 | L22 Bing grounding | Gap: verify current forced-tool payload |
| 149 | L09 MCP get started plus D2 L25 | Existing |

## 09 - Document Intelligence

| Q | Coverage | Status |
|---:|---|---|
| 51 | L02 Layout Markdown and tables | Existing |
| 74 | L02 Layout Markdown and tables | Existing |
| 158 | L01 Read OCR plus D4 L20 sentiment | Existing |
| 162 | L01 DI Read OCR | Existing current equivalent to legacy Vision Read |

## Study rules

1. Run the mapped lesson's preflight before any `--apply` or `--run` path.
2. Use the question supplement only to understand a request or design contract; it does not prove cloud authorization or feature availability.
3. Treat `Gap` rows as documentation work, not successful feature coverage.
4. Treat `Compatibility` rows as exam-history review. Do not add a retired API as a new runnable lab.
