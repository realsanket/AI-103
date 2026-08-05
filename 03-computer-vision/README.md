---
ai-usage: ai-assisted
---

# Domain 3: Computer vision

Runnable AI-103 study guide for image understanding, image/video generation,
content safety, provenance, and Content Understanding (CU). Run every command
from repository root:

```bash
uv run python 03-computer-vision/<lesson>.py
```

A successful lab proves one narrow request path. It does **not** prove output
accuracy, accessibility, rights clearance, production readiness, or policy
compliance.

## Outcomes and learning order

| Stage | Lessons | Learn | Do not infer |
|---|---|---|---|
| Understand | 01, 07 | Multimodal image input and accessibility drafts | OCR, object regions, fact verification, or accessibility conformance |
| Generate and edit | 02–04 | Image output, prompt editing, mask intent | Deterministic pixels or preservation outside mask |
| Generate video | 05, 10, 11 | Asynchronous Sora job, reference preflight, remix boundary | General video editing or automatic rights clearance |
| Control media risk | 06, 12, 13 | Harm signals, provenance signals, indirect-injection boundary | Universal approval, ownership proof, or complete attack prevention |
| Analyze hosted media | 08, 09, 14, 15 | CU analyzer, Blob SAS preflight, bounded handoff | Uploading, indexing, long-term storage, or a complete ingestion platform |

Recommended order: **01 → 07 → 06 → 02 → 03 → 04 → 05 → 10 → 11 →
12 → 13 → 14 → 08 → 09 → 15**. Run no billable `--apply`/`--run` lesson
until its no-cloud preflight and access checks pass.

## Architecture and service decisions

```text
local image ──data URL──> Azure OpenAI Responses ──> answer/draft
prompt ─────────────────> Azure OpenAI Images    ──> PNG
prompt ─────────────────> Sora video job         ──> poll ──> MP4

local image ──bytes─────> Content Safety          ──> category signals
Blob URL + read SAS ────> Content Understanding   ──> async analyzer result
OCR text ───────────────> Prompt Shields          ──> attack signal
Blob URL + read SAS ────> Provenance detection    ──> C2PA/watermark signal
```

### Endpoint, SDK, and authentication matrix

| Surface | Code setting / client | Endpoint shape | Auth | Lessons |
|---|---|---|---|---|
| Azure OpenAI SDK data plane | `AZURE_OPENAI_ENDPOINT`, `openai_client()` | `https://<resource>.openai.azure.com/openai/v1` | `DefaultAzureCredential`, `https://ai.azure.com/.default` | 01–04, 07, 10–11 |
| Sora direct REST | `AZURE_OPENAI_ENDPOINT`, `05_video_generation.py` | `https://<resource>.openai.azure.com/openai/v1` | Current request headers contain a redacted placeholder, not `_token()` output | 05 |
| Foundry project data plane | `PROJECT_ENDPOINT`, `project_client()` | `https://<resource>.services.ai.azure.com/api/projects/<project>` | `DefaultAzureCredential` | 06 model path |
| Azure AI Content Safety | `CONTENT_SAFETY_ENDPOINT`, `content_safety_client()` | `https://<resource>.cognitiveservices.azure.com` | `DefaultAzureCredential` | 06 direct path, 12, 13 |
| Content Understanding REST | `CU_ENDPOINT`, `_shared/cu_client.py` | `https://<resource>.services.ai.azure.com/contentunderstanding` | Current request headers contain a redacted placeholder, not a credential token | 08, 09, 15 |
| Azure Blob Storage | no cloud storage client in this domain | `https://<account>.blob.core.windows.net/<container>/<blob>` | SAS for CU/provenance fetch; Entra ID for application storage work | 08, 09, 12, 14, 15 |

Do not substitute a Foundry project endpoint for an Azure OpenAI endpoint.
Obtaining an Entra token proves identity authentication, not data-plane RBAC
authorization.

### Decision table

| Need | Use | Why | Do not use when |
|---|---|---|---|
| Question about one or more images | Multimodal Responses | Flexible language grounded on supplied image | You require fixed schema, coordinates, verified OCR, or deterministic extraction |
| New or changed pixels | Image generation/edit | Produces image bytes | You need pixel-perfect compositing or source preservation |
| Short generated video | Sora job | Explicit asynchronous video contract | You need synchronous response, a durable media store, or broad-region GA support |
| Four-category image harm signal | Direct Content Safety | Application decides before downstream model call | You need a complete business policy or legal decision |
| Origin/transparency signal | Provenance detection | Detects supported C2PA/Microsoft signals | You need proof of ownership, truth, safety, or human origin |
| Repeatable image/video analyzer result | CU prebuilt analyzer | Async, analyzer-shaped output for hosted media | Your source cannot be service-reachable or output must be permanent schema |
| Defend OCR/document text from instruction attacks | Prompt Shields plus application policy | Scans untrusted document content | You expect one detection call to make untrusted text safe |

## Before running

### Install, identity, and configuration

```bash
uv sync
cp .env.example .env
az login
```

Use a nonproduction subscription, approved non-sensitive samples, and a
least-privilege identity. On a developer machine `DefaultAzureCredential`
usually reaches Azure CLI credentials after `az login`; deployed workloads
should use managed identity or workload identity. Confirm effective principal,
tenant, endpoint, deployment, region, and role before changing application
code for a `401`, `403`, or `404`.

