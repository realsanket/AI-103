# Domain 5: Information extraction

> Study guide and runnable labs for Azure AI Search retrieval and Azure
> Content Understanding in Foundry Tools. Run commands from repository root:
> `uv run python 05-information-extraction/<lesson>.py`.
>
> This guide explains service behavior and documents this repository's exact
> implementation. A lesson proves only its stated path. Region, feature,
> pricing, quota, and permission availability remain subscription-specific.

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

Search is a retrieval system, not a document field-extraction service. Content
Understanding (CU) is an extraction system, not a corpus search engine. A
production system can use both: CU preserves difficult document structure,
then an embedding-capable ingestion path indexes that representation.

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

The indexer drives the pipeline. A skillset runs during indexing, never when a
user searches. A query searches already stored fields and vectors. The
vectorizer configured on the index turns query text into a vector at query
time; it does not create document vectors for a direct upload.

### Document-to-answer boundary

```text
Untrusted source document
  → extract/chunk/index with source and access metadata
  → retrieve only chunks caller can access
  → pass compact evidence to model
  → render answer with source citation
  → retain request, result IDs, source version, and policy decision for audit
```

Grounding improves answer quality; it does not replace authorization,
provenance, evaluation, prompt-injection defenses, or application-level
citations.

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

`DefaultAzureCredential` supplies the user token after `az login` on a
workstation. In Azure, use a workload or managed identity. Successful token
acquisition does not prove that identity has the required service data-plane
role.

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

The checked-in `.env.example` and `_shared.config.settings()` currently
default `CU_API_VERSION` to `2025-11-15-preview`. Local CU reference material
documents standard GA as `2025-11-01`; use the API version supported by the
target resource and analyzer. L13 requires the separate
`2025-05-01-preview` API for Pro mode. Restore the standard value after L13.

### Resources, RBAC, network, and storage

Create a nonproduction Azure AI Search service that supports vector workloads
and, for L03, semantic ranking in its region. Create a Blob account/container,
then upload PDFs from:

```text
_shared/sample_data/northwind_docs/
_shared/sample_data/northwind_policies/
_shared/sample_data/invoices/northwind_sample_invoice.pdf
_shared/sample_data/invoices/northwind_scanned_support_notice.pdf
```

Enable the **system-assigned managed identity** on the Search service. Grant
that identity:

| Principal | Scope | Minimum role for this lab | Why |
|---|---|---|---|
| Search service identity | Storage account or target container | **Storage Blob Data Reader** | Blob indexer reads source files. |
| Search service identity | Azure OpenAI resource that hosts embeddings | **Cognitive Services OpenAI User** | Embedding skill during indexing and vectorizer at query time. |
| Lab user/workload | Search service | Search index management and query data roles appropriate to its tasks | Creates schema/data-source/skillset/indexer and queries index. |
| Lab user/workload | Foundry project/resource | **Foundry User** or equivalent project access | Creates L07 agent and calls project Responses API. |
| CU caller | CU resource | **Cognitive Services Content Understanding Contributor** for L12/L13 creation; **Reader** can analyze existing analyzers | Calls CU data plane. |

You need **Owner**, **User Access Administrator**, or an equivalent role to
create role assignments. Search resource configuration and Search index data
operations are separate permissions. Grant least privilege and scope roles to
the narrowest resource/container practical.

The Blob data source contains a managed-identity resource-ID connection string:

```text
ResourceId=/subscriptions/<subscription>/resourceGroups/<resource-group>/providers/Microsoft.Storage/storageAccounts/<storage-account>/;
```

It intentionally contains no storage key. Do not replace it with a secret
connection string or add a secret to source control. For a network-protected
same-region storage account, configure the documented trusted-service or
resource-instance path; a public URL alone does not grant the indexer access.
Use shared private links/private endpoints where policy requires private Search
to Azure OpenAI connectivity.

CU's `analyze` call operates on a service-reachable HTTPS URL. For private
Blob input, issue a short-lived, read-only SAS URL containing only the required
object. Do not put a broad account SAS in a shell history, committed `.env`, a
model prompt, or a citation. A `file://` path is local to the caller and does
not work for CU.

