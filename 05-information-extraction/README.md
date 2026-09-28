# Domain 5 — Information Extraction (15–20%)

> Run any lesson: `uv run python 05-information-extraction/<file>.py` · Prereqs: `.env` filled, `az login` completed. See root [README.md](../README.md).
> **Scope warning:** these are runnable learning samples, not production pipelines. A successful call proves only the stated code path — not extraction quality, ACL enforcement, retrieval accuracy, or production readiness.

---

## What this domain teaches

Two complementary services for information extraction and retrieval:

| Need | Service | Lesson range |
|------|---------|-------------|
| Find evidence across many indexed files | Azure AI Search | 00–08, 17–20 |
| Extract structure from one submitted document | Azure Content Understanding | 09–16 |

```
┌── Stage 1: Search — Index + Queries (00–03) ──────────────────────┐
│  Create index → keyword → vector → hybrid + semantic              │
│  Understand all three modes before building the pipeline          │
└────────────────────────────────────────────────────────────────────┘
┌── Stage 2: Search — Ingestion Pipeline (04–06) ────────────────────┐
│  Blob data source + indexer → skillset (chunk + embed)            │
│  Custom skill contract (local demo)                               │
└────────────────────────────────────────────────────────────────────┘
┌── Stage 3: Manual RAG with Foundry Agent (07–08) ──────────────────┐
│  Create constrained agent → app-owned retrieve → prompt → answer  │
└────────────────────────────────────────────────────────────────────┘
┌── Stage 4: Content Understanding — Prebuilt Analyzers (09–11) ─────┐
│  prebuilt-read (OCR) → prebuilt-layout (structure)                │
│  prebuilt-invoice (domain fields)                                 │
└────────────────────────────────────────────────────────────────────┘
┌── Stage 5: Content Understanding — Custom and Advanced (12–16) ────┐
│  Custom analyzer → Pro cross-document → Markdown for RAG          │
│  CU fields → agent review → multimodal RAG handoff               │
└────────────────────────────────────────────────────────────────────┘
┌── Stage 6: Deploy, Monitor, Govern (17–20) ────────────────────────┐
│  Custom skill deploy → monitoring → Blob identity                  │
│  Managed Search agent tool                                        │
└────────────────────────────────────────────────────────────────────┘
┌── Stage 7: Agentic Retrieval — Knowledge Sources + KB (21–27) ─────┐
│  Blob / search-index / web knowledge sources → knowledge base      │
│  Retrieve → answer synthesis → reasoning-effort tiers              │
└────────────────────────────────────────────────────────────────────┘
```

> **Runtime note.** `_search_rest.py` and `_shared/cu_client.py` send an Entra ID bearer token (`https://search.azure.com/.default` and `https://cognitiveservices.azure.com/.default`). A token proves identity only; the caller still needs the data-plane role on the target Search service or Foundry resource.

---

## Service mental model

### Search ingestion pipeline

```
Azure Blob Storage container (source files)
  └─ northwind-blob-datasource
       └─ SEARCH_INDEXER (reads Blob, runs skillset)
            └─ SEARCH_SKILLSET
                 ├─ SplitSkill: /document/content → /document/pages/* (2000 chars, 500 overlap)
                 └─ AzureOpenAIEmbeddingSkill: each page → text_vector
                      └─ SEARCH_INDEX_VECTOR: one document per chunk
                           └─ BM25 keyword | HNSW vector | RRF hybrid | semantic reranker
```

The indexer drives ingestion. The skillset runs at indexing time — never at query time. The vectorizer converts query text to a vector at query time; it does NOT create document vectors.

### Content Understanding pipeline

```
Reachable HTTPS URL (PDF / image / video)
  └─ CU analyzer (prebuilt or custom)
       └─ Submit → 202 Accepted + Operation-Location → poll → result.contents[0]
            ├─ .markdown       (prebuilt-read, prebuilt-layout)
            └─ .fields         (prebuilt-invoice, custom analyzers)
```

CU is a document extraction service, not a corpus search engine. Search retrieves across many indexed files; CU extracts structure from one submitted document.

---

## Glossary

| Term | Meaning |
|------|---------|
| **Data source** | Named Search connection to Blob source. Contains managed-identity `ResourceId` connection string. |
| **Indexer** | Search job: reads source → runs skillset → writes index documents. |
| **Skillset** | Ordered enrichment graph at ingestion time only. |
| **Index projection** | One-to-many mapping: one Blob file → many chunk documents. Never manually map `parent_id`. |
| **Vectorizer** | Query-time text→embedding converter on the index. Must match indexing embedding model. |
| **BM25** | Keyword term-frequency scoring. Good for exact terms, IDs, rare vocabulary. |
| **Vector search** | HNSW nearest-neighbor over embeddings. Good for paraphrases and intent. |
| **Hybrid search** | BM25 + vector combined by reciprocal rank fusion (RRF). |
| **Semantic ranker** | L2 reranker over initial BM25/RRF candidates. Does NOT scan full corpus. |
| **WebApiSkill** | Custom enrichment: Search POSTs batched records to your HTTPS endpoint at ingestion. |
| **CU analyzer** | Reusable CU definition. GA `2025-11-01` analyzes one input per request. |
| **Standard mode** | GA CU mode (`2025-11-01`). Single input. Extract/classify/generate fields with optional confidence and grounding. |
| **Pro mode** | Retired preview (`2025-05-01-preview`, retired July 15, 2026). Multi-document reasoning in one request. Replace with per-document analysis plus app-side comparison (L13). |
| **Markdown RAG** | CU → structure-preserving Markdown → header+recursive chunking → embedding. |
| **Security trimming** | Enforcing document access BEFORE evidence is sent to model. ACL filter on query, not on prompt. |

---

## Setup

### Environment variables

```env
# Azure AI Search
SEARCH_ENDPOINT=https://<service>.search.windows.net
SEARCH_INDEX_VECTOR=northwind-docs-vector
SEARCH_INDEXER=northwind-indexer
SEARCH_SKILLSET=northwind-skillset

# Blob storage
STORAGE_ACCOUNT=<account-name>
STORAGE_CONTAINER=northwind-docs
AZURE_SUBSCRIPTION_ID=<subscription-id>
AZURE_RESOURCE_GROUP=<resource-group>

# Azure OpenAI (used by Search embedding skill + vectorizer)
AZURE_OPENAI_ENDPOINT=https://<resource>.openai.azure.com
EMBEDDING_MODEL=text-embedding-3-large

# Foundry project (L07, L08, L15, L20)
PROJECT_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<project>
DEFAULT_MODEL=<chat-deployment-name>

# Content Understanding
CU_ENDPOINT=https://<resource>.services.ai.azure.com
CU_API_VERSION=2025-11-01

# Managed Search agent (L20 only)
SEARCH_CONNECTION_NAME=<foundry-project-connection-name>
SEARCH_INDEX=northwind-docs-vector

# Agentic retrieval — knowledge sources + knowledge base (L21–L27)
SEARCH_KNOWLEDGE_BASE=northwind-kb
SEARCH_BLOB_CONNECTION=ResourceId=/subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Storage/storageAccounts/<account>
SEARCH_BLOB_CONTAINER=northwind-docs
SEARCH_KS_BLOB=northwind-blob-ks              # L21-L23 create these names; L24 references them
SEARCH_KS_INDEX=northwind-index-ks
SEARCH_KS_WEB=northwind-web-ks                # opt-in: unset means L24 has no web source
SEARCH_WEB_ALLOWED_DOMAIN=learn.microsoft.com
SEARCH_WEB_BLOCKED_DOMAIN=bing.com
```

`DefaultAzureCredential` resolves to `az login` on workstation, managed/workload identity in Azure.

Required roles:

| Principal | Scope | Role | Why |
|-----------|-------|------|-----|
| Search service MI | Storage container | Storage Blob Data Reader | Indexer reads Blob files |
| Search service MI | Azure OpenAI resource | Cognitive Services OpenAI User | Embedding skill + vectorizer |
| Lab user/workload | Search service | Search Index Data Contributor + Search Service Contributor | Schema management + queries |
| Lab user/workload | Foundry project | Foundry User | L07 agent creation + L08 call |
| CU caller | CU resource | Cognitive Services Content Understanding Contributor | L12/L13 analyzer creation |
| Search service MI | Storage account | Storage Blob Data Contributor; Reader and Data Access | L29/L30 knowledge-store object/file and table projections |
| Search service MI | Foundry resource | Cognitive Services User | L29 OCR billing; L30 Content Understanding skill |

### Safe run order

1. Upload source PDFs to `STORAGE_CONTAINER` (from `_shared/sample_data/`)
2. Enable Search service system-assigned MI; assign roles above
3. `uv run python 05-information-extraction/00_search_index_setup.py` — create index
4. `uv run python 05-information-extraction/05_search_skillset.py` — create skillset
5. `uv run python 05-information-extraction/04_search_indexer_setup.py --run --wait` — ingest
6. Verify indexer `success` in portal before querying
7. Run L01–L03 queries
8. `uv run python 05-information-extraction/07_rag_prompt_agent.py` — create RAG agent
9. `uv run python 05-information-extraction/08_rag_client_run.py` — run RAG
10. Run L09–L16 independently (need `CU_ENDPOINT` and file URLs)
11. Run L12–L13 without flags first (local preflight); `--apply` creates analyzers and `--delete` removes them
12. Run L17–L20 as needed (each has `--apply`/`--run` guards)
13. Agentic retrieval: L21 → L22 → L23 (build knowledge sources) → L24 (compose KB) → L25 (retrieve) → L26 (answer synthesis); L27 is docs-only
14. Enrichment: L28 is a local runbook; run L29–L30 without flags first, then `--apply` after the role and billing checks, and `--delete` when finished

### Costs and side effects