```dotenv
# Direct Azure OpenAI: deployment aliases, not model-family labels.
AZURE_OPENAI_ENDPOINT=https://<resource>.openai.azure.com
DEFAULT_MODEL=<multimodal-deployment>
IMAGE_MODEL=<gpt-image-deployment>
VIDEO_MODEL=<sora-2-deployment>

# Lesson 06 project-scoped model path.
PROJECT_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<project-name>

# Content Safety: lessons 06, 12, 13.
CONTENT_SAFETY_ENDPOINT=https://<resource>.cognitiveservices.azure.com

# Content Understanding: lessons 08, 09, 15.
CU_ENDPOINT=https://<resource>.services.ai.azure.com
CU_API_VERSION=2025-11-01

# CU source preflight and a production storage design.
STORAGE_ACCOUNT=<account>
STORAGE_CONTAINER=<container>
SAMPLE_IMAGE_URL=<https-blob-url-with-read-sas>
SAMPLE_VIDEO_URL=<https-blob-url-with-read-sas>
```

`SAMPLE_IMAGE_URL` and `SAMPLE_VIDEO_URL` are read directly from environment
by lessons 08–09; add them to local `.env` even if older `.env.example`
templates omit them. `STORAGE_CONNECTION_STRING` exists in shared settings,
but no Domain 3 lesson uses it. Do not add account keys or connection strings
to source code.

### Resource, region, quota, and cost decisions

1. In **Foundry portal**, check model deployment capability, Sora preview
   availability, supported region, quota, and pricing before a design commits
   to a model or video workflow.
2. In **Azure portal**, create/select Content Safety, CU, Storage, and
   monitoring resources in approved regions. CU, Sora, and provenance preview
   availability are service/region/version dependent.
3. Use **Azure CLI** for repeatable discovery and role review, for example:

   ```bash
   az account show --query "{subscription:id,tenant:tenantId,user:user.name}" -o json
   az role assignment list --assignee <principal-object-id> --all -o table
   az cognitiveservices account list -g <resource-group> -o table
   ```

   These commands discover state; they do not create a deployment or grant a
   role. Avoid putting SAS URLs in terminal history or command arguments.
4. Use **IaC** (Bicep/ARM/Terraform) for resource kind, region, public/private
   network policy, diagnostic settings, private endpoints, role assignments,
   tags, and approved model deployments. This domain contains no IaC template,
   and none of its scripts provisions infrastructure. Keep model/deployment
   availability checks in release gates because IaC cannot make an unsupported
   model available in a region.

Budget for image tokens/output, image-generation calls, Sora generated seconds,
Content Safety requests, CU operations/media processing, Blob storage and
egress, private-link/DNS operations, and Log Analytics/Application Insights
ingestion. Set budget alerts and per-environment quotas. Never use unbounded
retry to solve quota exhaustion.

### Media transport and prerequisites

| Transport | Lessons | Prerequisite | Security boundary |
|---|---|---|---|
| Base64 data URL | 01, 06, 07 | Readable local PNG/JPEG/WebP | Bytes enter model request; never log request body |
| Multipart local file | 03, 04, 10 | Valid source; mask/reference constraints | Local validation is not rights or safety validation |
| HTTPS Blob URL with short read SAS | 08, 09, 12, 14, 15 | CU/service can resolve and fetch URL before expiry | SAS delegates access; redact query string everywhere |
| Existing Sora video ID | 11 | Completed, authorized Sora output | ID is not a local file and does not establish ownership |

For image editing, shared `validate_edit_inputs` checks readable source format
(PNG/JPEG/WebP); with a mask it also checks PNG, matching dimensions, alpha
channel, and at least one transparent pixel. It does **not** enforce all
remote API size/model constraints or assess desired visual quality.

CU’s shared helper defaults to `CU_API_VERSION=2025-11-01`, accepts exactly
one HTTPS source URL, validates a partially specified Blob SAS, validates that
`Operation-Location` remains on configured CU host, and has a 300-second
polling deadline. Configure a supported version for resource; do not revive
older documentation’s `2025-11-15-preview` default.

## Lesson map

| # | Lesson | Primary dependency | Cloud side effect |
|---:|---|---|---|
| 01 | [Multimodal understanding](01_multimodal_understanding.py) | Multimodal deployment | Inference |
| 02 | [Image generation](02_image_generation.py) | Image deployment | Generated PNG and inference |
| 03 | [Prompt image edit](03_image_prompt_edit.py) | Image deployment | Generated PNG and inference |
| 04 | [Masked image edit](04_image_masked_edit.py) | Image deployment + valid mask | Generated PNG and inference |
| 05 | [Sora text-to-video](05_video_generation.py) | Sora preview deployment/region | Billable job and MP4 |
| 06 | [Image moderation](06_image_moderation.py) | Content Safety + project endpoint | Two data-plane calls |
| 07 | [Alt text and captions](07_alt_text_captions.py) | Multimodal deployment | Two inference calls |
| 08 | [CU image analysis](08_content_understanding_image.py) | CU + reachable image URL | Async analyzer operation |
| 09 | [CU video analysis](09_video_analysis.py) | CU + reachable video URL | Async analyzer operation |
| 10 | [Reference-media preflight](10_reference_media_preflight.py) | Optional Sora deployment | None unless `--apply` |
| 11 | [Video remix](11_video_remix.py) | Completed Sora video ID | None unless `--apply` |
| 12 | [Visual provenance policy](12_visual_provenance_policy.py) | Content Safety + Blob URL | None unless `--run` |
| 13 | [OCR injection safety](13_ocr_image_injection_safety.py) | Content Safety + local OCR text | None unless `--run` |
| 14 | [CU Blob preflight](14_cu_blob_preflight.py) | Optional storage/CU settings | None |
| 15 | [CU visual handoff](15_cu_visual_handoff.py) | CU + reachable source URL | None unless `--apply` |

## Detailed implementation walkthroughs

Each walkthrough states **what**, **why**, **how/architecture**, **prereqs and
dependencies**, **code path**, **output**, **use / do not use**, **best
practice**, **pitfalls**, and **takeaway**. “Production” describes work the
lesson does not claim to implement.

### 01 — Multimodal understanding

