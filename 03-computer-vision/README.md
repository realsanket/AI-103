---
ai-usage: ai-assisted
---

# Domain 3: Computer vision

> Teaching guide and runnable labs for visual understanding, image generation
> and editing, video generation, image moderation, accessibility descriptions,
> and Content Understanding. Run commands from repository root:
> `uv run python 03-computer-vision/<lesson>.py`.
>
> A lesson demonstrates one live service path. It is not a production media
> pipeline, and a successful response is not proof that an image, description,
> or video is correct, accessible, safe for a particular audience, or licensed
> for a particular use.

## What this domain teaches

Computer vision work begins with a question, not a model:

```text
Need an open-ended answer about an image?
  → Multimodal Responses API.

Need a new image or a prompt/mask-directed change?
  → Azure OpenAI image generation API.

Need a generated video?
  → Sora 2 asynchronous video job.

Need harm-category scores before another system receives an image?
  → Azure AI Content Safety direct image analysis.

Need an accessibility description?
  → Generate a draft, then validate it with people and context.

Need repeatable searchable image/video analysis?
  → Azure Content Understanding prebuilt analyzer.
```

The services overlap, but their contracts differ. A multimodal model produces
free-form language. Image generation produces pixels. Content Safety returns
harm classifications. Content Understanding returns an asynchronous,
analyzer-shaped result containing fields and Markdown. Do not substitute one
for another without defining acceptance criteria.

## Mental model

### Three visual workflows

| Workflow | Input | Output | Best starting use | This domain's evidence |
|---|---|---|---|---|
| **Multimodal understanding** | Text plus one or more images | Model-generated text | Questions, summaries, captions, and assisted analysis | Lessons 01, 06, and 07 |
| **Generative media** | Prompt, optionally an image/mask for image editing | Generated image or video bytes | Creative assets and controlled experiments | Lessons 02–05 |
| **Analyzer workflow** | Service-reachable content URL | Structured asynchronous analyzer result | Search/RAG ingestion and repeatable content extraction | Lessons 08–09 |

### Service and endpoint contracts

Endpoint shape is part of API contract. Do not send a client to a different
endpoint because resource names look similar.

| Surface | Setting used by code | Endpoint shape | Lessons | Authentication path |
|---|---|---|---|---|
| Direct Azure OpenAI-compatible API | `AZURE_OPENAI_ENDPOINT` | `https://<resource>.openai.azure.com` | 01–05, 07 | `DefaultAzureCredential`, token scope `https://ai.azure.com/.default` |
| Foundry project API | `PROJECT_ENDPOINT` | `https://<resource>.services.ai.azure.com/api/projects/<project-name>` | 06 model-call path | `AIProjectClient` with `DefaultAzureCredential` |
| Azure AI Content Safety | `CONTENT_SAFETY_ENDPOINT` | `https://<resource>.cognitiveservices.azure.com` | 06 direct moderation path | Content Safety SDK with `DefaultAzureCredential` |
| Azure Content Understanding in Foundry Tools | `CU_ENDPOINT` | `https://<resource>.services.ai.azure.com` | 08–09 | REST bearer token scope `https://cognitiveservices.azure.com/.default` |

`FOUNDRY_ENDPOINT` is available in shared settings but no Domain 3 lesson
calls it directly. `PROJECT_ENDPOINT` does not replace
`AZURE_OPENAI_ENDPOINT`, and the direct OpenAI client cannot derive a
deployment or authorization from project URL.

Roles must authorize the selected data-plane surface. A credential that
obtains a token is not proof that it can call every endpoint. In particular,
the local Sora 2 REST quickstart names **Cognitive Services User** as its
keyless prerequisite, and the image-edit troubleshooting guidance names
**Cognitive Services OpenAI User** for a managed identity. Validate actual
role assignments, resource, region, and deployment access before debugging
application code.

### Glossary

| Term | Study definition |
|---|---|
| **Multimodal model** | A model that accepts more than one input modality, such as text and images, and returns model output. |
| **Responses API** | Azure OpenAI-compatible request surface used here for `input_text` and `input_image` content. |
| **Data URL** | Inline URI containing MIME type and base64 bytes. Lessons 01, 06, and 07 use `data:image/png;base64,...` for local images. |
| **Deployment name** | Configured name passed as `model=`. It is not necessarily same as model-family name. |
| **Image generation** | Creating image pixels from prompt and generation options. |
| **Image edit / inpainting** | Creating a changed image from a source image, prompt, and optional mask. It is generative, not deterministic pixel editing. |
| **Mask** | PNG same size as input image. Fully transparent pixels (alpha 0) identify editable area. |
| **Guardrail / content filter** | Service or deployment safety behavior. It differs from calling Content Safety yourself and implementing a business decision. |
| **Severity** | Harm-category score. Direct image moderation returns trimmed image severities `0`, `2`, `4`, or `6`; it does not return every integer from 0–7. |
| **Sora 2 job** | Long-running video generation request with a job ID, status polling, and a generated-video download step. |
| **Analyzer** | Content Understanding configuration that produces structured result data from content. |
| **Operation-Location** | URL returned by asynchronous Content Understanding submission. Poll it until terminal status. |
| **Blob SAS URL** | HTTPS Blob URL with scoped, time-limited delegated access. It lets Content Understanding fetch input server-side. |

