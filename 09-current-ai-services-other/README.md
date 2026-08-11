# Domain 9: Current Azure AI Document Intelligence

> Preflight-first labs for Azure Document Intelligence v4.0 (REST API `2024-11-30 GA`) using `azure-ai-documentintelligence` ≥ 1.0.2 with `DocumentIntelligenceClient` + `DocumentIntelligenceAdministrationClient` + Entra auth. Run commands from repository root: `uv run python 09-current-ai-services-other/<lesson>.py`.
>
> Every default command is a local preflight. `--apply` submits exactly ONE remote analysis or custom-model build. A successful preflight does not establish authentication, RBAC, network reachability, model availability, or successful Azure execution.

## What this domain teaches

Document Intelligence (DI) sits alongside Content Understanding (CU) as the current Foundry document toolkit:

```text
Choose tool: DI vs CU (lesson 06 chooser)
        ↓
DI: deterministic extraction on structured/semi-structured forms
   ├── prebuilt-read      → OCR text (lesson 01)
   ├── prebuilt-layout    → tables + structure as Markdown (lesson 02)
   ├── prebuilt-invoice   → typed invoice fields (lesson 03)
   ├── prebuilt-idDocument → passport + ID fields (lesson 04)
   └── custom neural       → labeled custom extraction (lesson 05)

CU: LLM-powered analyzers for unstructured/inferred/multi-file work
   └── domain 05 lessons 09-16 cover CU
```

DI v4.0 is the current GA API. It replaces v3.x/v2.x SDK patterns. All lessons here use Entra auth via `DefaultAzureCredential` — API keys are NOT used.

## DI mental model

### Prebuilt vs custom

| Model | Best for | Output shape | Confidence source |
|---|---|---|---|
| `prebuilt-read` | Pure OCR text | `content` + `pages[]` + `paragraphs[]` + `languages[]` | Per word/line |
| `prebuilt-layout` | Structure (tables, sections, figures) as Markdown | Same as read + `tables[]` + `figures[]` + `sections[]` + selection marks | Per cell + per element |
| `prebuilt-invoice` | Invoices, utility bills, sales orders, purchase orders | `documents[0].fields` (typed) | Per field |
| `prebuilt-idDocument` | Passports + documented ID types | `documents[0].fields` (typed) | Per field |
| Custom neural | Labeled structured/semi-structured forms | `documents[0].fields` (labels you defined) | Per field + per cell (v4.0) |

### v4.0 GA improvements over v3.x

| Capability | v4.0 GA |
|---|---|
| Layout Markdown output | `output_content_format="markdown"` param |
| Complex tables in Markdown | HTML fallback for merged cells + captions |
| Custom neural signature detection | Yes |
| Table cell confidence | Yes |
| Overlapping fields | Yes |
| Free training hours | 10/month (Standard tier) |
| API version | `2024-11-30 GA` |

### Auth model

```text
DefaultAzureCredential
        ↓
Entra token for https://cognitiveservices.azure.com/.default
        ↓
Custom-subdomain endpoint: https://<resource>.cognitiveservices.azure.com
        ↓
RBAC: Cognitive Services User on Document Intelligence resource
```

Regional endpoints (like `https://<region>.api.cognitive.microsoft.com`) do NOT support Entra auth. Custom subdomain is required.

## Glossary

| Term | Definition |
|---|---|
| **DI v4.0** | Document Intelligence REST API `2024-11-30 GA`, SDK `azure-ai-documentintelligence` ≥ 1.0.2 |
| **prebuilt model** | Microsoft-trained model shipped with the service (read, layout, invoice, idDocument, etc.) |
| **custom neural** | Customer-trained model on labeled Blob data; requires ≥5 samples; supports v4.0 features |
| **build_mode: neural** | Custom-model training mode using deep learning (vs template mode); pattern in this domain |
| **max_training_hours** | Budget cap for custom neural build (0.5-10); overage rejected |
| **AzureBlobContentSource** | v4.0 request shape pointing to a training Blob container URL (SAS-bearing) |
| **Custom subdomain** | Resource endpoint like `https://<resource>.cognitiveservices.azure.com` (Entra-capable) |
| **documents[].fields** | Prebuilt/custom extraction output: typed field values with confidence |
| **content** | OCR text output (Read) or Markdown output (Layout with markdown=True) |
| **Content Understanding (CU)** | Foundry-integrated LLM-powered document analyzer (covered in domain 05); use for unstructured/inferred/multi-file |
| **DI containers** | On-premises deployment option for DI models (only air-gapped path in this ecosystem) |
| **Processed Pages** | Azure Monitor metric split by `FeatureName` for cost tracking |