Run:

```bash
uv run python 03-computer-vision/01_multimodal_understanding.py
```

**What.** Answers an open-ended question about local `sales_data.png`.

**Why.** A multimodal model combines task language with visual evidence; this
is simpler than designing an analyzer when result need is prose.

**Prereqs and dependencies.** `AZURE_OPENAI_ENDPOINT`, a visual-capable
`DEFAULT_MODEL`, Entra data-plane access, `_shared/sample_data/images/sales_data.png`,
and `_shared/vision_inputs.py`.

**How / architecture.** Local image bytes become `data:<mime>;base64,...`;
Responses receives one `input_text` and one `input_image`, then returns text.

**Code path.** `image_data_url()` validates/encodes image → `openai_client()`
uses direct Azure OpenAI endpoint → `responses.create(model=DEFAULT_MODEL)`
→ `r.output_text`.

**Output.** Variable summary text printed to stdout.

**Use.** Chart/screenshot explanations, assisted visual Q&A, or a reviewed
caption draft. **Do not use.** Fixed field extraction, reliable numeric OCR,
coordinates, object detection, or high-stakes factual decision.

**Best practice.** Ask narrow observable questions (“state unreadable text,
do not guess”), constrain output schema where downstream code needs it, and
evaluate representative images.

**Pitfalls.** A text-only deployment, malformed data URL, unknown MIME, large
payload, or image-embedded instructions can fail or mislead. Treat all visual
and OCR-like text as untrusted data, never as system instructions.

**Takeaway.** Data URL is inline request transport; model prose is not a
structured or verified computer-vision contract.

### 02 — Image generation

Run:

```bash
uv run python 03-computer-vision/02_image_generation.py
```

**What.** Generates one training-image PNG from an explicit prompt.

**Why.** Image generation makes pixels for creative work; it is different from
recognizing source-image facts.

**Prereqs and dependencies.** `AZURE_OPENAI_ENDPOINT`, deployed `IMAGE_MODEL`,
direct Azure OpenAI role/access, and writable `_shared/sample_data/generated/`.

**How / architecture.** Prompt → `images.generate` → base64 image response →
validated bytes → local PNG.

**Code path.** `openai_client()` → `images.generate(model, prompt, n=1,
size="1024x1024", quality="medium", output_format="png")` →
`save_generated_image()` decodes and verifies returned image bytes → writes
`training_image.png`.

**Output.** `saved: .../training_image.png`; open it for visual review.

**Use.** Draft creative assets, controlled design exploration, and prompt
experiments. **Do not use.** Brand-approved production collateral, evidence,
or content requiring factual/rights certainty without review.

**Best practice.** Version prompt, deployment, parameters, reviewer decision,
and approved asset ID. Change one visible requirement per experiment; apply
human/policy review before distribution.

**Pitfalls.** Deployment alias is not model-family name; output overwrites a
previous lab file; successful bytes can be inaccurate, unsafe, or unsuitable.
Higher quality/size can affect latency/cost and rate limits.

**Takeaway.** Generation success means image bytes arrived, not acceptance.

### 03 — Prompt-driven image edit

Run:

```bash
uv run python 03-computer-vision/03_image_prompt_edit.py
```

**What.** Edits `product_photo.png` with a full-frame preservation request.

**Why.** Prompt-only editing is appropriate when desired change is broad and
exact editable region is unnecessary.

**Prereqs and dependencies.** Same direct image deployment as 02, source
image, and `validate_edit_inputs(src)`.

**How / architecture.** Valid local file → multipart `images.edit` prompt →
base64 output → validated PNG on disk.

**Code path.** Input helper verifies source readability/format → script opens
source binary → `images.edit(... image=image_file, prompt, size, n, quality)`
→ `save_generated_image()` writes `edited_product_photo.png`.

**Output.** One `saved:` line and generated edit.

**Use.** Creative restyling, lighting/background concepts, and reviewed
marketing drafts. **Do not use.** Product photography requiring exact text,
logos, legal evidence, or pixel stability.

**Best practice.** Define visual acceptance checks for product identity,
logos, text, edges, background, and unintended changes; retain source/edit
prompt/reviewer lineage.

**Pitfalls.** “Keep unchanged” is intent, not a preservation guarantee. The
helper does not compare output to source or enforce every remote API limit.

**Takeaway.** Prompt-only edit is generative full-frame transformation.

### 04 — Masked image edit

Run:

```bash
uv run python 03-computer-vision/04_image_masked_edit.py
```

**What.** Requests a wall display only in transparent area of `mask.png`.

**Why.** Mask bounds intended edit region better than prose alone.

**Prereqs and dependencies.** Requirements from 03 plus source/mask same
dimensions; mask must be PNG with alpha and at least one transparent pixel.

**How / architecture.** Source + alpha mask + prompt → `images.edit` → PNG.
Transparent (alpha `0`) mask pixels are intended editable pixels; nontransparent
pixels are intended outside edit.

**Code path.** `validate_edit_inputs(src, mask)` validates source/mask contract
→ both handles passed as `image`/`mask` → response verified → writes
`masked_edit_product_photo.png`.

**Output.** One `saved:` line and output image to inspect alongside source and
mask.

**Use.** Bounded inpainting where review can tolerate generative variance.
**Do not use.** Deterministic compositing, compliance redaction, or any
workflow requiring exact preservation outside mask.

**Best practice.** Keep source/mask/output trio, inspect boundary artifacts,
and add pixel-difference/business acceptance tests when outside-mask stability
matters.

**Pitfalls.** Mask validation only proves local format geometry/alpha. It does
not prove semantic placement, output quality, or exact preservation.

**Takeaway.** A mask constrains requested change; it is not a pixel lock.

### 05 — Sora 2 text-to-video

Run only after preview, region, quota, policy, and cost checks:

