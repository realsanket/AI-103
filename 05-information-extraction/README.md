# Domain 5 — Implement Information Extraction Solutions (10–15%)

> Run any lesson: `uv run python 05-information-extraction/<file>.py`
> Prereqs: `.env` filled, `az login` completed. See root [README.md](../README.md).

15 lessons across two big topics: **Azure AI Search** (retrieval + RAG) and
**Content Understanding** (structured extraction from documents/images/video).
Where Domains 1–4 taught the models and services, Domain 5 teaches how to
turn unstructured data into things models can *use*.

---

## What this domain teaches you

Two production patterns fully wired end-to-end:

1. **Retrieval + RAG** — index a corpus into Azure AI Search (keyword +
   vector + semantic), enrich at ingest time with skillsets (built-in or
   custom Azure Function), then ground an agent on the retrieved chunks.
2. **Document → structured data** — Content Understanding analyzers
   (`prebuilt-read` for OCR, `prebuilt-layout` for tables + figures, plus
   domain analyzers like `prebuilt-invoice`), and custom analyzers via
   `baseAnalyzerId`. Includes **Pro mode** for cross-document reasoning
   (mortgage packages, compliance bundles).

You'll also see the two paths meet: **CU → Markdown → chunk → embed → AI
Search index** — the pattern that handles complex real-world documents
(tables, figures, mixed content) that plain-text chunkers mangle.

---

## Extraction in 90 seconds

- **Azure AI Search** — separate Azure resource. Pipeline is fixed:
  `Data Source → Indexer → Skillset → Index → Query`. Skillsets run at
  INDEX TIME, not query time.
- **Search modes** — Keyword (BM25), Vector (embedding cosine similarity),
  Hybrid (both combined), Semantic Ranking (cross-encoder re-ranks the top
  N). Production RAG = **hybrid + semantic**.
- **Skillsets** — enrich documents during ingestion. Built-in skills:
  OCR, Text Split, Language Detection, Key Phrase Extraction, NER, PII,
  Translation, Azure OpenAI Embedding. **Text Split is the RAG-critical
  one** — without chunking, one document = one index entry.
- **Custom skills** — your Azure Function called during indexing. Strict
  JSON contract: `{"values": [{"recordId", "data"}]}` in, same shape out.
- **Content Understanding (CU)** — separate service. Async
  submit→poll→read. Analyzers: prebuilt (`-read`, `-layout`, `-invoice`,
  `-receipt`, `-idDocument`, ...), custom (via `baseAnalyzerId` +
  `fieldSchema`), Pro mode (multi-file). GA API version `2025-11-01`;
  Pro mode preview `2025-05-01-preview`.
- **CU field extraction methods** — `extract` (find literal in doc),
  `classify` (pick from an enum), `generate` (LLM-authored summary).
- **CU → RAG pipeline** — the current best-practice ingestion:
  `PDF → prebuilt-layout → Markdown → chunk (headers + tokens) →
  embed → index`. Markdown preserves structure through chunking.

**Beginner shortcut:** *Find in a corpus → AI Search. Extract from one
doc → CU. Big real-world docs → CU → Markdown → AI Search.*

---

## Mental model of the 15 lessons

Three phases.

```
┌─── Phase 1: Azure AI Search (L01–L08) ────────────────────────────────┐
│  Query modes                                                            │
│    L01 Keyword baseline (BM25)                                         │
│    L02 Vector-only                                                     │
│    L03 Keyword vs Vector vs Hybrid+Semantic — side-by-side             │
│                                                                         │
│  Ingestion pipeline                                                    │
│    L04 Create/update the indexer (pulls Blob docs)                     │
│    L05 Create/update the skillset (OCR/split/embed built-ins)          │
│    L06 Custom skill — Azure Function with the WebApi payload contract  │
│                                                                         │
│  RAG-on-Search                                                         │
│    L07 Register a RAG Prompt Agent                                     │
│    L08 Manual RAG orchestration — retrieve → build prompt → invoke     │
└────────────────────────────────────────────────────────────────────────┘
        ↓ retrieval done — extraction next
┌─── Phase 2: Content Understanding (L09–L13) ──────────────────────────┐
│  Prebuilt analyzers                                                    │
│    L09 prebuilt-read (basic OCR)                                       │
│    L10 prebuilt-layout (tables + figures + reading order)              │
│    L11 prebuilt-invoice (domain-specific)                              │
│                                                                         │
│  Custom + Pro                                                           │
│    L12 Custom analyzer via baseAnalyzerId + fieldSchema                │
│    L13 Pro mode — cross-document reasoning (preview)                   │
└────────────────────────────────────────────────────────────────────────┘
        ↓ know both pipelines — combine them
┌─── Phase 3: CU meets Search (L14–L15) ─────────────────────────────────┐
│    L14 CU-Markdown → chunk (LangChain header + token splitter) → index │
│    L15 CU → agent (invoice fields → ephemeral agent → business review) │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 30-Second Domain 5 Cheat Sheet

```
Find info in a corpus?                       → Azure AI Search
  Exact keyword?                             → BM25                                 [L01]
  Meaning-based?                             → Vector                               [L02]
  Best for RAG?                              → Hybrid + Semantic Ranking            [L03]

Ingest docs into an index?
  Read from Blob / SQL / SharePoint?         → Indexer                              [L04]
  Enrich with OCR / split / NER / embed?     → Skillset (built-in skills)           [L05]
  Custom enrichment logic?                   → Custom Skill (Azure Function)        [L06]

Ground an agent on a corpus?
  Register the RAG agent?                    → Prompt Agent with instructions       [L07]
  Retrieval owned by your app?               → Manual RAG (retrieve→prompt→invoke)  [L08]
  Retrieval owned by the agent?              → Attach AI Search as an agent tool    (Domain 2 L06 pattern)

Extract from a document?
  Just OCR?                                  → CU prebuilt-read                     [L09]
  Text + tables + figures + reading order?   → CU prebuilt-layout                   [L10]
  Invoice / receipt / ID / contract?         → CU domain prebuilt                   [L11]
  Company-specific schema?                   → CU custom analyzer + baseAnalyzerId  [L12]
  Cross-file reasoning?                      → CU Pro mode (preview)                [L13]

