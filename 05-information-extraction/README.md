# Domain 5 — Implement Information Extraction Solutions (10-15%)

## Files

| # | File | Syllabus bullet |
|---|---|---|
| 01 | `01_search_basic_query.py` | Query an AI Search index (baseline keyword) |
| 02 | `02_search_vector.py` | Configure vector search |
| 03 | `03_search_hybrid_semantic.py` | Configure hybrid + semantic ranking (compared) |
| 04 | `04_search_indexer_setup.py` | Ingest + index via indexer |
| 05 | `05_search_skillset.py` | Enrichment — built-in skills (OCR + split + embed) |
| 06 | `06_search_custom_skill.py` | Enrichment — custom skill via Azure Function |
| 07 | `07_rag_agent_search_tool.py` | Connect retrieval pipeline to an agent tool |
| 08 | `08_rag_client_run.py` | Invoke the RAG agent |
| 09 | `09_cu_prebuilt_read.py` | Content Understanding — prebuilt-read (basic OCR) |
| 10 | `10_cu_prebuilt_layout.py` | Content Understanding — prebuilt-layout (tables/figures) |
| 11 | `11_cu_invoice.py` | Content Understanding — domain-specific analyzer |
| 12 | `12_cu_custom_analyzer.py` | Content Understanding — custom analyzer via baseAnalyzerId |
| 13 | `13_cu_pro_mode.py` | Pro-mode multi-document reasoning |
| 14 | `14_cu_markdown_for_rag.py` | CU → clean Markdown → chunk → index into AI Search |
| 15 | `15_cu_content_agent.py` | Agent using Content Understanding outputs |
| — | `skillset_configs/` | JSON skillset/indexer/index definitions |

## Run

```bash
python 05-information-extraction/01_search_basic_query.py
```

## Reference docs

- [Hybrid search overview](../.context/azure-ai-docs/articles/search/hybrid-search-overview.md)
- [Skillsets](../.context/azure-ai-docs/articles/search/cognitive-search-defining-skillset.md)
- [Custom skill interface](../.context/azure-ai-docs/articles/search/cognitive-search-custom-skill-interface.md)
- [Agentic knowledge sources](../.context/azure-ai-docs/articles/search/agentic-knowledge-source-overview.md)
- [CU analyzer reference](../.context/azure-ai-docs/articles/ai-services/content-understanding/concepts/analyzer-reference.md)
- [Standard vs Pro mode](../.context/azure-ai-docs/articles/ai-services/content-understanding/concepts/standard-pro-modes.md)

---

## Syllabus sections

| Section | Topics |
|---------|--------|
| Retrieval + grounding pipelines | Ingest + index, search modes, enrichment skills, RAG ingestion, connect to agent tools |
| Extract content from documents | Multimodal pipelines (OCR + layout + fields), grounded representations, analyzers |

> **MS Docs source:** [AI Search hybrid](../.context/azure-ai-docs/articles/search/hybrid-search-overview.md) · [Skillsets](../.context/azure-ai-docs/articles/search/cognitive-search-defining-skillset.md) · [CU overview](../.context/azure-ai-docs/articles/ai-services/content-understanding/overview.md) · [CU analyzer reference](../.context/azure-ai-docs/articles/ai-services/content-understanding/concepts/analyzer-reference.md)

---

# Azure AI Search

## Pipeline overview

```
Data Source (Blob / SQL / SharePoint / cosmos)
        │
        ▼
    Indexer (reads + runs skillset)
        │
        ▼
    Skillset (enrichment: OCR, NER, translate, embed, split)
        │
        ▼
    Index (searchable documents with fields)
        │
        ▼
    Query (keyword / vector / hybrid / semantic)
        │
        ▼
    Results (with scores + highlights)
```

Memory: **Data Source → Indexer → Skillset → Index → Query. Skillset runs at index time.**

---

# Search Modes

## Comparison table

| Mode | Mechanism | Best for |
|------|-----------|---------|
| **Keyword** (BM25) | Term frequency matching | Exact terms, known vocabulary |
| **Vector** | Embedding cosine similarity | Semantic meaning, paraphrases |
| **Hybrid** | BM25 + vector combined | Both exact + semantic (most common for RAG) |
| **Semantic Ranking** | Cross-encoder re-ranks results | Final relevance boost on top of hybrid |

## The recommended RAG stack

```
Hybrid search (BM25 + vector)
        +
Semantic Ranking
        =
Best retrieval quality for RAG
```