```bash
uv run python 03-computer-vision/05_video_generation.py
```

**What.** Creates a text-only 1280×720 five-second video through asynchronous
Sora API, polls it, and downloads first generated MP4.

**Why.** Video work lasts longer than an HTTP request; job state separates
submission, observation, and download.

**Prereqs and dependencies.** `AZURE_OPENAI_ENDPOINT`, supported Sora
`VIDEO_MODEL`, Entra role/access, Sora preview availability in selected region,
and writable generated directory.

**How / architecture.**

```text
POST job → job ID → GET status until terminal → first generation ID → GET video bytes → MP4
```

**Code path.** Direct REST defines `_token()` but current submit/poll/download
headers use a literal redacted placeholder → request attempt →
`_wait_for_job()` polls every five seconds with 300-second deadline →
raises on failed/canceled state with service detail → downloads first
generation to `northwind_video.mp4`.

**Output after an authenticated successful request.**

```text
submitted job: <id>
  status: <state>
saved: .../northwind_video.mp4
```

**Use.** Reviewed short-video prototyping and a reference for job lifecycle.
**Do not use.** Synchronous UI request path, durable media library, automatic
retry/recovery system, or reference/remix workflow.

**Best practice.** Persist job ID/owner/idempotency key, bound polling with
jitter/backoff, expose cancel/resume, verify downloaded content, apply
retention/deletion policy, and review output before publication.

**Pitfalls.** A timeout does not cancel remote job; no cancellation, resume,
variant selection, or cleanup is sent. First generation selection is not a
quality choice. Preview/model availability and policy outcomes vary by region.

**Takeaway.** Submit/poll/download is required asynchronous lifecycle, not a
single “generate MP4” call. As written, L05 needs a real token header before
it can complete that lifecycle.

### 06 — Image moderation and guardrails

Run:

```bash
uv run python 03-computer-vision/06_image_moderation.py
```

**What.** Compares explicit Content Safety image classification with
deployment/model guardrail behavior for same support screenshot.

**Why.** Direct moderation gives application an explicit decision point;
deployment safety behavior protects a model call but does not implement
business policy.

**Prereqs and dependencies.** `CONTENT_SAFETY_ENDPOINT`, `PROJECT_ENDPOINT`,
visual `DEFAULT_MODEL`, both relevant data-plane role assignments, and
`support.png`.

**How / architecture.**

```text
image bytes ─> Content Safety analyze_image ─> four category signals
image data URL + question ─> project OpenAI client ─> answer/filter metadata
```

**Code path.** `_direct_content_safety()` reads local bytes and calls
`AnalyzeImageOptions(ImageData(...))`; `_guardrail_through_model()` makes
project-scoped Responses call and prints optional `model_extra.content_filters`.

**Output.** Direct category severity lines, then a support answer or service
safety outcome; metadata may be absent.

**Use.** Pre-model image risk signals plus independent model deployment
guardrails. **Do not use.** A severity alone as policy, legal decision,
automatic approval, or audit record.

**Best practice.** Define per-category thresholds, intended-audience/context
rules, block/escalate/user message, reviewer workflow, appeal, and minimal
privacy-aware audit record. Test false positives/negatives.

**Pitfalls.** Direct image categories are Hate, SelfHarm, Sexual, Violence,
with trimmed severities **0, 2, 4, 6**—not all 0–7 values. Filter metadata is
optional and SDK/service-shape dependent. One image can signal several
categories.

**Takeaway.** Guardrail observation and explicit moderation are complementary,
not interchangeable.

### 07 — Accessible alt text and captions

Run:

```bash
uv run python 03-computer-vision/07_alt_text_captions.py
```

**What.** Produces a short `ALT:` plus extended `DESCRIPTION:` draft, then
one caption for two images.

**Why.** Vision can accelerate accessibility authoring, but image purpose
comes from page/task context, not pixels alone.

**Prereqs and dependencies.** Requirements from 01; `sales_data.png`,
`support_ticket_portal.png`, and local response-format validator.

**How / architecture.** Image data URLs → one instructed Responses call for
alt/description; two data URLs → separate caption call.

**Code path.** `_alt_text_and_extended()` calls model; `_accessibility_draft()`
checks labels and 125-character ALT ceiling, appending `REVIEW:` on mismatch;
`_multi_image_caption()` sends both image items.

**Output.**

```text
=== Alt-text ===
ALT: ...
DESCRIPTION: ...
=== Multi-image caption ===
...
```

**Use.** Human-reviewed authoring drafts. **Do not use.** Blind publishing,
substitute for real table/text/UI equivalent, or a claim of WCAG conformance.

**Best practice.** Generate near render time with surrounding context; retain
human-approved override; test with disabled users. Supply chart data and
screen UI as actual text, not only as image.

**Pitfalls.** Prompt labels and regex checks do not prove facts, useful intent,
correct language, decorative-image handling, or safe disclosure of sensitive
content. Caption is visible prose; alt text is nonvisual alternative.

**Takeaway.** Accessibility output is draft content requiring contextual human
review.

### 08 — CU image analysis

Run after hosting approved image behind service-reachable HTTPS:

```bash
uv run python 03-computer-vision/08_content_understanding_image.py
```

**What.** Sends `SAMPLE_IMAGE_URL` to `prebuilt-imageSearch`.

**Why.** CU supplies an asynchronous analyzer-shaped result for searchable
media rather than open-ended model prose.

**Prereqs and dependencies.** `CU_ENDPOINT`, supported `CU_API_VERSION`,
CU data-plane role, `SAMPLE_IMAGE_URL`, and Blob/public access reachable by
CU. Run 14 first for local SAS hygiene checks.

**How / architecture.** CU retrieves source server-side; it never receives
local `file://` path and this lesson does not upload media.