## Before running a lesson

### Install and authenticate

```bash
uv sync
cp .env.example .env
az login
```

Use a nonproduction resource and non-sensitive sample content. All lessons
make remote requests except for early failures caused by missing configuration.
Do not put API keys, connection strings, customer media, or Blob SAS URLs in
source control, terminal recordings, or telemetry without an approved data
handling plan.

`DefaultAzureCredential` commonly uses Azure CLI credentials after `az login`
on a workstation. In hosted workloads it can use managed identity or workload
identity. Confirm which identity is effective when a request fails with 401 or
403.

### Configure only what each path needs

Use deployment names, not a catalog model label unless they deliberately match.
The shipped defaults are examples; they do not create deployments.

```dotenv
# Direct multimodal and image-generation API
AZURE_OPENAI_ENDPOINT=https://<resource>.openai.azure.com
DEFAULT_MODEL=<multimodal-deployment>
IMAGE_MODEL=<gpt-image-series-deployment>
VIDEO_MODEL=<sora-2-deployment>

# Lesson 06 project-client model call
PROJECT_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<project-name>

# Lesson 06 direct Content Safety call
CONTENT_SAFETY_ENDPOINT=https://<resource>.cognitiveservices.azure.com

# Lessons 08–09 Content Understanding REST wrapper
CU_ENDPOINT=https://<resource>.services.ai.azure.com
CU_API_VERSION=<supported-version-for-your-resource>

# Lessons 08–09 URL inputs; not currently listed in .env.example
SAMPLE_IMAGE_URL=<https-image-url-or-read-only-Blob-SAS-URL>
SAMPLE_VIDEO_URL=<https-video-url-or-read-only-Blob-SAS-URL>
```

The code default for `CU_API_VERSION` is `2025-11-15-preview`, while local
Content Understanding REST quickstart examples use `2025-11-01`. Set a version
your resource supports; do not assume a preview version is accepted because a
local default names it.

### Prepare inputs

| Lesson(s) | Input preparation | What code actually sends |
|---|---|---|
| 01, 07 | Shipped PNGs under `_shared/sample_data/images/` | Local bytes as base64 PNG data URLs. |
| 03–04 | `product_photo.png`; 04 also uses `mask.png` | Open file handles passed to `images.edit`. |
| 06 | Shipped `support.png` | Local bytes to Content Safety and a base64 PNG to project-scoped Responses. |
| 08 | Upload permitted image yourself, then set reachable HTTPS URL | One JSON `inputs` item with `url`; no upload. |
| 09 | Upload permitted video yourself, then set reachable HTTPS URL | One JSON `inputs` item with `url`; no upload. |

For Content Understanding URL inputs, `file://` is invalid because the service
fetches content from its own infrastructure. A least-privilege, read-only,
HTTPS Blob SAS scoped to one blob is a practical lab input. Make its expiry
long enough for submission and polling, but no longer. Never log the complete
SAS query string. `STORAGE_ACCOUNT`, `STORAGE_CONTAINER`, and
`STORAGE_CONNECTION_STRING` are not used by Domain 3 to upload files or mint
SAS tokens.

Content Understanding image URL inputs support `.jpg`, `.jpeg`, `.jpe`,
`.png`, `.bmp`, `.heif`, and `.heic`, with a minimum 50 × 50 and maximum
10,000 × 10,000 pixels. For URL-reference video analysis, local service limits
document up to 4 GB and two hours; supported formats include MP4, M4V, FLV,
WMV/ASF, AVI, MKV, and MOV, with 320 × 240 through 1920 × 1080 resolution.
The lesson uses MP4 but does not validate format, duration, resolution, or
SAS reachability before submission.

### Cost, quota, and side effects

| Lesson(s) | Request and side effect | Cost or operational concern |
|---|---|---|
| 01, 06–07 | Multimodal inference | Image input and generated text consume model usage. |
| 02–04 | Image generation/edit | Writes a fixed PNG under `_shared/sample_data/generated/`; output overwrites prior lab result. |
| 05 | Sora 2 generation job | Billed per generated second; can run for minutes and writes/overwrites `northwind_video.mp4`. |
| 06 | Direct image moderation | Consumes Content Safety request capacity. |
| 08–09 | Content Understanding analysis | Consumes analyzer quota and polls until a terminal result. |