## Setup

### Environment

```bash
uv sync
cp .env.example .env
az login
```

Create a single-service Document Intelligence resource with a custom subdomain. Set:

```dotenv
DOCUMENT_INTELLIGENCE_ENDPOINT=https://<resource>.cognitiveservices.azure.com
```

Source URLs contain SAS tokens — treat as secrets. Set only via shell, Key Vault, or CI secret store. Never commit:

```bash
export DI_READ_SOURCE_URL="https://<storage>.blob.core.windows.net/<container>/<doc>?<sas>"
export DI_LAYOUT_SOURCE_URL="..."
export DI_INVOICE_SOURCE_URL="..."
export DI_ID_SOURCE_URL="..."
```

For custom neural (lesson 05):

```bash
export DI_CUSTOM_NEURAL_MODEL_ID="northwind-invoice-v1"
export DI_TRAINING_CONTAINER_URL="https://<storage>.blob.core.windows.net/<container>?<sas>"
export DI_CUSTOM_NEURAL_PREFIX="labeled"
export DI_CUSTOM_NEURAL_MAX_TRAINING_HOURS="0.5"
```

### Safe run order

1. **06 first** — pure local decision-tree chooser; no cloud, no cost.
2. **01, 02** preflight — OCR + layout on a disposable document.
3. **01, 02 --apply** with `--show-text` / `--show-markdown` only after data + role review.
4. **03, 04** preflight — invoice + ID field extraction.
5. **03, 04 --apply --show-values** only for approved data (invoice + ID = PII).
6. **05** preflight — custom neural build validation.
7. **05 --apply** ONLY after training data + labels + region + cost review (build takes minutes to hours; billable beyond 10 free hours/month).

### Costs and side effects

| Lesson | Cost / side effect |
|---|---|
| 01-04 preflight | Local; validates env + URL shape. |
| 01 `--apply` | 1 billable page analysis via prebuilt-read. |
| 02 `--apply` | 1 billable page analysis via prebuilt-layout (higher per-page than read). |
| 03 `--apply` | 1 billable invoice analysis. |
| 04 `--apply` | 1 billable ID analysis. |
| 05 preflight | Local; validates model ID + container URL + training-hour range. |
| 05 `--apply` | Custom neural build: 10 free hours/month, then billable per hour with 30-min minimum. |
| 06 | Never billable — local chooser only. |

Monitor Azure Monitor `Processed Pages` split by `FeatureName`. Page volume + optional features + custom-model training + regional price all affect cost.

## Decision tables

### DI vs CU (from lesson 06)

| Need | Current default |
|---|---|
| OCR or layout extraction only | **Content Understanding** `prebuilt-read` or `prebuilt-layout` |
| Standard structured invoice or ID | **Document Intelligence** prebuilt (this domain) |
| Labeled, structured custom extraction | **Document Intelligence** custom neural (lesson 05) |
| Unstructured, inferred, multimodal, or multi-file extraction | **Content Understanding** analyzer (domain 05) |
| On-premises / air-gapped processing | **Document Intelligence** containers |

### Which DI prebuilt to pick

```text
Just text? → prebuilt-read
Text + tables/structure? → prebuilt-layout
Invoice/utility/PO? → prebuilt-invoice
Passport/government ID? → prebuilt-idDocument
Labeled custom fields? → custom neural (lesson 05)
```

### When custom neural pays off

| Signal | Choice |
|---|---|
| Standard invoice fields cover >90% of need | Use prebuilt-invoice; skip custom |
| Domain-specific fields not in any prebuilt | Custom neural |
| <5 labeled samples available | Not enough — collect more first |
| Documents have novel structure not in prebuilts | Custom neural |
| Need signature detection or overlapping fields | Custom neural (v4.0 features) |