## Python query pattern

```python
from azure.search.documents.models import VectorizedQuery

# Hybrid + Semantic
results = search_client.search(
    search_text="refund policy",               # BM25 side
    vector_queries=[VectorizedQuery(
        vector=embed("refund policy"),         # vector side
        k_nearest_neighbors=10,
        fields="content_vector",
    )],
    query_type="semantic",                     # apply semantic ranking
    semantic_configuration_name="default",
    top=5,
)
```

## Semantic Ranking vs Vector Search

| | Semantic Ranking | Vector Search |
|--|-----------------|---------------|
| What it ranks | BM25 text results | Embedding vectors |
| Re-ranks | Yes (cross-encoder model) | No |
| Adds meaning | Yes (reads content) | Via embeddings |
| Combined with | BM25 (hybrid) | BM25 (hybrid) or alone |

Memory: **Semantic ranking re-reads results to re-rank; vector search finds by distance.**

---

# Skillsets (Enrichment at Index Time)

## Built-in skills

| Skill | What it does | Output |
|-------|-------------|--------|
| **OCR** | Extract text from images/PDFs | Text content |
| **Text Split** | Chunk text into pages/sentences | Text chunks (critical for RAG) |
| **Language Detection** | Detect document language | Language code |
| **Key Phrase Extraction** | Extract key phrases | Key phrase list |
| **Entity Recognition (NER)** | Extract named entities | Entity spans |
| **PII Detection** | Find + mask PII | Redacted text |
| **Translation** | Translate to target language | Translated text |
| **Azure OpenAI Embedding** | Generate vector embedding | Float array |

## Text Split is critical for RAG

```
Large document (50 pages)
        ↓ Text Split skill
Chunks (e.g. 512 tokens each)
        ↓ Embedding skill
Vectors per chunk
        ↓
Stored as separate index documents
        ↓
Vector search retrieves relevant chunks (not whole document)
```

Without Text Split: whole document becomes one index entry → poor retrieval.

## Custom skill contract

```
Indexer calls your Azure Function:

POST https://your-function.azurewebsites.net/api/custom-skill

Request body:
{
  "values": [
    { "recordId": "0", "data": { "text": "input text" } }
  ]
}

Your function must return:
{
  "values": [
    { "recordId": "0", "data": { "result": "your output" } }
  ]
}
```

The `recordId` must match request to response. Extra fields in `data` are passed through.

---

# Content Understanding (CU)

## Analyzer type table

| Analyzer | Input | Output | Use case |
|----------|-------|--------|---------|
| `prebuilt-read` | Doc/image | Text, paragraphs, words | Basic OCR, lightweight |
| `prebuilt-layout` | Doc/image | Text + tables + figures + sections + reading order | Structured docs for RAG |
| `prebuilt-document` | Doc | Text + key-value pairs + tables | Base for custom analyzers |
| `prebuilt-imageSearch` | Image | Structured description, tags, objects | Visual search / image indexing |
| Domain-specific prebuilts | Doc | Domain-specific fields | Invoices, receipts, IDs, contracts, tax |
| Custom (via `baseAnalyzerId`) | Doc/image | Your schema | Company-specific fields |
| **Pro mode** | Multiple docs | Cross-document reasoning + validation | Mortgage packages, compliance bundles |

## Domain-specific prebuilt examples

```
Financial: invoices, receipts, bank statements, checks
Identity:  passports, driver licenses, permits, SSN cards, Aadhaar
Legal:     contracts, NDAs
Procurement: purchase orders
Tax:       W-2, 1040, tax statements
Mortgage:  closing disclosure, loan estimate, 1003 application
```

## Custom analyzer pattern

```python
definition = {
    "baseAnalyzerId": "prebuilt-document",   # inherit from this prebuilt
    "fieldSchema": {
        "fields": {
            "ticket_id":    {"type": "string", "method": "extract"},
            "sla_tier":     {"type": "string", "method": "classify",
                            "enum": ["Bronze","Silver","Gold","Platinum"]},
            "breach_penalty_usd": {"type": "number", "method": "extract"},
            "summary":      {"type": "string", "method": "generate"},
        }
    }
}
create_analyzer("northwind-support-notice", definition)
result = analyze("northwind-support-notice", document_url)
```

## Standard vs Pro mode