### Costs and side effects

| Action | Persistent change or billable behavior |
|---|---|
| L00 | Creates or replaces Search index definition. |
| L05 | Creates or replaces Search skillset. |
| L04 `--run` | Creates/replaces data source and indexer, then starts ingestion. |
| L03 | Semantic requests can bill and require feature availability. |
| Indexer | Blob reads and embedding calls consume Search, Storage, and Azure OpenAI capacity. |
| L07 | Creates an agent version. |
| L09–L15 | CU analysis processes supplied content; L12/L13 create or replace analyzers; L15 also makes a model call. |

Use short sample files, bounded `top` values, and a disposable lab
environment. Delete lab resources and revoke SAS tokens when finished.

## Exact Search build and run order

The four JSON assets are one contract. Do not provision only part of it:

1. Upload source files to `${STORAGE_CONTAINER}`.
1. Enable the Search identity and assign Blob/OpenAI roles.
1. Create the index before its skillset or indexer:

   ```bash
   uv run python 05-information-extraction/00_search_index_setup.py
   ```

1. Create the skillset:

   ```bash
   uv run python 05-information-extraction/05_search_skillset.py
   ```

1. Create data source and indexer, then begin indexing:

   ```bash
   uv run python 05-information-extraction/04_search_indexer_setup.py --run
   ```

1. Wait for a **successful** indexer run in Azure portal or inspect
   `get_indexer_status()` through `indexer_client()`. Do not treat "run
   started" as indexed content.
1. Run L01–L03, then create L07 agent and run L08.

The scripts use Search REST API version `2025-09-01` for definitions because
the JSON assets use REST camel-case properties. They do not deserialize those
assets into Python SDK snake-case constructors.

### Schema contract

| Asset | Current contract |
|---|---|
| `index.json` | Chunk index `${SEARCH_INDEX_VECTOR}`. `id` is keyword key; `parent_id` is filterable parent key; `chunk`, `title`, and `source_url` are retrievable; `text_vector` is nonretrievable/stored false, 3072 dimensions. |
| `data_source.json` | `northwind-blob-datasource`, `azureblob`, managed-identity `ResourceId` connection, configured container. |
| `skillset.json` | Character-based SplitSkill: 2,000 characters, 500 overlap; Azure OpenAI embedding for each `/document/pages/*`; projects chunks, vector, filename, and Blob path. |
| `indexer.json` | Connects data source, target index, and skillset; extracts content and metadata with default parsing. |

`text-embedding-3-large` has a 3072-dimension default used by this index. If
you select a model or configured embedding dimension that differs, update the
vector field and embedding skill together. The query vectorizer and indexing
embedding skill must use compatible model, deployment, dimensions, and
distance assumptions.

Index projection creates one child Search document per page chunk. It repeats
`title` and `source_url`, maps `parent_id` automatically, and uses
`skipIndexingParentDocuments` so null-chunk parent records do not pollute
retrieval. Do not add a manual mapping for `parent_id`; that breaks projection
change tracking. If you add ACL metadata, project it to **every child chunk**.

## Search retrieval and ranking

| Mode | Lesson | What happens | Limitation |
|---|---:|---|---|
| Keyword | L01 | BM25 ranks `search_text`. | Misses paraphrases. |
| Vector | L02 | `VectorizableTextQuery` makes Search call its configured vectorizer, then nearest-neighbor search runs over `text_vector`. | Misses exact rare terms and requires vectorizer/model alignment. |
| Hybrid | L03/L08 | BM25 and vector candidates combine by RRF. | Candidate quality still depends on chunking and source content. |
| Semantic | L03 | Semantic ranker reranks an initial BM25/RRF result set based on configured `title` and `chunk`. | Does not retrieve new corpus matches; only top candidates progress. |

`k_nearest_neighbors` controls vector candidates, while `top` controls how
many results the application receives. L03's semantic output has
`@search.reranker_score`; keyword/vector output has `@search.score`. A
reranker score is not comparable to a BM25/vector score, and score thresholds
need evaluation data rather than guessed constants.

