# AI-103 Prep Codebase

Runnable code + notes for **Microsoft Certified: Azure AI Engineer — AI-103: Developing AI Apps and Agents on Azure**.

## Layout

```
_shared/                    reusable clients + sample data (all lessons import this)
01-plan-and-manage/         Domain 1 (25-30%)
02-generative-ai-and-agents/Domain 2 (30-35%)
03-computer-vision/         Domain 3 (10-15%)
04-text-and-speech/         Domain 4 (10-15%)
05-information-extraction/  Domain 5 (10-15%)
docs/coverage.md            syllabus bullet → file matrix
```

Study material (unchanged):

- `AI-103.md` — official exam objectives.
- `Slides.md` — full slide notes (extracted from `Slides.pdf`).
- `other-notes-link.md` — external resources.
- `.context/azure-ai-docs/` — cloned official Azure docs, linked from every domain README.

## First-time setup

```bash
cp .env.example .env    # fill in your Foundry / Search / Speech / Language / CU endpoints
uv sync                 # creates .venv + installs all deps from uv.lock
az login                # DefaultAzureCredential picks this up
```

Every lesson runs with:

```bash
uv run python 02-generative-ai-and-agents/01_first_api_call.py
```

Or activate the venv once and run directly:

```bash
source .venv/bin/activate
python 02-generative-ai-and-agents/01_first_api_call.py
```

Add a dependency:

```bash
uv add <package>        # updates pyproject.toml + uv.lock
```

No API keys live in any Python file. Auth is Entra bearer tokens via `DefaultAzureCredential`.

## Syllabus map

| Domain | Weight | Folder |
|---|---|---|
| Plan and manage an Azure AI solution | 25-30% | [`01-plan-and-manage/`](01-plan-and-manage/README.md) |
| Implement generative AI and agentic solutions | 30-35% | [`02-generative-ai-and-agents/`](02-generative-ai-and-agents/README.md) |
| Implement computer vision solutions | 10-15% | [`03-computer-vision/`](03-computer-vision/README.md) |
| Implement text analysis solutions | 10-15% | [`04-text-and-speech/`](04-text-and-speech/README.md) |
| Implement information extraction solutions | 10-15% | [`05-information-extraction/`](05-information-extraction/README.md) |

Each domain README maps every AI-103 syllabus bullet to a concrete file, links the relevant doc in `.context/azure-ai-docs/`, and shows the expected output.

## Conventions

- Folder names: `NN-kebab-case/`.
- File names: `NN_snake_case.py` — always zero-padded prefix.
- No hardcoded endpoints/keys in Python files. All config through `_shared/config.py` reading `.env`.
- Every lesson file has a runnable `if __name__ == "__main__":` block.
- Every non-trivial lesson prints something you can eyeball — a decision, a citation, a JSON blob, a moderation verdict.

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