Local image-generation docs state a typical 10–30 second generation time and
default quota of five images per minute per image deployment. Lower image
quality can reduce latency. Sora 2 is preview and video processing commonly
takes 1–5 minutes. Content Understanding standard quota lists 1,000
pages/images, four hours of audio/video, and 3,000 operations per minute.
Actual availability, quotas, and billing remain model, subscription, and
region specific.

### Safe learning order

1. Run 01 and 07 with shipped images to learn multimodal input and
   accessibility-draft output.
1. Run 06 to compare explicit moderation with deployment guardrail metadata.
1. Run 02, 03, and 04 after verifying image deployment access.
1. Run 05 only after confirming Sora 2 preview availability and a supported
   Azure OpenAI region.
1. Create read-only Blob SAS URLs, set both `SAMPLE_*_URL` values, then run
   08 and 09.

## Decision tables

### Choose service by required result

| Requirement | Choose | Why | Do not assume |
|---|---|---|---|
| Explain chart or screenshot in context of a question | Multimodal Responses | Flexible language answer using text plus image | Stable schema, coordinates, object boxes, or verified OCR. |
| Produce marketing concept image | Image generation | Creates pixels from prompt | Correct brand, legal clearance, factual accuracy, or repeatability. |
| Change one image area | Image edit plus transparent PNG mask | Mask bounds requested editable region | Pixel-perfect preservation outside mask. Inspect output. |
| Score image for four harm categories | Direct Content Safety image analysis | Explicit category/severity results before downstream call | That a score alone implements product policy or approves content. |
| Generate short video | Sora 2 job | Asynchronous text-to-video path | It is synchronous, editable by this lesson, or uses reference media. |
| Extract searchable image/video representation | Content Understanding `prebuilt-*Search` | Analyzer result includes Markdown/fields and video segments | A universal fixed response schema or automatic retention/indexing. |
| Locate objects, regions, brands, or watermarks | Different supported capability and explicit evaluation | Needs task-specific output contract | Any Domain 3 lesson returns object regions, brands, or watermarks. |

### Select image-input transport

| Input path | Used here? | Benefit | Boundary |
|---|---:|---|---|
| Base64 data URL | Yes: 01, 06, 07 | Sends local image inline; no public host needed. | Payload grows with image size; use correct MIME type. |
| Local multipart file | Yes: 03, 04 | Fits image-edit API file input. | Image and mask requirements still apply. |
| HTTPS/Blob SAS URL | Yes: 08, 09 | Service retrieves large external input asynchronously. | URL must remain reachable to service; it exposes delegated access. |
| Service-side upload/index | No | Can be appropriate for product workflow. | No code in this domain uploads, indexes, or retains input. |

### Choose moderation control

| Need | Starting design | Lesson evidence | App responsibility |
|---|---|---|---|
| Inspect image before model sees it | Direct Content Safety call at ingestion boundary | 06 `_direct_content_safety` | Set thresholds, block/escalate outcome, record minimal audit data. |
| Observe supported deployment safety behavior | Inspect model response/filter result | 06 `_guardrail_through_model` | Handle blocked/empty/error responses and do not depend on optional metadata shape. |
| Enforce business-specific policy | Explicit application policy after safety signals | Not implemented | Define decision table, human review, appeals, retention, and monitoring. |

## Lesson map

| # | Lesson | Runnable objective | Important boundary |
|---:|---|---|---|
| 01 | [Multimodal understanding](01_multimodal_understanding.py) | Summarize local chart image through Responses API. | Free-form summary, not structured chart extraction. |
| 02 | [Image generation](02_image_generation.py) | Generate one PNG from training-image prompt. | Generated asset needs review. |
| 03 | [Prompt image edit](03_image_prompt_edit.py) | Prompt-directed source-image edit. | No mask and no preservation guarantee. |
| 04 | [Masked image edit](04_image_masked_edit.py) | Add content in transparent mask area. | Mask bounds edit request; output still needs inspection. |
| 05 | [Video generation](05_video_generation.py) | Submit, poll, and download a Sora 2 text-to-video job. | No reference-media, remix, cancel, retry, or cleanup path. |
| 06 | [Image moderation](06_image_moderation.py) | Compare direct Content Safety and model guardrail signals. | Does not implement a moderation decision. |
| 07 | [Alt text and captions](07_alt_text_captions.py) | Draft short/extended and multi-image descriptions. | Prompt asks for format; code does not validate it. |
| 08 | [Content Understanding image](08_content_understanding_image.py) | Analyze reachable image URL with `prebuilt-imageSearch`. | Prints first content only. |
| 09 | [Content Understanding video](09_video_analysis.py) | Analyze reachable video URL with `prebuilt-videoSearch`. | Prints segment times and summaries only. |