Complex-doc RAG pipeline?                    → CU-Markdown → chunk → embed → Search [L14]
Agent that reasons over CU output?           → CU fields → ephemeral agent          [L15]
```

---

## Prereqs before you run anything

Steps 1–4 come from Domain 1. Steps 5–8 are Domain 5 additions.

1. **Azure subscription** with billing.
2. **Foundry resource** + `az login`.
3. **`Foundry User` role** on the Foundry resource.
4. **`.env` core:** `FOUNDRY_ENDPOINT`, `AZURE_OPENAI_ENDPOINT`, `DEFAULT_MODEL`, `EMBEDDING_MODEL`.
5. **`.env` Domain 5 — AI Search:**
   - `SEARCH_ENDPOINT` — separate Azure resource (created in Azure portal).
   - `SEARCH_INDEX` — a text-only index for L01.
   - `SEARCH_INDEX_VECTOR` — an index with a vector field + vectorizer for L02/L03/L14.
   - `SEARCH_INDEXER`, `SEARCH_SKILLSET` — names used by L04/L05.
6. **`.env` Domain 5 — Content Understanding:**
   - `CU_ENDPOINT` — services.ai.azure.com subdomain (or cognitiveservices).
   - `CU_API_VERSION=2025-11-01` (GA) or `2025-05-01-preview` for Pro mode.
7. **Blob Storage** for source documents (needed for the indexer + skillset + CU URLs).
   - `STORAGE_ACCOUNT`, `STORAGE_CONTAINER`, plus a SAS URL for whichever CU lesson you're running.
8. **Per-lesson env vars (when the lesson uses one):**
   - L10: `CU_LAYOUT_SOURCE_URL` = PDF Blob SAS URL.
   - L11 + L15: `SAMPLE_INVOICE_URL` = invoice PDF Blob SAS URL.
   - L12: `CU_SUPPORT_NOTICE_URL`.
   - L13: `CU_PRO_PACKAGE_URLS` = comma-separated Blob SAS URLs.
   - L14: `CU_MARKDOWN_SOURCE_URL`.

Sanity check: run L01 first (keyword search over a text index) — if the
index is populated and the query returns results, retrieval is wired.

---

## Glossary — Domain 5 terms

| Term | Beginner definition |
|------|--------------------|
| **Azure AI Search** | Managed search-as-a-service. Separate Azure resource. |
| **Data Source** | Where the indexer reads documents from (Blob / Cosmos / SQL / SharePoint). |
| **Indexer** | Scheduled job that pulls from a Data Source, runs a Skillset, writes to an Index. |
| **Skillset** | Named collection of enrichment steps (skills) that run at index time. |
| **Index** | The searchable store. Fields are typed; some are searchable, some are filterable, some are vector. |
| **Skill** | One step in a skillset. Built-in (OCR, Text Split, Language Detection, ...) or custom (your Function). |
| **BM25** | Term-frequency ranking algorithm. What "keyword search" uses. |
| **Vector search** | Similarity search over precomputed embeddings. `k_nearest_neighbors` by cosine. |
| **Hybrid search** | Fuses BM25 text results with vector results. Usually the RAG default. |
| **Semantic Ranking** | A cross-encoder that RE-RANKS your top N results — runs after BM25/hybrid. |
| **Vectorizer** | Server-side embedder attached to a vector field — lets you query with text instead of pre-computing embeddings. |
| **`VectorizableTextQuery`** | Python query that ships text and lets the vectorizer embed it server-side. |
| **`VectorizedQuery`** | Python query that ships a client-computed vector directly. |
| **Custom skill (WebApiSkill)** | Skill backed by an Azure Function. Strict I/O contract. |
| **Custom skill contract** | Input `{"values":[{"recordId","data"}]}`; return same shape with new fields in `data`. `recordId` must match request↔response. |
| **Content Understanding (CU)** | Async service for structured extraction from unstructured data. |
| **`prebuilt-read`** | CU analyzer — basic OCR: text, paragraphs, words. Lightweight. |
| **`prebuilt-layout`** | CU analyzer — text + tables + figures + reading order + Markdown output. RAG-preferred. |
| **`prebuilt-document`** | CU base analyzer for text + key-value pairs. Usually a `baseAnalyzerId` for custom. |
| **`prebuilt-invoice`** | CU domain analyzer for invoice fields (vendor, total, line items, dates). |
| **Domain-specific analyzers** | `prebuilt-receipt`, `prebuilt-idDocument`, `prebuilt-contract`, `prebuilt-w2`, `prebuilt-1003`, ... |
| **Custom analyzer** | Your `fieldSchema` on top of a `baseAnalyzerId`. |
| **`fieldSchema.method`** | How CU fills the field: `extract` (find in doc), `classify` (pick from enum), `generate` (LLM-authored). |
| **Standard mode** | One document at a time. GA API `2025-11-01`. |
| **Pro mode** | Multiple documents together, cross-file reasoning. Preview `2025-05-01-preview`. `.pdf/.tiff/image` inputs only. |
| **CU Markdown output** | Structured Markdown that survives chunking. Best RAG-ingest format for complex docs. |
| **RAG (Retrieval-Augmented Generation)** | Pattern: retrieve chunks → build a grounded prompt → invoke the model. |

---

## Common first-run failures

| Symptom | Root cause | Fix |
|---------|-----------|-----|
| L01: `0 results` | Index is empty | Run L04/L05 to populate; or point `SEARCH_INDEX` at a preloaded index |
| L02/L03: `No such field 'text_vector'` | Wrong index (must have a vector field + vectorizer) | Point `SEARCH_INDEX_VECTOR` at a vector-configured index |
| L03: `Semantic configuration 'default' not found` | Semantic ranking not configured on the index | Portal → Index → Semantic configuration → add one named `default` |
| L06: skill returns 400 in real pipeline | Response shape wrong | Return `{"values":[{"recordId":"<match>","data":{...},"errors":[],"warnings":[]}]}` |
| L08: `Agent not found: northwind-support-rag-agent` | L07 hasn't been run | Run L07 first — it creates the RAG agent |
| L09–L13: CU `cannot fetch file://` | Local paths won't work | Upload to Blob, generate SAS URL, set the lesson's env var |
| L11/L15: `SAMPLE_INVOICE_URL not set` | Missing env var | Set to a Blob SAS URL of an invoice PDF |
| L13: CU Pro mode error | Wrong API version or unsupported input | Set `CU_API_VERSION=2025-05-01-preview`; input must be `.pdf/.tiff/image` |
| L14: `Index missing 'chunk' field` | Target index schema mismatch | Ensure target index has `id`, `chunk`, `title` fields (matches merge_or_upload_documents call) |