```
Standard mode:
  One document/image/audio/video at a time
  → single-item field extraction
  → lower cost, lower latency
  → covers most use cases

Pro mode:
  Multiple documents together
  → cross-document reasoning
  → validation against reference data
  → linking related fields across docs
  → use for: mortgage packages, onboarding bundles, compliance reviews
```

Memory: **Standard = one item; Pro = many items cross-referenced.**

---

# CU → Markdown → RAG Pipeline

## Full ingestion chain

```
Document (PDF / image / Word)
        │
  ┌─────▼──────┐
  │ CU Layout  │  prebuilt-layout or custom analyzer
  │ Analyzer   │
  └─────┬──────┘
        │ Markdown output (tables preserved, headings preserved)
        │
  ┌─────▼──────┐
  │ Text Split │  chunk by token count (e.g. 512 tokens, 20% overlap)
  └─────┬──────┘
        │ chunks
        │
  ┌─────▼──────┐
  │  Embed     │  Azure OpenAI text-embedding-3-large
  └─────┬──────┘
        │ vectors
        │
  ┌─────▼──────┐
  │ AI Search  │  push to index with content + vector fields
  │   Index    │
  └────────────┘
        │
  hybrid + semantic query at runtime
```

Why Markdown? Tables and structure survive chunking better than plain text. Agents/LLMs parse Markdown naturally.

---

# RAG Path Comparison

| Path | Infrastructure | When |
|------|---------------|------|
| **File Search tool** | Foundry-managed blob + vector | Prototype, < 100 docs, zero setup |
| **AI Search tool** (agent) | AI Search service | Production, skillset enrichment, hybrid search |
| **Manual client RAG** | AI Search SDK + your code | Full control, custom reranking, filtering |
| **CU → Markdown → index** | CU + text split + embed + AI Search | Complex docs (tables, figures, mixed content) |

---

# Information Extraction Decision Tree

```
Need to FIND information in documents?  → Azure AI Search
        │
        ├── Exact keyword?              → keyword (BM25)
        ├── Semantic meaning?           → vector or hybrid
        └── Best for RAG?              → hybrid + semantic ranking

Need to EXTRACT FIELDS from a document?
        │
        ├── Just the text (OCR)?               → CU prebuilt-read
        ├── Text + tables + structure?          → CU prebuilt-layout
        ├── Invoice / receipt / ID?             → CU domain-specific prebuilt
        ├── Company-specific schema?            → CU custom (baseAnalyzerId)
        ├── Multiple docs, cross-reference?     → CU Pro mode
        └── For RAG chunk pipeline?             → CU prebuilt-layout → Markdown → split → embed → index

Need to ENRICH documents during indexing?
        │
        ├── OCR + NER + embed?          → built-in skillset skills
        └── Custom logic?               → custom skill (Azure Function, JSON contract)

Need AGENT to answer from a corpus?
        │
        ├── Small doc set, zero infra?  → File Search tool
        └── Production scale?           → AI Search tool (agent tool config)
```

---

# Common Exam Traps

| Trap | Truth |
|------|-------|
| "Semantic ranking is the same as vector search" | ❌ — semantic re-ranks BM25 text results; vector uses embeddings |
| "Skillsets run at query time" | ❌ — skillsets run at **index time** (when the indexer ingests documents) |
| "Custom skill can return any JSON shape" | ❌ — must return `{"values": [{"recordId": "...", "data": {...}}]}`; shape is contractual |
| "CU Pro mode = higher quality for one document" | ❌ — Pro = multi-document cross-reasoning |
| "`baseAnalyzerId` is optional in custom analyzers" | ❌ — you must specify a base (prebuilt-document or other) |
| "prebuilt-layout extracts just text like prebuilt-read" | ❌ — layout also extracts tables, figures, sections, reading order |

---

# 30-Second Domain 5 Trick

```
Find info in a corpus?          → AI Search
  Meaning-based?                → vector or hybrid
  Best for RAG?                 → hybrid + semantic ranking

Extract from document?
  Just text?                    → CU prebuilt-read
  Text + tables + structure?    → CU prebuilt-layout
  Invoice / receipt / ID?       → CU domain-specific prebuilt
  Custom fields?                → CU custom (baseAnalyzerId)
  Multiple docs together?       → CU Pro mode

Build RAG pipeline?
  Small prototype?              → File Search tool
  Production?                   → CU → Markdown → text split → embed → AI Search
  Add enrichment?               → Indexer + Skillset (built-in or custom skill)
```