## Lessons 01–04: understand, generate, and edit images

### 01 — Multimodal understanding

**Question answered:** How does a local PNG become multimodal model input?

Run:

```bash
uv run python 03-computer-vision/01_multimodal_understanding.py
```

The lesson reads `sales_data.png`, base64-encodes its bytes, and calls
`client.responses.create` using `DEFAULT_MODEL`. Its user message contains:

```python
{"type": "input_text", "text": "Summarize the content in the attached image."}
{"type": "input_image", "image_url": "data:image/png;base64,..."}
```

**Expected output:** A text summary printed from `r.output_text`. Wording,
length, and factual detail vary by model and image interpretation.

**Study points**

- Text establishes task and visual input supplies evidence. Ask narrow,
  testable questions when accuracy matters: for example, “List chart title,
  x-axis labels, and all displayed values; say `unreadable` rather than
  guessing.”
- Local Foundry vision guidance documents base64 data URLs as a valid local
  image path. It also documents image limits and model support separately;
  validate selected deployment rather than assuming every text deployment is
  multimodal.
- This lesson does not request a structured response format, detail level,
  output token limit, citations, confidence, OCR coordinates, or object
  regions. It has no image-prompt-injection defense path. Treat image text and
  embedded instructions as untrusted data in a real workflow.

### 02 — Image generation

**Question answered:** How does a prompt become a saved PNG?

Run:

```bash
uv run python 03-computer-vision/02_image_generation.py
```

The lesson calls `images.generate` with `IMAGE_MODEL`, one training-image
prompt, `n=1`, `size="1024x1024"`, `quality="medium"`, and
`output_format="png"`. It base64-decodes `r.data[0].b64_json` into:

```text
_shared/sample_data/generated/training_image.png
```

**Expected output:**

```text
saved: .../_shared/sample_data/generated/training_image.png
```

Open the PNG. Success means bytes were written, not that the result meets
visual, brand, accessibility, policy, or factual requirements.

**Study points**

- `IMAGE_MODEL` must name deployed GPT-image series model. The local docs
  support `1024x1024` for GPT-image-1 series and document base64 image output.
- Prompt includes subject, context, style, and audience. Iteration means
  changing one observable requirement at a time, saving prompt/version/output
  metadata, and reviewing a representative set.
- Code requests one final result. It does not stream partial images, set a
  user identifier, configure transparency/compression, select arbitrary GPT-
  image-2 dimensions, or implement retries.
- Built-in input/output moderation and abuse monitoring do not remove need for
  product policy. The lesson does not configure custom content-filter policy,
  watermark handling, brand verification, or a human approval gate.

### 03 — Prompt-driven image edit

**Question answered:** What does prompt-only image editing demonstrate?

Run:

```bash
uv run python 03-computer-vision/03_image_prompt_edit.py
```

The lesson opens `product_photo.png`, passes it as `image` to `images.edit`,
and asks for cleaner lighting/background while preserving the main product.
It saves:

```text
_shared/sample_data/generated/edited_product_photo.png
```

**Expected output:** One `saved:` line and a generated PNG. Compare source and
output manually, especially product shape, text, logos, edges, lighting, and
unrequested changes.

**Limitations**

- There is no mask. The prompt requests preservation, but code does not bound
  an editable region or use `input_fidelity`.
- Image editing is a generative transformation. “Keep unchanged” is intent,
  not a pixel-preservation contract.
- Local image-edit docs require input image under 50 MB and PNG or JPG. The
  lesson assumes its shipped PNG meets that contract; it does not validate
  arbitrary replacement input.
- It does not demonstrate variations, multiple source images, object-region
  detection, brand protection, watermark detection, or an automated quality
  comparison.

### 04 — Masked image edit

**Question answered:** How does a transparent mask constrain intended editing?

Run:

```bash
uv run python 03-computer-vision/04_image_masked_edit.py
```

The lesson sends source `product_photo.png`, `mask.png`, and prompt to
`images.edit`, then saves:

```text
_shared/sample_data/generated/masked_edit_product_photo.png
```

**Expected output:** One `saved:` line and a PNG in the generated folder.
Inspect source, mask, and output together.

**Mask behavior**

| Mask pixels | Meaning for edit request |
|---|---|
| Fully transparent (alpha = 0) | Editable area. |
| Nontransparent | Area intended to remain outside edit. |

The local image-edit guidance requires a PNG mask with same dimensions as
input image. The script passes shipped files but performs no dimension, PNG,
alpha-channel, or size validation. It also does not prove exact preservation
outside the mask. Use output review and image-difference acceptance tests if
that matters.