---

## Files

| # | File | Syllabus bullet |
|---|---|---|
| 01 | `01_search_basic_query.py` | Query an AI Search index (BM25 keyword baseline) |
| 02 | `02_search_vector.py` | Vector-only search via VectorizableTextQuery |
| 03 | `03_search_hybrid_semantic.py` | Keyword vs Vector vs Hybrid+Semantic — side-by-side |
| 04 | `04_search_indexer_setup.py` | Create/update the indexer (Blob → index) |
| 05 | `05_search_skillset.py` | Create/update the built-in skillset |
| 06 | `06_search_custom_skill.py` | Custom skill contract (Azure Function payload) |
| 07 | `07_rag_agent_search_tool.py` | Register a RAG Prompt Agent |
| 08 | `08_rag_client_run.py` | Manual RAG orchestration (retrieve → prompt → invoke) |
| 09 | `09_cu_prebuilt_read.py` | CU prebuilt-read (basic OCR) |
| 10 | `10_cu_prebuilt_layout.py` | CU prebuilt-layout (tables + figures + reading order) |
| 11 | `11_cu_invoice.py` | CU prebuilt-invoice (domain analyzer) |
| 12 | `12_cu_custom_analyzer.py` | Custom analyzer via baseAnalyzerId + fieldSchema |
| 13 | `13_cu_pro_mode.py` | Pro mode — cross-document reasoning (preview) |
| 14 | `14_cu_markdown_for_rag.py` | CU-Markdown → chunk → index into AI Search |
| 15 | `15_cu_content_agent.py` | CU fields → ephemeral agent → business review |
| — | `skillset_configs/` | JSON skillset / indexer / index definitions |

## Reference docs

- [Hybrid search overview](../.context/azure-ai-docs/articles/search/hybrid-search-overview.md)
- [Skillsets](../.context/azure-ai-docs/articles/search/cognitive-search-defining-skillset.md)
- [Custom skill interface](../.context/azure-ai-docs/articles/search/cognitive-search-custom-skill-interface.md)
- [Agentic knowledge sources](../.context/azure-ai-docs/articles/search/agentic-knowledge-source-overview.md)
- [CU analyzer reference](../.context/azure-ai-docs/articles/ai-services/content-understanding/concepts/analyzer-reference.md)
- [CU Standard vs Pro modes](../.context/azure-ai-docs/articles/ai-services/content-understanding/how-to/content-understanding-foundry-classic.md)
- [CU overview](../.context/azure-ai-docs/articles/ai-services/content-understanding/overview.md)

---

## Syllabus sections

| Section | Topics |
|---------|--------|
| Retrieval + grounding pipelines | Ingest + index, search modes, enrichment skills, RAG ingestion, connect to agent tools |
| Extract content from documents | Multimodal pipelines (OCR + layout + fields), grounded representations, analyzers |

---

## Azure AI Search — the pipeline

```
Data Source (Blob / SQL / SharePoint / Cosmos)
        │
        ▼
    Indexer  ── reads documents + runs the skillset
        │
        ▼
    Skillset ── enrichment: OCR / Text Split / Language Detect / NER / PII / Translate / Embed
        │
        ▼
     Index   ── stored documents with typed searchable + vector fields
        │
        ▼
     Query   ── keyword (BM25) / vector / hybrid / semantic
        │
        ▼
   Results   ── with scores, highlights, and (for semantic) reranker scores
```

**Memory:** *Data Source → Indexer → Skillset → Index → Query. Skillsets run at INDEX time, not query time.*

---

## Search modes compared

| Mode | Mechanism | Best for |
|------|-----------|----------|
| **Keyword (BM25)** | Term frequency + IDF | Exact terms, known vocab |
| **Vector** | Embedding cosine similarity | Paraphrases, meaning |
| **Hybrid** | BM25 + vector combined | Both exact + semantic (most RAG) |
| **Semantic Ranking** | Cross-encoder re-ranks the top N | Final relevance boost on top of hybrid |

**Production RAG stack:** `Hybrid (BM25 + vector) + Semantic Ranking`.

**Python — three modes side-by-side (L03):**

```python
# Keyword-only
client.search(search_text=query, top=3)

# Vector-only
client.search(
    search_text=None,
    vector_queries=[VectorizableTextQuery(text=query, k_nearest_neighbors=10, fields="text_vector")],
)

# Hybrid + semantic
client.search(
    search_text=query,
    vector_queries=[VectorizableTextQuery(text=query, k_nearest_neighbors=10, fields="text_vector")],
    query_type=QueryType.SEMANTIC,
    semantic_configuration_name="default",
)
```

---

## Skillset skills — quick reference

| Skill | Purpose |
|-------|---------|
| **OCR** | Extract text from image/PDF content |
| **Text Split** | Chunk into pages/sentences — CRITICAL FOR RAG (without it, one doc = one entry) |
| **Language Detection** | Detect document language |
| **Key Phrase Extraction** | Extract topic phrases |
| **NER** | Extract named entities |
| **PII Detection** | Find + optionally redact PII |
| **Translation** | Translate content |
| **Azure OpenAI Embedding** | Generate a vector for each chunk (paired with Text Split) |
| **Merge / Shaper** | Combine multiple field values into one shape |
| **WebApiSkill (custom)** | Call your Azure Function with the standard contract |

**Custom skill contract — exact shape:**