| Lesson(s) | What it writes / costs |
|-----------|----------------------|
| L00 | Replaces Search index definition (persistent schema change) |
| L05 | Replaces Search skillset |
| L04 `--run` | Starts indexer → Blob reads + embedding calls → writes index documents |
| L01–L03 | Search query capacity |
| L07 | Creates persistent agent version |
| L08 | Search query + model tokens |
| L09–L14 | CU analysis calls (billable); L12/L13 create persistent analyzers |
| L15 | CU invoice analysis + model tokens |
| L16 `--apply` | CU analysis (billable); does NOT write to Search |
| L17 `--apply [--run]` | Replaces skillset/indexer; `--run` starts indexer |
| L20 `--enable --apply` | Creates persistent agent version |
| L18, L19 `--run` | Read-only; no writes |
| L21 `--apply` | Creates blob KS + auto-generated data source/skillset/index/indexer (persistent) |
| L22 `--apply` | Creates search-index KS wrapper (persistent) |
| L23 `--apply` | Creates web KS; retrieve calls are billed by Bing |
| L24 `--apply` | Creates knowledge base (persistent) |
| L25 `--apply` | Runs retrieve; LLM tokens billed by AOAI |
| L26 `--apply` | Runs retrieve + answer synthesis; more LLM tokens billed |
| L27, L28 | Preflight-only; no cloud calls |
| L29 `--apply` | Creates index, skillset, indexer (runs at once); image extraction + OCR billed; knowledge-store blobs/tables persist after `--delete` |
| L30 `--apply` | Creates index, skillset, indexer (runs at once); Content Understanding billed per page; image blobs persist after `--delete` |

---

## Decision tables

### Retrieval mode selection

| Mode | Lesson | When to use | Limitation |
|------|--------|-------------|-----------|
| Keyword/BM25 | 01 | Exact terms, IDs, SKUs, rare vocabulary | Misses paraphrases |
| Vector | 02 | Semantic similarity, paraphrase recall | Misses exact rare terms |
| Hybrid + semantic | 03, 08 | General RAG — best of both, semantically boosted | Semantic ranker region/SKU dependent |

### Manual RAG vs Managed Search tool

| | Manual RAG (07–08) | Managed tool (20) |
|--|-------------------|------------------|
| Retrieval control | App owns query, filters, ranking | Agent decides when to query |
| ACL enforcement | App applies OData filter before prompt | Must configure tool with security filter |
| Use when | Custom ranking, explicit audit, ACL required | Standard Foundry integration, simpler setup |

### Content Understanding analyzer selection

| Analyzer | Lesson | Input | Output |
|----------|--------|-------|--------|
| `prebuilt-read` | 09 | Any doc | Text/Markdown (no table structure) |
| `prebuilt-layout` | 10 | Any doc | Markdown with tables, figures, sections |
| `prebuilt-invoice` | 11 | Invoice PDF | Structured invoice fields |
| Custom standard | 12 | Any doc | Your defined fields (extract/classify/generate) |
| Cross-document validation | 13 | One analyze per document + app comparison | Consistency findings (replaces retired Pro mode) |
| Content Understanding skill in Search | 30 | Blob files through an indexer | Markdown chunks with page and polygon metadata |

---

## Practice questions

After completing this domain, use the [Domain 5 question review](questions/README.md). The new ingestion supplement reinforces page and ACL provenance without replacing the Search asset lifecycle.

## Lesson map

| # | File | Runnable objective | Status |
|---|------|--------------------|--------|
| 00 | `00_search_index_setup.py` | Create/replace vector index schema | Persistent schema change |
| 01 | `01_search_basic_query.py` | BM25 keyword retrieval | Needs populated index |
| 02 | `02_search_vector.py` | Vector semantic retrieval | Needs vectorizer + vectors |
| 03 | `03_search_hybrid_semantic.py` | Hybrid + semantic comparison | Needs semantic ranker enabled |
| 04 | `04_search_indexer_setup.py` | Create data source + indexer; optionally start | `--run` triggers ingestion |
| 05 | `05_search_skillset.py` | Create chunk + embed skillset | Persistent skillset change |
| 06 | `06_search_custom_skill.py` | Custom WebApiSkill contract (local) | No cloud call; local only |
| 07 | `07_rag_prompt_agent.py` | Create constrained manual-RAG agent | Creates persistent agent version |
| 08 | `08_rag_client_run.py` | App-owned hybrid retrieve → agent → answer | Needs L07 agent |
| 09 | `09_cu_prebuilt_read.py` | Basic OCR → Markdown | CU_READ_SOURCE_URL optional |
| 10 | `10_cu_prebuilt_layout.py` | Layout-preserving extraction | CU_LAYOUT_SOURCE_URL required |
| 11 | `11_cu_invoice.py` | Invoice field extraction | SAMPLE_INVOICE_URL required |
| 12 | `12_cu_custom_analyzer.py` | Custom schema with confidence/grounding + review routing; schema proposal | `--apply` creates persistent analyzer; `--delete` cleans up |
| 13 | `13_cu_cross_document_validation.py` | Cross-document validation on GA (replaces retired Pro mode) | `--apply` creates analyzer + one analyze per file |
| 14 | `14_cu_markdown_for_rag.py` | `prebuilt-layout` or `prebuilt-documentSearch` Markdown → chunk inspection | Inspect only; no indexing |
| 15 | `15_cu_content_agent.py` | CU invoice fields → ephemeral agent review | SAMPLE_INVOICE_URL required |
| 16 | `16_cu_multimodal_rag.py` | CU media → provenance-safe records | `--apply` for cloud call |
| 17 | `17_search_custom_skill_deploy.py` | Wire WebApiSkill into pipeline | `--apply` for cloud; endpoint required |
| 18 | `18_search_monitoring.py` | Search indexer health snapshot | `--run` for live check |
| 19 | `19_blob_identity_paths.py` | Verify Blob data-plane identity | `--run` for live check |
| 20 | `20_managed_search_agent_tool.py` | Managed Foundry agent with Search tool | `--enable --apply --run` |
| 21 | `21_knowledge_source_blob.py` | Create indexed **blob** knowledge source (auto data source + skillset + index + indexer) | `--apply` sends PUT |
| 22 | `22_knowledge_source_search_index.py` | Wrap existing search index as a knowledge source | `--apply` sends PUT |
| 23 | `23_knowledge_source_web.py` | Remote **web** knowledge source (Grounding with Bing Custom Search) | `--apply` sends PUT |
| 24 | `24_agentic_knowledge_base.py` | Knowledge base referencing multiple knowledge sources | `--apply` sends PUT |
| 25 | `25_agentic_retrieve.py` | Call retrieve action; print subqueries + references + activity | `--apply` invokes retrieve |
| 26 | `26_agentic_answer_synthesis.py` | Retrieve with `answerSynthesis` → synthesized answer + citations | `--apply` invokes retrieve |
| 27 | `27_agentic_reasoning_effort_preflight.py` | Reasoning-effort tiers (`minimal`/`low`/`medium`/`auto`) walkthrough | No `--apply`; docs-only |
| 28 | `28_sharepoint_indexer_acls_preflight.py` | SharePoint indexer ACL ingestion (preview) — permissions/index/mappings/resync runbook | Local reference only |
| 29 | `29_search_ocr_knowledge_store.py` | OCR images via `normalized_images`, merge text, project to a knowledge store | Local by default; `--apply` creates + runs; `--delete` |
| 30 | `30_search_cu_skill_citations.py` | Content Understanding skill: chunks with page/polygon citations, cross-page tables | Local by default; `--apply` creates + runs; `--delete` |

---

## Stage 1 — Search: Index and Queries (lessons 00–03)

These lessons introduce Azure AI Search's three retrieval modes. Run L00 to create the schema, ingest via L04–L05, then compare how keyword, vector, and hybrid ranking behave on the same query. Understanding retrieval mode differences is the core exam topic for this domain.

### 00 — Create Vector Index

**Question answered:** What schema must exist before Search can ingest and retrieve chunked vector documents?

**Background.** The index defines field contracts, vector dimensions, and semantic configuration. It must exist before ingestion. Running it again replaces the schema — incompatible changes (different dimensions or key type) may break existing data.

```bash
uv run python 05-information-extraction/00_search_index_setup.py
```

**Code path.**
1. `load_definition(index.json)` resolves env-var placeholders
2. `put("indexes", index)` → Entra-authenticated REST PUT `/indexes/<name>`
3. Print `index '<name>' saved.`

**What to watch in the output.** `index '<name>' saved.` A 403 = missing index-management role. A 409 = dimension or key-field conflict with existing index.

**Exam cues.** Index is a prerequisite for ingestion, not a trigger for it. Vector dimensions and the embedding model must match the skillset and vectorizer consistently.