**Code path.** Environment URL → `validate_source_url()` → `analyze(
"prebuilt-imageSearch", url)` → POST submit → validated `Operation-Location`
poll → prints status, first content Markdown, optional `Summary`, or
redacted diagnostic.

**Output.** `status: Succeeded` plus first result slice; empty contents is
valid script behavior.

**Use.** Analyzer experiments and input for a separately designed searchable
ingestion pipeline. **Do not use.** Upload implementation, all-result export,
fixed permanent schema, or evidence that CU indexed data elsewhere.

**Best practice.** Copy/customize analyzer when schema must be stable; store
operation ID, analyzer/version, source metadata without SAS, warnings, and
evaluation outcome. Inspect raw approved result only in controlled diagnostics.

**Pitfalls.** Expired/over-broad SAS, inaccessible private endpoint/DNS,
unsupported input, wrong region/version, quota, or absent summary can fail.
Prebuilt IDs can evolve. Current shared CU request headers are a redacted
placeholder, so this path also needs real token handling before it can complete
a live request.

**Takeaway.** CU fetches URL asynchronously; URL submission is not Blob upload
or search indexing.

### 09 — CU video analysis

Run after hosting an approved video:

```bash
uv run python 03-computer-vision/09_video_analysis.py
```

**What.** Analyzes `SAMPLE_VIDEO_URL` with `prebuilt-videoSearch`.

**Why.** Video requires segment-aware analyzer results rather than one generic
image answer.

**Prereqs and dependencies.** Requirements from 08, valid CU-reachable video,
and a source compatible with selected analyzer/service limits. Run 14 first.

**How / architecture.** HTTPS video URL → async CU job → content segments with
times and optional summaries.

**Code path.** URL validation → `analyze("prebuilt-videoSearch", url)` →
terminal result → iterate `result.contents` → print each `startTimeMs`,
`endTimeMs`, and optional `Summary`.

**Output.**

```text
status: Succeeded
[<start>–<end> ms] <summary>
```

**Use.** Video retrieval/triage prototype and segment handoff. **Do not use.**
Full transcript/chapters/keyframes export, guaranteed frame-level detection,
or a durable search index.

**Best practice.** Preserve segment timing/source grounding, test short events
and small text against labeled video, and design a bounded downstream schema.

**Pitfalls.** `prebuilt-video` is base analyzer for custom analyzers;
lesson uses `prebuilt-videoSearch`. A blank summary does not prove no useful
media information. Sampling can miss rapid events/small details. Current
shared CU request headers are a redacted placeholder, so this path is not
authenticated for a live request as written.

**Takeaway.** Video analyzer output is segmented and partial; inspect task
relevant fields before downstream action.

### 10 — Sora reference-media preflight

Default run is local only:

```bash
uv run python 03-computer-vision/10_reference_media_preflight.py
# Only after review:
uv run python 03-computer-vision/10_reference_media_preflight.py --apply --reference-image <owned-image>
```

**What.** Default run prints reference-media requirements. Only explicit
`--apply` validates one image-to-video input and submits it.

**Why.** Reference media introduces privacy, consent, IP, and source-control
risks before a billable generation call.

**Prereqs and dependencies.** For preflight: none. For apply: requirements
from 05, Pillow, readable owned/consented JPEG/PNG/WebP exactly 1280×720 or
720×1280, and no human faces because current Sora policy rejects them.

**How / architecture.** Local file validation → opt-in `videos.create` with
`input_reference`; output retrieval/deletion is separate API work.

**Code path.** `preflight()` makes no cloud call and does not inspect a file.
`apply()` calls `reference_image()` to check existence/suffix/dimensions, then
opens the file and invokes `openai_client().videos.create`.

**Output.** Preflight instructions or `Submitted reference-media job:
<id> (<status>)`.

**Use.** Explicitly authorized first-frame creative anchors. **Do not use.**
Personal/facial images, unlicensed assets, arbitrary dimensions, or assumed
local output download.

**Best practice.** Record rights/consent basis, source digest, prompt,
requestor, output review, retention, and deletion decision before submit.

**Pitfalls.** Passing preflight does not establish rights/policy acceptance.
`--apply` creates billable preview job; script does not poll/download/delete.

**Takeaway.** Reference media needs governance before model invocation.

### 11 — Sora video remix

```bash
uv run python 03-computer-vision/11_video_remix.py
# Only after review:
uv run python 03-computer-vision/11_video_remix.py --apply --video-id video_<completed-id>
```

**What.** Preflights or submits one narrow lighting remix of completed Sora
video.

**Why.** Remix changes an existing generated-video lineage; it is not a general
local video editor.

**Prereqs and dependencies.** Preflight has none. Apply needs direct Sora
access, a completed authorized Sora video ID beginning `video_`, and rights/
retention review of source/output.

**How / architecture.** Completed Sora ID + one narrow prompt →
`videos.remix` → new asynchronous job.

**Code path.** CLI enforces `--apply` and prefix; `apply()` invokes
`openai_client().videos.remix(video_id, prompt)`.

**Output.** Preflight guidance or `Submitted remix job: <id> (<status>)`.

**Use.** Controlled variation of approved Sora output. **Do not use.**
Arbitrary local video upload, broad unreviewed transformation, or a claim
that remix preserves every source attribute.

**Best practice.** Keep parent/child video IDs, precise change request,
reviewer, output policy decision, and deletion linkage.

**Pitfalls.** A `video_` prefix is shallow validation, not proof ID completed
or caller authorized. Apply does not poll, download, cancel, or delete.

**Takeaway.** Remix is a new async job rooted in Sora video ID, not file edit.

### 12 — Visual provenance policy

```bash
uv run python 03-computer-vision/12_visual_provenance_policy.py
# Only after review:
uv run python 03-computer-vision/12_visual_provenance_policy.py --run --media-url <https-blob-sas-url>
```

