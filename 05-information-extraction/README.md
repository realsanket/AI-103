# Domain 5: Information extraction

> Study guide and runnable labs for Azure AI Search retrieval and Azure Content Understanding in Foundry Tools. Run commands from repository root: `uv run python 05-information-extraction/<lesson>.py`.
>
> This guide explains service behavior and documents this repository's exact implementation. A lesson proves only its stated path. Region, feature, pricing, quota, API version, and permission availability remain subscription-specific. A successful call is not an extraction-quality, grounding, authorization, or production-readiness result.

> **Current runtime boundary.** `_search_rest.py`, L17's REST helper, and `_shared/cu_client.py` acquire an Entra token but currently send the literal redacted `Authorization: ******` header. Their live REST calls (L00, L04, L05, L09–L17) therefore cannot authenticate as checked in. This guide describes their intended service architecture and marks durable effects that occur only after that header is repaired to send the acquired bearer token. SDK-backed Search queries/status (L01–L03, L18), Blob check (L19), and project-client agent paths (L07, L08, L15, L20) have separate credential paths. Never copy a real token into source merely to make a sample run.

## What this domain teaches

Domain 5 has two complementary jobs:

| Need | Use | This repository's path |
|---|---|---|
| Find relevant evidence across a corpus | Azure AI Search | Blob indexer, chunking/embedding skillset, vector index, then keyword, vector, or hybrid query. |
| Turn one input document into readable structure or fields | Azure Content Understanding in Foundry Tools | Submit URL asynchronously to a prebuilt or custom analyzer, then consume Markdown or fields. |

```text
Search: Blob files → indexer → skillset → chunk/vector index → retrieve → answer
CU:     reachable file URL → analyzer → asynchronous result → Markdown/fields → application or RAG
```

Search is a retrieval system, not a document field-extraction service. Content Understanding (CU) is an extraction system, not a corpus search engine. A production system can use both: CU preserves difficult document structure, then an embedding-capable ingestion path indexes that representation.

## Mental model

### Search pipeline in this directory

```text
Azure Blob Storage container
  └─ northwind-blob-datasource
       └─ ${SEARCH_INDEXER}
            └─ ${SEARCH_SKILLSET}
                 ├─ SplitSkill: /document/content → /document/pages/*
                 └─ AzureOpenAIEmbeddingSkill: every page → vector
                      └─ ${SEARCH_INDEX_VECTOR}: one document per chunk
                           └─ keyword, vector, hybrid, semantic reranking
```

The indexer drives the pipeline. A skillset runs during indexing, never when a user searches. A query searches already stored fields and vectors. The vectorizer configured on the index turns query text into a vector at query time; it does not create document vectors for a direct upload.

### Document-to-answer boundary

```text
Untrusted source document
  → extract/chunk/index with source and access metadata
  → retrieve only chunks caller can access
  → pass compact evidence to model
  → render answer with source citation
  → retain request, result IDs, source version, and policy decision for audit
```

Grounding improves answer quality; it does not replace authorization, provenance, evaluation, prompt-injection defenses, or application-level citations.

## Glossary

| Term | Meaning in this domain |
|---|---|
| **Data source** | Named Search connection to source data. This lab uses an Azure Blob container. |
| **Indexer** | Search job that reads source data, runs its skillset, and writes index documents. |
| **Skillset** | Ordered enrichment graph used only at ingestion. |
| **Index projection** | One-to-many mapping from one parent file to many child chunk documents. |
| **Vectorizer** | Query-time converter from text to an embedding; it must match the document embedding model. |
| **BM25** | Keyword scoring. Good for exact terms, IDs, SKUs, and rare vocabulary. |
| **Vector search** | Nearest-neighbor retrieval over embeddings. Good for paraphrases and intent. |
| **Hybrid search** | BM25 and vector candidates combined by reciprocal-rank fusion (RRF). |
| **Semantic ranker** | L2 reranker for initial text or hybrid candidates; it does not scan the whole corpus. |
| **Citation/provenance** | Evidence identifying where retrieved text originated and how it reached an answer. |
| **Security trimming** | Enforcing document access before evidence is sent to a model. |
| **Custom skill** | Your HTTPS Web API invoked by a Search indexer during enrichment. |
| **Analyzer** | Reusable CU definition that extracts content or fields from an input. |
| **Standard mode** | CU's normal single-input mode. GA API supports this mode. |
| **Pro mode** | Preview CU mode for multi-input document reasoning and reference data. |
| **Markdown RAG** | Structure-preserving document representation, then chunking, embedding, retrieval, and generation. |

## Service, API, and deployment choices

| Surface | This lab uses | Authentication and boundary | Production choice |
|---|---|---|---|
| Search data plane | `azure-search-documents` for queries/status; REST JSON definitions for index, skillset, data source, and indexer | `DefaultAzureCredential` requests `https://search.azure.com/.default`; role must cover management or query action | Keep schema and ingestion definitions in IaC/API deployment; application queries through SDK or REST. |
| Search enrichment | `2026-04-01` REST resource definitions in `_search_rest.py` | Search system-assigned MI reads Blob and calls embedding deployment | Pin a tested API version; test schema and indexer in nonproduction before replacement. |
| Foundry agent | `AIProjectClient`, then project OpenAI-compatible Responses client | Project endpoint and `Foundry User` are separate from Search authorization | Use manual RAG when application must own filtering/ranking; managed tool when supported service integration is desired. |
| CU | `httpx` REST wrapper; asynchronous `Operation-Location` polling | `DefaultAzureCredential` requests `https://cognitiveservices.azure.com/.default`; CU fetches URL itself | Submit background jobs, store job/source/version state, poll with bounded retry, then validate result. |
| Blob | Search MI resource-ID connection; L19 Azure Storage SDK with Entra | Blob role and network path are independent of Search/CU roles | Prefer MI for workloads. Use one-object, read-only, short-lived SAS only when CU must fetch private input. |

**Portal / CLI / IaC split.** Use Foundry and Azure portals to verify supported regions, model deployments, semantic ranker, CU analyzer runs, indexer history, and costs. Use Azure CLI for identity and discovery, not secret-bearing URLs:

```bash
az account show --query "{subscription:id,tenant:tenantId,user:user.name}" -o json
az role assignment list --assignee <principal-object-id> --all -o table
az search service show -g <resource-group> -n <search-service> -o json
az storage container show --account-name <storage-account> -n <container> --auth-mode login
```