## Lesson 05: Sora 2 video generation

### Asynchronous job lifecycle

**Question answered:** Why is video generation not one synchronous request?

Run only after checking supported region, deployment, access, quota, and
preview suitability:

```bash
uv run python 03-computer-vision/05_video_generation.py
```

The lesson uses direct REST over `AZURE_OPENAI_ENDPOINT`, not
`FOUNDRY_ENDPOINT` or `PROJECT_ENDPOINT`:

```text
POST {AZURE_OPENAI_ENDPOINT}/openai/v1/video/generations/jobs?api-version=preview
GET  {AZURE_OPENAI_ENDPOINT}/openai/v1/video/generations/jobs/{job-id}?api-version=preview
GET  {AZURE_OPENAI_ENDPOINT}/openai/v1/video/generations/{generation-id}/content/video?api-version=preview
```

It requests a text-only 1280 × 720, five-second render:

```text
submit → receive job ID → poll every five seconds → first generation → download MP4
```

The code treats `succeeded`/`completed`, `failed`, and `cancelled` as terminal
states. On success, it downloads first `generations` item to:

```text
_shared/sample_data/generated/northwind_video.mp4
```

**Expected output:**

```text
submitted job: <job-id>
  status: <queued-or-processing-status>
  ...
saved: .../_shared/sample_data/generated/northwind_video.mp4
```

Sora 2 documentation lists 1–20 second durations and supported dimensions
including 1280 × 720, so lesson request is within documented shape. The
service supports up to two concurrent creation jobs and retains jobs up to 24
hours. Store job IDs securely enough to investigate failures, but avoid
treating a job ID as permanent asset storage.

### What this lesson does not cover

Sora 2 documentation describes image-to-video, generated-video-to-video,
reference inputs, and remix. This code implements **text-to-video only**. It
does not upload or reference images/videos, send multipart `inpaint_items`,
use `input_reference`, remix an existing video, edit a video, request
variants, cancel a job, resume after process restart, delete generated media,
or inspect generated audio.

Sora 2 is preview. Local guidance documents output audio support, possible
quality problems with physics, spatial reasoning, and time-based sequencing,
and built-in responsible-AI controls. It also says Sora 2 blocks IP and
photorealistic content, and documents rejection of input images containing
human faces. The lesson does not configure, test, customize, or bypass those
policies; plan for policy failures and inspect `failure_reason` from failed
jobs.

### Production lifecycle additions

For a production implementation, add bounded polling deadline, jitter/backoff,
status persistence, cancellation/cleanup policy, job-owner identity, explicit
failure-reason handling, download integrity checks, output retention/deletion,
and review before distribution. Those additions are recommendations, not
claimed behavior of `05_video_generation.py`.

## Lesson 06: image moderation and guardrails

**Question answered:** What is difference between explicit moderation and
model-deployment safety signals?

Run:

```bash
uv run python 03-computer-vision/06_image_moderation.py
```

The lesson has two independent calls:

1. **Direct Content Safety** reads `support.png` and calls
   `ContentSafetyClient.analyze_image(AnalyzeImageOptions(...))`. It prints
   each returned `Hate`, `Sexual`, `Violence`, and `SelfHarm` category and
   severity.
1. **Multimodal project call** base64-encodes same image, sends it with
   support instructions through project client’s OpenAI client, prints
   `output_text`, then prints optional `content_filters` metadata if exposed
   through current client response object.

**Expected output:**

```text
=== Flow 1: Content Safety API (0-7 severity) ===
  Hate         severity=<0|2|4|6>
  ...
=== Flow 2: Multimodal call (ephemeral agent, guardrail inspection) ===
<support answer or service safety outcome>
```

The heading’s “0-7” is imprecise for direct image analysis: local Content
Safety documentation says image classifier returns trimmed severities `0`, `2`,
`4`, or `6`. A multimodal image-with-text classifier can use full 0–7 scale,
but this script’s second path is a model response with optional filter
metadata, not a direct Content Safety multimodal analysis request.

**Study points**

- Direct moderation gives application a deliberate pre-processing decision
  point. It does not automatically block anything in code.
- Deployment guardrails can filter or alter model behavior. Do not rely on
  `model_extra.content_filters` always being present, stable, or sufficient as
  an audit record.
- Harm categories are multi-label. One item can have more than one category.
- Severity is classifier output, not legal, medical, or universal suitability
  decision. Choose action thresholds by category, intended audience, context,
  locale, escalation path, and evaluation data.
- This lab does not test custom categories, blocklists, prompt shields,
  provenance, threshold configuration, human review, data retention, or a
  user-facing appeal flow.

## Lesson 07: accessible alt text and captions