**What.** Detects supported C2PA/Microsoft watermark provenance signals in
hosted image, audio, or video and prints bounded marker facts.

**Why.** Origin signals support transparent disclosure and routing decisions;
they do not establish truth or ownership.

**Prereqs and dependencies.** `CONTENT_SAFETY_ENDPOINT`, Content Safety
authorization, supported HTTPS Blob/SAS source, service/region/API-version
availability, and retention review. Lesson uses literal `2026-07-01-preview`;
verify supported API version before use.

**How / architecture.** HTTPS URI → POST provenance detect operation → poll
terminal operation → outcome plus detected marker provider/model.

**Code path.** `media_uri()` checks HTTPS/extension → `submit_detection()`
sends REST request through Content Safety client → max 60 polls at two seconds
→ `run()` prints outcome and result markers.

**Output.** Preflight policy text or `outcome: ...` and zero/more marker lines.

**Use.** Provenance disclosure, policy routing, and audit signal. **Do not use.**
Proof of ownership, creator identity, copyright status, truth,
authenticity, safety, or proof that absent marker means human-made.

**Best practice.** Preserve detector version, source identifier (not SAS),
timestamp, raw outcome, policy action, and accurate user disclosure. Build
appeal/review path for consequential decisions.

**Pitfalls.** No marker is not a negative origin conclusion; unknown or
unsupported formats can fail. This script has bounded polling but no external
job persistence/cancel/retry strategy.

**Takeaway.** Provenance is evidence signal, never a universal trust verdict.

### 13 — OCR image-injection safety

```bash
uv run python 03-computer-vision/13_ocr_image_injection_safety.py
# Only after review:
uv run python 03-computer-vision/13_ocr_image_injection_safety.py --run --ocr-file <utf8-file>
```

**What.** Treats existing OCR text as untrusted document content and submits
it to Content Safety Prompt Shields only on opt-in run.

**Why.** Image text can contain indirect instructions intended to redirect
model behavior; OCR does not turn that text into trusted user intent.

**Prereqs and dependencies.** Preflight has none. Apply needs
`CONTENT_SAFETY_ENDPOINT`, role/access, local UTF-8 OCR extract, and an
upstream OCR stage (not implemented here).

**How / architecture.**

```text
image → OCR (outside lesson) → untrusted document text → Prompt Shields
     → policy block/review/continue → model receives data only when allowed
```

**Code path.** Reads file → `scan_ocr_text()` calls `shield_prompt()` →
helper enforces max five documents/10,000 aggregate characters and 10,000
user-prompt characters → prints `documentsAnalysis[0].attackDetected`.

**Output.** Preflight guidance or `document attack detected: True|False` and
next policy action.

**Use.** Defense-in-depth before document/OCR content joins model context.
**Do not use.** OCR itself, proof content benign, or a replacement for
authorization/tool-output validation.

**Best practice.** Delimit OCR as data, bind model instructions to trusted
application policy, validate tool calls independently, minimize/sanitize
downstream context, and log redacted security events.

**Pitfalls.** No detection is not approval; the lesson scans one text file and
does not call OCR/model. Never paste OCR output into system prompt.

**Takeaway.** Text extracted from pixels remains untrusted external content.

### 14 — CU Blob, SAS, and identity preflight

```bash
uv run python 03-computer-vision/14_cu_blob_preflight.py
uv run python 03-computer-vision/14_cu_blob_preflight.py --source-url <https-blob-sas-url>
```

**What.** Locally reports CU/storage configuration and safe source metadata
without printing SAS query values.

**Why.** CU retrieves media server-side; Blob access, delegated SAS, DNS, and
identity are separate concerns that should fail before an expensive analyzer
request.

**Prereqs and dependencies.** Optional `STORAGE_ACCOUNT`, `STORAGE_CONTAINER`,
`CU_ENDPOINT`, and a Blob HTTPS URL. No Azure call occurs.

**How / architecture.** URL parser extracts host/container/blob path, reads
SAS query only to identify missing signature/read/expiry, then discards it.

**Code path.** `preflight()` reads settings and `source_metadata()`; with a
URL, `validate_source_url()` warns about non-HTTPS/non-Blob/no `sig`, no read
`sp=r`, or no expiry; stdout omits query string.

**Output.** Configuration status, SAS-free source path, warnings, and role/
network handoff guidance.

**Use.** Pre-submit operator check and training on SAS boundaries. **Do not use.**
SAS creation, Blob upload, cloud reachability proof, network-policy
enforcement, or a security approval.

**Best practice.** Application upload identity: `Storage Blob Data Contributor`
at narrow container scope; runtime read identity: `Storage Blob Data Reader`
where needed. Prefer user-delegation SAS, one blob, read only, HTTPS, minimal
expiry, and no list/write/delete permissions.

**Pitfalls.** A local parser cannot verify signature validity, expiry time,
RBAC, service access, firewall, private DNS, or CU egress. Avoid SAS in shell
history and logs.

**Takeaway.** SAS is delegated access; managed identity for application storage
does not automatically make CU able to fetch private Blob URL.

### 15 — Bounded CU visual handoff

```bash
uv run python 03-computer-vision/15_cu_visual_handoff.py --source-url <https-blob-sas-url>
# Only after review:
uv run python 03-computer-vision/15_cu_visual_handoff.py --apply --source-url <https-blob-sas-url>
```

**What.** Selects image/video prebuilt CU analyzer by extension and emits a
bounded, SAS-free normalized handoff payload.

**Why.** Passing opaque analyzer JSON downstream spreads credentials, payload
size, schema drift, and prompt-injection risk.

**Prereqs and dependencies.** `CU_ENDPOINT`, supported CU version/role,
approved reachable source URL, and lessons 14 plus either 08 or 09 concepts.
Supported local extension lists are script policy, not service capability
guarantee.