Use Bicep, Terraform, or ARM for resource kind/SKU, tags, diagnostics, private endpoints/DNS, managed identities, RBAC, firewall policy, and budgets. Keep index JSON, skillset JSON, and indexer JSON versioned and deploy them via reviewed REST/SDK automation. IaC cannot make a model, semantic ranker, CU feature, or private-link path available in an unsupported region.

## Choose a path

```text
Need an answer from many indexed files?
  Need exact terms only?          → keyword/BM25 (L01)
  Need semantic similarity?       → vector query (L02)
  Need both plus relevance boost? → hybrid + semantic (L03)

Need to enrich source files at ingestion?
  Split and embed existing text?  → this Search skillset (L04–L05)
  Need domain code/service call?  → deploy and wire a WebApiSkill (L06 is contract only)
  Need layout-aware multimodal extraction? → evaluate Search CU skill or CU pipeline; neither is wired here

Need information from one document?
  OCR text only?                  → prebuilt-read (L09)
  Layout, tables, figures?        → prebuilt-layout (L10)
  Invoice fields?                 → prebuilt-invoice (L11)
  Domain schema?                  → custom standard analyzer (L12)
  Compare several related files?  → Pro preview analyzer (L13)

Need an agent answer?
  Application needs retrieval/ranking/filter control? → manual RAG (L07–L08)
  Agent should choose retrieval tool itself?           → managed Azure AI Search tool, not implemented here
```

## Before running lessons

### Install, authenticate, and configure

From repository root:

```bash
uv sync
cp .env.example .env
az login
```

`DefaultAzureCredential` supplies the user token after `az login` on a workstation. In Azure, use a workload or managed identity. Successful token acquisition does not prove that identity has the required service data-plane role.

Set values in `.env`; do not commit it:

```dotenv
# Search and Blob
SEARCH_ENDPOINT=https://<search-service>.search.windows.net
SEARCH_INDEX_VECTOR=northwind-docs-vector
SEARCH_INDEXER=northwind-indexer
SEARCH_SKILLSET=northwind-skillset
STORAGE_ACCOUNT=<storage-account-name>
STORAGE_CONTAINER=northwind-docs
AZURE_SUBSCRIPTION_ID=<subscription-id>
AZURE_RESOURCE_GROUP=<resource-group>

# Azure OpenAI embeddings used by Search
AZURE_OPENAI_ENDPOINT=https://<resource>.openai.azure.com
EMBEDDING_MODEL=text-embedding-3-large

# Foundry project used by L07, L08, and L15
PROJECT_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<project>
DEFAULT_MODEL=<chat-deployment-name>

# Content Understanding
CU_ENDPOINT=https://<resource>.services.ai.azure.com
CU_API_VERSION=2025-11-01
```

The checked-in `.env.example` and `_shared.config.settings()` currently default `CU_API_VERSION` to `2025-11-15-preview`. Local CU reference material documents standard GA as `2025-11-01`; use the API version supported by the target resource and analyzer. L13 requires the separate `2025-05-01-preview` API for Pro mode. Restore the standard value after L13.

### Resources, RBAC, network, and storage

Create a nonproduction Azure AI Search service that supports vector workloads and, for L03, semantic ranking in its region. Create a Blob account/container, then upload PDFs from:

```text
_shared/sample_data/northwind_docs/
_shared/sample_data/northwind_policies/
_shared/sample_data/invoices/northwind_sample_invoice.pdf
_shared/sample_data/invoices/northwind_scanned_support_notice.pdf
```

Enable the **system-assigned managed identity** on the Search service. Grant that identity:

| Principal | Scope | Minimum role for this lab | Why |
|---|---|---|---|
| Search service identity | Storage account or target container | **Storage Blob Data Reader** | Blob indexer reads source files. |
| Search service identity | Azure OpenAI resource that hosts embeddings | **Cognitive Services OpenAI User** | Embedding skill during indexing and vectorizer at query time. |
| Lab user/workload | Search service | Search index management and query data roles appropriate to its tasks | Creates schema/data-source/skillset/indexer and queries index. |
| Lab user/workload | Foundry project/resource | **Foundry User** or equivalent project access | Creates L07 agent and calls project Responses API. |
| CU caller | CU resource | **Cognitive Services Content Understanding Contributor** for L12/L13 creation; **Reader** can analyze existing analyzers | Calls CU data plane. |

You need **Owner**, **User Access Administrator**, or an equivalent role to create role assignments. Search resource configuration and Search index data operations are separate permissions. Grant least privilege and scope roles to the narrowest resource/container practical.

The Blob data source contains a managed-identity resource-ID connection string:

```text
ResourceId=/subscriptions/<subscription>/resourceGroups/<resource-group>/providers/Microsoft.Storage/storageAccounts/<storage-account>/;
```

It intentionally contains no storage key. Do not replace it with a secret connection string or add a secret to source control. For a network-protected same-region storage account, configure the documented trusted-service or resource-instance path; a public URL alone does not grant the indexer access. Use shared private links/private endpoints where policy requires private Search to Azure OpenAI connectivity.

CU's `analyze` call operates on a service-reachable HTTPS URL. For private Blob input, issue a short-lived, read-only SAS URL containing only the required object. Do not put a broad account SAS in a shell history, committed `.env`, a model prompt, or a citation. A `file://` path is local to the caller and does not work for CU.

### Costs and side effects

| Action | Persistent change or billable behavior |
|---|---|
| L00 | Creates or replaces Search index definition. |
| L05 | Creates or replaces Search skillset. |
| L04 `--run` | Creates/replaces data source and indexer, then starts ingestion; `--wait` polls its terminal result. |
| L03 | Semantic requests can bill and require feature availability. |
| Indexer | Blob reads and embedding calls consume Search, Storage, and Azure OpenAI capacity. |
| L07 | Creates an agent version. |
| L09–L15 | CU analysis processes supplied content; L12/L13 create or replace analyzers; L15 also makes a model call. |

Use short sample files, bounded `top` values, and a disposable lab environment. Delete lab resources and revoke SAS tokens when finished.

## Exact Search build and run order

The four JSON assets are one contract. Do not provision only part of it:

1. Upload source files to `${STORAGE_CONTAINER}`.
1. Enable the Search identity and assign Blob/OpenAI roles.
1. Create the index before its skillset or indexer:

```bash uv run python 05-information-extraction/00_search_index_setup.py ```

1. Create the skillset:

```bash uv run python 05-information-extraction/05_search_skillset.py ```

1. Create data source and indexer, then begin indexing:

```bash uv run python 05-information-extraction/04_search_indexer_setup.py --run ```