```json
// Request (indexer → your Function)
{
  "values": [
    { "recordId": "0", "data": { "text": "input text" } }
  ]
}

// Response (your Function → indexer)
{
  "values": [
    { "recordId": "0",
      "data": { "result": "your output" },
      "errors": [],
      "warnings": [] }
  ]
}
```

`recordId` MUST match request↔response. Extra fields in `data` are passed through untouched.

---

## Content Understanding — analyzer decision tree

```
Have a document/image/audio/video?
    │
    ├── Just OCR (text only)?                                    → prebuilt-read (L09)
    ├── Text + tables + figures + reading order?                 → prebuilt-layout (L10)
    ├── Invoice / receipt / ID / contract / tax form?            → domain prebuilt (L11)
    │      (prebuilt-invoice, prebuilt-receipt, prebuilt-idDocument,
    │       prebuilt-w2, prebuilt-1003 …)
    ├── Company-specific schema?                                 → custom analyzer (L12)
    │      Set `baseAnalyzerId: prebuilt-document` + `fieldSchema`.
    │      `method` per field: extract | classify | generate.
    ├── Cross-document reasoning (multi-file)?                   → Pro mode (L13)
    │      `mode: "pro"` on the analyzer definition.
    │      Preview API `2025-05-01-preview`, `.pdf/.tiff/image` input only.
    └── Building a RAG ingest pipeline?                          → prebuilt-layout → Markdown → chunk (L14)
```

**Custom analyzer example (L12):**

```python
definition = {
    "baseAnalyzerId": "prebuilt-document",
    "fieldSchema": {
        "fields": {
            "ticket_id":         {"type": "string",  "method": "extract"},
            "sla_tier":          {"type": "string",  "method": "classify",
                                   "enum": ["Bronze","Silver","Gold","Platinum"]},
            "breach_penalty_usd":{"type": "number",  "method": "extract"},
            "summary":           {"type": "string",  "method": "generate"},
        }
    }
}
create_analyzer("northwind-support-notice", definition)
result = analyze("northwind-support-notice", document_url)
```

---

## Standard vs Pro mode

| | Standard (GA) | Pro (preview) |
|--|--------------|--------------|
| API version | `2025-11-01` | `2025-05-01-preview` |
| Reasoning scope | Within one item | Across multiple items (cross-reference, validate) |
| Input types | All | `.pdf`, `.tiff`, image only |
| Cost / latency | Lower | Higher |
| Use case | Invoices, receipts, transcripts, RAG prep | Mortgage packages, compliance bundles, multi-doc onboarding |

---

## CU → Markdown → RAG ingestion (L14)

The current best-practice ingestion for complex real-world documents:

```
PDF / DOCX / image
        │
    prebuilt-layout   (or a custom analyzer)
        │
        ▼
   Markdown output   ← tables + headings + reading order preserved
        │
    Header-splitter → sub-Markdown documents per section
        │
    Token-splitter  → chunks ~500–800 tokens with overlap
        │
    Azure OpenAI embedding → vectors per chunk
        │
    AI Search index (chunk + vector + title + parent_id fields)
        │
    Hybrid + semantic query at runtime → agent
```

Why Markdown? Tables and structure survive chunking; agents/LLMs parse Markdown natively; heading hierarchy is a free retrieval signal.

---

## RAG path comparison

| Path | Infrastructure | When |
|------|---------------|------|
| **File Search tool** (Foundry-managed) | Foundry blob + vector store | Prototype, < 100 docs, zero infra |
| **AI Search tool** (agent-attached) | AI Search service | Production, hybrid + semantic ranking, skillset enrichment |
| **Manual client RAG** | AI Search SDK + your code | Full control — custom reranking, filters, hybrid strategy |
| **CU-Markdown → Search** | CU + text split + embed + AI Search | Complex docs (tables, figures, mixed content) — the "real production" pipeline |

---

# Lesson 01 — AI Search Baseline Keyword Query

**You'll learn:** the simplest possible search call — text in, ranked BM25 results out; the baseline for every later lesson.
**Prereqs:** `SEARCH_ENDPOINT` + `SEARCH_INDEX` in `.env`; the index has been populated (from portal, L04, or elsewhere).
**Time:** ~3 min.

**Concept:** `search_client.search(search_text="...")` runs a BM25 query
against your index. Results carry `@search.score` (higher = better).
Baseline mode — no vectors, no semantic ranking, no filters.

**Code:**

```python
# 01_search_basic_query.py
from _shared.search_client import search_client
from _shared.config import settings


def main() -> None:
    client = search_client()
    results = client.search(search_text="refund", select=["chunk", "title"])
    for r in results:
        print(f"score={r['@search.score']:.4f}  title={r.get('title')}")
        print(r.get("chunk", "")[:200])
        print("---")
    print(f"\nindex={settings().search_index}  endpoint={settings().search_endpoint}")
```

**Expected output:** several result blocks with score + title + chunk preview.

**Key points:**
- If you see 0 results, the index is empty — run L04 + L05 first, or point at a preloaded index.
- `select=[...]` returns just those fields — cheaper than pulling the whole doc.
- BM25 misses paraphrases — "refund" won't match "get my money back". Vector search (L02) fixes that.

---

# Lesson 02 — Vector Search

**You'll learn:** semantic search via embeddings — retrieval based on meaning, not literal terms.
**Prereqs:** `SEARCH_INDEX_VECTOR` in `.env` — an index with a vector field (`text_vector`) and a vectorizer.
**Time:** ~5 min.

**Concept:** `VectorizableTextQuery` ships your query text; the index's
attached vectorizer embeds it server-side; nearest-neighbor search runs
over precomputed vectors. Contrast with `VectorizedQuery` where YOU
compute the embedding client-side.

**Code:**

```python
# 02_search_vector.py
from azure.search.documents.models import VectorizableTextQuery
from _shared.config import settings
from _shared.search_client import search_client


def main() -> None:
    client = search_client(settings().search_index_vector)
    results = client.search(
        search_text=None,  # vector-only, no BM25 side
        vector_queries=[
            VectorizableTextQuery(
                text="how do I get my money back",
                k_nearest_neighbors=5,
                fields="text_vector",
            )
        ],
        select=["chunk", "title"],
        top=5,
    )
    for r in results:
        print(f"score={r['@search.score']:.4f}  title={r.get('title')}")
        print(r.get("chunk", "")[:200], "\n---")
```