**How / architecture.**

```text
Blob SAS URL → extension selects analyzer → CU async result
             → normalize: source metadata + ≤10 warnings + ≤20 segments
             → downstream policy/retrieval/review boundary
```

**Code path.** `select_analyzer()` chooses `prebuilt-imageSearch` or
`prebuilt-videoSearch`; `production_handoff()` requires HTTPS and calls CU;
`normalize_result()` strips query credentials, redacts credential-like text,
limits summary to 400 characters, warnings to 10, segments to 20.

**Output.** Preflight reports chosen analyzer/bounds; apply prints formatted
JSON with status, analyzer, source metadata, warnings, segments, and
`segments_truncated`.

**Use.** A deliberately narrow integration boundary after policy/routing
review. **Do not use.** Complete CU archive, raw result forwarding,
authorization system, search index, or replacement for source validation.

**Best practice.** Schema-version this normalized payload, preserve analyzer/
API version and provenance, authorize downstream reader, assess summaries
against source, and quarantine/review warnings before agent retrieval.

**Pitfalls.** File extension can lie; result text remains untrusted; bounded
output can omit relevant segment; secret regex is defense-in-depth not a reason
to log raw data. Apply can incur service cost and does not persist operation
state. Current shared CU request headers are a redacted placeholder, so a real
token is required before this path can complete a live request.

**Takeaway.** Normalize and bound analyzer output before another AI or service
consumes it.

## Production workflow

### Build and release flow

```text
Requirements/data classification
  → choose region, service, deployment, quota, cost ceiling
  → IaC: resource + RBAC + network + diagnostics
  → private DNS/connectivity test with workload identity
  → media intake: validate type/size/authorization; malware scan where required
  → source store: private Blob + user-delegation read SAS or approved access path
  → safety/provenance/prompt-injection controls by risk
  → model/generation/CU job with idempotency, deadline, and redacted telemetry
  → output validation + human/policy decision
  → publish only approved output; retention/deletion and incident workflow
  → evaluate, monitor cost/quota/quality/safety, then release or rollback
```

### Identity, RBAC, secrets, and network

| Concern | Decision |
|---|---|
| Human local access | Azure CLI-backed `DefaultAzureCredential`; least role at resource/project scope |
| Workload access | Managed identity/workload identity; do not ship client secret/account key |
| Azure OpenAI inference | Grant only needed Cognitive Services/OpenAI data-plane role to runtime identity; verify exact role against resource/service documentation |
| Foundry project calls | Grant project role that permits requested agent/model action; control-plane contributor is not inference access |
| Content Safety/CU | Grant service-specific data-plane role; test with runtime identity, not administrator |
| Blob upload | `Storage Blob Data Contributor` at container scope when application needs write |
| Blob read | `Storage Blob Data Reader` only where application needs direct read; CU normally receives scoped read SAS |
| SAS | Prefer user-delegation SAS, HTTPS-only, one blob, read-only, short expiry; redact `sig`, `se`, `sp`, and full query |
| Secrets | Key Vault references for unavoidable secrets/certificates; RBAC, purge protection/retention policy, rotation, and no secret telemetry |
| Public network | Disable when policy requires; validate each service’s private endpoint support and DNS zone requirements |
| Private endpoint | Plan separate endpoint/DNS/egress test for Storage, Azure OpenAI/Foundry, Content Safety, CU, Key Vault, and Monitor. Private endpoint alone does not grant RBAC or make service-to-service URL fetch work |

Use portal for discovery/one-off troubleshooting, CLI for repeatable inspection,
and IaC for desired state. Never make portal clicks the only record of region,
role, network, diagnostic, or deployment decision.

### Observability, quota, reliability, and cost

Emit structured, redacted telemetry: correlation ID, environment, service,
region, deployment/analyzer/version, operation/job ID, status, latency,
retry count, response class, content-policy action, cost/usage estimate, and
SAS-free source identifier. Do **not** emit request image/video bytes, OCR
text, prompt, generated media, full SAS, token, connection string, or customer
identifiers unless approved secure telemetry policy says otherwise.

Alert on 401/403/404 spikes, 429s, job failures/timeouts, CU terminal failure,
private DNS/connectivity failure, content-policy block/review volume, dropped
segments, latency, spend/budget, and storage growth. Monitor Azure resource
metrics/diagnostic logs with Azure Monitor/Application Insights; service
telemetry does not replace application acceptance metrics.

For mutable work: idempotency key, bounded retry only for classified transient
errors, exponential backoff/jitter, timeout, cancellation/reconciliation, and
dead-letter/manual-review path. Never retry 400/401/403/404 blindly or
re-submit video job after unknown timeout without checking existing job ID.

## Troubleshooting

| Symptom | Likely cause | First action |
|---|---|---|
| 401/403 | Wrong endpoint/scope/tenant/identity/role | Confirm endpoint surface, `az account show`, workload identity, and resource-scoped data-plane role |
| 404 model/deployment | Model-family label supplied instead of deployment alias, unsupported region/version | Check deployed alias/capability in Foundry portal |
| Image request rejected | Deployment no visual capability, malformed/oversized input, policy filter | Check model/input contract and service error; do not bypass safety policy |
| 429/slow generation | Quota/capacity/quality-size pressure | Respect retry-after, back off, reduce only acceptable quality/size, examine quota/budget |
| Edit fails before cloud call | Invalid/unreadable source or invalid mask | Read helper error; use supported source, same-size PNG alpha mask with transparent pixels |
| Sora failure/timeout | Preview access/region/policy/quota/request issue | Inspect returned `failure_reason`; timeout leaves remote job active, so reconcile job ID |
| CU rejects/no result | Missing `SAMPLE_*_URL`, expired SAS, service cannot reach URL, analyzer/version/input mismatch | Run 14, test approved connectivity/DNS, validate resource-supported API/analyzer and inspect terminal diagnostic |
| CU poll fails host validation | Unexpected `Operation-Location` host | Treat as security failure; compare CU endpoint configuration, do not follow arbitrary URL |
| Provenance no marker | Unsupported/no detectable signal | Do not infer human origin/ownership; record result and apply policy |
| Prompt Shields false/negative result | Detection is one signal, context/change attack | Keep OCR as data, layer authorization/validation/review, evaluate on representative attacks |
| Private endpoint works locally but CU fetch fails | DNS/egress/service-fetch path differs from app path | Test CU source retrieval design explicitly; private networking is per service/path |