1. Wait for a **successful** indexer run in Azure portal or inspect
`get_indexer_status()` through `indexer_client()`. Do not treat "run started" as indexed content.
1. Run L01–L03, then create L07 agent and run L08.

The scripts use Search REST API version `2026-04-01` for definitions because the JSON assets use REST camel-case properties. They do not deserialize those assets into Python SDK snake-case constructors.

### Schema contract

| Asset | Current contract |
|---|---|
| `index.json` | Chunk index `${SEARCH_INDEX_VECTOR}`. `chunk_id` is keyword key; `parent_id` is filterable parent key; `chunk`, `title`, and `source_url` are retrievable; `text_vector` is nonretrievable/stored false, 3072 dimensions. |
| `data_source.json` | `northwind-blob-datasource`, `azureblob`, managed-identity `ResourceId` connection, configured container. |
| `skillset.json` | Character-based SplitSkill: 2,000 characters, 500 overlap; Azure OpenAI embedding for each `/document/pages/*`; projects chunks, vector, filename, and Blob path. |
| `indexer.json` | Connects data source, target index, and skillset; extracts content and metadata with default parsing. |

`text-embedding-3-large` has a 3072-dimension default used by this index. If you select a model or configured embedding dimension that differs, update the vector field and embedding skill together. The query vectorizer and indexing embedding skill must use compatible model, deployment, dimensions, and distance assumptions.

Index projection creates one child Search document per page chunk. It repeats `title` and `source_url`, maps `parent_id` automatically, and uses `skipIndexingParentDocuments` so null-chunk parent records do not pollute retrieval. Do not add a manual mapping for `parent_id`; that breaks projection change tracking. If you add ACL metadata, project it to **every child chunk**.

## Search retrieval and ranking

| Mode | Lesson | What happens | Limitation |
|---|---:|---|---|
| Keyword | L01 | BM25 ranks `search_text`. | Misses paraphrases. |
| Vector | L02 | `VectorizableTextQuery` makes Search call its configured vectorizer, then nearest-neighbor search runs over `text_vector`. | Misses exact rare terms and requires vectorizer/model alignment. |
| Hybrid | L03/L08 | BM25 and vector candidates combine by RRF. | Candidate quality still depends on chunking and source content. |
| Semantic | L03 | Semantic ranker reranks an initial BM25/RRF result set based on configured `title` and `chunk`. | Does not retrieve new corpus matches; only top candidates progress. |

`k_nearest_neighbors` controls vector candidates, while `top` controls how many results the application receives. L03's semantic output has `@search.reranker_score`; keyword/vector output has `@search.score`. A reranker score is not comparable to a BM25/vector score, and score thresholds need evaluation data rather than guessed constants.

Semantic ranker uses text in its semantic configuration. This index's `default` configuration prioritizes `title` and `chunk`. It can provide captions and answers when requested, but semantic answers/captions are extractive Search output, not generated answers.

## Evidence, citation, ACL, and provenance

L08 retrieves `chunk`, `title`, `parent_id`, and `source_url`, then includes them in its prompt. This is application-owned provenance. The agent is told to cite source URLs, but L08 does not validate that each answer claim maps to a source or render structured citation annotations.

Production retrieval must enforce access **before** prompt construction. This lab index has no ACL field and L08 sends no filter, so it is unsuitable for mixed-permission content. Choose a supported native ACL ingestion path, or store a nonretrievable, filterable `Collection(Edm.String)` of caller/group identifiers on each chunk and apply an OData security filter such as `group_ids/any(g:search.in(g, '<caller-group-ids>'))`. Derive identities from trusted authentication context, not model or client text.

At ingestion, retain immutable source identifier/version, Blob path or business source URI, content hash, indexer/skillset version, chunk ID, parent ID, ACL version, and ingestion timestamp. At answer time, record user or tenant, normalized query, effective authorization filter, index version, retrieved chunk IDs/source URLs, ranking configuration, model/agent version, and citation rendering. Redact or access-control logs containing sensitive prompts or document text. Reindex when source permissions change.

## Manual RAG versus managed Search tools

L07 and L08 implement **manual RAG**, not a managed Azure AI Search agent tool:

```text
L08 application → hybrid Search query → prompt contains source blocks
                → Foundry prompt agent → answer text
```

The application chooses query parameters, applies filters, limits chunks, and must enforce ACLs, cite sources, handle no-result cases, and evaluate quality. Use this pattern when those controls are product requirements.

A managed Foundry Azure AI Search tool is different; L20 supplies an explicit opt-in example:

```text
Agent → configured Azure AI Search tool/project connection → Search index
      → tool result and URL citation annotations → agent response
```

It requires a Foundry project connection, supported Search index fields (retrievable content and source URL), tool configuration, and project managed-identity roles for the selected keyless setup. L20 creates a persistent agent version only with `--enable --apply`, and invokes it only with `--enable --run`; it prints URL citations when returned. It does not replace index-level ACL design, citation evaluation, or tool-result authorization. Do not claim that L07's agent autonomously searches the index.

Azure AI Search agentic retrieval/knowledge bases are another, separate managed preview path: Search can plan subqueries, execute them, semantically rerank results, return source references/activity, and supply grounding data to an agent. This repository does not create a knowledge source, knowledge base, MCP connection, or agentic-retrieval call.

## Custom skill boundary

L06 is a local demonstration of a **Web API custom-skill payload contract**:

```json
{
  "values": [{
    "recordId": "0",
    "data": {"normalized_text": "…", "sla_tier": "Gold"},
    "errors": [],
    "warnings": []
  }]
}
```

L17 creates a derived skillset with that `WebApiSkill`, retargets the indexer, and starts it only with `--apply --run`; default mode is local preflight. It does **not** deploy an Azure Function or authenticate its inbound endpoint. To make it production-ready, host HTTPS code, validate its batch contract, configure Entra ID/`authResourceId` support where available, bound batch, timeout, and parallelism, and return per-record errors instead of failing unrelated records. Never use a function key or static bearer token in source.

## Content Understanding: API, inputs, and modes

`_shared.cu_client.analyze()` posts:

```json
{"inputs": [{"url": "https://<reachable-file>"}]}
```

It receives `202 Accepted`, reads `Operation-Location`, and polls every two seconds until `succeeded`, `failed`, or `canceled`. The helper accepts either one URL or a list. This is important: standard GA `2025-11-01` accepts one input item, while L13 changes the configured API version to Pro preview, where the helper's URL list represents multi-document input.

CU uses `DefaultAzureCredential` for `https://cognitiveservices.azure.com/.default`. It does not use a Foundry project endpoint or an Azure OpenAI endpoint as a substitute for `CU_ENDPOINT`. For production, add bounded polling timeout/backoff, cancellation, failure diagnostics, and a queue/job store rather than holding a web request open.