**Question answered:** How can vision output create an accessibility draft?

Run:

```bash
uv run python 03-computer-vision/07_alt_text_captions.py
```

The first call asks `DEFAULT_MODEL` for two labeled paragraphs from
`sales_data.png`:

```text
ALT: one sentence, <125 chars, screen-reader friendly.
DESCRIPTION: 2-4 sentences, describe visual details useful for a low-vision user.
```

The second call sends `sales_data.png` and `support_ticket_portal.png` in one
request and asks for one narrative caption. Both calls use base64 data URLs.

**Expected output:**

```text
=== Alt-text ===
ALT: ...
DESCRIPTION: ...

=== Multi-image caption ===
...
```

### Accessibility rules for this lab

- Alt text communicates image purpose in its surrounding context. It should not
  mechanically list every visible detail.
- Extended description can communicate data, relationships, or controls that
  do not fit concise alt text.
- A caption is visible prose; alt text is nonvisual alternative. They can
  overlap, but are not automatically interchangeable.
- The `<125` and paragraph requirements are prompt instructions. The script
  does not parse labels, enforce character count, validate facts, detect
  decorative images, or publish HTML `alt` attributes.
- Review descriptions with subject-matter experts and disabled users where
  feasible. Generated descriptions can omit critical values, invent details,
  misidentify people, or expose sensitive information.

The local Image Analysis alt-text guidance reinforces why generated descriptions
help accessibility, but this lesson uses a multimodal model rather than Image
Analysis. Do not claim an Image Analysis confidence score or language contract
for this lesson.

## Lessons 08–09: Content Understanding image and video analysis

### Shared REST lifecycle

Both lessons call `_shared.cu_client.analyze`, which submits:

```http
POST {CU_ENDPOINT}/contentunderstanding/analyzers/{analyzer-id}:analyze?api-version={CU_API_VERSION}
Authorization: Bearer <token for https://cognitiveservices.azure.com/.default>
Content-Type: application/json

{"inputs":[{"url":"<SAMPLE_*_URL>"}]}
```

It reads `Operation-Location` from accepted response, polls it every two
seconds, and returns when status is `succeeded`, `failed`, or `canceled`.
There is no total timeout, retry/backoff, cancellation request, output storage,
or upload in shared helper.

```text
HTTPS URL → POST analyze → 202 and Operation-Location
       → poll result URL → terminal status
       → inspect result.contents / fields / Markdown
```

Prebuilt analyzer definitions can change across API versions. Use a copied or
custom analyzer if production behavior requires a stable schema; these lessons
call mutable prebuilt IDs directly.

### 08 — Image analysis with `prebuilt-imageSearch`

Run after setting a service-reachable `SAMPLE_IMAGE_URL`:

```bash
uv run python 03-computer-vision/08_content_understanding_image.py
```

The script rejects missing and `file://` values, sends one URL to
`prebuilt-imageSearch`, prints operation status, then prints only first
`result.contents` item’s `markdown` and optional
`fields.Summary.valueString`.

**Expected output:**

```text
status: Succeeded

--- Image Analysis Result ---
<Markdown representation, if returned>

Summary: <one-paragraph image description, if returned>
```

`prebuilt-imageSearch` is a retrieval-oriented prebuilt analyzer that produces
image descriptions and insights. Empty `contents`, absent `Summary`, warnings,
or analyzer failure are possible result conditions. The lesson does not print
all content items, fields, warnings, confidence/source metadata, or create a
search index.

### 09 — Video analysis with `prebuilt-videoSearch`

Run after setting a service-reachable `SAMPLE_VIDEO_URL`:

```bash
uv run python 03-computer-vision/09_video_analysis.py
```

The script sends one URL to `prebuilt-videoSearch`, prints top-level status,
then iterates `result.contents`. For each item it prints `startTimeMs`,
`endTimeMs`, and optional `fields.Summary.valueString`.

**Expected output:**

```text
status: Succeeded

[<start>–<end> ms] <summary>
```

The prebuilt analyzer is documented to extract transcripts and descriptions
for meaningful video segments, plus keyframes/transcript/chapter-style
information. The script does **not** print Markdown, transcript, keyframes,
chapters, warnings, all field values, or any complete raw result. A blank
summary is a possible code output, not proof that no visual/audio information
exists.

`prebuilt-video` is a base analyzer for creating custom analyzers. This lesson
correctly calls `prebuilt-videoSearch`; do not swap IDs when reproducing it.
Video analysis samples approximately one frame per second and scales frames to
512 × 512, so quick events, small text, and distant details can be missed.

## Security, privacy, and responsible use

### Treat media as untrusted and sensitive