## Lesson map

| # | Lesson | Runnable objective | Status / limitation |
|---:|---|---|---|
| 01 | [Read OCR](01_read_ocr.py) | Extract OCR text from one document | `--apply` bills 1 analysis; text redacted unless `--show-text` |
| 02 | [Layout Markdown + tables](02_layout_markdown_tables.py) | Extract structure as Markdown with tables | `--apply` bills 1 analysis; markdown redacted unless `--show-markdown` |
| 03 | [Invoice](03_invoice.py) | Extract typed invoice fields | `--apply` bills 1 analysis; values redacted unless `--show-values` |
| 04 | [ID document](04_id_document.py) | Extract typed ID fields | `--apply` bills 1 analysis; values redacted unless `--show-values` |
| 05 | [Custom neural build](05_custom_neural_preflight.py) | Preflight + build a custom neural model | `--apply` billable + persistent; 30-min min per job |
| 06 | [DI vs CU chooser](06_di_vs_cu_decision.py) | Local decision-tree for DI vs CU | Never billable |

---

## Stage 1 — Prebuilt OCR + layout (lessons 01–02)

The two lightest-weight prebuilts. Use them to learn v4.0 response contracts and for workloads where their documented behavior fits.

### 01 — Read OCR

**Question answered:** How do I extract OCR text from a document using DI v4.0?

**Background.** `prebuilt-read` returns OCR words, lines, paragraphs, language, and page locations. Use for pure text extraction; use `prebuilt-layout` (lesson 02) when you also need tables + structure.

```bash
# Preflight
uv run python 09-current-ai-services-other/01_read_ocr.py

# Apply (with text output)
uv run python 09-current-ai-services-other/01_read_ocr.py --apply --show-text
```

**Code path.**
1. `preflight()` validates `DOCUMENT_INTELLIGENCE_ENDPOINT` + `DI_READ_SOURCE_URL` present + URL shape valid.
2. `--apply`: `analyze("prebuilt-read", url)` → `DocumentIntelligenceClient.begin_analyze_document` → poll → result.
3. Print `pages: N`, `languages: M`; text only if `--show-text`.

**What to watch.** Preflight: env `configured`/`missing`. `--apply`: counts + optional text (truncated 2000 chars).

**Study points.**
- v4.0 handles multi-page documents; page count is authoritative.
- Language detection covers documented languages — validate for your target scripts.
- OCR text can contain PII — `--show-text` opt-in for approved data only.