**Expected output:** results whose chunks discuss refunds — even though the query never used the word "refund".

**Key points:**
- The index must have a vectorizer OR you must pass a client-computed vector via `VectorizedQuery`.
- `k_nearest_neighbors` controls recall; `top` controls how many you take from those.
- Vector-only misses exact-term matches (SKUs, error codes). Combine with BM25 (hybrid) in L03.

---

# Lesson 03 — Hybrid + Semantic Ranking

**You'll learn:** why hybrid + semantic ranking is the production RAG choice; see three modes side-by-side on the same query.
**Prereqs:** vector index has a `semantic_configuration_name="default"` set up in the portal.
**Time:** ~10 min.

**Concept:** Three passes on the same query:
- Keyword-only (BM25).
- Vector-only.
- Hybrid + semantic (BM25 + vector fused, then cross-encoder re-ranks).

The reranker reads the actual content of the top N results and rewrites the
ranking — usually the best-quality retrieval you can get without training
a custom model.

**Code:**

```python
# 03_search_hybrid_semantic.py (excerpts)
def _print_top(mode: str, results) -> None:
    print(f"\n=== {mode} ===")
    for i, r in enumerate(list(results)[:3], 1):
        score = r.get("@search.reranker_score") or r.get("@search.score")
        print(f"  {i}. score={score:.4f}  {r.get('title')}")
        print(f"     {r.get('chunk', '')[:140]}")


# Hybrid + Semantic
client.search(
    search_text=_QUERY,
    vector_queries=[VectorizableTextQuery(text=_QUERY, k_nearest_neighbors=10, fields="text_vector")],
    query_type=QueryType.SEMANTIC,
    semantic_configuration_name="default",
    select=["chunk", "title"],
    top=3,
)
```

**Expected output:** three ranked lists — semantic reranker scores in the last block are usually different from BM25/vector scores in the first two.

**Key points:**
- `@search.reranker_score` (0.0–4.0) exists ONLY on semantic-query results — check for it, fall back to `@search.score`.
- Semantic ranking is billed separately + region-limited. Check availability before assuming it's on.
- Never run semantic ranking on more than the top ~50 — the reranker is expensive per document.

---

# Lesson 04 — Indexer Setup

**You'll learn:** provision an AI Search indexer that reads from Blob, runs a skillset, and writes into an index.
**Prereqs:** `skillset_configs/indexer.json` present; source Blob container has documents.
**Time:** ~5 min.

**Concept:** `create_or_update_indexer` is idempotent — safe to run
repeatedly. The JSON body defines: source connection, target index,
skillset to run, field mappings, scheduling.

**Code:**

```python
# 04_search_indexer_setup.py
import json
from pathlib import Path
from azure.search.documents.indexes.models import SearchIndexer
from _shared.search_client import indexer_client


_INDEXER_JSON = Path(__file__).parent / "skillset_configs" / "indexer.json"


def main() -> None:
    client = indexer_client()
    body = json.loads(_INDEXER_JSON.read_text())
    indexer = SearchIndexer(**body)
    client.create_or_update_indexer(indexer)
    print(f"indexer '{indexer.name}' saved. Run it via .run_indexer() or in the portal.")
```

**Expected output:** `indexer 'northwind-indexer' saved.`

**Key points:**
- The indexer runs on a schedule (or on-demand via `.run_indexer()`), NOT synchronously here.
- Field mappings translate source columns/blob metadata into index fields — usually where a broken indexer breaks.
- Change tracking on Blob = last-modified time. Reset via `.reset_indexer()` if you need a full re-index.

---

# Lesson 05 — Skillset

**You'll learn:** attach OCR / split / language detection / key phrases / embedding to the indexer via a skillset.
**Prereqs:** `skillset_configs/skillset.json` present.
**Time:** ~5 min.

**Concept:** A skillset is a graph of skills. Each skill takes some input
fields and produces some output fields; downstream skills reference those
outputs. Idempotent — `create_or_update_skillset` handles both.

**Code:**

```python
# 05_search_skillset.py
import json
from pathlib import Path
from azure.search.documents.indexes.models import SearchIndexerSkillset
from _shared.search_client import indexer_client


_SKILLSET_JSON = Path(__file__).parent / "skillset_configs" / "skillset.json"


def main() -> None:
    client = indexer_client()
    body = json.loads(_SKILLSET_JSON.read_text())
    skillset = SearchIndexerSkillset(**body)
    client.create_or_update_skillset(skillset)
    print(f"skillset '{skillset.name}' saved.")
```

**Expected output:** `skillset 'northwind-skillset' saved.`