**References:** [Azure AI Search overview](https://learn.microsoft.com/azure/search/search-what-is-azure-search) · [Create a search index](https://learn.microsoft.com/azure/search/search-what-is-an-index) · [Integrated vectorization](https://learn.microsoft.com/azure/search/vector-search-integrated-vectorization)

---

### 01 — Keyword Search (BM25)

**Question answered:** How does BM25 keyword search rank exact-term matches?

**Background.** BM25 scores results by term frequency and inverse document frequency. It finds chunks that contain the exact search term — great for policy terms, IDs, SKUs, and rare vocabulary. It completely misses paraphrases. Compare with lesson 02 to see what vector search finds that BM25 doesn't.

```bash
uv run python 05-information-extraction/01_search_basic_query.py
```

**Code path.**
1. `search_client(index_name)` → `client.search(search_text="refund", select=[chunk,title])`
2. Print `@search.score`, title, and 200-char chunk preview per result

**What to watch in the output.** BM25 scores (e.g., 2.3, 1.8) for chunks mentioning "refund". Chunks that discuss "money back" or "return policy" without using the word "refund" will score zero.

**Exam cues.** BM25 score is not comparable to vector scores or semantic reranker scores. No score threshold is appropriate without evaluation data.

**References:** [Full-text search in Azure AI Search](https://learn.microsoft.com/azure/search/search-lucene-query-architecture) · [Hybrid search overview](https://learn.microsoft.com/azure/search/hybrid-search-overview)

---

### 02 — Vector Search

**Question answered:** How does vector search retrieve semantically similar chunks that don't share exact terms?

**Background.** `VectorizableTextQuery` sends query text to the index's configured vectorizer (which calls the embedding model), then performs HNSW approximate nearest-neighbor search over `text_vector`. Finds paraphrases ("how do I get my money back" finds refund chunks). Misses exact rare terms that vector space compresses. Requires: populated `text_vector` field, matching embedding dimensions, and vectorizer configured.

```bash
uv run python 05-information-extraction/02_search_vector.py
```

**Code path.**
1. `VectorizableTextQuery(text, k_nearest_neighbors=5, fields="text_vector")`
2. `client.search(search_text=None, vector_queries=[...], top=5)` → print scores + previews

**What to watch in the output.** Chunks about refunds surface even without the word "refund". Scores are cosine-distance based — not comparable to BM25 scores from lesson 01.

**Exam cues.** `k_nearest_neighbors` controls vector candidates; `top` controls returned results. `search_text=None` disables BM25 — lesson 03 combines both.

**References:** [Vector search overview](https://learn.microsoft.com/azure/search/vector-search-overview) · [Vector search query how-to](https://learn.microsoft.com/azure/search/vector-search-how-to-query)

---

### 03 — Hybrid + Semantic Reranking

**Question answered:** How does hybrid search with semantic reranking compare to keyword-only and vector-only retrieval?

**Background.** Hybrid search combines BM25 and HNSW candidates via reciprocal rank fusion (RRF), then semantic ranker reranks the top RRF results. This is the production RAG baseline: exact matches AND meaning, semantically boosted. The semantic ranker does NOT scan the full corpus — it only reranks candidates already surfaced. Requires semantic ranker enabled on the Search service (region/SKU dependent).

```bash
uv run python 05-information-extraction/03_search_hybrid_semantic.py
```

**Code path.**
1. Three `client.search()` calls on `_QUERY = "does the refund window include the trial period?"`
2. `_print_top()` shows rank, score, title, preview for top-3 per mode

**What to watch in the output.** Compare which chunks appear across three columns. Semantic reranker score (`@search.reranker_score`) is a different scale from BM25/vector scores — do not compare across modes.

**Exam cues.** Semantic ranker ≠ vector search. It reranks initial candidates only. A high semantic score does not mean the answer is correct — evaluate on labeled data.

**References:** [Hybrid search overview](https://learn.microsoft.com/azure/search/hybrid-search-overview) · [Semantic search overview](https://learn.microsoft.com/azure/search/semantic-search-overview) · [Hybrid search ranking](https://learn.microsoft.com/azure/search/hybrid-search-ranking)

---

## Stage 2 — Search: Ingestion Pipeline (lessons 04–06)

The three components that fill the index: indexer (orchestrator), skillset (enrichment), and custom skill (domain logic). Run in order 05 → 04; L06 is local-only.

### 04 — Blob Data Source and Indexer

**Question answered:** How do you provision the Blob ingestion connection and start the indexer?

**Background.** The indexer reads from a Blob data source, runs the skillset on each file, and writes chunk documents to the index. It uses the Search service's managed identity (not the calling user's identity) to read Blob. `--run` starts the indexer; `--wait` polls until terminal status (5-min timeout). A "started" indexer is not done — wait for `success` before querying.

```bash
uv run python 05-information-extraction/04_search_indexer_setup.py
uv run python 05-information-extraction/04_search_indexer_setup.py --run --wait
```

**Code path.**
1. `load_definition(data_source.json)` → PUT `/datasources`; `load_definition(indexer.json)` → PUT `/indexers`
2. With `--run`: `indexer_client().run_indexer(name)`
3. With `--wait`: poll `get_indexer_status().last_result` until terminal or timeout

**What to watch in the output.** `data source saved`, `indexer saved`. With `--run --wait`: status polls until `success`. A `401`/`403` with the indexer = the Search MI lacks Blob Data Reader or OpenAI User roles.

**Exam cues.** The Search MI (not the calling user) reads Blob and calls OpenAI. `ResourceId` connection string in data_source.json uses MI, not a storage key. Starting is not the same as completion.

**References:** [Search indexer overview](https://learn.microsoft.com/azure/search/search-indexer-overview) · [Blob indexer](https://learn.microsoft.com/azure/search/search-blob-storage-integration) · [Search managed identities](https://learn.microsoft.com/azure/search/search-howto-managed-identities-storage)

---

### 05 — Split + Embedding Skillset

**Question answered:** How does the indexer chunk documents and generate embeddings at ingestion time?

**Background.** The skillset defines enrichment at ingestion time only — not at query time. SplitSkill breaks `/document/content` into overlapping pages (2000-char, 500-char overlap). AzureOpenAIEmbeddingSkill embeds each page. Index projections write one child Search document per chunk, mapping `parent_id` automatically. Do not manually map `parent_id` — it breaks change tracking.

```bash
uv run python 05-information-extraction/05_search_skillset.py
```

**Code path.**
1. `load_definition(skillset.json)` resolves `AZURE_OPENAI_ENDPOINT` + `EMBEDDING_MODEL` placeholders
2. PUT `/skillsets/<name>` → print `skillset '<name>' saved.`

**What to watch in the output.** `skillset '<name>' saved.` A 400 = JSON structure mismatch. Embedding dimension in skillset must match the index's `text_vector` field and vectorizer.

**Exam cues.** Skillsets run at indexing, not query time. The vectorizer at query time must use the same model/dimensions as the embedding skill at index time.

**References:** [Skillset concepts](https://learn.microsoft.com/azure/search/cognitive-search-working-with-skillsets) · [Defining skillsets](https://learn.microsoft.com/azure/search/cognitive-search-defining-skillset) · [Integrated vectorization](https://learn.microsoft.com/azure/search/vector-search-integrated-vectorization)

---

### 06 — Custom Skill Contract (local)

**Question answered:** What payload shape does a WebApiSkill expect, and how does a custom transform implement it?

**Background.** A WebApiSkill POSTs a batch of records to your HTTPS endpoint during indexing. Each record has `recordId` and `data`. Your endpoint must return the same shape with transformed data plus optional `errors`/`warnings`. This lesson implements and exercises the contract locally — no cloud call. Lesson 17 wires this contract into the actual Search pipeline.

```bash
uv run python 05-information-extraction/06_search_custom_skill.py
```

**Code path.**
1. `main()` builds two sample records
2. `handle_batch()` calls `transform()` per record → normalizes text + detects SLA tier
3. Print JSON output matching the WebApiSkill contract

**What to watch in the output.** Two records with `normalized_text` and `sla_tier`. `GOLD` and `PLATINUM` tiers detected. A record with no matching tier → `sla_tier: null`.

**Exam cues.** WebApiSkill contract: `{values: [{recordId, data}]}` in, same shape out with transformed `data`. Per-record errors don't fail other records. Production skill needs HTTPS, Entra auth, batch limits, and timeout.

**References:** [Custom skill interface](https://learn.microsoft.com/azure/search/cognitive-search-custom-skill-web-api) · [Custom skill example](https://learn.microsoft.com/azure/search/cognitive-search-custom-skill-scale)

---

## Stage 3 — Manual RAG with Foundry Agent (lessons 07–08)

App-owned retrieval: the application queries Search, builds the prompt, and calls a constrained agent. Compare with lesson 20 where the agent owns retrieval.

### 07 — Manual-RAG Prompt Agent

**Question answered:** How do you create a constrained Foundry agent that answers only from application-supplied sources?

**Background.** This agent has no Azure AI Search tool — the application (lesson 08) performs retrieval and supplies chunks as prompt context. The system prompt instructs it to answer only from provided sources and never invent policies or prices. Each run creates a new agent version — clean up versions in production.

```bash
uv run python 05-information-extraction/07_rag_prompt_agent.py
```

**Code path.**
1. `project_client()` → `agents.create_version(AGENT_NAME, PromptAgentDefinition(model, instructions))`
2. Print agent name and version

**What to watch in the output.** `Agent northwind-manual-rag-agent v<version> created.` Run lesson 08 after to use it.

**Exam cues.** This agent is NOT a managed Search agent — it has no Search tool. L08 does retrieval in application code and passes chunks as prompt text.

**References:** [Azure AI Foundry RAG overview](https://learn.microsoft.com/azure/foundry/concepts/retrieval-augmented-generation) · [RAG evaluators](https://learn.microsoft.com/azure/foundry/concepts/evaluation-evaluators/rag-evaluators)

---

### 08 — App-Owned Manual RAG

**Question answered:** How does an application own the full retrieval + prompt + agent pipeline?

**Background.** The application controls retrieval: it runs a hybrid query (BM25 + vector), formats the top-3 chunks as source blocks with title/URL, and supplies them in the prompt to the L07 agent. The model answers only from supplied sources and cites the URL. No ACL filter is applied here — do not use with mixed-permission content without adding an OData security filter.

```bash
uv run python 05-information-extraction/08_rag_client_run.py
```

**Code path.**
1. `_retrieve(question)` → hybrid query with `VectorizableTextQuery` → format 3 chunks as source blocks
2. `project.get_openai_client()` → `responses.create()` with `agent_reference` (L07 agent) and source blocks
3. Print `output_text`

**What to watch in the output.** A grounded refund answer or "I don't have that information" refusal + cited source URL. If the agent hallucinates, check index population.

**Exam cues.** Manual RAG = app owns retrieval, filtering, ranking. Prompt instructions do NOT enforce authorization. ACL must trim Search results before model input.

**References:** [RAG overview in Foundry](https://learn.microsoft.com/azure/foundry/concepts/retrieval-augmented-generation) · [Hybrid search overview](https://learn.microsoft.com/azure/search/hybrid-search-overview) · [Security trimming](https://learn.microsoft.com/azure/search/search-security-trimming-for-azure-search)

---

## Stage 4 — Content Understanding: Prebuilt Analyzers (lessons 09–11)

Three prebuilt CU analyzers: plain OCR, structure-preserving layout, and invoice field extraction. All use the same async submit-poll pattern.

### 09 — CU `prebuilt-read` (Basic OCR)

**Question answered:** How do you extract plain text from a document using Content Understanding?

**Background.** `prebuilt-read` extracts words, paragraphs, and formulas as Markdown. No table or figure structure — use `prebuilt-layout` (lesson 10) for that. The same async pattern as all CU analyzers: submit URL → 202 + `Operation-Location` → poll → consume result. CU fetches the URL server-side; `file://` paths don't work.

```bash
uv run python 05-information-extraction/09_cu_prebuilt_read.py
```

**Code path.**
1. `analyze("prebuilt-read", src)` → POST to CU endpoint → poll until succeeded
2. Print `status` and first 500 chars of `contents[0].markdown`

**What to watch in the output.** `status: succeeded` and a Markdown text preview. No table syntax — that's expected for `prebuilt-read`.

**Exam cues.** `prebuilt-read` = OCR text only. `prebuilt-layout` = structure. These are different analyzers, not options on the same call.

**References:** [Content Understanding overview](https://learn.microsoft.com/azure/ai-services/content-understanding/overview) · [Document overview](https://learn.microsoft.com/azure/ai-services/content-understanding/document/overview) · [Prebuilt analyzers](https://learn.microsoft.com/azure/ai-services/content-understanding/concepts/prebuilt-analyzers)

---

### 10 — CU `prebuilt-layout` (Structure-Preserving)

**Question answered:** How do you preserve tables, figures, and reading order in extracted Markdown?

**Background.** `prebuilt-layout` extracts pages, tables, figures, sections, and reading order as Markdown. Tables become `| col | col |` Markdown syntax; figures are referenced. This is better RAG evidence than flattened OCR for documents with structure. Does NOT extract domain-specific fields — use `prebuilt-invoice` (lesson 11) for those.

```bash
uv run python 05-information-extraction/10_cu_prebuilt_layout.py
```

**Code path.**
1. `CU_LAYOUT_SOURCE_URL` → `analyze("prebuilt-layout")` → poll
2. Print page/table/figure/section counts + first 800 chars of `markdown`

**What to watch in the output.** Table count > 0 and Markdown with `| col |` syntax. Compare to lesson 09 on the same document to see the structural difference.

**Exam cues.** Use structured document (PDF with tables) to demonstrate the difference. `prebuilt-layout` output is NOT directly vector-searchable without embedding and index upload.

**References:** [Content Understanding document elements](https://learn.microsoft.com/azure/ai-services/content-understanding/document/elements) · [CU Markdown output](https://learn.microsoft.com/azure/ai-services/content-understanding/document/markdown)

---

### 11 — CU `prebuilt-invoice`

**Question answered:** How do you extract structured fields (vendor, total, line items) from an invoice PDF?

**Background.** `prebuilt-invoice` extracts VendorName, CustomerName, InvoiceDate, InvoiceTotal, Items, and more as a structured dict in `contents[0].fields`. This is extraction, not payment approval — a field's presence doesn't prove correctness. Validate totals/dates against business rules. Lesson 15 shows how to pass extracted fields to a model for bounded review.

```bash
uv run python 05-information-extraction/11_cu_invoice.py
```

**Code path.**
1. Validate `SAMPLE_INVOICE_URL` (rejects `file://`)
2. `analyze("prebuilt-invoice", invoice_url)` → poll → print `contents[0].fields`

**What to watch in the output.** A structured dict with VendorName, InvoiceTotal, InvoiceDate, Items. Missing fields mean CU couldn't extract them — inspect the source PDF layout.

**Exam cues.** CU fetches the URL server-side — upload to Blob, generate SAS URL, set `SAMPLE_INVOICE_URL`. Extraction ≠ validation; a field present doesn't mean correct.

**References:** [Prebuilt invoice analyzer](https://learn.microsoft.com/azure/ai-services/document-intelligence/prebuilt/invoice) · [CU prebuilt analyzers](https://learn.microsoft.com/azure/ai-services/content-understanding/concepts/prebuilt-analyzers)

---

## Stage 5 — Content Understanding: Custom and Advanced (lessons 12–16)

Custom schemas with confidence and grounding, cross-document validation, Markdown chunking for RAG, and the CU→agent→multimodal handoff patterns.

### 12 — Custom CU Analyzer with confidence and grounding

**Question answered:** How do you define a domain-specific field schema, prove where each value came from, and route uncertain values to people?

**Background.** A custom analyzer adds a `fieldSchema` to a `baseAnalyzerId` (`prebuilt-document`). Field methods: `extract` (value as written), `classify` (map to an `enum`), `generate` (model-produced value — not source truth). In GA `2025-11-01`, confidence and grounding are opt-in: `config.estimateFieldSourceAndConfidence: true` returns a 0–1 `confidence` and a `source` location for every field, and per-field `estimateSourceAndConfidence` overrides it. **`extract` fields must set `estimateSourceAndConfidence: true`.** To discover fields for a new document type, the utility analyzer `prebuilt-documentFieldSchema` proposes a starting schema from a sample.

```bash
# Preflight: validate and print the analyzer definition; no Azure call
uv run python 05-information-extraction/12_cu_custom_analyzer.py

# Propose a schema from a sample (runtime-only SAS URL in your shell)
CU_SUPPORT_NOTICE_URL='<https-blob-sas-url>' uv run python 05-information-extraction/12_cu_custom_analyzer.py --propose-schema

# Create the analyzer (persistent), analyze the sample, then clean up
CU_SUPPORT_NOTICE_URL='<https-blob-sas-url>' uv run python 05-information-extraction/12_cu_custom_analyzer.py --apply
uv run python 05-information-extraction/12_cu_custom_analyzer.py --delete
```

**Code path.**
1. `validate_definition()` rejects `extract` fields without `estimateSourceAndConfidence` and `classify` fields without an `enum`.
2. `--propose-schema` → `analyze("prebuilt-documentFieldSchema", url)` → print the proposed fields for review.
3. `--apply` → `create_analyzer()` (PUT, polls the operation) → `analyze()` → `review_queue()` prints value, confidence, source, and `needs_review` (below 0.80 or missing confidence).
4. `--delete` → `delete_analyzer()`.

**What to watch in the output.** `REVIEW` rows for low-confidence fields, each with a `source` such as `D(1,…)` (page + polygon) the reviewer can open. `summary` is generated; treat it as a draft even with high confidence.

**Roles.** Cognitive Services Content Understanding Reader can analyze; Contributor can create/update but not delete; Owner can delete.

**Exam cues.** Per-field confidence plus source location → `estimateFieldSourceAndConfidence`. Labeled samples improve accuracy but do not add confidence. `enableSegment` splits content; it does not add confidence. Propose a schema for a new document type → `prebuilt-documentFieldSchema`.

**References:** [Create a custom analyzer](https://learn.microsoft.com/azure/ai-services/content-understanding/tutorial/create-custom-analyzer) · [Analyzer reference: `estimateFieldSourceAndConfidence`](https://learn.microsoft.com/azure/ai-services/content-understanding/concepts/analyzer-reference) · [Confidence, grounding, and labeled samples](https://learn.microsoft.com/azure/ai-services/content-understanding/document/analyzer-improvement) · [Prebuilt and utility analyzers](https://learn.microsoft.com/azure/ai-services/content-understanding/concepts/prebuilt-analyzers)

---

### 13 — Cross-document validation (replaces retired Pro mode)

**Question answered:** How do you check consistency across related documents now that CU Pro mode is retired?

**Background.** Standard mode analyzes one file per request; it is the only mode in GA `2025-11-01`, whose analyze `inputs` array accepts a single item. Pro mode (`2025-05-01-preview`) accepted several related files in one request and reasoned across them, optionally against reference data — the exam still uses it as "multiple files → pro, single file → standard". That preview API was retired on July 15, 2026 and returns HTTP 410. Agentic mode (`2026-06-01-preview`) reasons over one document for calculations and validation; it is not multi-file. The current pattern: extract the same identity fields from each document with confidence and grounding, then compare them in application code.

```bash
# Preflight: analyzer JSON and comparison rules; no Azure call
uv run python 05-information-extraction/13_cu_cross_document_validation.py

# Analyze each package document (runtime-only SAS URLs), then clean up
CU_PACKAGE_SOURCE_URLS='<sas-1>,<sas-2>,<sas-3>' uv run python 05-information-extraction/13_cu_cross_document_validation.py --apply
uv run python 05-information-extraction/13_cu_cross_document_validation.py --delete
```

**Code path.**
1. `_DEFINITION` classifies `document_type` and extracts `borrower_name` and `date_of_birth` with `estimateSourceAndConfidence`.
2. `--apply` → `create_analyzer()` → one `analyze()` call per URL.
3. `consistency_report()` normalizes case and whitespace, lists consistent fields, mismatches (value per document), and review items below 0.80 confidence with their source location.

**What to watch in the output.** `mismatched.borrower_name` shows which document disagrees; `review` lists low-confidence values to check before accepting a match.

**Exam cues.** Single file, extract/classify/generate → standard mode. Multiple related files reasoned together, or validation against reference data → Pro mode on the exam; in current services, per-document extraction plus deterministic comparison (or agentic mode per document).

**References:** [What's new in Content Understanding](https://learn.microsoft.com/azure/ai-services/content-understanding/whats-new) · [Migrate from preview to GA](https://learn.microsoft.com/azure/ai-services/content-understanding/how-to/migration-preview-to-ga) · [Agentic mode](https://learn.microsoft.com/azure/ai-services/content-understanding/concepts/agentic-mode)

---

### 14 — CU Markdown for RAG Chunking

**Question answered:** Which analyzer produces RAG-ready Markdown, and how do you inspect chunk boundaries?

**Background.** `prebuilt-layout` Markdown preserves headers, tables, hyperlinks, and figures without a language model. `prebuilt-documentSearch` is the RAG analyzer: layout Markdown plus figure descriptions, chart/diagram analysis, handwritten annotations, and a one-paragraph summary; it uses the resource's default model deployments. `prebuilt-read` is raw OCR text, and `prebuilt-documentFieldSchema` proposes a field schema — neither produces RAG-optimized Markdown. `MarkdownHeaderTextSplitter` splits on H1/H2/H3, then `RecursiveCharacterTextSplitter` (800 chars, 100 overlap) cuts further. This lesson prints chunks for inspection only — it does NOT embed or index them.

```bash
CU_MARKDOWN_SOURCE_URL='<https-blob-sas-url>' uv run python 05-information-extraction/14_cu_markdown_for_rag.py
CU_MARKDOWN_SOURCE_URL='<https-blob-sas-url>' uv run python 05-information-extraction/14_cu_markdown_for_rag.py --analyzer prebuilt-documentSearch
```

**Code path.**
1. `analyze(--analyzer, CU_MARKDOWN_SOURCE_URL)` → `contents[0].markdown` (+ the summary field for `prebuilt-documentSearch`).
2. `MarkdownHeaderTextSplitter` → `RecursiveCharacterTextSplitter` → print count + first chunk.

**What to watch in the output.** Chunk count and first chunk. Tables should stay together within a chunk. `prebuilt-documentSearch` adds a summary line and figure descriptions inside the Markdown.

**Exam cues.** RAG-optimized Markdown with semantic structure → `prebuilt-documentSearch`. Layout plus tables/QR codes without a language model → `prebuilt-layout`. Raw text only, cheapest → `prebuilt-read`. These chunks are NOT indexed; use L04/L05 (integrated skillset) or generate client-side embeddings with provenance fields.

**References:** [Prebuilt analyzers](https://learn.microsoft.com/azure/ai-services/content-understanding/concepts/prebuilt-analyzers) · [CU Markdown output](https://learn.microsoft.com/azure/ai-services/content-understanding/document/markdown) · [CU build RAG solution tutorial](https://learn.microsoft.com/azure/ai-services/content-understanding/tutorial/build-rag-solution)

---

### 15 — CU Fields → Agent Review

**Question answered:** How do you separate CU extraction from bounded model reasoning over extracted fields?

**Background.** Two-stage pipeline: CU `prebuilt-invoice` extracts fields; an ephemeral Foundry agent with inline instructions produces a business-friendly review. The agent is created inline — no pre-created agent needed. Model output is a proposed review, NOT automated approval — validate fields against deterministic rules and require human approval for consequential actions.

```bash
uv run python 05-information-extraction/15_cu_content_agent.py
```

**Code path.**
1. `_extract_fields()` → `analyze("prebuilt-invoice")` → format fields as prompt text
2. `project_client()` → `create_version()` with inline `_INSTRUCTIONS` → `responses.create()` with field text
3. Print output_text

**What to watch in the output.** Business summary, approval status, issues, next step. If the agent invents values not in the extracted fields, tighten the system prompt.

**Exam cues.** CU extraction ≠ model reasoning. Model generates proposed decisions — they require validation. Two separate billing events: CU analysis + model tokens.

**References:** [CU build RAG solution tutorial](https://learn.microsoft.com/azure/ai-services/content-understanding/tutorial/build-rag-solution) · [RAG evaluators](https://learn.microsoft.com/azure/foundry/concepts/evaluation-evaluators/rag-evaluators)

---

### 16 — Multimodal CU → RAG Records

**Question answered:** How do you convert CU analysis of documents, images, or video into bounded provenance-safe RAG records?

**Background.** Selects the right prebuilt CU analyzer by file extension (prebuilt-layout for docs, prebuilt-imageSearch for images, prebuilt-videoSearch for video), then converts the result to bounded records (max 20 items, max 4000 chars). SAS query credentials are stripped from source metadata. Default run is a local preflight; `--apply` submits to CU. Records are NOT uploaded to Search — add a validated ingestion worker with vector generation.

```bash
uv run python 05-information-extraction/16_cu_multimodal_rag.py
uv run python 05-information-extraction/16_cu_multimodal_rag.py --apply --source <https-url>
```

**Code path.**
1. `analyzer_for(url)` → choose by extension; `source_metadata(url)` → strip SAS query
2. With `--apply`: `analyze(analyzer, url)` → poll → cap at 20 records → print JSON

**What to watch in the output.** Preflight: config checks. With `--apply`: JSON records with chunk, title, source, and CU content. Source URL in records has credentials stripped.

**Exam cues.** Extension determines analyzer — this is not MIME validation. Production needs validated MIME routing, malware scanning, ownership checks, and a durable ingestion worker.

**References:** [CU video overview](https://learn.microsoft.com/azure/ai-services/content-understanding/video/overview) · [CU image overview](https://learn.microsoft.com/azure/ai-services/content-understanding/image/overview) · [CU document overview](https://learn.microsoft.com/azure/ai-services/content-understanding/document/overview)

---

## Stage 6 — Deploy, Monitor, Govern (lessons 17–20)

Production-readiness patterns: wiring the custom skill into Search, monitoring indexer health, verifying identity paths, and using the managed Search agent tool.

### 17 — Custom Skill Deploy

**Question answered:** How do you wire lesson 06's WebApiSkill contract into the actual Search pipeline?

**Background.** Default run validates prerequisites (HTTPS URL, importability of L06). `--apply` clones the base skillset, inserts a WebApiSkill at the custom endpoint URL, and retargets the indexer. `--run` also starts the indexer. The endpoint must be deployed, HTTPS, Entra-authenticated, and validated with L06's batch contract before production use.

```bash
uv run python 05-information-extraction/17_search_custom_skill_deploy.py
uv run python 05-information-extraction/17_search_custom_skill_deploy.py --apply --run
```

**Code path.**
1. Validate `CUSTOM_SKILL_URL` (HTTPS required)
2. With `--apply`: clone skillset.json → insert `WebApiSkill` → PUT derived skillset; clone indexer.json → retarget → PUT
3. With `--run`: `run_indexer(name)`

**What to watch in the output.** Preflight: config checks. With `--apply`: `skillset saved`, `indexer saved`. Check portal execution history for per-record custom skill errors.

**Exam cues.** Custom skill runs at index time, not query time. `--apply` changes persistent resources. Test rollback — derived skillset changes the text that gets embedded.

**References:** [Custom skill interface](https://learn.microsoft.com/azure/search/cognitive-search-custom-skill-web-api) · [Skillset concepts](https://learn.microsoft.com/azure/search/cognitive-search-working-with-skillsets)

---

### 18 — Search Monitoring

**Question answered:** How do you read indexer health and document count as a smoke diagnostic?

**Background.** Default run is a local preflight. `--run` calls `get_indexer_status()` and `get_document_count()`, formats a redacted summary (SAS tokens/keys stripped from error strings). This is a read-only snapshot — not complete observability. Production needs alerts on failed runs, stale schedules, failed-item ratios, and query latency.

```bash
uv run python 05-information-extraction/18_search_monitoring.py
uv run python 05-information-extraction/18_search_monitoring.py --run
```

**Code path.**
1. `indexer_client().get_indexer_status(name)` → `status_summary()` → redact secrets → print
2. `search_client().get_document_count()` → print

**What to watch in the output.** `indexer_status`, `items_processed`, `items_failed`, `last_status`. A `failed` run with zero `items_failed` = the indexer itself failed (network/auth), not individual records.

**Exam cues.** `get_indexer_status()` returns the last result only. Failed items ≠ failed indexer run — check both. Redact error strings before logging.

**References:** [Search indexer overview](https://learn.microsoft.com/azure/search/search-indexer-overview) · [Monitor indexer status](https://learn.microsoft.com/azure/search/search-indexer-monitoring)

---

### 19 — Blob Identity Path Check

**Question answered:** How do you verify that the operator/runtime identity has Blob data-plane access?

**Background.** The calling user's identity (via `DefaultAzureCredential`) is different from the Search service's managed identity. This lesson proves the operator path works — if it succeeds but the indexer still fails Blob access, the Search MI lacks its own role. Default run: local preflight. `--run` reads container properties using Entra (no account key).

```bash
uv run python 05-information-extraction/19_blob_identity_paths.py
uv run python 05-information-extraction/19_blob_identity_paths.py --run
```

**Code path.**
1. `account_url(STORAGE_ACCOUNT)` validates no slashes/dots
2. `BlobServiceClient(url, DefaultAzureCredential()).get_container_client(container)`
3. `get_container_properties()` → print name and last_modified

**What to watch in the output.** Container name and last_modified timestamp. A 403 = current identity lacks Storage Blob Data Reader. Network error = private endpoint/firewall blocks access.

**Exam cues.** This proves the operator identity, not the Search MI. Two separate role assignments are required. Don't broaden roles after failure — investigate effective principal, scope, and network path.

**References:** [Managed identities for Azure resources](https://learn.microsoft.com/entra/identity/managed-identities-azure-resources/overview) · [Search managed identities storage](https://learn.microsoft.com/azure/search/search-howto-managed-identities-storage)

---

### 20 — Managed Search Agent Tool

**Question answered:** How does a Foundry agent with an Azure AI Search tool differ from app-owned RAG?

**Background.** Attaches `AzureAISearchTool` to a Foundry Prompt Agent — the agent decides when to query Search with VECTOR_SEMANTIC_HYBRID, top_k=3. Requires a Foundry project connection to the Search service. Three explicit flags prevent accidental mutation: `--enable` unlocks consent, `--apply` creates the agent version, `--run` invokes it. Does NOT replace ACL enforcement — no security filter is configured here.

```bash
uv run python 05-information-extraction/20_managed_search_agent_tool.py --enable --apply --run
```

**Code path.**
1. `configuration()` → validate `SEARCH_CONNECTION_NAME` + `SEARCH_INDEX`
2. With `--apply`: `AzureAISearchTool(indexes=[AISearchIndexResource(connection_id, index, HYBRID, top_k=3)])` → `agents.create_version()`
3. With `--run`: `responses.create()` with `agent_reference` → print output_text + URL citations

**What to watch in the output.** With `--apply`: `agent '<name>' v<version> created.` With `--run`: answer plus source URLs cited from the Search index.

**Exam cues.** Managed tool ≠ manual RAG. Agent calls Search tool when it decides to — not every turn. Tool does not enforce application ACLs. Project connection + project identity roles must be configured separately from Search data-plane roles.

**References:** [Azure AI Search tool for Foundry agents](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/ai-search) · [Agentic retrieval overview](https://learn.microsoft.com/azure/search/agentic-retrieval-overview)

---

## Stage 7 — Agentic Retrieval: Knowledge Sources + Knowledge Base (lessons 21–27)

Agentic retrieval replaces the manual "app owns retrieval" pattern (L07/L08) and the managed-tool pattern (L20) with a service-side pipeline. A *knowledge source* declares content (indexed or remote); a *knowledge base* stitches sources together and exposes one `/retrieve` endpoint that fans a single request out to every source in parallel, generates subqueries with an LLM, merges results, and optionally synthesizes an answer with citations. All lessons in this stage target REST API `2026-08-01-preview` — the GA `2026-04-01` version supports fewer knowledge-source kinds and no answer synthesis or configurable reasoning effort.

### 21 — Blob Knowledge Source

**Question answered:** How do you create a knowledge source that auto-generates the entire ingestion pipeline from a blob container?

**Background.** A single `azureBlob` knowledge source PUT tells Search to create a data source, skillset, index, and indexer for you (contrast with L04/L05, which build the same four objects by hand). `ingestionParameters` names the embedding model (for chunk vectors) and chat completion model (for image verbalization); both must be reachable by the Search MI with **Cognitive Services User**. Preview features include `networkAccessMode: private`, `ingestionPermissionOptions` (ACL / Purview label propagation), and per-language analyzers.

```bash
uv run python 05-information-extraction/21_knowledge_source_blob.py
uv run python 05-information-extraction/21_knowledge_source_blob.py --apply
```

**Code path.**
1. `configuration()` reads `SEARCH_KS_BLOB`, `SEARCH_BLOB_CONNECTION`, `SEARCH_BLOB_CONTAINER`, plus `AZURE_OPENAI_ENDPOINT`, `EMBEDDING_MODEL`, `DEFAULT_MODEL`
2. `build_body()` mirrors the doc's preview PUT body exactly
3. With `--apply`: PUT `/knowledgesources/<name>?api-version=2026-08-01-preview`

**What to watch in the output.** Preflight: JSON body with `ResourceId=...` connection form. `--apply`: `knowledge source '<name>' saved.` A 400 with "cannot resolve embedding" means the Search MI lacks Cognitive Services User on the AOAI resource.

**Exam cues.** The generated indexer follows the same rules as a hand-built blob indexer (L04) — supported formats, indexer limits, and skill limits all apply. `ingestionPermissionOptions` and `assetStore` cannot be set on the same knowledge source.

**References:** [What is a knowledge source?](https://learn.microsoft.com/azure/search/agentic-knowledge-source-overview) · [Create a blob knowledge source](https://learn.microsoft.com/azure/search/agentic-knowledge-source-how-to-blob)

---

### 22 — Search-Index Knowledge Source

**Question answered:** How do you expose an existing search index (like the one from L00) as a knowledge source without any ingestion?

**Background.** The `searchIndex` kind is a pointer — no pipeline is generated. `sourceDataFields` lists which fields appear in retrieve response `references`. `searchFields` controls which fields participate in query execution. Preview (`2026-05-01-preview`+) makes `semanticConfigurationName` optional; on GA it's still required.

```bash
uv run python 05-information-extraction/22_knowledge_source_search_index.py --apply
```

**Code path.**
1. `configuration()` reads `SEARCH_KS_INDEX` + `SEARCH_INDEX_VECTOR`
2. `build_body()` produces the wrapper JSON
3. With `--apply`: PUT `/knowledgesources/<name>?api-version=2026-08-01-preview`

**What to watch in the output.** `knowledge source '<name>' saved.` A 400 "searchIndexName not found" means the referenced index isn't on this service. Advanced features (base filter, query hints) are covered in the source doc.

**Exam cues.** Agentic retrieval ignores the underlying index's `scoringProfiles` (including `defaultScoringProfile`) and never returns `@search.rerankerBoostedScore`. Use [freshness-aware retrieval](https://learn.microsoft.com/azure/search/agentic-retrieval-how-to-configure-freshness) for recency bias.

**References:** [Create a search index knowledge source](https://learn.microsoft.com/azure/search/agentic-knowledge-source-how-to-search-index) · [Create an index for agentic retrieval](https://learn.microsoft.com/azure/search/agentic-retrieval-how-to-create-index)

---

### 23 — Web Knowledge Source

**Question answered:** How do you add live web results (Grounding with Bing) as a remote knowledge source?

**Background.** Remote knowledge sources are queried at request time — no ingestion. The `web` kind uses Grounding with Bing Custom Search, always summarizes results with an LLM (never verbatim text), and requires the KB to include a `models` reference. Web knowledge source is a First-Party Consumption Service — Microsoft DPA doesn't apply and use waives Government Community Cloud commitments. Public-cloud regions only.

```bash
uv run python 05-information-extraction/23_knowledge_source_web.py
uv run python 05-information-extraction/23_knowledge_source_web.py --apply
```

**Code path.**
1. `configuration()` reads `SEARCH_KS_WEB` + optional `SEARCH_WEB_ALLOWED_DOMAIN` / `SEARCH_WEB_BLOCKED_DOMAIN`
2. `build_body()` sets `allowedDomains` and `blockedDomains`
3. With `--apply`: PUT `/knowledgesources/<name>?api-version=2026-08-01-preview`

**What to watch in the output.** `knowledge source '<name>' saved.` At retrieve time (L25/L26), the response `activity` array includes `web` records (Bing runtime parameters) and `modelWebSummarization` records (token usage).

**Exam cues.** Web is remote (no citation URLs into an index). Answer synthesis (L26) is only available with `2026-08-01-preview`; on GA the web KB is extractive summaries only.

**References:** [Create a web knowledge source](https://learn.microsoft.com/azure/search/agentic-knowledge-source-how-to-web) · [Manage web knowledge source access](https://learn.microsoft.com/azure/search/agentic-knowledge-source-how-to-web-manage) · [Grounding with Bing terms](https://www.microsoft.com/en-us/bing/apis/grounding-legal-enterprise)

---

### 24 — Knowledge Base (multi-source)

**Question answered:** How do you compose multiple knowledge sources into one queryable retrieval endpoint?

**Background.** A knowledge base is a top-level object with one URL per KB (`/knowledgebases/<name>/retrieve`). It lists knowledge sources by name, optionally supplies an LLM for query planning / answer synthesis / web summarization, and stores defaults: `retrievalInstructions` (routing hints), `answerInstructions` (output shape), `outputMode`, `retrievalReasoningEffort`, and `retrieveDefaults` (runtime/token budgets). L24 wires L21 and L22 (plus L23 when `SEARCH_KS_WEB` is set) into one KB with `outputMode=answerSynthesis` and `retrievalReasoningEffort.kind=auto`.

```bash
uv run python 05-information-extraction/24_agentic_knowledge_base.py --apply
```

**Code path.**
1. `configuration()` reads `SEARCH_KNOWLEDGE_BASE`, `SEARCH_KS_BLOB`, `SEARCH_KS_INDEX`, `SEARCH_KS_WEB`, `AZURE_OPENAI_ENDPOINT`, `DEFAULT_MODEL`
2. `build_body()` composes the KB JSON
3. With `--apply`: PUT `/knowledgebases/<name>?api-version=2026-08-01-preview`

**What to watch in the output.** `knowledge base '<name>' saved.` A 400 "knowledge source not found" means L21–L23 didn't run. If the KB includes a web source, the `models` entry is mandatory (web summarization). On GA `2026-04-01` most preview fields are rejected.

**Exam cues.** The KB stores *defaults*; retrieve requests (L25/L26) override per call. `retrievalInstructions` is a natural-language hint to the planner — not a security filter. Use `ingestionPermissionOptions` on sources plus `x-ms-query-source-authorization` at retrieve time for real permission trimming.

**References:** [Create a knowledge base](https://learn.microsoft.com/azure/search/agentic-retrieval-how-to-create-knowledge-base) · [Agentic retrieval overview](https://learn.microsoft.com/azure/search/agentic-retrieval-overview)

---

### 25 — Retrieve Action

**Question answered:** How do you call the retrieve endpoint and inspect the subqueries + references it returns?

**Background.** POST `/knowledgebases/<name>/retrieve` fans one user message out to every knowledge source in the KB. The response body has three parts: `response` (extracted grounding text or synthesized answer), `activity` (per-subquery timing, tokens, and knowledge-source calls), and `references` (per-cited-chunk records, each with an `activitySource` pointing back into `activity`). Preview accepts a `messages` array (assistant instruction + user turn); GA `2026-04-01` uses the older `intents` shape. This lesson uses `outputMode=extractiveData` + `low` reasoning effort.

```bash
uv run python 05-information-extraction/25_agentic_retrieve.py
uv run python 05-information-extraction/25_agentic_retrieve.py --apply
```

**Code path.**
1. `configuration()` reads `SEARCH_KNOWLEDGE_BASE` + optional `SEARCH_RETRIEVE_QUESTION`
2. `build_request(question)` produces the POST body
3. With `--apply`: POST `/knowledgebases/<name>/retrieve?api-version=2026-08-01-preview` → print response preview, subqueries from `activity`, and up to 5 references

**What to watch in the output.** With `--apply`: `Response text preview`, then `Subquery [<type> via <ks>] <elapsed>ms` lines, then `Reference id=... docKey=...` lines. Indexed sources include a `docKey`; remote (web) sources leave it as `-`.

**Exam cues.** Retrieve is *not* a chat completion — its output is grounding data. The `references` array is what a downstream agent should cite. `maxOutputSizeInTokens` on the request (or `maxOutputSizeInTokens` in KB `retrieveDefaults`) bounds the output; the most-relevant document may be dropped if it exceeds the budget — check `activity` for the warning.

**References:** [Query a knowledge base](https://learn.microsoft.com/azure/search/agentic-retrieval-how-to-retrieve) · [Agentic retrieval pipeline tutorial](https://learn.microsoft.com/azure/search/agentic-retrieval-how-to-create-pipeline)

---

### 26 — Answer Synthesis

**Question answered:** How do you switch retrieve from raw grounding chunks to a formulated natural-language answer with inline citations?

**Background.** Set `outputMode` to `answerSynthesis` on the retrieve request (or as a KB default in L24). The KB's LLM writes an answer and inlines citations as `[ref_id:<n>]` tokens that map to entries in the `references` array. Requires `2026-08-01-preview`, a `models` entry on the KB, and reasoning effort `low`/`medium`/`auto` (not `minimal`).

```bash
uv run python 05-information-extraction/26_agentic_answer_synthesis.py --apply
```

**Code path.**
1. `configuration()` reads `SEARCH_KNOWLEDGE_BASE` + optional `SEARCH_RETRIEVE_QUESTION`
2. `build_request(question)` sets `outputMode=answerSynthesis` and `answerInstructions`
3. With `--apply`: POST retrieve → print synthesized answer, up to 8 references, aggregated `inputTokens`/`outputTokens` from `activity`

**What to watch in the output.** A bulleted or paragraph answer with `[ref_id:1]`-style citations, then reference rows with `docKey`, then a token summary. Empty answer with zero results in `activity` = the KB has no matching documents.

**Exam cues.** Synthesized answers are model output — they can hallucinate around gaps in retrieved content. The citations are grounded by construction, but the sentence between citations is not. Answer synthesis + `minimal` reasoning is a 400 error.

**References:** [Answer synthesis how-to](https://learn.microsoft.com/azure/search/agentic-retrieval-how-to-answer-synthesis) · [Set retrieval reasoning effort](https://learn.microsoft.com/azure/search/agentic-retrieval-how-to-set-retrieval-reasoning-effort)

---

### 27 — Reasoning-Effort Tiers (docs-only)

**Question answered:** How much LLM processing runs per retrieve call, and what are the trade-offs between the four tiers?

**Background.** `retrievalReasoningEffort.kind` chooses `minimal` / `low` / `medium` / `auto`. `minimal` disables LLM planning entirely — fastest, cheapest, forces `outputMode=extractiveData`, no answer synthesis, no web sources. `low` (default) runs one planning pass with 5,000 answer tokens. `medium` adds a semantic-classifier iteration with 10,000 answer tokens (region-limited). `auto` starts light and escalates up to medium if grounding is thin — requires preview + a KB `models` entry. This lesson is preflight-only; it prints the exact request body for each tier so you can drop the JSON into L25/L26.

```bash
uv run python 05-information-extraction/27_agentic_reasoning_effort_preflight.py
```

**Code path.**
1. For each tier, `build_request(kind)` prints `retrievalReasoningEffort` plus operational limits
2. No PUT, no POST — this is a documentation lesson

**What to watch in the output.** Four labeled JSON snippets and a limits table per tier. Nothing is sent.

**Exam cues.** Effort is set at the KB (default) or per retrieve request (override). If neither is set, the service uses `low`. `minimal` is the migration path from the classic `/docs/search` API — direct text/vector search across every source, no query expansion, and `alwaysQueryKnowledgeSource` is ignored.

**References:** [Set the retrieval reasoning effort](https://learn.microsoft.com/azure/search/agentic-retrieval-how-to-set-retrieval-reasoning-effort) · [Agentic retrieval migration](https://learn.microsoft.com/azure/search/agentic-retrieval-how-to-migrate)

---

## Stage 8 — Permission-aware, image, and layout enrichment (lessons 28–30)

Lessons 28–30 extend the L04–L05 indexer pipeline: SharePoint ACLs travel with the content (28), text inside images becomes searchable and is kept in a knowledge store (29), and one Content Understanding skill replaces extraction, chunking, and layout parsing with page-level citations (30). All three are local by default.

### 28 — SharePoint indexer with ACL ingestion (preview runbook)

**Question answered:** How do SharePoint permissions follow content into a search index so retrieval is security-trimmed?

**Background.** The SharePoint indexer can store per-item user and group IDs (`indexerPermissionOptions`) in permission-filter fields and enforce them at query time. The portal doesn't support it; configure it with REST (`2026-05-01-preview` or later). The ingestion app needs **application** permissions; any scenario with SharePoint API permissions needs a **federated credential**, not a client secret. With chunking (`skipIndexingParentDocuments`), ACL fields must be mapped through `indexProjections.mappings`, not indexer field mappings. Parent-scope permission changes need `/resync` with `options: ["permissions"]`. Knowledge store, enrichment cache, custom Web API skills, and debug sessions don't preserve document permissions.

```bash
uv run python 05-information-extraction/28_sharepoint_indexer_acls_preflight.py
```

**What to watch.** A printed runbook: permission table per scenario, data source, index fields (`UserIds`, `GroupIds`, `SharePointSiteUrl`), mappings, and resync calls. `No cloud calls made.`

**References:** [SharePoint indexer ACLs](https://learn.microsoft.com/azure/search/search-indexer-sharepoint-access-control-lists)

---

### 29 — OCR scanned files and embedded images; keep enrichments in a knowledge store

**Question answered:** How do I make text inside scanned invoices and PDF images searchable with a citation to the source file, and keep the enriched output for analytics?

**Background.**
1. **Indexer `imageAction: "generateNormalizedImages"`** extracts every image (image files and images embedded in PDFs or Office files) into `/document/normalized_images` while cracking the blob. That collection is the only input the built-in OCR skill accepts; a Shaper skill, `outputFieldMappings`, or pointing OCR at `/document/content` cannot create it.
2. **OCR skill** (`#Microsoft.Skills.Vision.OcrSkill`, context `/document/normalized_images/*`) reads printed and handwritten text from each image. Image Analysis returns tags and captions, not the text; Text Split and Translation need text that already exists.
3. **Text Merge skill** inserts each image's OCR text into `/document/content` at the image's `contentOffset`, producing `merged_text`, which is indexed next to `source_url` for citations.
4. **Knowledge store** projections write enrichments to Azure Storage for Power BI, data science, or audit:

| Projection | Storage | Use for |
|---|---|---|
| `objects` | Blob container, one JSON per source file | JSON and other hierarchical data |
| `tables` | Table storage rows and columns | Extracted text you query or analyze as records |
| `files` | Blob container of binary images | Normalized images |

Projections in one group are related through generated keys. A table property holds at most 64 KB, so long merged text goes to the object projection; the tables hold metadata and per-image OCR text.

```bash
uv run python 05-information-extraction/29_search_ocr_knowledge_store.py            # validate + print REST bodies
uv run python 05-information-extraction/29_search_ocr_knowledge_store.py --apply    # PUT index, skillset, indexer
uv run python 05-information-extraction/29_search_ocr_knowledge_store.py --delete   # remove them
```

**Code path.** `validate_pipeline()` checks that skills reading `normalized_images` have an indexer `imageAction`, that OCR reads only `/document/normalized_images/*`, that every mapping targets an index field, and that the knowledge store uses an identity-based `ResourceId=` connection (never an account key). `merge_text()` simulates Text Merge locally. `--apply` resolves `${...}` placeholders and PUTs index → skillset → indexer with `2026-04-01`.

**Prerequisites.** Lesson 04's data source; `AZURE_SUBSCRIPTION_ID`, `AZURE_RESOURCE_GROUP`, `STORAGE_ACCOUNT`; `FOUNDRY_ENDPOINT` for keyless billing (`AIServicesByIdentity`) beyond 20 free documents per indexer per day. Search identity roles: Storage Blob Data Reader (source), Storage Blob Data Contributor (object projections), Reader and Data Access (table projections), Cognitive Services User (Foundry resource).

**Cost and cleanup.** A new indexer runs immediately; image extraction and OCR are billable. `--delete` removes Search objects only; knowledge-store tables and containers stay in Storage until you delete them.

**Exam cues.** Images → `normalized_images` → OCR. JSON → object projection; extracted text → table projection; images → file projection.

**References:** [OCR skill](https://learn.microsoft.com/azure/search/cognitive-search-skill-ocr) · [Projections](https://learn.microsoft.com/azure/search/knowledge-store-projection-overview) · [Attach a billing resource](https://learn.microsoft.com/azure/search/cognitive-search-attach-cognitive-services)

---

### 30 — Content Understanding skill: page-level citations with polygons and cross-page tables

**Question answered:** Which single built-in skill gives page-level citations with bounding polygons for text and images, and keeps tables that span pages whole?

**Background.** `#Microsoft.Skills.Util.ContentUnderstandingSkill` (GA in `2026-04-01`) extracts and chunks in one step. `extractionOptions: ["images", "locationMetadata"]` returns every chunk and image with `pageNumberFrom`, `pageNumberTo`, `ordinalPosition`, and `source` polygons such as `D(2,0.64,9.26,...)`. Tables come back as Markdown and a table that spans pages is one unit. Document Extraction has no layout or polygons; Document Layout returns tables as plain text and cannot join cross-page tables; GenAI Prompt transforms text rather than extracting layout.

```bash
uv run python 05-information-extraction/30_search_cu_skill_citations.py            # validate + sample citation
uv run python 05-information-extraction/30_search_cu_skill_citations.py --apply    # PUT index, skillset, indexer
uv run python 05-information-extraction/30_search_cu_skill_citations.py --delete
```

**Code path.** The indexer sets `allowSkillsetToReadFileData: true` (creates `/document/file_data`, the skill's only input) and `batchSize: 1`. The skillset attaches the Foundry resource with `AIServicesByIdentity`, maps each `text_sections` item to a chunk document with `indexProjections`, and projects `normalized_images` as files so each chunk's `imagePath` resolves to a blob. `citation()` turns a chunk into `file.pdf, pages 2-3` plus parsed polygons.

**Prerequisites and limits.** A Foundry resource in a Content Understanding region; Search identity with Cognitive Services User on it, Storage Blob Data Reader on the source, and Storage Blob Data Contributor for images. No free documents; files needing more than five minutes of analysis time out but are still charged. Semantic chunking and AI image descriptions are preview (`2026-05-01-preview`+) and are not used here.

**References:** [Content Understanding skill](https://learn.microsoft.com/azure/search/cognitive-search-skill-content-understanding) · [Chunk and vectorize with Content Understanding](https://learn.microsoft.com/azure/search/search-how-to-semantic-chunking-content-understanding)

---

## Feature status and hard limits

| Feature | Status | Practical boundary |
|---------|--------|--------------------|
| CU Pro mode | Retired (`2025-05-01-preview`, July 15, 2026) | Calls return HTTP 410; L13 shows the GA replacement pattern |
| CU standard (L09–L16) | GA (`2025-11-01`) | Extract/classify/generate; one input per analyze; `extract` fields need `estimateSourceAndConfidence` |
| CU agentic mode | Preview (`2026-06-01-preview`) | `config.workflow: "agentic"`; one input file per request |
| Semantic ranker (L03) | GA | Region/SKU dependent; separate billing |
| `AzureAISearchTool` (L20) | GA | Requires Foundry project connection + matching roles |
| Integrated vectorization (L04–L05) | GA | Embedding model/dimension must match index schema |
| SharePoint indexer ACL ingestion (L28) | Preview (`2026-05-01-preview`+) | REST only; application permissions; federated credential for SharePoint API scenarios |
| OCR skill + knowledge store (L29) | GA | Needs indexer `imageAction`; billable beyond 20 free documents per indexer per day; table property limit 64 KB |
| Content Understanding skill (L30) | GA (`2026-04-01`) | No free documents; five-minute analysis limit per file; semantic chunking and image descriptions are preview |

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| Search 401/403 | Wrong identity or role scope | Check effective `DefaultAzureCredential` identity and Search RBAC |
| Indexer cannot read Blob | Search MI missing Blob Data Reader or network path | Enable Search MI; assign role; validate `ResourceId` + firewall |
| Embedding skill 401/403 | Search MI missing Cognitive Services OpenAI User | Assign role; verify endpoint/deployment |
| Dimension mismatch | Index, skill, vectorizer describe different embedding output | Align model/dimensions; rebuild index |
| No vector results | Vectors not populated (indexer didn't finish) | Inspect indexer history; wait for success |
| Semantic ranker unavailable | SKU/region doesn't support it | Check service tier + regional availability |
| L08 agent not found | L07 not run or wrong agent name | Run `07_rag_prompt_agent.py` first |
| CU cannot fetch URL | `file://`, expired SAS, blocked network | Use HTTPS public URL or fresh read-only Blob SAS |
| CU polling never succeeds | Job failed or throttled | Check final job body/status; reduce input size |
| L13 rejects input | Standard API still active or `extract` field used | Set preview API; remove `extract` fields |
| Markdown chunks not searchable | L14 prints chunks only — no vectors | Use Blob + L04/L05 integrated pipeline, or generate vectors before upload |
| L17 custom skill fails | Endpoint unreachable, rejects batch, or auth wrong | Test with L06 local payload first; verify HTTPS + Entra auth + batch errors |
| L19 passes but indexer Blob fails | Caller MI ≠ Search MI | Validate Search system-assigned MI has its own Blob role |
| L20 connection/tool fails | Wrong connection name, missing fields, or role | Validate project connection ID, retrievable source_url field, and project RBAC |

---

## CI/CD and operational release

```
Plan → Schema design → IaC review → Stage deploy → Indexer run → Quality gate → Release
         │                               │               │               │
     index/skillset/              Bicep/Terraform    --run --wait    retrieval recall
     indexer JSON                 role assignments   → success       > threshold
     versioned in Git             private endpoints  before query    citation check
```

**What to version:** index JSON schema, skillset JSON, indexer JSON, CU analyzer definitions, API versions, embedding model names, semantic configuration names.

**Release gates:** indexer terminates `success` (not just started); document count matches expected range; smoke query returns non-empty results; L18 `--run` shows zero failed items.

---

## Security, networking, and IaC

| Decision | Recommendation | Common pitfall |
|----------|---------------|---------------|
| Search data source auth | Managed-identity `ResourceId` connection — no storage key | Replacing with connection string when MI setup is hard |
| CU input auth | Short-lived read-only one-object SAS URL | Broad account SAS or `file://` path |
| Blob → Search private | Shared private link or private endpoint + DNS | Private endpoint does not grant a role; RBAC is separate |
| Embedding skill → OpenAI | Search MI with Cognitive Services OpenAI User | Using AZURE_OPENAI_ENDPOINT that doesn't match deployment region |
| Custom skill endpoint | HTTPS, Entra auth, per-record error handling | Localhost URL or static bearer token in skillset JSON |
| ACL enforcement | OData security filter on query derived from trusted auth context | Model prompt instructions as authorization control |
| SAS URLs in output | Strip query credentials before logging or returning to clients | Logging raw SAS URLs in error messages or citations |

---

## Common exam traps

| Claim | Correct interpretation |
|-------|----------------------|
| "Semantic ranker is vector search" | ❌ — semantic ranker reranks initial BM25/RRF candidates; it doesn't scan full corpus |
| "Skillsets run when a user queries" | ❌ — skillsets run at indexer time only, never at query time |
| "The vectorizer embeds documents" | ❌ — vectorizer embeds query text at query time; the embedding skill embeds documents at ingestion |
| "Uploading L14 chunks makes them vector-searchable" | ❌ — needs client-generated vector + complete index document shape |
| "Search and CU are interchangeable" | ❌ — Search = retrieve across corpus; CU = extract from one submitted document |
| "CU accepts local files because Python can read them" | ❌ — CU service fetches HTTPS URL; `file://` is not reachable |
| "Pro mode = better standard extraction" | ❌ — Pro was multi-document reasoning (retired preview); it never improved single-document extraction |
| "Prompt instructions enforce document permissions" | ❌ — ACL must trim Search results before model input |
| "L07 agent autonomously searches the index" | ❌ — L07 has no Search tool; L08 does retrieval in app code |
| "Source URL citation proves an answer is grounded" | ❌ — provenance must be evaluated; URL alone doesn't prove claim-to-source mapping |

---

## Objective coverage and limits

This domain covers **Search ingestion** (index schema, Blob indexer, skillset, custom skill), **Search retrieval** (keyword, vector, hybrid+semantic), **manual RAG** (app-owned retrieval + constrained agent), **Content Understanding** (prebuilt-read, prebuilt-layout, prebuilt-invoice, custom standard analyzer, Pro cross-document, Markdown chunking, CU→agent, multimodal), and **operational patterns** (monitoring, identity verification, managed Search tool).

Not covered: Search index projections with ACL fields, Search agentic retrieval knowledge base, image/audio/video ingestion through the Search skillset (only CU multimodal shown), CU confidence thresholds and analyzer improvement workflow, and end-to-end claim-to-citation evaluation. These are noted gaps — do not treat these samples as proving those scenarios.

---

## References

### Azure AI Search
- [Azure AI Search overview](https://learn.microsoft.com/azure/search/search-what-is-azure-search)
- [Search index concepts](https://learn.microsoft.com/azure/search/search-what-is-an-index)
- [Vector search overview](https://learn.microsoft.com/azure/search/vector-search-overview)
- [Vector search query how-to](https://learn.microsoft.com/azure/search/vector-search-how-to-query)
- [Hybrid search overview](https://learn.microsoft.com/azure/search/hybrid-search-overview)
- [Hybrid search ranking (RRF)](https://learn.microsoft.com/azure/search/hybrid-search-ranking)
- [Semantic search overview](https://learn.microsoft.com/azure/search/semantic-search-overview)
- [Integrated vectorization](https://learn.microsoft.com/azure/search/vector-search-integrated-vectorization)
- [Search indexer overview](https://learn.microsoft.com/azure/search/search-indexer-overview)
- [Blob indexer](https://learn.microsoft.com/azure/search/search-blob-storage-integration)
- [Skillset concepts](https://learn.microsoft.com/azure/search/cognitive-search-working-with-skillsets)
- [Defining skillsets](https://learn.microsoft.com/azure/search/cognitive-search-defining-skillset)
- [Custom WebApiSkill interface](https://learn.microsoft.com/azure/search/cognitive-search-custom-skill-web-api)
- [Search managed identities (storage)](https://learn.microsoft.com/azure/search/search-howto-managed-identities-storage)
- [Security trimming](https://learn.microsoft.com/azure/search/search-security-trimming-for-azure-search)
- [Agentic retrieval overview](https://learn.microsoft.com/azure/search/agentic-retrieval-overview)

### Azure Content Understanding
- [Content Understanding overview](https://learn.microsoft.com/azure/ai-services/content-understanding/overview)
- [Document overview](https://learn.microsoft.com/azure/ai-services/content-understanding/document/overview)
- [CU Markdown output](https://learn.microsoft.com/azure/ai-services/content-understanding/document/markdown)
- [Document elements](https://learn.microsoft.com/azure/ai-services/content-understanding/document/elements)
- [Prebuilt analyzers](https://learn.microsoft.com/azure/ai-services/content-understanding/concepts/prebuilt-analyzers)
- [CU service limits](https://learn.microsoft.com/azure/ai-services/content-understanding/service-limits)
- [Create custom analyzer](https://learn.microsoft.com/azure/ai-services/content-understanding/tutorial/create-custom-analyzer)
- [Build RAG solution with CU](https://learn.microsoft.com/azure/ai-services/content-understanding/tutorial/build-rag-solution)
- [CU image overview](https://learn.microsoft.com/azure/ai-services/content-understanding/image/overview)
- [CU video overview](https://learn.microsoft.com/azure/ai-services/content-understanding/video/overview)

### RAG and Foundry agents
- [RAG overview in Foundry](https://learn.microsoft.com/azure/foundry/concepts/retrieval-augmented-generation)
- [RAG evaluators](https://learn.microsoft.com/azure/foundry/concepts/evaluation-evaluators/rag-evaluators)
- [Azure AI Search tool for Foundry agents](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/ai-search)

### Security and identity
- [Managed identities overview](https://learn.microsoft.com/entra/identity/managed-identities-azure-resources/overview)
- [Storage managed identities for Search](https://learn.microsoft.com/azure/search/search-howto-managed-identities-storage)
- [Azure Key Vault security](https://learn.microsoft.com/azure/key-vault/general/security-features)

### Compliance and Responsible AI

- [Azure AI Search transparency note](https://learn.microsoft.com/azure/foundry/responsible-ai/search/transparency-note)
- [Content Understanding transparency note](https://learn.microsoft.com/azure/foundry/responsible-ai/content-understanding/transparency-note)
- [Content Understanding data privacy](https://learn.microsoft.com/azure/foundry/responsible-ai/content-understanding/data-privacy)
- [Content Understanding provenance disclosure](https://learn.microsoft.com/azure/foundry/responsible-ai/content-understanding/provenance-disclosure)
- [Document Intelligence transparency note](https://learn.microsoft.com/azure/foundry/responsible-ai/document-intelligence/transparency-note)
- [Document Intelligence data privacy + security](https://learn.microsoft.com/azure/foundry/responsible-ai/document-intelligence/data-privacy-security)
- [Question answering transparency](https://learn.microsoft.com/azure/foundry/responsible-ai/language-service/transparency-note-question-answering)
- [Question answering data privacy + security](https://learn.microsoft.com/azure/foundry/responsible-ai/language-service/data-privacy-security-question-answering)
- [Question answering integration guidance](https://learn.microsoft.com/azure/foundry/responsible-ai/language-service/guidance-integration-responsible-use-question-answering)
- [Question answering characteristics + limitations](https://learn.microsoft.com/azure/foundry/responsible-ai/language-service/characteristics-and-limitations-question-answering)
- [Custom NER transparency](https://learn.microsoft.com/azure/foundry/responsible-ai/language-service/custom-named-entity-recognition-transparency-note)
- [Custom NER characteristics + limitations](https://learn.microsoft.com/azure/foundry/responsible-ai/language-service/custom-named-entity-recognition-characteristics-and-limitations)
- [Custom NER data privacy + security](https://learn.microsoft.com/azure/foundry/responsible-ai/language-service/custom-named-entity-recognition-data-privacy-security)
- [Custom NER integration guidance](https://learn.microsoft.com/azure/foundry/responsible-ai/language-service/custom-named-entity-recognition-guidance-integration-responsible-use)
- [Custom text classification transparency](https://learn.microsoft.com/azure/foundry/responsible-ai/language-service/custom-text-classification-transparency-note)
- [Custom text classification characteristics + limitations](https://learn.microsoft.com/azure/foundry/responsible-ai/language-service/custom-text-classification-characteristics-and-limitations)
- [Custom text classification data privacy + security](https://learn.microsoft.com/azure/foundry/responsible-ai/language-service/custom-text-classification-data-privacy-security)
- [Custom text classification integration guidance](https://learn.microsoft.com/azure/foundry/responsible-ai/language-service/custom-text-classification-guidance-integration-responsible-use)
