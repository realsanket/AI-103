# 09 — Current Azure AI Document Intelligence

These six supplemental lessons use Azure Document Intelligence v4.0 REST API `2024-11-30` (GA) and Python package `azure-ai-documentintelligence` 1.0.2 or later. They use `DocumentIntelligenceClient` and `DocumentIntelligenceAdministrationClient` with Microsoft Entra authentication. They do not use earlier APIs or SDKs.

Each default command is a local preflight and makes no cloud call. `--apply` submits exactly one remote analysis or one custom-model build. A successful local preflight does not establish authentication, RBAC, network reachability, model availability, or successful Azure execution.

## Lessons

| Lesson | Model or decision | Default command | `--apply` effect |
|---|---|---|---|
| `01_read_ocr.py` | `prebuilt-read` OCR | Validates endpoint and source presence. | Analyzes one HTTPS document. |
| `02_layout_markdown_tables.py` | `prebuilt-layout` | Validates endpoint and source presence. | Returns Layout output requested as Markdown and reports tables, figures, and sections. |
| `03_invoice.py` | `prebuilt-invoice` | Validates endpoint and source presence. | Extracts invoice fields from one HTTPS document. |
| `04_id_document.py` | `prebuilt-idDocument` | Validates endpoint and source presence. | Extracts ID document fields from one HTTPS document. |
| `05_custom_neural_preflight.py` | Custom neural | Validates local build inputs. | Starts and waits for one neural model build. |
| `06_di_vs_cu_decision.py` | DI versus CU | Chooses locally. | Not applicable; this lesson never calls Azure. |

`prebuilt-read` extracts OCR text, words, lines, paragraphs, language, and locations. Use it for document OCR. `prebuilt-layout` adds document structure, including tables, selection marks, paragraph roles, figures, and sections. Requesting Markdown preserves document structure; complex tables are HTML inside the Markdown so merged cells and captions remain represented.

`prebuilt-invoice` is for invoices, utility bills, sales orders, and purchase orders. `prebuilt-idDocument` supports worldwide passports and documented ID coverage. Both return typed fields in `documents[].fields`; validate confidence and business rules before automated payment, access, or identity decisions.

## Setup

Run from repository root:

```bash
uv sync
cp .env.example .env
az login
```

For Microsoft Entra authentication, create a single-service Document Intelligence resource and set its non-secret custom subdomain endpoint in `.env`:

```bash
DOCUMENT_INTELLIGENCE_ENDPOINT=https://<resource>.cognitiveservices.azure.com
```

This must be a custom subdomain endpoint. Regional endpoints don't support Microsoft Entra authentication. The sample uses `DefaultAzureCredential`, so it has no API-key environment variable.

Document URLs and the custom-model training container URL can contain a SAS token. Treat them as secrets. Supply them only through your shell, Key Vault, or CI secret store, never `.env.example`, source, output, or logs.

```bash
export DI_READ_SOURCE_URL="https://<storage>.blob.core.windows.net/<container>/<document>?<sas>"
export DI_LAYOUT_SOURCE_URL="https://<storage>.blob.core.windows.net/<container>/<document>?<sas>"
export DI_INVOICE_SOURCE_URL="https://<storage>.blob.core.windows.net/<container>/<invoice>?<sas>"
export DI_ID_SOURCE_URL="https://<storage>.blob.core.windows.net/<container>/<id>?<sas>"
```

Use service-reachable HTTPS inputs. Do not use `file://` URLs. The lessons avoid printing source URLs. Analysis text and field values are also suppressed unless you explicitly request them with `--show-text`, `--show-markdown`, or `--show-values`.

## Run safely

Preflight first:

```bash
uv run python 09-current-ai-services-other/01_read_ocr.py
uv run python 09-current-ai-services-other/02_layout_markdown_tables.py
uv run python 09-current-ai-services-other/03_invoice.py
uv run python 09-current-ai-services-other/04_id_document.py
uv run python 09-current-ai-services-other/05_custom_neural_preflight.py
uv run python 09-current-ai-services-other/06_di_vs_cu_decision.py --scenario standard-form
```

After data, role, network, region, and cost review, submit one bounded request:

```bash
uv run python 09-current-ai-services-other/01_read_ocr.py --apply --show-text
uv run python 09-current-ai-services-other/02_layout_markdown_tables.py --apply --show-markdown
uv run python 09-current-ai-services-other/03_invoice.py --apply --show-values
uv run python 09-current-ai-services-other/04_id_document.py --apply --show-values
```

Use `--source-url` to override the corresponding environment value for one command. Start with a disposable, minimal document. Review confidence, type, and extracted content before persisting output or triggering downstream action.

## Custom neural model