Semantic ranker uses text in its semantic configuration. This index's
`default` configuration prioritizes `title` and `chunk`. It can provide
captions and answers when requested, but semantic answers/captions are
extractive Search output, not generated answers.

## Evidence, citation, ACL, and provenance

L08 retrieves `chunk`, `title`, `parent_id`, and `source_url`, then includes
them in its prompt. This is application-owned provenance. The agent is told to
cite source URLs, but L08 does not validate that each answer claim maps to a
source or render structured citation annotations.

Production retrieval must enforce access **before** prompt construction.
This lab index has no ACL field and L08 sends no filter, so it is unsuitable
for mixed-permission content. Choose a supported native ACL ingestion path, or
store a nonretrievable, filterable `Collection(Edm.String)` of caller/group
identifiers on each chunk and apply an OData security filter such as
`group_ids/any(g:search.in(g, '<caller-group-ids>'))`. Derive identities from
trusted authentication context, not model or client text.

At ingestion, retain immutable source identifier/version, Blob path or
business source URI, content hash, indexer/skillset version, chunk ID,
parent ID, ACL version, and ingestion timestamp. At answer time, record user
or tenant, normalized query, effective authorization filter, index version,
retrieved chunk IDs/source URLs, ranking configuration, model/agent version,
and citation rendering. Redact or access-control logs containing sensitive
prompts or document text. Reindex when source permissions change.

## Manual RAG versus managed Search tools

L07 and L08 implement **manual RAG**, not a managed Azure AI Search agent
tool:

```text
L08 application → hybrid Search query → prompt contains source blocks
                → Foundry prompt agent → answer text
```

The application chooses query parameters, applies filters, limits chunks, and
must enforce ACLs, cite sources, handle no-result cases, and evaluate quality.
Use this pattern when those controls are product requirements.

A managed Foundry Azure AI Search tool is different:

```text
Agent → configured Azure AI Search tool/project connection → Search index
      → tool result and URL citation annotations → agent response
```

It requires a Foundry project connection, supported Search index fields
(retrievable content and source URL), tool configuration, and project
managed-identity roles including **Search Index Data Contributor** and
**Search Service Contributor** for the documented keyless setup. It is not
imported, configured, or exercised by any Domain 5 script. Do not claim that
L07's agent autonomously searches the index.

Azure AI Search agentic retrieval/knowledge bases are another, separate
managed preview path: Search can plan subqueries, execute them, semantically
rerank results, return source references/activity, and supply grounding data
to an agent. This repository does not create a knowledge source, knowledge
base, MCP connection, or agentic-retrieval call.

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

It does not deploy an Azure Function, add a `WebApiSkill` to
`skillset.json`, authenticate an endpoint, or project its results. To make it
an ingestion feature, host an HTTPS endpoint, configure its skill inputs,
outputs, batch size, timeout, and output mapping, and secure it with the
Search managed identity plus `authResourceId`/Entra validation. Size and
throttle for indexer parallelism; return per-record errors instead of failing
unrelated records. Never use a function key or static bearer token in source.

## Content Understanding: API, inputs, and modes

`_shared.cu_client.analyze()` posts:

```json
{"inputs": [{"url": "https://<reachable-file>"}]}
```

It receives `202 Accepted`, reads `Operation-Location`, and polls every two
seconds until `succeeded`, `failed`, or `canceled`. The helper accepts either
one URL or a list. This is important: standard GA `2025-11-01` accepts one
input item, while L13 changes the configured API version to Pro preview, where
the helper's URL list represents multi-document input.

CU uses `DefaultAzureCredential` for
`https://cognitiveservices.azure.com/.default`. It does not use a Foundry
project endpoint or an Azure OpenAI endpoint as a substitute for `CU_ENDPOINT`.
For production, add bounded polling timeout/backoff, cancellation, failure
diagnostics, and a queue/job store rather than holding a web request open.