**Key points:**
- Order matters — chain OCR → split → embed correctly by wiring outputs to inputs.
- For RAG the Text Split skill is non-negotiable — without it, one document = one index entry.
- Attach the skillset to your indexer (L04's indexer JSON references it by name).

---

# Lesson 06 — Custom Skill (Azure Function Contract)

**You'll learn:** the exact JSON payload your Azure Function must accept + return to plug into a Search skillset.
**Prereqs:** understanding of the built-in skills (L05).
**Time:** ~10 min.

**Concept:** A custom skill is an Azure Function called by the indexer.
The contract is strict:

- Input: `{"values": [{"recordId", "data"}, ...]}`.
- Output: same shape, with your enrichments in each `data`.
- `recordId` MUST match request↔response so the indexer can pair items.

**Code (contract handler + a demo transform):**

```python
# 06_search_custom_skill.py
def transform(record_data: dict) -> dict:
    text = record_data.get("text", "")
    upper = text.upper()
    tier = next((t for t in ("BRONZE","SILVER","GOLD","PLATINUM") if t in upper), None)
    return {"normalized_text": text.strip().lower(), "sla_tier": tier}


def handle_batch(payload: dict) -> dict:
    out = []
    for record in payload.get("values", []):
        out.append({
            "recordId": record.get("recordId"),
            "data": transform(record.get("data", {})),
            "errors": [],
            "warnings": [],
        })
    return {"values": out}
```

**Expected output:** JSON with normalized_text + sla_tier per record.

**Key points:**
- Never skip `recordId` — mismatched ids break indexer pairing silently.
- Return `errors`/`warnings` arrays (can be empty) — the indexer surfaces them in the run history.
- Deploy as an Azure Function; wire into the skillset via `WebApiSkill` pointing at the function URL.

---

# Lesson 07 — Create the RAG Prompt Agent

**You'll learn:** register a Prompt Agent whose only job is to answer strictly from provided sources — the "R + G" side of RAG.
**Prereqs:** L01 works. `PROJECT_ENDPOINT` in `.env`.
**Time:** ~3 min.

**Concept:** The system prompt is doing the heavy lifting — enforce
"answer ONLY from provided sources", "cite the URL", "say 'I don't know'
otherwise". The retrieval side lives in L08 (your app owns it) or in an
attached AI Search tool (Foundry portal setup).

**Code:**

```python
# 07_rag_agent_search_tool.py
from azure.ai.projects.models import PromptAgentDefinition
from _shared.config import settings
from _shared.foundry_client import project_client

AGENT_NAME = "northwind-support-rag-agent"

_SYSTEM_PROMPT = """
You are a customer support assistant for Northwind Technology Services.

Answer the customer's question using ONLY the provided sources.
After your answer, cite the source URL you used.
If the sources do not contain the answer, say:
"I don't have that information in the available knowledge base."
Then suggest contacting support@northwind.com.

Never invent policies, prices, refund rules, or timelines.
"""


def main() -> None:
    client = project_client()
    agent = client.agents.create_version(
        agent_name=AGENT_NAME,
        definition=PromptAgentDefinition(
            model=settings().default_model,
            instructions=_SYSTEM_PROMPT,
        ),
    )
    print(f"Agent {agent.name} v{agent.version} created.")
```

**Expected output:** `Agent northwind-support-rag-agent v1 created.`

**Key points:**
- L08 depends on this — run L07 first.
- For fully-managed RAG where the agent owns retrieval, attach AI Search as an agent tool in the Foundry portal (a variation of Domain 2 L06's pattern).
- Guardrails still apply — put Prompt Shields (Domain 1 L09/L10) around this in production.

---

# Lesson 08 — Manual RAG Orchestration

**You'll learn:** the "app owns retrieval" pattern — search → build prompt with sources → invoke the agent → return grounded answer.
**Prereqs:** L07 has been run; `SEARCH_INDEX` populated.
**Time:** ~5 min.

**Concept:** Use when you need custom retrieval logic — filters, reranking,
hybrid strategy, per-user access control. Contrast with the fully-managed
alternative (AI Search attached to the agent as a tool) where the agent
handles retrieval itself.

**Code:**

```python
# 08_rag_client_run.py (excerpts)
def _retrieve(question: str, top: int = 3) -> str:
    client = search_client()
    results = client.search(
        search_text=question,
        vector_queries=[VectorizableTextQuery(text=question, k_nearest_neighbors=top, fields="text_vector")],
        select=["chunk", "title", "parent_id"],
        top=top,
    )
    return "\n\n".join(
        f"[Source title: {r.get('title','unknown')}]\n[Parent ID: {r.get('parent_id','')}]\n{r.get('chunk','')}"
        for r in results
    )


def ask(question: str) -> str:
    sources = _retrieve(question)
    prompt = (
        "You are a customer support agent for Northwind Technology Services.\n"
        "Answer using only the sources provided below. If the sources do not contain "
        "enough information, say so.\n\n"
        f"Sources:\n{sources}\n\n"
        f"Customer question:\n{question}\n"
    )
    project = project_client()
    openai = project.get_openai_client()
    r = openai.responses.create(
        extra_body={"agent_reference": {"type": "agent_reference", "name": AGENT_NAME}},
        input=prompt,
    )
    return r.output_text
```

**Expected output:** an answer that cites source titles/URLs, or `"I don't have that information..."` if retrieval misses.

**Key points:**
- Retrieval quality is the ceiling for answer quality — invest in hybrid + semantic (L03) before tuning the prompt.
- `parent_id` + `title` are the citation carriers — keep them in your index for grounded answers.
- Watch for over-retrieval: stuffing 20 chunks into the prompt hurts more than it helps. 3–5 is usually right.

---

# Lesson 09 — CU prebuilt-read (Basic OCR)

**You'll learn:** get text out of a document/image with the minimal CU analyzer; the lightest-weight starting point.
**Prereqs:** `CU_ENDPOINT` in `.env`; a URL CU can fetch (Blob SAS or public URL).
**Time:** ~5 min.

**Concept:** `prebuilt-read` outputs text as Markdown-style paragraphs.
No tables, no figures, no sections — just words. Use when the doc is
plain enough that layout doesn't matter (article text, transcript, note).

**Code:**

```python
# 09_cu_prebuilt_read.py
import os
from _shared.cu_client import analyze


def main() -> None:
    src = os.environ.get(
        "CU_READ_SOURCE_URL",
        "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-sample-data-files/master/Language/example.pdf",
    )
    result = analyze("prebuilt-read", src)
    print("status:", result.get("status"))
    contents = result.get("result", {}).get("contents", [])
    if contents:
        print(contents[0].get("markdown", "")[:500])
```

**Expected output:** `status: Succeeded` + first 500 chars of extracted text.

**Key points:**
- Async under the hood — `analyze()` polls to completion before returning.
- For tables + figures + reading order, use `prebuilt-layout` (L10).
- Barcode + formula recognition come along for free when present.

---

# Lesson 10 — CU prebuilt-layout (Tables + Figures)

**You'll learn:** structure-preserving extraction — Markdown output with tables + figures + section headings intact.
**Prereqs:** `CU_LAYOUT_SOURCE_URL` = Blob SAS URL of a PDF with tables/figures.
**Time:** ~5 min.

**Concept:** `prebuilt-layout` produces Markdown that survives chunking.
Tables come back as GitHub-flavored Markdown; figures are described.
Reading order is preserved even for multi-column layouts. This is the
input for L14's RAG pipeline.

**Code:**

```python
# 10_cu_prebuilt_layout.py
import os
from _shared.cu_client import analyze


def main() -> None:
    src = os.environ.get("CU_LAYOUT_SOURCE_URL")
    if not src:
        raise SystemExit("Set CU_LAYOUT_SOURCE_URL to a PDF URL (Blob SAS is easiest).")
    result = analyze("prebuilt-layout", src)
    doc = result["result"]["contents"][0]
    print(f"pages: {len(doc.get('pages', []))}")
    print(f"tables: {len(doc.get('tables', []))}")
    print(f"figures: {len(doc.get('figures', []))}")
    print(f"sections: {len(doc.get('sections', []))}")
    print(doc.get("markdown", "")[:800])
```

**Expected output:** counts of pages/tables/figures/sections + Markdown preview showing GFM tables and headings.

**Key points:**
- **Best RAG-ingest analyzer for complex docs** — L14 uses it.
- Markdown output preserves table structure through downstream chunking; plain text doesn't.
- For a lightweight text-only alternative, use `prebuilt-read` (L09).

---

# Lesson 11 — CU prebuilt-invoice (Domain Analyzer)

**You'll learn:** use a domain-specific prebuilt to extract vendor / customer / total / line items / dates from any invoice PDF.
**Prereqs:** `SAMPLE_INVOICE_URL` = invoice PDF Blob SAS URL.
**Time:** ~5 min.

**Concept:** Foundry ships dozens of domain analyzers — invoice, receipt,
idDocument, w2, 1040, 1003 (mortgage), contract, ... Each carries a
purpose-built field schema, so you skip the custom-analyzer work when a
prebuilt covers your case.

**Code:**

```python
# 11_cu_invoice.py
import os
from _shared.config import SAMPLE_DATA
from _shared.cu_client import analyze


def main() -> None:
    invoice_url = os.environ.get("SAMPLE_INVOICE_URL")
    if not invoice_url:
        raise SystemExit("Set SAMPLE_INVOICE_URL to a Blob SAS URL of an invoice PDF.")
    if invoice_url.startswith("file://"):
        raise SystemExit("CU cannot fetch file:// URLs — upload to Blob and use a SAS URL.")

    result = analyze("prebuilt-invoice", invoice_url)
    fields = result["result"]["contents"][0].get("fields", {})
    for name, data in fields.items():
        print(f"  {name}: {data}")
```

**Expected output:** invoice fields (VendorName, InvoiceId, InvoiceTotal, LineItems, ...) with confidence scores.

**Key points:**
- **Old code hardcoded `file://` — now requires `SAMPLE_INVOICE_URL`.** CU cannot fetch local files.
- If your domain isn't covered by a prebuilt, use a custom analyzer with `baseAnalyzerId: prebuilt-document` (L12).
- Domain analyzers already come with the right field schema — don't rebuild it.

---

# Lesson 12 — Custom Analyzer (baseAnalyzerId + fieldSchema)

**You'll learn:** define company-specific fields on top of a prebuilt base; pick per-field extraction method (extract / classify / generate).
**Prereqs:** `CU_SUPPORT_NOTICE_URL` for the analyze step (analyzer creation still runs without it).
**Time:** ~10 min.

**Concept:** `baseAnalyzerId` inherits base capabilities (OCR + document
structure). `fieldSchema.fields[*].method` selects HOW each field gets
filled:
- `extract` — find literal value in the doc.
- `classify` — pick one value from an enum.
- `generate` — LLM writes it (summary, explanation).

**Code:**

```python
# 12_cu_custom_analyzer.py
_DEFINITION = {
    "description": "Extract Northwind support-notice fields.",
    "baseAnalyzerId": "prebuilt-document",
    "fieldSchema": {
        "fields": {
            "ticket_id":          {"type": "string",  "method": "extract"},
            "customer_name":      {"type": "string",  "method": "extract"},
            "sla_tier":           {"type": "string",  "method": "classify",
                                    "enum": ["Bronze","Silver","Gold","Platinum"]},
            "breach_penalty_usd": {"type": "number",  "method": "extract"},
            "summary":            {"type": "string",  "method": "generate"},
        }
    },
}

create_analyzer(ANALYZER_ID, _DEFINITION)
result = analyze(ANALYZER_ID, source_url)
```

**Expected output:** analyzer created; if source URL provided, structured fields per your schema.

**Key points:**
- `method: classify` requires `enum` — the classifier picks from that list.
- `method: generate` uses a Foundry LLM under the hood — costs more, watch cardinality.
- Analyzer ids are project-scoped — reuse across many callers.

---

# Lesson 13 — Pro Mode (Cross-Document Reasoning)

**You'll learn:** analyze several related documents together — reason across them (consistency checks, validation, joint field extraction).
**Prereqs:** `CU_API_VERSION=2025-05-01-preview`; `CU_PRO_PACKAGE_URLS` = comma-separated Blob SAS URLs.
**Time:** ~15 min (preview, slow).

**Concept:** Pro mode is CU's cross-file reasoning. Same analyzer surface,
add `"mode": "pro"` to the definition and pass a LIST of URLs to
`analyze`. Best for compliance/underwriting scenarios where you need
"do these documents agree with each other?"

**Code:**

```python
# 13_cu_pro_mode.py (excerpt)
_DEFINITION = {
    "description": "Cross-document review of a mortgage application package.",
    "baseAnalyzerId": "prebuilt-document",
    "mode": "pro",
    "fieldSchema": {
        "fields": {
            "consistency": {
                "type": "object",
                "method": "generate",
                "properties": {
                    "borrower_name_matches": {"type": "boolean"},
                    "borrower_dob_matches":  {"type": "boolean"},
                    "income_supports_loan":  {"type": "boolean"},
                    "notes": {"type": "string"},
                },
            }
        }
    },
    "referenceData": {"policy": "Underwriting Guide 2026-v4"},
}

urls = [u.strip() for u in os.environ["CU_PRO_PACKAGE_URLS"].split(",")]
result = analyze(ANALYZER_ID, urls)   # list = multi-doc
```

**Expected output:** consistency object with per-check booleans + a `notes` field explaining any discrepancy.

**Key points:**
- **Preview only** — requires `CU_API_VERSION=2025-05-01-preview`.
- Inputs restricted to `.pdf`, `.tiff`, image types.
- Cost + latency higher than Standard mode — use when the cross-file reasoning actually earns it.
- `referenceData` lets you inject a policy string the LLM can compare against.

---

# Lesson 14 — CU-Markdown → Chunk → Search Index

**You'll learn:** the production RAG ingest pipeline for complex documents — CU produces Markdown, LangChain chunks by headers + tokens, embeddings go into AI Search.
**Prereqs:** `CU_MARKDOWN_SOURCE_URL` = PDF Blob SAS URL; `SEARCH_INDEX` populated schema (chunk / title / id fields).
**Time:** ~15 min.

**Concept:** Chunking is the RAG variable that most affects quality.
- Structure-aware split first (`MarkdownHeaderTextSplitter`) → preserve section boundaries.
- Token split within sections (`RecursiveCharacterTextSplitter` ~500–800 tokens, 100 overlap) → controlled chunk size.
- Push to index with `merge_or_upload_documents` (upsert semantics).

**Code:**

```python
# 14_cu_markdown_for_rag.py (excerpts)
def _cu_markdown(source_url: str) -> str:
    result = analyze("prebuilt-layout", source_url)
    return result["result"]["contents"][0].get("markdown", "")


def _chunk(markdown: str) -> list[dict]:
    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[("#", "h1"), ("##", "h2"), ("###", "h3")],
    )
    docs = header_splitter.split_text(markdown)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    chunks = text_splitter.split_documents(docs)
    return [{"id": f"chunk-{i}", "chunk": c.page_content, "title": c.metadata.get("h1", "")}
             for i, c in enumerate(chunks)]


markdown = _cu_markdown(src)
docs = _chunk(markdown)
client = search_client(settings().search_index)
client.merge_or_upload_documents(documents=docs)
```

**Expected output:** `CU markdown: N chars`, `chunked into M pieces`, `uploaded to index ...`.

**Key points:**
- **`prebuilt-layout` is what makes this pipeline work** — its Markdown output is why chunking preserves structure.
- Chunk-size tradeoff: bigger chunks = more context per hit but fewer distinct hits per query. 500–800 tokens is a good starting range.
- `merge_or_upload_documents` = upsert; safe to re-run.

---

# Lesson 15 — CU → Agent (Structured Extraction → Reasoning)

**You'll learn:** the "CU as data prep, agent as reasoning layer" pattern; extract structured fields, then hand them to an ephemeral agent for judgment.
**Prereqs:** `SAMPLE_INVOICE_URL` = invoice PDF Blob SAS URL.
**Time:** ~5 min.

**Concept:** Divide labor: CU extracts precisely (fields), the agent
reasons flexibly (approve / flag / recommend). Contrast with L08 where
the agent grounds on retrieved text — here it grounds on
already-structured field-value pairs.

The lesson uses an **ephemeral agent** (`instructions=` inline) — no
portal setup, no missing-agent lookup. Older versions referenced a
`northwind-support` agent that didn't exist.

**Code:**

```python
# 15_cu_content_agent.py (excerpts)
_INSTRUCTIONS = (
    "You are a Northwind operations reviewer. Given extracted invoice fields, "
    "produce a business-friendly summary, an approval status, any issues found, "
    "and the recommended next step. Do not invent values that aren't in the fields."
)


def main() -> None:
    fields_dump = _extract_fields()   # uses SAMPLE_INVOICE_URL, blocks file://
    project = project_client()
    openai = project.get_openai_client()
    r = openai.responses.create(
        model=settings().default_model,
        instructions=_INSTRUCTIONS,
        input=(
            "Review this invoice using only the extracted fields below.\n\n"
            "Your task:\n"
            "1. Summarize the invoice in business-friendly language.\n"
            "2. Provide an approval status.\n"
            "3. Identify any issues found.\n"
            "4. Recommend the next step.\n\n"
            f"Extracted invoice fields:\n{fields_dump}\n"
        ),
    )
    print(r.output_text)
```

**Expected output:** a four-part review (summary, approval status, issues, next step) grounded only in the extracted fields.

**Key points:**
- Ephemeral agent = no portal setup, no missing-agent errors.
- Reject `file://` URLs — CU can't fetch local paths.
- For cross-invoice reasoning (batch approval, budget checks), switch to CU Pro mode (L13) + a more sophisticated agent.

---

# Common Exam Traps

| Trap | Truth |
|------|-------|
| "Semantic Ranking is the same as vector search" | ❌ — semantic re-ranks BM25/hybrid results; vector finds by embedding distance |
| "Skillsets run at query time" | ❌ — skillsets run at INDEX time; queries hit the already-enriched documents |
| "Custom skill can return any JSON shape" | ❌ — must be `{"values":[{"recordId","data","errors","warnings"}]}`; `recordId` must match |
| "CU Pro mode = higher quality for one document" | ❌ — Pro = MULTI-document cross-reasoning; preview |
| "`baseAnalyzerId` is optional in custom analyzers" | ❌ — always required; inherit from a prebuilt (usually `prebuilt-document`) |
| "prebuilt-layout extracts just text like prebuilt-read" | ❌ — layout adds tables, figures, sections, reading order, Markdown |
| "CU accepts local file paths" | ❌ — CU fetches server-side; needs a URL it can reach (Blob SAS) |
| "Custom analyzer field method is always `extract`" | ❌ — three methods: `extract` (literal), `classify` (enum), `generate` (LLM) |
| "AI Search is part of Foundry" | ❌ — separate Azure resource; you provision it independently |
| "Vector-only beats hybrid for RAG" | ❌ — hybrid + semantic reranking is the recommended default; vector-only misses exact-term matches |

---

> The 30-second cheat sheet lives at the [top of this README](#30-second-domain-5-cheat-sheet)
> — scroll up any time an exam question makes you second-guess which lesson covers it.