| Capability | Standard | Pro preview |
|---|---|---|
| API | GA `2025-11-01` | `2025-05-01-preview` |
| Inputs | One URL per analysis request | Multiple related document URLs. |
| Modalities | Documents, images, audio, video, and text subject to analyzer/limits. | Documents only; current limits restrict input to PDF, TIFF, and images, 100 MB/150 pages total. |
| Field methods | Extract, classify, generate. | Classify and generate; `extract` is unsupported. |
| Confidence/source grounding | Available when explicitly enabled for document fields. | Unavailable. |
| Reasoning/reference data | Per-input extraction. | Multi-step cross-document reasoning and reference data. |

Use standard for high-volume extraction and Pro only when a cross-document decision actually needs it. Pro is preview, has higher latency/cost, and is not a "better one-document OCR" switch.

## Markdown RAG and reasoning boundary

L14 calls `prebuilt-layout`, header-splits returned Markdown, then applies an 800-character recursive splitter with 100-character overlap. It prints chunk count and first chunk. It **does not upload, embed, or index** those chunks.

That boundary is intentional. This index requires `text_vector`; a direct Search upload of only `chunk` cannot participate in vector retrieval. To use the repository's integrated pipeline, upload the original source document to Blob and rerun L05/L04 so Search creates vectors. For a direct Markdown ingestion design, create client-side embeddings and upload a valid complete document shape, including source/provenance and ACL fields.

CU Markdown retains headings, tables (including HTML for merged cells), figures, formulas, selection marks, links, and page metadata. It is better evidence than flattened text, but still inspect chunk boundaries, table splits, figure references, prompt injection in source text, and retrieval quality.

L15 is a different pattern: CU extracts invoice fields, then an ephemeral Responses call produces a review. CU performs extraction; the language model performs bounded business reasoning. Treat model approval status as a proposed decision unless deterministic controls or human review validate it.

## Lesson map and run order

| # | Question | Run | Expected output | Limitation |
|---:|---|---|---|---|
| 00 | What schema accepts this pipeline? | `uv run python 05-information-extraction/00_search_index_setup.py` | `index '<name>' saved.` | Replaces persistent index definition; does not ingest. |
| 01 | How does exact-term retrieval rank? | `uv run python 05-information-extraction/01_search_basic_query.py` | Scores, titles, chunk previews. | Queries vector index despite old descriptions of a text-only index. |
| 02 | Can paraphrase retrieve relevant chunks? | `uv run python 05-information-extraction/02_search_vector.py` | Up to five semantic matches. | Requires populated vectors and configured vectorizer. |
| 03 | How do ranking modes differ? | `uv run python 05-information-extraction/03_search_hybrid_semantic.py` | Keyword, vector, hybrid+semantic top-three lists. | Semantic ranker availability/billing required. |
| 04 | How is Blob ingestion defined and started? | `uv run python 05-information-extraction/04_search_indexer_setup.py --run --wait` | Data source/indexer saved; run reaches success or returns failure/timeout. | Persistent resource changes; bounded five-minute wait is not production orchestration. |
| 05 | How are chunks and embeddings produced? | `uv run python 05-information-extraction/05_search_skillset.py` | `skillset '<name>' saved.` | Creates only Split + embedding skills. |
| 06 | What does a custom skill return? | `uv run python 05-information-extraction/06_search_custom_skill.py` | Two local contract records. | No hosted custom skill or indexer wiring. |
| 07 | How is a constrained manual-RAG agent created? | `uv run python 05-information-extraction/07_rag_prompt_agent.py` | `Agent northwind-manual-rag-agent v<version> created.` | No Search tool attached. |
| 08 | How does an app own retrieval? | `uv run python 05-information-extraction/08_rag_client_run.py` | Grounded refund answer or refusal. | No ACL filter/citation validation/evaluation. |
| 09 | How does basic OCR work? | `uv run python 05-information-extraction/09_cu_prebuilt_read.py` | Status and Markdown preview. | Layout semantics are limited. |
| 10 | How does layout preserve structure? | `uv run python 05-information-extraction/10_cu_prebuilt_layout.py` | Page/table/figure/section counts and Markdown. | Needs reachable PDF URL; no indexing. |
| 11 | How are invoice fields extracted? | `uv run python 05-information-extraction/11_cu_invoice.py` | Prebuilt field objects. | Requires `SAMPLE_INVOICE_URL`; field confidence depends on result/configuration. |
| 12 | How is a custom document schema created? | `uv run python 05-information-extraction/12_cu_custom_analyzer.py` | Analyzer created; fields if URL supplied. | Creates persistent analyzer; schema quality needs evaluation. |
| 13 | How are related documents reasoned over? | `CU_API_VERSION=2025-05-01-preview uv run python 05-information-extraction/13_cu_pro_mode.py` | Generated `consistency_summary`. | Preview; only `generate` field used; inputs must meet Pro limits. |
| 14 | How does layout Markdown chunk? | `uv run python 05-information-extraction/14_cu_markdown_for_rag.py` | Markdown length, chunk count, first chunk. | Inspect-only; no embedding/index upload. |
| 15 | How can extracted fields ground a review? | `uv run python 05-information-extraction/15_cu_content_agent.py` | Summary, approval status, issues, next step. | Model call can still make unsupported inferences. |
| 16 | How can CU media output become bounded RAG records? | `uv run python 05-information-extraction/16_cu_multimodal_rag.py` | Local preflight; `--apply` prints at most 20 redacted-source records. | Does not index output. |
| 17 | How is a Web API skill wired safely? | `uv run python 05-information-extraction/17_search_custom_skill_deploy.py` | Local preflight; `--apply [--run]` deploys/starts derived pipeline. | Endpoint hosting and inbound authentication remain yours. |
| 18 | How is ingestion health observed? | `uv run python 05-information-extraction/18_search_monitoring.py` | Local preflight; `--run` prints redacted status/count. | Read-only snapshot, not alerting. |
| 19 | Which identity reads Blob at runtime? | `uv run python 05-information-extraction/19_blob_identity_paths.py` | Local preflight; `--run` reads container properties. | Tests operator/runtime identity, not Search MI. |
| 20 | How does a managed agent call Search? | `uv run python 05-information-extraction/20_managed_search_agent_tool.py` | Local preflight; explicit enable/apply/run creates or invokes agent. | Tool use does not enforce application ACLs. |