| Capability | Standard | Pro preview |
|---|---|---|
| API | GA `2025-11-01` | `2025-05-01-preview` |
| Inputs | One URL per analysis request | Multiple related document URLs. |
| Modalities | Documents, images, audio, video, and text subject to analyzer/limits. | Documents only; current limits restrict input to PDF, TIFF, and images, 100 MB/150 pages total. |
| Field methods | Extract, classify, generate. | Classify and generate; `extract` is unsupported. |
| Confidence/source grounding | Available when explicitly enabled for document fields. | Unavailable. |
| Reasoning/reference data | Per-input extraction. | Multi-step cross-document reasoning and reference data. |

Use standard for high-volume extraction and Pro only when a cross-document
decision actually needs it. Pro is preview, has higher latency/cost, and is
not a "better one-document OCR" switch.

## Markdown RAG and reasoning boundary

L14 calls `prebuilt-layout`, header-splits returned Markdown, then applies an
800-character recursive splitter with 100-character overlap. It prints chunk
count and first chunk. It **does not upload, embed, or index** those chunks.

That boundary is intentional. This index requires `text_vector`; a direct
Search upload of only `chunk` cannot participate in vector retrieval. To use
the repository's integrated pipeline, upload the original source document to
Blob and rerun L05/L04 so Search creates vectors. For a direct Markdown
ingestion design, create client-side embeddings and upload a valid complete
document shape, including source/provenance and ACL fields.

CU Markdown retains headings, tables (including HTML for merged cells),
figures, formulas, selection marks, links, and page metadata. It is better
evidence than flattened text, but still inspect chunk boundaries, table splits,
figure references, prompt injection in source text, and retrieval quality.

L15 is a different pattern: CU extracts invoice fields, then an ephemeral
Responses call produces a review. CU performs extraction; the language model
performs bounded business reasoning. Treat model approval status as a proposed
decision unless deterministic controls or human review validate it.

## Lesson map and run order

| # | Question | Run | Expected output | Limitation |
|---:|---|---|---|---|
| 00 | What schema accepts this pipeline? | `uv run python 05-information-extraction/00_search_index_setup.py` | `index '<name>' saved.` | Replaces persistent index definition; does not ingest. |
| 01 | How does exact-term retrieval rank? | `uv run python 05-information-extraction/01_search_basic_query.py` | Scores, titles, chunk previews. | Queries vector index despite old descriptions of a text-only index. |
| 02 | Can paraphrase retrieve relevant chunks? | `uv run python 05-information-extraction/02_search_vector.py` | Up to five semantic matches. | Requires populated vectors and configured vectorizer. |
| 03 | How do ranking modes differ? | `uv run python 05-information-extraction/03_search_hybrid_semantic.py` | Keyword, vector, hybrid+semantic top-three lists. | Semantic ranker availability/billing required. |
| 04 | How is Blob ingestion defined and started? | `uv run python 05-information-extraction/04_search_indexer_setup.py --run` | Data source/indexer saved; run started. | It does not wait for completion. |
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

Run L00, L05, L04 `--run`, wait, then L01–L03. Run L07 before L08. CU
lessons are independent after endpoint/authentication setup; run L13 with its
preview version and return `.env` to a standard API version afterward.

## Security and ingestion hygiene

- Treat Blob documents, OCR text, Markdown, custom-skill payloads, and Search
  chunks as untrusted input. A document can contain indirect prompt injection.
- Validate MIME type, size, page/count limits, malware-scanning policy, and
  tenant/source ownership before indexing. Reject password-protected or
  malformed content according to policy.
- Use managed identities and short-lived SAS URLs. Scope SAS to one object,
  read only, short expiry, HTTPS, and no account-wide permission.
- Separate customer/tenant indexes or apply enforced filters. Never rely on an
  instruction such as "only answer authorized content."
- Project ACL/provenance fields to every chunk. Reindex/revoke when source
  access changes. Do not expose nonretrievable ACLs in answer payloads.
- Keep source URL citations meaningful but avoid leaking signed URLs. Render a
  stable business/source link or opaque source identifier when necessary.
- Redact/minimize logs; prompts and retrieved chunks can contain confidential
  data. Apply retention, deletion, and data-residency requirements.
- Evaluate retrieval recall, citation correctness, answer groundedness, ACL
  enforcement, extraction accuracy, latency, cost, and failure behavior with
  representative documents before production.

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