| Boundary | Risk | Minimum control |
|---|---|---|
| User image/video upload | Malicious or unexpected visual/text instruction, sensitive content | Validate media type/size, authorize caller, moderate at chosen boundary, and isolate processing. |
| Base64 data URL | Sensitive bytes sent inline to model service | Limit size, avoid logging request body, and document data flow. |
| Blob SAS URL | URL grants delegated read access | HTTPS only, least privilege, one blob, short expiry, no broad container write/list permissions, redact logs. |
| Generated media | Inaccurate, unsafe, or rights-sensitive output | Review before publication and retain provenance/approval data appropriate to policy. |
| Analyzer/model response | Fabricated, incomplete, or sensitive text | Validate against source and avoid treating output as authoritative record. |

Built-in moderation and filtering are service safeguards, not complete
application governance. This domain’s code has no user authentication,
upload validation, malware scanning, private networking design, secret store,
tenant isolation, abuse-rate limit, retention/deletion system, policy engine,
or human escalation workflow.

### Accessibility is product behavior

Generate a draft close to rendering time, use page context, expose editor
controls, and preserve a human-approved override. For charts and screenshots,
make equivalent data or instructions available as real text/table/UI—not only
inside an image. Never use generated “ALT:” text verbatim without checking
that it names meaningful content and omits decorative noise.

## Troubleshooting

| Symptom | Likely cause | First check |
|---|---|---|
| `401` or `403` from direct OpenAI API | Wrong endpoint, identity, token scope, or data-plane role | Use `AZURE_OPENAI_ENDPOINT`, run `az login`, inspect effective principal and role. |
| `404` deployment/model error | Deployment absent or model-family name used instead of deployment | Verify configured deployment names in portal/resource. |
| Responses call rejects image | Deployment lacks visual input support, malformed data URL, or unsupported/oversized input | Confirm model capability, PNG bytes, MIME prefix, and service image limits. |
| Image generation/edit returns `contentFilter` | Prompt, source, or output triggered service safety system | Read error, revise permitted request, and do not attempt to bypass policy. |
| Image edit fails | Bad source/mask shape, type, or size | Use PNG/JPG source under 50 MB; use PNG mask with matching dimensions and transparent editable pixels. |
| Image generation is slow or 429 | Quality/size work or image quota exhausted | Wait, reduce quality/size when acceptable, and use bounded retry/backoff. |
| Sora job fails | Preview access, unsupported region/deployment, policy, or request problem | Inspect returned job including `failure_reason`; verify `VIDEO_MODEL`, endpoint, role, size, duration. |
| Sora job appears stuck | Video work can take minutes; code has no deadline | Check status/job ID, apply operational timeout in production, avoid duplicate uncontrolled submissions. |
| 08/09 rejects URL or returns no content | Missing env var, `file://`, expired SAS, service cannot reach URL, unsupported input | Test only permitted HTTPS access, renew scoped SAS, validate file limits, inspect raw result. |
| Content Understanding poll never returns | Service remains nonterminal or helper has no total timeout | Use bounded timeout/retry and persist operation URL in production. |
| Alt text ignores requested format | Model output is free-form | Parse/validate output or use schema; always review before publishing. |

## Exam traps and review questions

| Trap | Correct distinction |
|---|---|
| “A data URL and Blob SAS URL are same input pattern.” | Data URL embeds bytes in request; SAS URL is server-side retrieval with delegated access. |
| “A model guardrail replaces direct moderation.” | Guardrails are service behavior; direct moderation supplies explicit signal where app can decide. Use both only when architecture needs both. |
| “Image severity is every value 0–7.” | Direct image Content Safety uses trimmed values 0, 2, 4, and 6. |
| “Mask opaque pixels are changed.” | Fully transparent PNG mask pixels identify area intended for edit. |
| “Prompt says preserve means deterministic pixels.” | Image editing is generative; evaluate preservation. |
| “Sora returns MP4 immediately.” | Submit job, poll status, then download generation on success. |
| “Sora 2 reference media is covered by lesson 05.” | Sora supports documented reference/remix paths, but lesson 05 is text-only. |
| “Content Understanding upload happens when URL is supplied.” | Code submits URL only; service fetches it. No local upload/SAS creation occurs. |
| “`prebuilt-video` and `prebuilt-videoSearch` are interchangeable.” | `prebuilt-video` is base analyzer; lesson uses retrieval-oriented `prebuilt-videoSearch`. |
| “Generated alt text fulfills accessibility.” | It is a draft. Context, accuracy, concise purpose, and human review matter. |
| “Vision lesson returns object regions, brands, watermarks, or policies.” | None of this domain’s scripts implement those outputs or runtime controls. |

## Coverage boundaries, code/doc drift, and recommended additions

### Exact current drift