Run L00, L05, L04 `--run --wait`, then L01–L03. Run L07 before L08. CU lessons are independent after endpoint/authentication setup; run L13 with its preview version and return `.env` to a standard API version afterward.

## Detailed lesson walkthroughs

Each lesson below states its **what/why**, **architecture and code path**, **use / do not use**, and **output, security, cost, and production pitfall**. All cloud actions use configured nonproduction resources; default preflight paths in L16–L20 make no cloud request.

### 00 — Create vector index

**What / why.** Creates or replaces schema before ingestion, so vector, semantic, filter, and retrieval contracts agree. **Path.** `index.json` → `_search_rest.load_definition()` replaces environment markers → Entra REST `PUT /indexes` → saved-name output. **Use** to establish a clean disposable lab index; **not** for additive production schema migration.

**Security, cost, pitfall.** Requires index-management permission and changes a persistent resource; vector/semantic capability affects service cost. Preserve ACL/provenance fields in a production schema before first ingestion. Current asset key is `chunk_id`, not `id`; changing dimensions/model requires a compatible skill, vectorizer, and index rebuild.

### 01 — Keyword/BM25 query

**What / why.** Sends `refund` to `search_text` to demonstrate lexical ranking for exact policy terms, identifiers, and rare vocabulary. **Path.** `search_client(index)` → `search(search_text, select=chunk,title)` → score and preview stdout. **Use** exact-token retrieval or as hybrid's lexical leg; **not** paraphrase-only retrieval or access control.

**Security, cost, pitfall.** Query role is required and returned chunks may be sensitive; do not log them blindly. Search query capacity is consumed. This lesson has no security filter, `top`, citation validation, retry, or empty result policy; apply trusted caller/tenant filters before requesting fields.

### 02 — Vector query

**What / why.** Retrieves paraphrases using server-side query embedding rather than a literal match. **Path.** `VectorizableTextQuery(text, fields=text_vector, k=5)` → index vectorizer → HNSW nearest neighbors → scores/previews. **Use** semantic similarity; **not** when exact codes dominate or model/vectorizer compatibility is unknown.

**Security, cost, pitfall.** Query text reaches embedding service; protect it as customer data. Search/vectorizer and embedding capacity can bill. It needs finished ingestion, populated vectors, matching 3072 dimensions, deployment, and MI access; `k` candidates are not a relevance or authorization guarantee.

### 03 — Hybrid plus semantic reranking

**What / why.** Compares lexical, vector, then RRF hybrid candidates reranked by semantic configuration, teaching why one score does not fit all modes. **Path.** Three `client.search()` calls; final call combines text and `VectorizableTextQuery`, `QueryType.SEMANTIC`, and `default` config. **Use** general RAG baseline after evaluation; **not** as proof semantic ranker finds documents absent from initial candidates.

**Security, cost, pitfall.** Same unfiltered-result exposure as L01/L02. Semantic ranker availability and billing are region/SKU dependent. Do not compare reranker and BM25/vector scores or hard-code an arbitrary cutoff; evaluate recall, citations, latency, and no-answer behavior on labeled data.

### 04 — Blob data source and indexer

**What / why.** Provisions ingestion connection/job and optionally starts it. **Path.** `data_source.json` + `indexer.json` → REST `PUT` resources → `run_indexer()`; `--wait` polls `last_result` to success/failure/timeout. **Use** managed Blob ingestion; **not** a synchronous request path.

**Security, cost, pitfall.** Search MI needs Blob Data Reader and OpenAI User; network/DNS/firewall reachability remains separate. Blob reads, enrichment, and embeddings cost money. Starting is not complete ingestion without `--wait`; production should schedule, alert, retain failure diagnostics, and handle deletes, change detection, poison documents, and reindexing.

### 05 — Split and embedding skillset

**What / why.** Defines repeatable chunks and document embeddings at index time. **Path.** JSON SplitSkill `/document/content` → overlapping `pages` → AzureOpenAIEmbeddingSkill → index projection child chunks. **Use** integrated text vectorization; **not** a query-time transform or CU layout pipeline.

**Security, cost, pitfall.** Search MI calls Azure OpenAI, so private endpoint, role, and deployment must all work. Every chunk consumes embedding capacity. Character chunks can split tables/semantics; tune against documents, retain parent/provenance/ACL metadata on every child, and never map `parent_id` manually in index projections.

### 06 — Custom-skill contract

**What / why.** Demonstrates WebApiSkill's batched record-in/record-out shape without cloud dependencies. **Path.** sample `values[]` → `handle_batch()` → `transform()` normalizes text/identifies tier → JSON output. **Use** to test deterministic enrichment contract; **not** as hosted, authenticated enrichment.

**Security, cost, pitfall.** Default path is free/local but source text is untrusted. A deployed skill must authenticate Search, validate size/content, bound work, and return per-record errors/warnings. Do not expose secrets or make external network calls for each record without throttling/idempotency.

### 07 — Manual-RAG prompt agent

**What / why.** Stores a constrained agent definition that answers only from evidence later supplied by application code. **Path.** `project_client()` → `PromptAgentDefinition(model,instructions)` → `agents.create_version()` → name/version. **Use** versioned response policy with application-owned search; **not** autonomous Search retrieval.

**Security, cost, pitfall.** Requires Foundry project access and creates a persistent agent version; inference occurs only later. Instructions do not prevent poisoned retrieved text, ACL bypass, or fabricated citations. Version and evaluate prompts; separately authorize retrieval and enforce structured claim/citation checks.

### 08 — Application-owned RAG

**What / why.** Shows retrieval before generation when product owns ranking and filters. **Path.** `_retrieve()` runs hybrid query → builds source blocks with title/parent/URL → Responses call references L07 agent → output text. **Use** custom filters, ranking, deterministic prompt budget, and audit; **not** an excuse to send unbounded corpus text to a model.

**Security, cost, pitfall.** Search plus model calls incur two services' latency/cost and retrieved text may inject instructions. Current code has no ACL filter, token budget, duplicate removal, citation parser, or evaluation. Apply authorization before `select`, retain chunk IDs/index version, cap and sanitize evidence, and refuse when evidence is insufficient.

### 09 — CU prebuilt-read

**What / why.** Extracts basic readable text/Markdown from one remotely reachable document. **Path.** source URL → `analyze("prebuilt-read")` → async CU submit/poll → status plus first 500 Markdown characters. **Use** OCR baseline; **not** table/figure-aware extraction or corpus search.

**Security, cost, pitfall.** Default public sample still sends its URL to CU; private data needs short-lived read-only HTTPS SAS. CU processing is billable. OCR errors, reading order, and injection text remain possible; validate quality/language/limits and do not treat preview output as authoritative facts.

