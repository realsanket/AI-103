# Domain 5: Information extraction

This domain covers two distinct services:

- **Azure AI Search** retrieves grounded chunks from a corpus.
- **Azure Content Understanding (CU)** extracts markdown and fields from an individual document.

Run lessons from repository root:

```bash
uv run python 05-information-extraction/<lesson>.py
```

## Search pipeline

This directory contains one coherent, on-demand Blob pipeline:

```text
Blob container
  -> northwind-blob-datasource
  -> ${SEARCH_INDEXER}
  -> ${SEARCH_SKILLSET}: SplitSkill -> AzureOpenAIEmbeddingSkill
  -> ${SEARCH_INDEX_VECTOR}
  -> keyword, vector, or hybrid + semantic queries
```

`skillset_configs/` contains REST JSON, not Python SDK constructor arguments. `04_search_indexer_setup.py` and `05_search_skillset.py` deploy it through Azure AI Search REST so camel-case REST fields remain intact. This avoids passing `dataSourceName`, `targetIndexName`, and `skillsetName` to snake-case SDK constructors.

The pipeline uses the Search service's system-assigned managed identity. It does not store a storage connection string or Azure OpenAI key.

### Setup order

1. Create an Azure AI Search service with vector search and semantic ranker availability in its region.
1. Enable the system-assigned managed identity on that Search service.
1. Create Blob Storage and upload documents to the configured container. Start with PDFs in `_shared/sample_data/northwind_docs/` or `_shared/sample_data/northwind_policies/`.
1. Grant the Search service identity **Storage Blob Data Reader** on the storage account or container.
1. Deploy an Azure OpenAI embedding model. Grant the Search service identity **Cognitive Services OpenAI User** on that Azure OpenAI or Foundry resource.
1. Set environment values. `EMBEDDING_MODEL` is both the Azure OpenAI deployment ID and model name in these JSON assets; use a deployment named after its model, such as `text-embedding-3-large`.
1. Run provisioning in this order:

   ```bash
   uv run python 05-information-extraction/00_search_index_setup.py
   uv run python 05-information-extraction/05_search_skillset.py
   uv run python 05-information-extraction/04_search_indexer_setup.py --run
   ```

1. Wait for the indexer to finish successfully in Azure portal, then run L01–L03.

Required values already read by `_shared.config.settings()`:

```text
SEARCH_ENDPOINT
SEARCH_INDEX_VECTOR                 # default: northwind-docs-vector
SEARCH_INDEXER                      # default: northwind-indexer
SEARCH_SKILLSET                     # default: northwind-skillset
AZURE_OPENAI_ENDPOINT
EMBEDDING_MODEL                     # default: text-embedding-3-large
AZURE_SUBSCRIPTION_ID
AZURE_RESOURCE_GROUP
STORAGE_ACCOUNT
STORAGE_CONTAINER                   # default: northwind-docs
```

`DefaultAzureCredential` also requires a usable developer login, such as `az login`, or a managed identity when deployed.

### Storage and Search permissions

The data source uses a managed-identity storage resource-ID connection string:

```text
ResourceId=/subscriptions/<subscription>/resourceGroups/<resource-group>/providers/Microsoft.Storage/storageAccounts/<storage-account>/;
```

Do not replace it with a connection string in source control. The Search service identity needs Storage Blob Data Reader. Your identity needs permission to create Search indexes, data sources, skillsets, and indexers, and to query the index. The Search service identity needs Cognitive Services OpenAI User to invoke the embedding skill and query vectorizer. Restrict index-definition write access: a vectorizer sends its managed-identity token to its configured `resourceUri`.

### Index contract

`skillset_configs/index.json` defines one chunk-per-document index:

| Field | Role |
|---|---|
| `id` | Search-generated child document key. |
| `parent_id` | Filterable projected parent key. Do not map it manually in the skillset. |
| `chunk` | Searchable, retrievable chunk text. |
| `title` | Searchable Blob filename. Semantic title field. |
| `source_url` | Retrievable Blob storage path for citations. |
| `text_vector` | Nonretrievable 3072-dimension vector, profile `text-vector-profile`. |

The semantic configuration is named `default`, with `title` and `chunk`. `text_vector` uses `hnsw-cosine`, profile `text-vector-profile`, and vectorizer `azure-openai-vectorizer`. The supplied definition targets the default 3072 dimensions of `text-embedding-3-large`. Change the vector field dimension when you change models.

Index projections create one Search document per page chunk and repeat `title` and `source_url`. `skipIndexingParentDocuments` keeps nonchunk parent documents out of query results.

### Search lessons

| Lesson | Purpose |
|---|---|
| `00_search_index_setup.py` | Creates or updates index schema. |
| `01_search_basic_query.py` | BM25 query against same vector index. |
| `02_search_vector.py` | Server-side query embedding with `VectorizableTextQuery`. |
| `03_search_hybrid_semantic.py` | Compares keyword, vector, and hybrid + semantic. |
| `04_search_indexer_setup.py` | Creates Blob data source and indexer; `--run` starts work. |
| `05_search_skillset.py` | Creates split-and-embed skillset. |
| `06_search_custom_skill.py` | Shows Azure AI Search Web API custom-skill batch contract only. |
| `07_rag_prompt_agent.py` | Creates agent used by manual RAG. No Search tool attached. |
| `08_rag_client_run.py` | App-owned hybrid retrieval, prompt construction, agent invocation. |

L02, L03, and L08 require both `text_vector` and its configured vectorizer. L03 also requires semantic ranking to be available on the service. Semantic query results include `@search.reranker_score`; other queries use `@search.score`.