**References:** [Read model](https://learn.microsoft.com/azure/ai-services/document-intelligence/prebuilt/read) · [What's new](https://learn.microsoft.com/azure/ai-services/document-intelligence/whats-new)

### 02 — Layout Markdown + tables

**Question answered:** How do I extract tables + structure as Markdown from a document?

**Background.** `prebuilt-layout` adds document structure: tables, selection marks, paragraph roles, figures, sections. Requesting Markdown preserves structure — complex tables render as HTML inside Markdown so merged cells + captions survive.

```bash
# Preflight
uv run python 09-current-ai-services-other/02_layout_markdown_tables.py

# Apply (with markdown output)
uv run python 09-current-ai-services-other/02_layout_markdown_tables.py --apply --show-markdown
```

**Code path.**
1. `preflight()` validates env + `DI_LAYOUT_SOURCE_URL`.
2. `--apply`: `analyze("prebuilt-layout", url, markdown=True)` → v4.0 client with `output_content_format="markdown"` → result.
3. Print counts: pages, tables, figures, sections; markdown only if `--show-markdown`.

**What to watch.** Preflight: env status. `--apply`: `pages: N`, `tables: M`, `figures: K`, `sections: L`. Markdown body truncated at 4000 chars.

**Layout Markdown rules.**
- Simple tables render as Markdown tables.
- Complex tables (merged cells, captions) fall back to embedded HTML — still parseable.
- Section headings become Markdown headings — useful for downstream chunking.
- Selection marks (checkboxes, radio buttons) render inline.

**References:** [Layout model](https://learn.microsoft.com/azure/ai-services/document-intelligence/prebuilt/layout) · [Layout Markdown](https://learn.microsoft.com/azure/ai-services/document-intelligence/concept/markdown-elements)

---

## Stage 2 — Prebuilt structured extraction (lessons 03–04)

Typed field extraction for domain-common documents. `documents[].fields` returns fields Microsoft trained the models on.

### 03 — Invoice

**Question answered:** How do I extract typed invoice fields (vendor, amounts, line items) from an invoice PDF?

**Background.** `prebuilt-invoice` handles invoices, utility bills, sales orders, purchase orders. Returns typed fields in `documents[0].fields`: VendorName, InvoiceTotal, LineItems, InvoiceDate, DueDate, etc. Extraction ≠ validation — check confidence + business rules before automated payment.

```bash
# Preflight
uv run python 09-current-ai-services-other/03_invoice.py

# Apply (with field values — approved data only)
uv run python 09-current-ai-services-other/03_invoice.py --apply --show-values
```

**Code path.**
1. `preflight()` validates env + `DI_INVOICE_SOURCE_URL`.
2. `--apply`: `analyze("prebuilt-invoice", url)` → result. `print_fields()` walks `documents[0].fields`, prints name + type + confidence; values only if `--show-values`.

**What to watch.** Field list with types + confidence. Low confidence (< ~0.7-0.8 depending on field) → route to human review, not automatic payment.

**Payment-automation discipline.**
- Confidence threshold per field: high for InvoiceTotal + Amount; medium for LineItems.
- Vendor allow-list check + duplicate invoice check outside DI.
- Never automatically pay solely on DI extraction; enforce a human-review threshold.
- Extract → validate → approve → pay — DI covers only extract.

**References:** [Invoice model](https://learn.microsoft.com/azure/ai-services/document-intelligence/prebuilt/invoice) · [Choose model](https://learn.microsoft.com/azure/ai-services/document-intelligence/concept/choose-model-feature)

### 04 — ID document

**Question answered:** How do I extract typed identity fields from a passport or government ID?

**Background.** `prebuilt-idDocument` supports worldwide passports + documented government ID coverage. Returns typed fields (FirstName, LastName, DateOfBirth, DocumentNumber, ExpirationDate, etc.). Extraction ≠ identity proofing — this alone does not validate an identity claim.

```bash
# Preflight
uv run python 09-current-ai-services-other/04_id_document.py

# Apply (with field values — PII data)
uv run python 09-current-ai-services-other/04_id_document.py --apply --show-values
```

**Code path.**
1. `preflight()` validates env + `DI_ID_SOURCE_URL`.
2. `--apply`: `analyze("prebuilt-idDocument", url)` → `print_fields()` with same redaction pattern as invoice.

**What to watch.** Field list with types + confidence. Reject low-confidence extractions before onboarding decisions.

**Identity discipline.**
- ID data is PII — approved data boundaries + retention policy required before running.
- DI extraction is one signal; identity proofing needs additional checks (liveness, document authenticity, watch-list, KYC).
- Never store raw ID image + extracted fields together without encryption + strict RBAC.
- Regulatory constraints on ID data retention vary by jurisdiction — check local law.

**References:** [ID Document model](https://learn.microsoft.com/azure/ai-services/document-intelligence/prebuilt/id-document) · [Choose model](https://learn.microsoft.com/azure/ai-services/document-intelligence/concept/choose-model-feature)

---

## Stage 3 — Custom neural training (lesson 05)

Train a custom model on labeled documents when no prebuilt fits. Only path in DI for domain-specific fields.

### 05 — Custom neural build

**Question answered:** How do I train a custom neural model on labeled Blob data?

**Background.** Custom neural targets structured + semi-structured documents with labeled examples. Requires ≥5 labeled samples; training data must represent real template/language/value/table variation. v4.0 supports signature detection, table cell confidence, and overlapping fields.

**Before code.** Custom neural regional availability is limited. Confirm region support before creating the resource. You can copy a trained model to another region for analysis where supported.

```bash
# Preflight (env + validation checks; no cloud call)
uv run python 09-current-ai-services-other/05_custom_neural_preflight.py

# Apply (persistent + billable build)
uv run python 09-current-ai-services-other/05_custom_neural_preflight.py --apply
```

**Code path.**
1. `preflight()` validates:
   - `MODEL_ID` matches regex `^[A-Za-z0-9][A-Za-z0-9._~-]{1,63}$`.
   - `DI_TRAINING_CONTAINER_URL` is HTTPS.
   - `DI_CUSTOM_NEURAL_MAX_TRAINING_HOURS` between 0.5 and 10.
2. `--apply`: `build_request()` → `BuildDocumentModelRequest(build_mode="neural", azure_blob_source=AzureBlobContentSource(container_url, prefix), max_training_hours)`.
3. `DocumentIntelligenceAdministrationClient(endpoint, DefaultAzureCredential()).begin_build_document_model(request).result()` — waits for completion.
4. Print `Model built: <model_id>`.

**What to watch.** Preflight: `Local validation: ready for --apply.` or clear error message. `--apply`: `Model built: <model_id>` on success (minutes to hours).

**Training discipline.**
- Label ≥5 samples covering real variation (templates, languages, value types, table shapes).
- v4.0 free tier: 10 training hours/month; excess bills; each job 30-min minimum.
- Save `model_id` — analyze endpoints (`begin_analyze_document(model_id=...)`) reference this after build.
- Copy trained model to a different region for analysis when training + analysis regions differ.

**References:** [Custom neural](https://learn.microsoft.com/azure/ai-services/document-intelligence/train/custom-neural) · [Estimate cost](https://learn.microsoft.com/azure/ai-services/document-intelligence/how-to-guides/estimate-cost)

---

## Stage 4 — Tool selection (lesson 06)

Local decision-tree encoding current DI-vs-CU guidance. Zero cloud calls; a starting default to validate with real documents.

### 06 — DI vs CU chooser

**Question answered:** For a given scenario, which tool (DI or CU) is the current documented default?

**Background.** Encodes the DI-vs-CU decision. Air-gapped → DI containers. LLM triggers (reasoning, multi-file, unstructured) → CU. Standard forms → DI prebuilt. Labeled structured → DI custom neural.

```bash
uv run python 09-current-ai-services-other/06_di_vs_cu_decision.py --scenario ocr-layout
uv run python 09-current-ai-services-other/06_di_vs_cu_decision.py --scenario standard-form
uv run python 09-current-ai-services-other/06_di_vs_cu_decision.py --scenario custom-labeled
uv run python 09-current-ai-services-other/06_di_vs_cu_decision.py \
  --scenario unstructured --needs-reasoning --multiple-files
uv run python 09-current-ai-services-other/06_di_vs_cu_decision.py \
  --scenario custom-labeled --air-gapped
```

**Code path.**
1. `choose_tool(scenario, needs_reasoning, multiple_files, air_gapped)`.
2. Early return for `air_gapped` → DI containers.
3. LLM triggers (`needs_reasoning`, `multiple_files`, `unstructured`) → CU analyzers.
4. `ocr-layout` → CU prebuilt-read/prebuilt-layout.
5. `custom-labeled` → DI custom neural.
6. Default (`standard-form`) → DI prebuilt.
7. Print `Choose: <tool>` + `Why: <reason>`.

**What to watch.** Different flag combinations produce different routes. This is a chooser, not a benchmark — validate with representative documents + production requirements before commitment.

**Study points.**
- OCR/layout guidance now favors **CU** (a change from earlier DI-first defaults).
- DI custom neural remains preferred for deterministic labeled extraction.
- Air-gapped is the ONE scenario where DI containers are the mandatory choice.
- Multi-file or inference/reasoning tips scale to CU regardless of scenario.

**References:** [Choose model](https://learn.microsoft.com/azure/ai-services/document-intelligence/concept/choose-model-feature) · [What's new](https://learn.microsoft.com/azure/ai-services/document-intelligence/whats-new)

---

## Feature status and hard limits

| Feature | Status | Practical boundary |
|---|---|---|
| DI v4.0 REST API `2024-11-30` | GA | Custom subdomain endpoint required for Entra |
| `prebuilt-read` | GA | OCR text, words, lines, paragraphs, language |
| `prebuilt-layout` | GA | Adds tables, sections, figures, selection marks; Markdown output supported |
| `prebuilt-invoice` | GA | Invoices, utility bills, sales orders, purchase orders |
| `prebuilt-idDocument` | GA | Worldwide passports + documented ID coverage |
| Custom neural (build_mode: neural) | GA | ≥5 labeled samples; v4.0 features: signatures, table cell confidence, overlapping fields |
| Custom neural free training | GA | 10 hours/month (Standard); each job 30-min minimum |
| DI containers | GA | Only air-gapped path in this ecosystem |
| Layout Markdown output | GA | Complex tables render as HTML inside Markdown |
| Entra auth | GA | Requires custom subdomain; regional endpoint not supported |
| API keys | Available | Not used in these labs — Entra only |
| Region availability | Varies | Custom neural training regions narrower than analysis regions |

## Troubleshooting

| Symptom | Likely cause | Resolution |
|---|---|---|
| `AuthenticationError` on `--apply` | Regional endpoint used; Entra requires custom subdomain | Set `DOCUMENT_INTELLIGENCE_ENDPOINT` to `https://<resource>.cognitiveservices.azure.com` |
| `403 Forbidden` | Caller lacks `Cognitive Services User` role | Assign at resource scope; log out and back in |
| `InvalidRequest: source` | Source URL not reachable HTTPS or SAS expired | Regenerate SAS; verify URL from same network |
| Empty OCR text but analysis succeeded | Scanned image with no text or unsupported language | Check page count > 0; verify document is readable |
| Layout Markdown missing tables | Document has no detectable tables | Confirm actual tables present; check `tables[]` array in result |
| Invoice fields all low confidence | Non-standard invoice template | Consider custom neural (lesson 05) with your templates |
| `Model ID must be 1-64 letters...` | Custom model ID contains invalid chars | Use only `[A-Za-z0-9._~-]`, start with letter or digit |
| Custom neural build fails: `Storage access denied` | DI managed identity lacks Blob role | Assign `Storage Blob Data Reader` (or Contributor for writes) to DI MI |
| Custom neural build times out | `max_training_hours` too low for dataset size | Increase within 0.5-10 range; document size + label count drive time |
| `Region not supported` on custom neural build | Chosen region lacks training capacity | Deploy DI resource in a supported region; copy model post-build if needed |
| `Processed Pages` metric missing in Monitor | Diagnostic settings not enabled | Enable diagnostics on DI resource → Log Analytics workspace |

## CI/CD and operational release

DI is per-document billable + custom-neural training is persistent. Preflight in CI; keep `--apply` manual.

```text
PR modifies source URL var or model ID
  → CI runs preflight for each lesson (no cloud)
  → reviewer approves
  → operator runs --apply manually with reviewed source URL
  → verify output confidence + field completeness
  → for custom neural: --apply build, monitor training log, review analyze test
  → deploy analyze integration after quality gate
```

### What to version

- Source URL environment variable names (values live in secret store)
- Custom neural model IDs (`northwind-invoice-v1`, `-v2`, etc.)
- Training container structure + label taxonomy
- Analyze-endpoint client code + confidence thresholds
- Downstream business rules per extracted field

### Release gates

| Change | Minimum gate |
|---|---|
| New source URL | Preflight passes; caller network can reach URL |
| Custom neural model | Build succeeds; representative test set beats prior model on held-out metrics |
| Confidence threshold change | Human-review escalation rate change measured |
| Region change | Model availability verified; latency/cost delta measured |

## Security, networking, and IaC

| Decision | Recommendation | Common pitfall |
|---|---|---|
| Auth | Entra + `DefaultAzureCredential` on custom subdomain | API key in `.env` — rotate reactively when leaked |
| Caller role | `Cognitive Services User` at DI resource scope | `Contributor` at resource group grants excess control-plane rights |
| DI managed identity | System-assigned + `Storage Blob Data Reader` on training container | Public Blob URL — data leak vector |
| Source URLs | SAS-bearing HTTPS; never in `.env.example`, source, or logs | SAS in commit history — rotate + audit access log |
| Private network | Private endpoint on DI resource + trusted-service exception on Storage | Public DI + private Storage = data path fails |
| Field values | Redact by default; opt-in `--show-values` for approved data only | Print invoice/ID data by default in dev logs |
| Retention | Approved retention + deletion policy on all output | Persist raw content indefinitely in dev container |
| Custom neural model lifecycle | Version model IDs; delete abandoned models | Accumulate unused custom models — RBAC + cost drift |

## Common exam traps

| Claim | Correct interpretation |
|---|---|
| "DI v4.0 uses regional endpoints for Entra auth." | False. Regional endpoints don't support Entra; custom subdomain required. |
| "prebuilt-invoice validates the invoice." | False. Extracts fields only; validation + payment authorization are separate. |
| "prebuilt-idDocument is identity proofing." | False. Extracts fields; identity proofing needs liveness + auth checks + KYC. |
| "Custom neural needs 100+ samples." | False. Minimum is 5 — but coverage matters more than count. |
| "10 free training hours means unlimited experimentation." | False. Excess bills; each job 30-min minimum; 10 hours applies to Standard tier. |
| "Custom neural trained in region A can be analyzed anywhere." | False. Copy model to target region first where supported. |
| "Layout Markdown loses table structure." | False. Complex tables render as HTML inside Markdown to preserve merges. |
| "DI containers work in Azure Cloud." | Partially true — containers exist for on-prem/air-gapped; not the default deployment. |
| "OCR text and CU output are interchangeable." | False. DI is deterministic extraction; CU is LLM-inferred. Different failure modes. |
| "prebuilt-read includes tables." | False. Read is text only; use Layout for tables. |
| "DI can process file:// URLs." | False. HTTPS-reachable URLs only. |
| "DI encrypts source URL by default." | False. Source URL is passed as request payload — treat SAS as credential; do not log. |

## Objective coverage and limits

Runnable evidence in this folder covers DI v4.0 GA API + SDK usage for: OCR text extraction (Read), layout with tables + Markdown (Layout), typed invoice/ID field extraction (prebuilt), custom neural build lifecycle, and DI-vs-CU decision routing.

It does **not** cover: DI containers deployment, DI classifier models, custom template models (v3.x pattern), other prebuilts (`prebuilt-businessCard`, `prebuilt-tax*`, `prebuilt-marriageCertificate`), analyze API on custom neural models after build, model copy across regions, or classification tasks. It does not test private network reachability — verify from your caller identity + network.

## References

### DI v4.0 core

- [What's new](https://learn.microsoft.com/azure/ai-services/document-intelligence/whats-new)
- [Choose model](https://learn.microsoft.com/azure/ai-services/document-intelligence/concept/choose-model-feature)

### Prebuilt models

- [Read model](https://learn.microsoft.com/azure/ai-services/document-intelligence/prebuilt/read)
- [Layout model](https://learn.microsoft.com/azure/ai-services/document-intelligence/prebuilt/layout)
- [Layout Markdown](https://learn.microsoft.com/azure/ai-services/document-intelligence/concept/markdown-elements)
- [Invoice model](https://learn.microsoft.com/azure/ai-services/document-intelligence/prebuilt/invoice)
- [ID Document model](https://learn.microsoft.com/azure/ai-services/document-intelligence/prebuilt/id-document)

### Custom neural

- [Custom neural](https://learn.microsoft.com/azure/ai-services/document-intelligence/train/custom-neural)

### Security + cost

- [Managed identity and secured network access](https://learn.microsoft.com/azure/ai-services/document-intelligence/authentication/managed-identities-secured-access)
- [Estimate cost](https://learn.microsoft.com/azure/ai-services/document-intelligence/how-to-guides/estimate-cost)

### Compliance and Responsible AI

- [Document Intelligence transparency note](https://learn.microsoft.com/azure/foundry/responsible-ai/document-intelligence/transparency-note)
- [Document Intelligence data privacy + security](https://learn.microsoft.com/azure/foundry/responsible-ai/document-intelligence/data-privacy-security)
- [Content Understanding transparency note](https://learn.microsoft.com/azure/foundry/responsible-ai/content-understanding/transparency-note)
- [Content Understanding data privacy](https://learn.microsoft.com/azure/foundry/responsible-ai/content-understanding/data-privacy)

### Related domains

- [Domain 5: Information extraction](../05-information-extraction/README.md) — Content Understanding lessons (09-16)
- [Domain 7: Production platform](../07-production-platform-other/README.md) — private cell for DI resource