### 10 — CU prebuilt-layout

**What / why.** Preserves pages, tables, figures, sections, and Markdown for structure-aware downstream processing. **Path.** `CU_LAYOUT_SOURCE_URL` → `analyze("prebuilt-layout")` → first content object's counts/Markdown. **Use** layout-aware document representation; **not** direct vector indexing.

**Security, cost, pitfall.** CU must resolve URL through network/firewall/SAS before expiry; content processing costs apply. Output counts are not accuracy metrics. Inspect table/header/figure boundaries and page references; preserve source/version metadata and route low-confidence or consequential fields to human review.

### 11 — CU prebuilt-invoice

**What / why.** Extracts invoice vendor, customer, totals, dates, and line items from one invoice. **Path.** `SAMPLE_INVOICE_URL` validation → `analyze("prebuilt-invoice")` → print `contents[0].fields`. **Use** standard invoice schema; **not** payment approval, fraud decision, or local-file input.

**Security, cost, pitfall.** Invoice data is sensitive; use one-object SAS, redact logs, and restrict result access. CU calls are billable. A field's presence/score does not prove correctness; check totals/currency/vendor against deterministic business rules and retain source/page evidence.

### 12 — Custom standard analyzer

**What / why.** Creates reusable `prebuilt-document`-based schema for support notice extraction/classification/generation. **Path.** `_DEFINITION` → `create_analyzer()` → optional URL → `analyze()` → fields. **Use** a tested domain schema; **not** Pro cross-document logic or unreviewed production generation.

**Security, cost, pitfall.** Creation needs CU Contributor and creates persistent state; analysis can bill. Generated `summary` is model output, not source truth. Version analyzer/schema/examples, evaluate precision/recall by field, track analyzer ID/version, and avoid silently replacing a production definition.

### 13 — CU Pro cross-document review

**What / why.** Uses preview Pro mode to generate one consistency summary over related mortgage documents. **Path.** comma-separated URLs → `create_analyzer(mode="pro")` → multi-input `analyze()` → fields. **Use** bounded related-document reasoning; **not** normal single-file OCR.

**Security, cost, pitfall.** Set `CU_API_VERSION=2025-05-01-preview` only for this run and restore standard configuration after it. Preview has feature, region, latency, input, and billing constraints; keep highly sensitive documents segregated. Pro lacks standard grounding/confidence behavior and supports generate/classify, not extract; require human/deterministic review.

### 14 — CU Markdown chunk inspection

**What / why.** Demonstrates structure-aware splitting without pretending printed chunks are indexed. **Path.** layout analysis → Markdown header splitter → recursive 800/100 character splitter → count/first chunk. **Use** to inspect chunk policy; **not** direct upload to this vector index.

**Security, cost, pitfall.** CU input and Markdown may contain secrets or injections; do not print/store raw production text casually. CU costs apply; local splitting does not. Tables and headings can still split badly. For production, evaluate chunks/retrieval and generate valid vectors plus complete ACL/provenance records, or feed original files through L04/L05.

### 15 — CU fields to model review

**What / why.** Separates extraction from bounded language reasoning over invoice fields. **Path.** CU invoice fields → formatted field dump → project Responses `instructions` + input → business-style review. **Use** draft triage with review; **not** an automated approval authority.

**Security, cost, pitfall.** Two data services process invoice information; minimize prompts, log safely, and enforce access before model call. CU and model tokens cost money. The prompt cannot repair bad extraction or prevent unsupported inference; validate fields/thresholds, require policy checks and human approval for consequential action.

### 16 — Multimodal CU-to-RAG handoff

**What / why.** Selects prebuilt layout/imageSearch/videoSearch by extension and converts one CU result to bounded, provenance-aware records. **Path.** HTTPS source → analyzer choice → `analyze()` → max 20 records of max 4,000 characters with SAS-free source metadata. **Use** controlled ingestion-worker handoff; **not** direct Search upload or universal media routing.

**Security, cost, pitfall.** `--apply` submits content; source query credentials are intentionally omitted from output. CU media processing costs and limits vary. Extension is not trusted MIME validation; production validates media, malware, ownership, tenancy, time ranges, retention, embeddings, ACLs, and chunk/citation quality before indexing.

### 17 — Deploy derived Web API skill pipeline

**What / why.** Bridges L06's contract into Search enrichment only after explicit mutation consent. **Path.** local preflight → HTTPS URL validation → clone skillset, insert WebApiSkill, retarget indexer → REST `PUT`; optional `run_indexer()`. **Use** verified deterministic preprocessing; **not** localhost or a function endpoint without authentication.

**Security, cost, pitfall.** `--apply` changes persistent skillset/indexer and `--run` can invoke it per batch; manage endpoint ingress, Entra auth, timeout, rate, and least privilege. Test rollback because derived skillset changes text that gets embedded. Current HTTP helper intentionally redacts authorization in source; verify real token/header behavior in integration tests.

### 18 — Search monitoring snapshot

**What / why.** Reads indexer health and document count without exposing indexed content. **Path.** `get_indexer_status()` + `get_document_count()` → `status_summary()` → regex-redacted error message. **Use** a smoke diagnostic; **not** complete observability or SLO evidence.

**Security, cost, pitfall.** `--run` is read-only but status errors can contain URLs/secrets, hence redaction; restrict monitoring-log access. Read calls use service capacity. Production alerts on failed/stale runs, failed-item ratio, unexpected count delta, latency, quota, and query/retrieval quality; export minimal telemetry to approved retention/storage.

### 19 — Blob identity-path check

**What / why.** Distinguishes application/operator Blob access from indexer's Search MI access. **Path.** account-name validation → `BlobServiceClient` with `DefaultAzureCredential` → `get_container_properties()` → name/timestamp. **Use** to prove current runtime's Entra data path; **not** to prove indexer access.

**Security, cost, pitfall.** `--run` requires container-scoped Blob Data Reader and network/DNS access but no account key. It is a small read transaction. Do not broaden roles after failure: inspect effective principal, scope, tenant, firewall/private endpoint, and separately validate Search service MI.

### 20 — Managed Azure AI Search agent tool

**What / why.** Creates a Foundry prompt-agent version with an Azure AI Search vector-semantic-hybrid tool, then optionally invokes it. **Path.** connection name + index → project connection lookup → tool resource → `create_version()` → Responses `agent_reference` with required tool choice → URL citations. **Use** supported managed retrieval integration; **not** replacement for application authorization/control requirements.