## AI-103 traps and interview prompts

| Trap | Correct answer |
|---|---|
| “Data URL and Blob SAS are equivalent.” | Data URL embeds bytes in request; SAS URL delegates server-side source retrieval. |
| “Project endpoint can call direct OpenAI client.” | Endpoint/SDK/auth surface must match; project and OpenAI endpoints differ. |
| “Managed identity removes RBAC work.” | It removes stored credential need; role/scope/network still require design and verification. |
| “Content Safety severity approves content.” | It is one classifier signal; application policy decides block/escalate/allow. |
| “Image severity uses all values 0–7.” | Direct image analysis returns trimmed 0, 2, 4, 6 values. |
| “Mask guarantees preservation outside transparent pixels.” | It bounds edit intent; generation remains nondeterministic. |
| “Sora returns video synchronously.” | Submit job, poll terminal state, retrieve generation; manage timeout/cancel/reconcile. |
| “Reference preflight establishes rights.” | Local type/dimension validation is not consent, ownership, policy, or model acceptance. |
| “No provenance marker proves human-made.” | Absence is not proof of origin, safety, truth, or ownership. |
| “CU URL input uploads media.” | CU fetches existing reachable URL; scripts do not upload or index. |
| “`prebuilt-video` equals `prebuilt-videoSearch`.” | Base analyzer differs from retrieval-oriented analyzer used in lesson 09. |
| “Generated alt text solves accessibility.” | It is a contextual draft; equivalent information, human review, and user testing matter. |

Interview prompts:

1. **Design private video analysis.** Explain private Blob, narrow upload
   identity, short read SAS/service access decision, CU endpoint/network/DNS,
   analyzer polling, normalized output, monitoring, retention, and rollback.
2. **Choose moderation controls.** Explain direct pre-ingestion signal,
   model/deployment safety, policy thresholds, human review, audit minimization,
   and why neither is a universal approval.
3. **Recover Sora timeout.** Persist job/idempotency identity, reconcile remote
   state before retry, show user status, cancel/cleanup where policy allows,
   and preserve only needed lineage.
4. **Protect OCR RAG.** Keep OCR as data, scan indirect attacks, delimit input,
   validate tools/output, least privilege retrieval, and evaluate bypass cases.

## Official references

Use current service documentation to validate preview status, region, API
version, quota, role names, and model support before deployment:

- [Azure OpenAI image generation](https://learn.microsoft.com/azure/foundry/openai/how-to/dall-e)
- [Sora 2 video generation](https://learn.microsoft.com/azure/foundry/openai/concepts/video-generation)
- [Vision-enabled image input](https://learn.microsoft.com/azure/foundry/openai/how-to/gpt-with-vision)
- [Azure AI Content Safety overview](https://learn.microsoft.com/azure/ai-services/content-safety/overview)
- [Content Safety image quickstart](https://learn.microsoft.com/azure/ai-services/content-safety/quickstart-image)
- [Content Safety harm categories](https://learn.microsoft.com/azure/ai-services/content-safety/concepts/harm-categories)
- [Provenance detection](https://learn.microsoft.com/azure/ai-services/content-safety/concepts/provenance-detection)
- [Prompt Shields](https://learn.microsoft.com/azure/ai-services/content-safety/concepts/jailbreak-detection)
- [Content Understanding overview](https://learn.microsoft.com/azure/ai-services/content-understanding/overview)
- [Content Understanding REST quickstart](https://learn.microsoft.com/azure/ai-services/content-understanding/quickstart/use-rest-api)
- [Content Understanding prebuilt analyzers](https://learn.microsoft.com/azure/ai-services/content-understanding/concepts/prebuilt-analyzers)
- [Content Understanding limits](https://learn.microsoft.com/azure/ai-services/content-understanding/service-limits)
- [Content Understanding regions](https://learn.microsoft.com/azure/ai-services/content-understanding/language-region-support)
- [Azure Storage SAS overview](https://learn.microsoft.com/azure/storage/common/storage-sas-overview)
- [Assign Azure roles for Blob data access](https://learn.microsoft.com/azure/storage/blobs/assign-azure-role-data-access)
- [Managed identities](https://learn.microsoft.com/entra/identity/managed-identities-azure-resources/overview)
- [Azure RBAC overview](https://learn.microsoft.com/azure/role-based-access-control/overview)
- [Azure Private Endpoint](https://learn.microsoft.com/azure/private-link/private-endpoint-overview)
- [Application Insights overview](https://learn.microsoft.com/azure/azure-monitor/app/app-insights-overview)

Repository snapshots:

- [Image generation local reference](../.context/azure-ai-docs/articles/foundry/openai/how-to/dall-e.md)
- [Sora local reference](../.context/azure-ai-docs/articles/foundry/openai/concepts/video-generation.md)
- [Content Safety image local reference](../.context/azure-ai-docs/articles/ai-services/content-safety/quickstart-image.md)
- [Content Understanding REST local reference](../.context/azure-ai-docs/articles/ai-services/content-understanding/quickstart/use-rest-api.md)