Custom neural targets structured and semi-structured documents with labeled examples. It requires at least five labeled samples, and training data must represent real template, language, value, and table variation. Version v4.0 supports signature detection, table cell confidence, and overlapping fields.

Provide a Blob *container* URL containing labels and training documents. Keep the SAS-bearing URL out of repository files. Set an optional prefix when labels live below a Blob folder.

```bash
export DI_CUSTOM_NEURAL_MODEL_ID="northwind-invoice-v1"
export DI_TRAINING_CONTAINER_URL="https://<storage>.blob.core.windows.net/<container>?<sas>"
export DI_CUSTOM_NEURAL_PREFIX="labeled"
export DI_CUSTOM_NEURAL_MAX_TRAINING_HOURS="0.5"

uv run python 09-current-ai-services-other/05_custom_neural_preflight.py
uv run python 09-current-ai-services-other/05_custom_neural_preflight.py --apply
```

`--apply` starts a persistent model build and waits for its result. It does not delete or deploy the model. Use an unused model ID for initial experiments. The lesson accepts `0.5` through `10` training hours. v4.0 includes 10 free training hours; training beyond the included allowance can bill, and each job has a 30-minute minimum. Check current pricing and processed-page metrics before training.

Custom neural training has limited region availability. Confirm current training-region support before creating the resource; you can copy a trained model to another region for analysis where supported.

## DI versus CU local decision

Use the local chooser as a current default, then validate it with representative documents and production requirements:

```bash
uv run python 09-current-ai-services-other/06_di_vs_cu_decision.py --scenario ocr-layout
uv run python 09-current-ai-services-other/06_di_vs_cu_decision.py --scenario standard-form
uv run python 09-current-ai-services-other/06_di_vs_cu_decision.py --scenario custom-labeled
uv run python 09-current-ai-services-other/06_di_vs_cu_decision.py \
  --scenario unstructured --needs-reasoning --multiple-files
uv run python 09-current-ai-services-other/06_di_vs_cu_decision.py \
  --scenario custom-labeled --air-gapped
```

| Need | Current default |
|---|---|
| OCR or layout extraction only | Content Understanding `prebuilt-read` or `prebuilt-layout`. |
| Standard structured invoice or ID | Document Intelligence prebuilt model. |
| Labeled, structured custom extraction | Document Intelligence custom neural model. |
| Unstructured, inferred, multimodal, or multi-file extraction | Content Understanding analyzer. |
| On-premises or air-gapped processing | Document Intelligence containers. |

The DI Read and Layout lessons remain useful for learning v4.0 response contracts and for workloads that need their documented behavior. The chooser reflects current guidance, not a performance or cost guarantee.

## Security, RBAC, network, cost, and region checks

- Use Microsoft Entra ID with `DefaultAzureCredential`; do not place keys in
source or local templates. Grant the calling user or workload identity `Cognitive Services User` at the Document Intelligence resource scope.
- For private training storage, enable the Document Intelligence resource's
system-assigned managed identity and grant it `Storage Blob Data Reader`. Custom-project and secure-network flows that write or require access to training data need `Storage Blob Data Contributor`.
- If storage uses selected networks or a firewall, configure its trusted
service exception and validate the Document Intelligence-to-Storage path. For private deployment, place client and resource access behind approved virtual networks and private endpoints, then test DNS and authorization.
- Keep identity documents, invoice data, OCR, Markdown, custom labels, and
model output in approved data boundaries. Don't log raw content. Apply retention, deletion, human-review, and audit controls before production.
- Monitor **Processed Pages**, split by **FeatureName**, in Azure Monitor.
Estimate current prices with the Azure pricing calculator. Page volume, optional features, custom-model training, and regional price affect cost.
- Verify model, custom-training, quota, and private-network availability in
your target region immediately before applying. These lessons don't query availability.

## Local references

- [What's new](../.context/azure-ai-docs/articles/ai-services/document-intelligence/whats-new.md)
- [Model selection](../.context/azure-ai-docs/articles/ai-services/document-intelligence/concept/choose-model-feature.md)
- [Read model](../.context/azure-ai-docs/articles/ai-services/document-intelligence/prebuilt/read.md)
- [Layout model](../.context/azure-ai-docs/articles/ai-services/document-intelligence/prebuilt/layout.md)
- [Layout Markdown](../.context/azure-ai-docs/articles/ai-services/document-intelligence/concept/markdown-elements.md)
- [Custom neural](../.context/azure-ai-docs/articles/ai-services/document-intelligence/train/custom-neural.md)
- [Managed identity and network access](../.context/azure-ai-docs/articles/ai-services/document-intelligence/authentication/managed-identities-secured-access.md)
- [Cost estimate](../.context/azure-ai-docs/articles/ai-services/document-intelligence/how-to-guides/estimate-cost.md)