**Security, cost, pitfall.** `--enable` makes mutation/invocation deliberate; agent creation persists and invocation consumes Search/model capacity. Project connection, project identity, Search role, source URL policy, network path, and index ACL design must all align. Test tool failures/no-result/citation accuracy and retain agent/index/config versions; never let agent instructions substitute for security trimming.

## Security and ingestion hygiene

- Treat Blob documents, OCR text, Markdown, custom-skill payloads, and Search
chunks as untrusted input. A document can contain indirect prompt injection.
- Validate MIME type, size, page/count limits, malware-scanning policy, and
tenant/source ownership before indexing. Reject password-protected or malformed content according to policy.
- Use managed identities and short-lived SAS URLs. Scope SAS to one object,
read only, short expiry, HTTPS, and no account-wide permission.
- Store exceptional third-party secrets, Function credentials, and any
connection material in Azure Key Vault or a Foundry connection backed by it; grant the runtime identity `get` only. A Key Vault secret or Foundry connection does not grant its caller permission to Blob, Search, or CU.
- For private deployments, create and test private endpoints plus private DNS
separately for Search, Storage, Azure OpenAI, Foundry/CU, Key Vault, and monitoring. Confirm the actual indexer/agent/runtime egress path; private endpoint and RBAC solve different problems.
- Separate customer/tenant indexes or apply enforced filters. Never rely on an
instruction such as "only answer authorized content."
- Project ACL/provenance fields to every chunk. Reindex/revoke when source
access changes. Do not expose nonretrievable ACLs in answer payloads.
- Keep source URL citations meaningful but avoid leaking signed URLs. Render a
stable business/source link or opaque source identifier when necessary.
- Redact/minimize logs; prompts and retrieved chunks can contain confidential
data. Apply retention, deletion, and data-residency requirements.
- Evaluate retrieval recall, citation correctness, answer groundedness, ACL
enforcement, extraction accuracy, latency, cost, and failure behavior with representative documents before production.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `Missing env var …` | Placeholder/empty `.env` value. | Fill the exact setting required by the script. |
| Search `401`/`403` | Wrong identity or Search data role. | Check effective `DefaultAzureCredential` identity and Search RBAC scope. |
| Indexer cannot read Blob | Missing Search identity, Blob role, container, or network path. | Enable Search MI; assign **Storage Blob Data Reader**; validate resource ID, container, firewall/private connectivity. |
| Embedding skill/vectorizer `401`/`403` | Search MI cannot use Azure OpenAI. | Assign **Cognitive Services OpenAI User**; verify endpoint/deployment/model. |
| Dimension mismatch | Index, skill, and vectorizer describe different embedding outputs. | Make model/deployment/dimensions compatible; rebuild affected index. |
| No vector results | Indexer did not finish or chunks lack vectors. | Inspect indexer execution history and `text_vector` population. |
| Semantic configuration error | `default` missing or ranker unavailable. | Provision L00 schema and confirm regional semantic feature/billing. |
| L08 agent not found | L07 absent or agent name differs. | Run current `07_rag_prompt_agent.py`; it creates `northwind-manual-rag-agent`. |
| CU cannot fetch URL | `file://`, expired SAS, blocked network, or bad URL. | Use service-reachable HTTPS public URL or fresh least-privilege Blob SAS. |
| CU polling never succeeds | Job failed/throttled or caller has no bounded timeout. | Inspect final body/status; reduce input; add timeout/backoff/queue in production. |
| L13 rejects input | Standard API active or Pro input/field unsupported. | Set preview API, use supported files, omit `extract` fields. |
| Markdown chunks cannot vector-search | L14 only prints chunks. | Use Blob + integrated indexer, or generate vectors before direct upload. |
| L17 custom skill fails | Endpoint is unreachable, rejects batch contract, or indexer identity/network path is wrong. | Start with local L06 payload; verify HTTPS, Entra/inbound auth, timeout, batch errors, and indexer history. |
| L18 shows stale/failed run | Scheduler did not run, source changed, or enrichment/network dependency failed. | Inspect indexer execution history and redacted diagnostics; fix cause, then rerun/reindex deliberately. |
| L19 succeeds but indexer fails | Caller MI differs from Search service MI. | Validate Search system-assigned identity's Blob role and storage network resource-instance/private-link path. |
| L20 connection/tool fails | Wrong Foundry connection/index/role, unsupported setup, or network reachability. | Validate project connection ID, retrievable fields/source URL, project/Search RBAC, and agent version before invocation. |

Validate local assets after documentation or configuration changes:

```bash
python -m json.tool 05-information-extraction/skillset_configs/index.json >/dev/null
python -m json.tool 05-information-extraction/skillset_configs/data_source.json >/dev/null
python -m json.tool 05-information-extraction/skillset_configs/skillset.json >/dev/null
python -m json.tool 05-information-extraction/skillset_configs/indexer.json >/dev/null
python -m compileall -q 05-information-extraction
```

## Objective coverage and intentional gaps

| Objective | Current evidence | Gap/recommended next lesson |
|---|---|---|
| Ingest and index documents | L00/L04/L05 Blob-to-vector pipeline. | Add image, audio, and video ingestion with appropriate multimodal extraction. |
| Vector, hybrid, and semantic retrieval | L02/L03. | Add relevance test set, captions/answers, filters, score analysis, and monitoring. |
| Built-in/custom enrichment | Built-in split/embedding deploys; L06 validates custom contract. | Deploy/secure a WebApiSkill and add image/layout enrichment. |
| RAG ingestion with OCR/layout | L09/L10/L14 show extraction/chunk inspection. | Feed CU Markdown into an embedding-capable, provenance/ACL-preserving index pipeline. |
| Connect retrieval to agent tools | L07/L08 manual RAG. | Add documented Foundry Azure AI Search tool or Search agentic-retrieval knowledge base/MCP lesson. |
| Multimodal OCR/layout/fields | Separate L09–L12 calls. | Add one composed, evaluated workflow with routing, confidence threshold, and human review. |
| Clean grounded representations | L14 Markdown inspection and L15 field-to-model reasoning. | Persist citations/source grounding and verify claim-to-source mapping. |
| Standard and Pro CU | L09–L13. | Add explicit API-version isolation, Pro multi-document test fixtures, and failure/limit handling. |
| CU multimodal RAG handoff | L16 creates bounded, source-safe records. | Add validated MIME routing and a durable ACL/provenance-preserving ingestion worker. |
| Hosted custom enrichment | L06 contract and L17 opt-in wiring. | Deploy/authenticate endpoint, load test indexer concurrency, and automate rollback. |
| Retrieval operations | L18 snapshot and L19 identity check. | Add alerts, dashboards, cost budgets, traces, and incident runbooks. |
| Managed Search agent | L20 explicit agent/tool creation and invocation. | Evaluate tool/citations, enforce authorization, and automate lifecycle cleanup. |

