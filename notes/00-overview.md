# AI-103 Exam — Overview & Quick Reference

## Exam weights

| Domain | Title | Weight | Lesson files |
|--------|-------|--------|-------------|
| 1 | Plan and Manage an Azure AI Solution | 25–30% | 13 files |
| 2 | Implement Generative AI and Agentic Solutions | 30–35% | 22 files |
| 3 | Implement Computer Vision Solutions | 10–15% | 9 files |
| 4 | Implement Text Analysis Solutions | 10–15% | 19 files |
| 5 | Implement Information Extraction Solutions | 10–15% | 15 files |

Passing score: **700 / 1000**

---

## The Azure AI Exam House

```
                    AI-103 Exam House
                           │
 ┌─────────────────────────────────────────────────────────┐
 │                                                         │
 │  🏗️ Domain 1          🤖 Domain 2                       │
 │  Plan & Manage         GenAI & Agents                   │
 │  (25–30%)              (30–35%)  ← biggest domain       │
 │                                                         │
 │  👁️ Domain 3          📝 Domain 4                       │
 │  Computer Vision       Text + Speech                    │
 │  (10–15%)              (10–15%)                         │
 │                                                         │
 │  🔍 Domain 5                                            │
 │  Information Extraction                                 │
 │  (10–15%)                                               │
 └─────────────────────────────────────────────────────────┘
```

Memory: **Plan → Build Agents → See → Read/Hear → Extract**

---

## Azure AI Service Families (what the code calls)

| Service | Purpose | Entry point |
|---------|---------|------------|
| **Azure AI Language** | Understand text | `azure-ai-textanalytics` SDK |
| **Azure AI Translator** | Translate text/docs | REST via `azure-ai-translation-text` |
| **Azure AI Speech** | Voice ↔ Text | `azure-cognitiveservices-speech` SDK |
| **Azure Content Understanding** | Multimodal extraction | REST (`/contentunderstanding/`) |
| **Azure AI Search** | Search + RAG | `azure-search-documents` SDK |
| **Azure AI Content Safety** | Moderate content | `azure-ai-contentsafety` SDK |
| **Microsoft Foundry** | Orchestrate everything | `azure-ai-projects`, OpenAI SDK |

---

## Cross-domain confusables

| Confusable A | Confusable B | Key difference |
|---|---|---|
| **File Search** (tool) | **AI Search** (service) | File Search = managed blob in Foundry; AI Search = full indexer + skillset pipeline |
| **Azure Content Understanding** | **Azure AI Document Intelligence** | CU = newer multimodal (docs/images/audio/video); Doc Intelligence = older forms extraction |
| **Azure AI Translator** | **Azure AI Language** | Translator = change language; Language = understand text (NER/PII/sentiment) |
| **Content Safety** | **Prompt Shields** | Content Safety = moderation (hate/violence/sexual); Prompt Shields = injection defense |
| **Semantic Ranking** | **Vector Search** | Semantic re-ranks BM25 text results; vector uses embedding cosine similarity |
| **CU Pro mode** | **CU Standard mode** | Pro = multi-doc cross-reasoning; Standard = single-item extraction |
| **PTU** | **Global Standard** | PTU = provisioned throughput unit (reserved, no 429s); Global = pay-per-token, first new models |
| **Managed Identity** | **Keyless auth** | Managed Identity = VM/App identity in Azure AD; keyless = using that identity to get a bearer token (they work together) |
| **fast-transcription** | **real-time STT** | fast = file sync API; real-time = live audio stream via SDK |

---

## Foundry Tools (services accessible via Foundry portal)

The exam uses "Foundry Tools" to mean Azure AI services integrated into the Foundry portal:

```
Foundry Tools
│
├── Azure AI Translator
├── Azure AI Language
├── Azure AI Speech
├── Azure AI Content Safety
├── Azure Content Understanding
└── Azure AI Search
```

When the exam says "using Foundry Tools" it means calling these services through a Foundry project endpoint.

---

## Domain → lesson file pointer

| Domain | Folder | Key files to run first |
|--------|--------|----------------------|
| 1 — Plan & Manage | `01-plan-and-manage/` | `07_managed_identity_agent.py`, `08_content_safety_filters.py` |
| 2 — GenAI & Agents | `02-generative-ai-and-agents/` | `01_first_api_call.py`, `08_prompt_agent_create.py` |
| 3 — Computer Vision | `03-computer-vision/` | `01_multimodal_understanding.py`, `02_image_generation.py` |
| 4 — Text + Speech | `04-text-and-speech/` | `05_language_pii.py`, `11_stt_fast_file.py` |
| 5 — Info Extraction | `05-information-extraction/` | `03_search_hybrid_semantic.py`, `11_cu_invoice.py` |

---

## 30-second exam strategy

When a question describes a scenario, ask in this order:

```
What is the INPUT?
        ↓
Text?         → Domain 4 (Language / Translator / LLM NLP)
Voice?        → Domain 4 (Speech)
Image?        → Domain 3 (Vision / CU / Content Safety)
Video?        → Domain 3 (CU video / generation)
Document?     → Domain 5 (CU / AI Search / Doc Intelligence)
Agent/RAG?    → Domain 2 (Agents / Responses API / tools)
Managing?     → Domain 1 (Deployment / security / monitoring)
```