| Area | Current code | Earlier short guide / local docs | README correction |
|---|---|---|---|
| Content Safety image severity | 06 prints returned SDK severity. | Earlier guide calls direct image severity “0–7”; local Content Safety docs specify image values `0`, `2`, `4`, `6`. | Document direct image trimmed scale and distinguish it from multimodal classification. |
| Content Understanding API version | `_shared/config.py` defaults `CU_API_VERSION` to `2025-11-15-preview`. | Earlier guide names `2025-11-01`; local REST quickstart examples use that version. | Make API version resource-configured and call out mismatch. |
| Content Understanding setup | 08/09 require `SAMPLE_IMAGE_URL`/`SAMPLE_VIDEO_URL` but `.env.example` omits both. | Earlier guide lists values but does not emphasize missing template entries. | Show both settings and state they are code-local additions to `.env`. |
| Baseline endpoint requirement | Domain 3 calls direct OpenAI, project, Content Safety, or CU endpoints by lesson; it never reads `FOUNDRY_ENDPOINT`. | Earlier guide implies baseline settings are validated even when unused. | State exact per-lesson endpoint contract. |
| Lesson 06 configuration | Needs Content Safety endpoint **and** project endpoint/default deployment. | Earlier guide describes direct and guardrail flows without complete endpoint split. | Document two independent calls and required surfaces. |
| Masked edit | Code passes source and mask without validation. | Local image-edit docs require PNG mask, matching dimensions, transparent edit pixels. | State requirements and no code-side validation. |
| Sora job contract | Code is text-to-video, polls every five seconds, downloads first generation, has no cancellation/retry/resume. | Local docs also describe image/video inputs, remix, job lifetime, variants, and policy constraints. | Keep text-only claim and list unimplemented paths. |
| Content Understanding result use | 08 prints first content Markdown/optional Summary; 09 prints segment times/optional Summary. | Local docs describe richer image/video results. | State output slices, not full result coverage. |

### Recommended additions from local Foundry documentation

These are follow-on work, not behavior claimed by current scripts:

1. Add `SAMPLE_IMAGE_URL` and `SAMPLE_VIDEO_URL` comments to `.env.example`,
   plus documented Blob upload/SAS creation workflow.
1. Add Content Understanding bounded polling, retry/backoff, operation URL
   persistence, raw-result inspection, and terminal failure diagnostics.
3. Add image source/mask validation before edit: file type, 50 MB limit,
   matching dimensions, and alpha channel.
4. Add generated-image evaluation/review workflow, including prompt/version
   metadata and explicit handling for filter failures and rate limits.
5. Add Sora job deadline, failure reason, cancellation, restart/resume,
   cleanup/deletion, output integrity, and retention controls.
6. Add separate, clearly labeled Sora labs for image/video reference input and
   remix only if multipart/runtime behavior is implemented and tested. Do not
   present documentation examples as covered code.
7. Add output schema/length validation and human approval workflow for
   accessibility descriptions.
8. Add explicit application moderation thresholds and escalation design.
   Guardrail metadata inspection alone is not a policy engine.
9. Add a dedicated, evaluated implementation before claiming support for image
   prompt-injection defense, object regions, watermark/brand detection, or
   custom safety policies.

## Local references

- [Azure OpenAI image generation models](../.context/azure-ai-docs/articles/foundry/openai/how-to/dall-e.md)
- [Vision-enabled model image input](../.context/azure-ai-docs/articles/foundry/openai/includes/how-to-gpt-with-vision-content.md)
- [Vision input limitations](../.context/azure-ai-docs/articles/foundry/openai/includes/gpt-with-vision-input-limitations.md)
- [Sora 2 video generation](../.context/azure-ai-docs/articles/foundry/openai/concepts/video-generation.md)
- [Sora 2 REST quickstart](../.context/azure-ai-docs/articles/foundry/openai/includes/video-generation-rest.md)
- [Content Safety image quickstart](../.context/azure-ai-docs/articles/ai-services/content-safety/quickstart-image.md)
- [Content Safety harm categories](../.context/azure-ai-docs/articles/ai-services/content-safety/concepts/harm-categories.md)
- [Content Understanding REST quickstart](../.context/azure-ai-docs/articles/ai-services/content-understanding/quickstart/use-rest-api.md)
- [Content Understanding prebuilt analyzers](../.context/azure-ai-docs/articles/ai-services/content-understanding/concepts/prebuilt-analyzers.md)
- [Content Understanding service limits](../.context/azure-ai-docs/articles/ai-services/content-understanding/service-limits.md)
- [Content Understanding region support](../.context/azure-ai-docs/articles/ai-services/content-understanding/language-region-support.md)
- [Image Analysis alt-text guidance](../.context/azure-ai-docs/articles/ai-services/computer-vision/use-case-alt-text.md)