## Common exam traps

| Misconception | Correct answer |
|---|---|
| Semantic ranker is vector search. | Vector search finds embedding neighbors; semantic ranker reranks initial text/RRF candidates. |
| Skillsets run when a user queries. | Skillsets run during indexer enrichment. |
| A vectorizer embeds source documents. | It embeds query text at query time. The embedding skill/indexer creates document vectors here. |
| Directly uploading L14 text makes it vector-searchable. | Not without a matching client-generated vector and full index-document contract. |
| Search and CU are interchangeable. | Search retrieves across indexed corpus; CU extracts one submitted content item into structure/fields. |
| CU accepts local files because Python can read them. | CU service fetches HTTPS URL input; `file://` is not reachable. |
| Pro mode means better standard extraction. | Pro preview is for multi-document reasoning; it has feature/input limits and lacks grounding/confidence. |
| Prompt instructions enforce document permissions. | Authorization must trim results before model input. |
| L07 is a managed Search agent. | It is a prompt agent with no Search tool. L08 performs retrieval in application code. |
| A source URL alone proves an answer is grounded. | Preserve source/chunk provenance and evaluate citation-to-claim correctness. |

## AI-103 and interview rehearsal

**AI-103 decision prompts.**

- Need exact lookup plus paraphrase recall? Select hybrid retrieval; semantic
ranker reranks candidates and does not replace vector search.
- Need structured fields or layout from one submitted invoice? Select CU
analyzer; need answers over many files? Index then retrieve with Search.
- Need pre-query authorization? Put tenant/group ACL metadata on every child
chunk and apply trusted OData filter before prompt/tool input.
- Need indexer Blob access without a key? Enable Search MI, grant narrowly
scoped Blob Data Reader, configure resource-ID connection and network path.
- Need CU private input? Give CU a service-reachable, short-lived, read-only
object SAS; never a local path or broad account SAS.
- Need app-controlled ranking/citations? Manual RAG. Need Foundry-managed
Search tool behavior? Configure project connection/tool, then still test ACL, citations, costs, and lifecycle.

**Interview questions.**

1. Why use an embedding skill and a vectorizer? Document vectors are created
at ingestion; vectorizer embeds query text at query time.
2. How do you prevent RAG data leakage? Derive identity externally, filter
chunks before retrieval/model input, project ACLs to children, and test cross-tenant negatives.
3. Why is `--wait` not enough for production indexing? A web process should
not own long jobs; use scheduling/queue state, retries, metrics, alerts, poison-document handling, and an idempotent reindex plan.
4. When choose CU Markdown rather than flattened OCR? When headings, tables,
figures, and reading order help chunk/retrieval quality; still evaluate extraction and chunk boundaries.
5. How investigate a 403? Identify endpoint, effective principal, requested
data-plane action, scope, firewall/DNS path, and whether runtime identity differs from developer/CI/Search MI.

## Official references

- [Azure AI Search documentation](https://learn.microsoft.com/azure/search/)
- [Integrated vectorization](https://learn.microsoft.com/azure/search/vector-search-integrated-vectorization)
- [Vector, hybrid, and semantic search](https://learn.microsoft.com/azure/search/vector-search-how-to-query)
- [Search index projections](https://learn.microsoft.com/azure/search/search-how-to-define-index-projections)
- [Search managed identities and Storage access](https://learn.microsoft.com/azure/search/search-how-to-managed-identities)
- [Security trimming for Search](https://learn.microsoft.com/azure/search/search-security-trimming-for-azure-search)
- [Custom Web API skills](https://learn.microsoft.com/azure/search/cognitive-search-custom-skill-web-api)
- [Azure AI Search tool for Foundry agents](https://learn.microsoft.com/azure/ai-foundry/agents/how-to/tools/ai-search)
- [Content Understanding documentation](https://learn.microsoft.com/azure/ai-services/content-understanding/)
- [CU standard and Pro modes](https://learn.microsoft.com/azure/ai-services/content-understanding/concepts/standard-pro-modes)
- [CU Markdown output](https://learn.microsoft.com/azure/ai-services/content-understanding/document/markdown)
- [Azure managed identities](https://learn.microsoft.com/entra/identity/managed-identities-azure-resources/overview)
- [Azure Blob user delegation SAS](https://learn.microsoft.com/azure/storage/blobs/storage-blob-user-delegation-sas-create-cli)
- [Azure Key Vault security](https://learn.microsoft.com/azure/key-vault/general/security-features)

## Local reference material

- [Integrated vectorization](../.context/azure-ai-docs/articles/search/vector-search-integrated-vectorization.md)
- [Index projections](../.context/azure-ai-docs/articles/search/search-how-to-define-index-projections.md)
- [Semantic ranking](../.context/azure-ai-docs/articles/search/semantic-search-overview.md)
- [Search managed identities](../.context/azure-ai-docs/articles/search/search-how-to-managed-identities.md)
- [Blob managed-identity connection](../.context/azure-ai-docs/articles/search/search-howto-managed-identities-storage.md)
- [Security trimming](../.context/azure-ai-docs/articles/search/search-security-trimming-for-azure-search.md)
- [Custom Web API skill](../.context/azure-ai-docs/articles/search/cognitive-search-custom-skill-web-api.md)
- [Azure AI Search tool for Foundry agents](../.context/azure-ai-docs/articles/foundry/agents/how-to/tools/ai-search.md)
- [Search agentic retrieval](../.context/azure-ai-docs/articles/search/agentic-retrieval-overview.md)
- [CU analyzer overview](../.context/azure-ai-docs/articles/ai-services/content-understanding/document/overview.md)
- [CU prebuilt analyzers](../.context/azure-ai-docs/articles/ai-services/content-understanding/concepts/prebuilt-analyzers.md)
- [CU standard and Pro modes](../.context/azure-ai-docs/articles/ai-services/content-understanding/concepts/standard-pro-modes.md)
- [CU Markdown representation](../.context/azure-ai-docs/articles/ai-services/content-understanding/document/markdown.md)
- [CU security and RBAC](../.context/azure-ai-docs/articles/ai-services/content-understanding/concepts/secure-communications.md)
- [CU limits](../.context/azure-ai-docs/articles/ai-services/content-understanding/service-limits.md)