`07_rag_prompt_agent.py` and `08_rag_client_run.py` are **manual RAG**, not a managed AI Search agent. L08 owns retrieval, gives chunks and `source_url` to the model, and asks it to answer from those sources. This directory does not import or configure a documented managed Search tool, so it makes no claim that an agent autonomously searches the index.

## Content Understanding lessons

CU is an asynchronous REST service. A document must be accessible to the service, so use a public URL or a Blob SAS URL. `file://` paths and local PDFs do not work.

| Lesson | Purpose | Input |
|---|---|---|
| `09_cu_prebuilt_read.py` | OCR-oriented text extraction. | Optional `CU_READ_SOURCE_URL`. |
| `10_cu_prebuilt_layout.py` | Markdown, tables, figures, and reading order. | `CU_LAYOUT_SOURCE_URL`. |
| `11_cu_invoice.py` | Prebuilt invoice fields. | `SAMPLE_INVOICE_URL`. |
| `12_cu_custom_analyzer.py` | Custom schema based on `prebuilt-document`. | Optional `CU_SUPPORT_NOTICE_URL`. |
| `13_cu_pro_mode.py` | Creates a pro-mode review analyzer. | Optional comma-separated `CU_PRO_SOURCE_URLS`. |
| `14_cu_markdown_for_rag.py` | Inspects header and text chunks from CU markdown. | `CU_MARKDOWN_SOURCE_URL`. |
| `15_cu_content_agent.py` | Sends extracted invoice fields to an ephemeral model call. | `SAMPLE_INVOICE_URL`. |

Useful local files to upload:

```text
_shared/sample_data/invoices/northwind_sample_invoice.pdf
_shared/sample_data/invoices/northwind_scanned_support_notice.pdf
_shared/sample_data/northwind_docs/*.pdf
_shared/sample_data/northwind_policies/*.pdf
```

Set `CU_ENDPOINT` and `CU_API_VERSION=2025-11-01` for standard prebuilt/custom lessons. Switch to `CU_API_VERSION=2025-05-01-preview` only for L13 pro mode. Prebuilt and custom analyzer examples use the shared `analyze()` and `create_analyzer()` helper; no lesson reimplements its REST polling loop.

Pro mode is preview and supports multi-document reasoning, but it does not support `extract` fields or grounding/confidence scores. The current shared `analyze()` helper accepts one source URL, so L13 exercises analyzer creation and a one-document invocation only. Extending that helper to submit the REST API's `inputs` array is required before using multiple input documents.

L14 intentionally does **not** upload chunks to the vector index. A direct Search upload needs client-generated vectors; uploading only `chunk` creates documents excluded by vector retrieval. Put original files in Blob and use the Search indexer when you want this repository's integrated embedding pipeline.

## Objective coverage

- Build retrieval pipelines: Blob data source, indexer, skillset, text splitting, embeddings, index projections, vectorizer, vector, hybrid, and semantic queries.
- Ground responses: retrieve chunk citations and pass them to a constrained prompt.
- Extend enrichment: understand Web API custom-skill request and response shape.
- Extract document content: CU prebuilt read, layout, and invoice analyzers.
- Build CU analyzers: custom fields, `extract`, `classify`, and `generate` in standard mode; pro-mode limitations.
- Prepare complex documents for retrieval: CU layout markdown and visible chunk boundaries.

## Costs, side effects, and limits

- `00`, `04`, and `05` update persistent Search resources. `04 --run` starts an indexer run and can reprocess changed Blob files.
- Indexing invokes Azure OpenAI embeddings. Semantic ranking, Search capacity, Blob storage, CU analysis, and model calls can bill independently.
- `12`, `13`, and `07` create or version remote analyzers or agents. Re-running can create versions or overwrite definitions according to service behavior.
- `15` sends extracted invoice fields to a model. Do not use production confidential content without appropriate data handling, access controls, retention review, and approval.
- The sample index uses character-based chunks (2,000 characters with 500 overlap). Tune chunking, embedding dimensions, `k_nearest_neighbors`, and `top` against evaluated data rather than assuming these values fit production.
- Indexer enrichment is not a CU replacement. Use CU layout markdown when document structure matters; route resulting content through an embedding-capable ingestion path.

## Validation and troubleshooting

Run static checks after edits:

```bash
python -m json.tool 05-information-extraction/skillset_configs/index.json >/dev/null
python -m json.tool 05-information-extraction/skillset_configs/data_source.json >/dev/null
python -m json.tool 05-information-extraction/skillset_configs/skillset.json >/dev/null
python -m json.tool 05-information-extraction/skillset_configs/indexer.json >/dev/null
python -m compileall -q 05-information-extraction
```

Common failures:

| Symptom | Fix |
|---|---|
| Indexer cannot read Blob | Enable Search managed identity and grant Storage Blob Data Reader. Confirm resource ID, container name, and network access. |
| Embedding skill or vectorizer returns 401/403 | Grant Search identity Cognitive Services OpenAI User; confirm Azure OpenAI endpoint, deployment ID, and model name. |
| Vector dimensions mismatch | This definition uses the default 3072 dimensions for `text-embedding-3-large`; if you configure a nondefault embedding-skill dimension, set the index field to the same value. |
| Semantic configuration missing | Provision this `index.json`; query `default` only after it exists and semantic ranking is available. |
| No vector results | Wait for successful indexer completion and verify chunks contain `text_vector`. |
| CU cannot fetch document | Use reachable HTTPS Blob SAS URL, not a local path. |
