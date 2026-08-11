--- ai-usage: ai-assisted ---

# Domain 3: Computer vision

> Runnable labs for image understanding, alt text, image moderation, image/video generation, visual safety, provenance detection, and Content Understanding (CU). Run every numbered lesson from repository root: `uv run python 03-computer-vision/<lesson>.py`
>
> Code proves one narrow request path per lesson. It is not a production deployment, rights clearance, accessibility conformance, or policy approval.

## What this domain teaches

```text
Visual understanding (multimodal Q&A, alt text, moderation signals)
    → Image generation and editing (text-to-image, prompt edit, mask edit)
    → Video generation (Sora text-to-video, reference media, video remix)
    → Visual safety and provenance (C2PA detection, OCR injection defense)
    → Content Understanding (Blob preflight, image analysis, video analysis, handoff)
```

Domain 3 covers the full lifecycle of visual media in an AI application: reading images for understanding, generating new pixels, moderating content, detecting provenance signals, and extracting structured information from hosted media. Each stage builds on the previous — start with lessons 01–03 to validate your visual pipeline before committing to generation or hosted-media workflows.

## Visual services mental model

```text
Local image bytes ──data URL──> Azure OpenAI Responses  ──> text answer / alt text
Prompt ─────────────────────> Azure OpenAI Images       ──> PNG (generated / edited)
Prompt ─────────────────────> Sora video job            ──> poll ──> MP4

Local image bytes ──────────> Content Safety            ──> 4-category severity signals
HTTPS Blob URL + SAS ───────> Content Safety Provenance ──> C2PA/watermark signal
OCR text (from image) ──────> Prompt Shields            ──> injection attack signal
HTTPS Blob URL + SAS ───────> Content Understanding     ──> async analyzer result
```

### Endpoint and client map

| Surface | Setting | Client | Lessons |
|---|---|---|---|
| Azure OpenAI data plane | `AZURE_OPENAI_ENDPOINT` | `openai_client()` | 01–06 |
| Sora direct REST | `AZURE_OPENAI_ENDPOINT` | `httpx` + bearer token | 07–09 |
| Foundry project (guardrail path) | `PROJECT_ENDPOINT` | `project_client()` | 03 (flow 2) |
| Azure AI Content Safety | `CONTENT_SAFETY_ENDPOINT` | `content_safety_client()` | 03 (flow 1), 10, 11 |
| Content Understanding REST | `CU_ENDPOINT` | `_shared/cu_client.py` | 13, 14, 15 |
| CU preflight (local) | `STORAGE_ACCOUNT`, `CU_ENDPOINT` | none — local only | 12 |

Do not substitute a project endpoint for an Azure OpenAI endpoint. Both may contain the same resource name but use different SDK routes, API contracts, and RBAC scopes.

---

## Glossary

| Term | Study definition |
|---|---|
| **Data URL** | `data:<mime>;base64,...` — image bytes embedded inline in an API request; no storage needed |
| **Blob SAS URL** | HTTPS Blob URL with a signed query string delegating time-limited read access |
| **Content Safety severity** | Integer score 0, 2, 4, or 6 for image harm categories (NOT 0–7) |
| **Provenance signal** | Detected C2PA metadata or Microsoft watermark — an origin indicator, not proof of truth or ownership |
| **Prompt Shields** | Content Safety API that scans text for indirect prompt injection attacks (jailbreak / document) |
| **CU** | Content Understanding — async REST service that fetches a hosted URL and returns analyzer results |
| **Prebuilt analyzer** | CU's built-in analyzer for image, video, or document: `prebuilt-imageSearch`, `prebuilt-videoSearch` |
| **Sora** | Azure OpenAI video generation model; uses async job lifecycle: submit → poll → download |
| **Masked edit** | `images.edit` with an alpha-channel mask; transparent pixels mark intended editable region |
| **Human review** | Required approval step for generated/AI-processed visual content before publication |

---

## Setup

### Environment variables

```dotenv
# Azure OpenAI — deployment aliases, NOT model-family labels
AZURE_OPENAI_ENDPOINT=https://<resource>.openai.azure.com
DEFAULT_MODEL=<visual-capable-chat-deployment>       # gpt-4.1, gpt-4o
IMAGE_MODEL=<image-generation-deployment>            # gpt-image-1
VIDEO_MODEL=<sora-deployment>                        # sora-2

# Lesson 03 guardrail path
PROJECT_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<project>

# Content Safety — lessons 03, 10, 11
CONTENT_SAFETY_ENDPOINT=https://<resource>.cognitiveservices.azure.com

# Content Understanding — lessons 12–15
CU_ENDPOINT=https://<resource>.services.ai.azure.com
CU_API_VERSION=2025-11-01

# CU source media (lessons 12–15)
STORAGE_ACCOUNT=<account>
STORAGE_CONTAINER=<container>
SAMPLE_IMAGE_URL=<https-blob-url-with-read-sas>
SAMPLE_VIDEO_URL=<https-blob-url-with-read-sas>
```

All lessons use `DefaultAzureCredential`. Run `az login` on a workstation; use managed identity in Azure. A successful credential chain proves identity, not correct RBAC scope. Never commit `.env`, SAS URLs, or connection strings to source.

### Safe run order

| Stage | Run | Gate |
|---|---|---|
| Visual understanding | 01, 02, 03 | 03 needs both `AZURE_OPENAI_ENDPOINT` and `CONTENT_SAFETY_ENDPOINT` |
| Image generation/editing | 04, 05, 06 | 05–06 need `product_photo.png`; 06 also needs `mask.png` |
| Video generation | 07, 08 (preflight), 09 (preflight) | 07 needs Sora preview access + region support; 08–09 use `--apply` for billable jobs |
| Visual safety and provenance | 10 (preflight), 11 (preflight) | 10 needs `--run` for cloud call; 11 needs `--run` + local OCR file |
| Content Understanding | 12 (preflight), 13, 14, 15 | Run 12 first to validate Blob/SAS config; 13–15 need `SAMPLE_IMAGE_URL`/`SAMPLE_VIDEO_URL` |

### Costs and side effects

| Lesson | What it writes / costs |
|---|---|
| 01 | Inference tokens (visual model) |
| 02 | Two inference calls (visual model) |
| 03 | Content Safety image analysis + visual model inference |
| 04 | Image generation call + local PNG written |
| 05 | Image edit call + local PNG written |
| 06 | Image edit call (with mask) + local PNG written |
| 07 | Billable Sora video job + local MP4 downloaded |
| 08 | **Read-only** until `--apply` (then: billable Sora reference-image job, no download) |
| 09 | **Read-only** until `--apply` (then: billable Sora remix job, no download) |
| 10 | **Read-only** until `--run` (then: Content Safety Provenance API call) |
| 11 | **Read-only** until `--run` (then: Prompt Shields document scan) |
| 12 | Local only — no cloud calls |
| 13 | CU async analyzer operation (requires `SAMPLE_IMAGE_URL`) |
| 14 | CU async analyzer operation (requires `SAMPLE_VIDEO_URL`) |
| 15 | **Read-only** until `--apply` (then: CU async analyzer operation) |

---

## Decision tables

### When to use which visual approach

| Need | Use | Do not use when |
|---|---|---|
| Open-ended question about an image | Multimodal Responses API (01, 02) | Need fixed schema, coordinates, or verified OCR |
| Accessibility draft (alt text) | Multimodal Responses with labeled prompts (02) | Publishing without human review and contextual approval |
| Image harm signals before model | Content Safety `analyze_image` (03 flow 1) | Treating severity alone as policy decision |
| Model deployment guardrail | Multimodal Responses (03 flow 2) | Expecting guardrail to replace business policy |
| New pixels from a prompt | `images.generate` (04) | Need pixel-perfect reproduction or rights-cleared output |
| Restyle existing image (full-frame) | `images.edit` no mask (05) | Need exact preservation of logos, text, product identity |
| Bounded region edit | `images.edit` with mask (06) | Need deterministic compositing or exact outside-mask preservation |
| Short generated video | Sora `job` (07) | Need synchronous response, GA availability, or durable media store |
| First-frame video anchor | Sora reference media (08) | Input contains human faces, unlicensed assets, or wrong dimensions |
| Change existing Sora video | Sora remix (09) | Input is a local video file (only completed Sora ID accepted) |
| Origin signal for media | Provenance detection (10) | Treating detected/absent marker as proof of ownership or safety |
| OCR text before model | Prompt Shields document scan (11) | Expecting one scan to make untrusted text safe |
| Structured image extraction | CU `prebuilt-imageSearch` (13) | Source can't be reached by CU server, or output must be permanent schema |
| Video segment summaries | CU `prebuilt-videoSearch` (14) | Need guaranteed keyframes, full transcript, or durable search index |
| Bounded normalized handoff | CU visual handoff (15) | Need complete CU archive or raw result forwarding |

### Media transport comparison

| Transport | Lessons | When to use |
|---|---|---|
| Base64 data URL | 01, 02, 03 | Small local images; no storage setup; bytes enter model request |
| Multipart local file | 04, 05, 06, 08 | Image generation/edit API; local file sent as multipart form data |
| HTTPS Blob URL + short SAS | 13, 14, 15 | CU service fetches URL server-side; local paths not supported |
| Completed Sora video ID | 09 | Sora remix; requires previously completed job, not a local file |

---

## Lesson map

| # | File | Runnable objective | Default side effect |
|---|---|---|---|
| 01 | `01_multimodal_understanding.py` | Ask a question about `sales_data.png` via Responses API | Inference tokens |
| 02 | `02_alt_text_captions.py` | Generate alt text + extended description + multi-image caption | Inference tokens |
| 03 | `03_image_moderation.py` | Direct Content Safety + model guardrail for `support.png` | CS call + inference tokens |
| 04 | `04_image_generation.py` | Generate `training_image.png` from prompt | Image generation + local PNG |
| 05 | `05_image_prompt_edit.py` | Full-frame prompt edit of `product_photo.png` | Image edit + local PNG |
| 06 | `06_image_masked_edit.py` | Mask-bounded edit of `product_photo.png` | Image edit + local PNG |
| 07 | `07_video_generation.py` | Submit Sora text-to-video job, poll, download MP4 | Billable Sora job + local MP4 |
| 08 | `08_reference_media_preflight.py` | Preflight; `--apply` submits reference-image Sora job | **Read-only** until `--apply` |
| 09 | `09_video_remix.py` | Preflight; `--apply` submits Sora remix for completed video ID | **Read-only** until `--apply` |
| 10 | `10_visual_provenance_policy.py` | Preflight; `--run` detects C2PA/watermark signals in Blob URL | **Read-only** until `--run` |
| 11 | `11_ocr_image_injection_safety.py` | Preflight; `--run` scans local OCR file via Prompt Shields | **Read-only** until `--run` |
| 12 | `12_cu_blob_preflight.py` | Local Blob/SAS/identity config check — no cloud calls | None |
| 13 | `13_content_understanding_image.py` | CU `prebuilt-imageSearch` on `SAMPLE_IMAGE_URL` | CU async operation |
| 14 | `14_video_analysis.py` | CU `prebuilt-videoSearch` on `SAMPLE_VIDEO_URL` | CU async operation |
| 15 | `15_cu_visual_handoff.py` | Bounded CU handoff; `--apply` submits and normalizes result | **Read-only** until `--apply` |

---

## Stage 1 — Visual understanding (lessons 01–03)

These three lessons use only local images and the Azure OpenAI Responses API (lesson 03 adds Content Safety). No Blob Storage, no CU service, no Sora. Run them first to validate your visual deployment and credential chain.

### 01 — Multimodal understanding

**Question answered:** How do you ask a question about a local image using the Responses API?

**Background.** The Responses API accepts `input_image` content items alongside text. The `_shared/vision_inputs.py` helper encodes a local PNG as `data:<mime>;base64,...` — no Azure Storage or CU service needed. This is the simplest visual input path and the foundation for all other image-to-text lessons.

```bash
uv run python 03-computer-vision/01_multimodal_understanding.py
```

**Code path.**
1. `image_data_url(image_path)` → encodes `sales_data.png` as base64 data URL
2. `openai_client()` → direct Azure OpenAI SDK client via `AZURE_OPENAI_ENDPOINT`
3. `client.responses.create(model=DEFAULT_MODEL, input=[{role, content: [input_text, input_image]}])`
4. Prints `r.output_text`

**What to watch in the output.** Free-form prose summary of the sales chart. Model may misread small numbers or axis labels — treat as unreviewed draft. If output is empty or error, check `DEFAULT_MODEL` is a visual-capable deployment.

**What this proves / does NOT prove.** Proves data URL + visual model + credential chain work. Does NOT prove structured extraction, reliable OCR, object coordinates, or factual accuracy.

**References:** [GPT with vision how-to](https://learn.microsoft.com/azure/foundry/openai/how-to/gpt-with-vision) · [Responses API quickstart](https://learn.microsoft.com/azure/foundry/agents/quickstarts/responses-api)

---

### 02 — Alt text and captions

**Question answered:** How can a multimodal model generate accessibility drafts for images?

**Background.** AI-generated alt text can accelerate accessibility authoring but requires human review for every output. The model generates text from pixels without knowing the page context, decorative vs informative intent, or how a screen-reader user will experience surrounding content. This lesson enforces structural constraints — 125-char ALT ceiling, required `ALT:` and `DESCRIPTION:` labels — to make the draft more actionable.

```bash
uv run python 03-computer-vision/02_alt_text_captions.py
```

**Code path.**
1. Flow A: `_alt_text_and_extended(image_url)` → model returns `ALT:` + `DESCRIPTION:` blocks; `_accessibility_draft()` checks 125-char ceiling and labels, appends `REVIEW:` warning if violated
2. Flow B: `_multi_image_caption([url1, url2])` → model returns single narrative caption for both images

**What to watch in the output.** `ALT:` line under 125 characters, `DESCRIPTION:` paragraph. If `REVIEW:` appears, the draft needs human editing. The caption is for visual description, not as a replacement for actual text content.

**Exam cues.** AI alt text is a draft, not WCAG conformance. Caption is visible prose; alt text is a non-visual alternative. Never auto-publish without human review and contextual approval.

**References:** [GPT with vision how-to](https://learn.microsoft.com/azure/foundry/openai/how-to/gpt-with-vision) · [OCR transparency note](https://learn.microsoft.com/azure/foundry/responsible-ai/computer-vision/ocr-transparency-note)

---

### 03 — Image moderation

**Question answered:** What does direct Content Safety image analysis return, and how does it compare to deployment guardrails?

**Background.** Two complementary moderation paths exist: (1) Direct — call Content Safety `analyze_image` before any model sees the image; returns 0/2/4/6 severity per category. (2) Guardrail — send the image to a multimodal model; the deployment's content filter evaluates both the prompt and response. Neither is a complete business policy alone; they are complementary signals.

```bash
uv run python 03-computer-vision/03_image_moderation.py
```

**Code path.**
1. Flow 1: `content_safety_client().analyze_image(AnalyzeImageOptions(image=ImageData(content=image_bytes)))` → prints severity for Hate / SelfHarm / Sexual / Violence
2. Flow 2: `project_client().get_openai_client().responses.create(model=DEFAULT_MODEL, …)` → ephemeral agent call; prints optional `model_extra.content_filters` guardrail metadata

**What to watch in the output.** Direct path: four category severity lines (0, 2, 4, or 6). Guardrail path: support answer or filter metadata. Filter metadata may be absent — its presence/absence depends on SDK and service version.

**Exam cues.** Image severity values are **0, 2, 4, 6** — NOT 0–7 like text. A severity alone is not a policy decision. Guardrail behavior varies by deployment; it does not replace explicit application policy.

**References:** [Content Safety image quickstart](https://learn.microsoft.com/azure/ai-services/content-safety/quickstart-image) · [Harm categories](https://learn.microsoft.com/azure/ai-services/content-safety/concepts/harm-categories)

---

## Stage 2 — Image generation and editing (lessons 04–06)

These lessons use `images.generate` and `images.edit` via the Azure OpenAI data plane. Generated images are stored locally in `_shared/sample_data/generated/`. All generation is non-deterministic — run twice to observe variance.

### 04 — Image generation

**Question answered:** How do you generate a new image from a text prompt?

**Background.** `images.generate` makes new pixels from a prompt description. It is creative output, not factual reproduction — the model has no access to real brand assets or product photos. Generated images require human review and policy approval before distribution.

```bash
uv run python 03-computer-vision/04_image_generation.py
```

**Code path.**
1. `openai_client().images.generate(model=IMAGE_MODEL, prompt=_PROMPT, n=1, size="1024x1024", quality="medium", output_format="png")`
2. `save_generated_image(r, out)` → decodes base64 bytes, validates, writes `training_image.png`

**What to watch in the output.** "saved: .../training_image.png" — open the file for visual review. Re-run to see generation variance. `IMAGE_MODEL` must be a deployed image-capable alias, not a model-family name.

**Exam cues.** Deployment alias ≠ model-family name. Each run overwrites the previous output. Generation success means bytes arrived, not visual acceptance or rights clearance.

**References:** [Image generation how-to (DALL-E)](https://learn.microsoft.com/azure/foundry/openai/how-to/dall-e) · [Video generation concepts](https://learn.microsoft.com/azure/foundry/openai/concepts/video-generation)

---

### 05 — Prompt-driven image edit

**Question answered:** How do you transform an existing image with a prompt, without specifying a region?

**Background.** `images.edit` takes a source image and a natural-language prompt describing the desired change. Without a mask, the API applies a full-frame interpretation — "keep the product unchanged" is intent, not a pixel-level preservation guarantee. Logos, text, and product identity can change even with preservation language. For bounded edits, use lesson 06.

**Before code.** Ensure `product_photo.png` exists in `_shared/sample_data/images/`. The helper validates format before making an API call.

```bash
uv run python 03-computer-vision/05_image_prompt_edit.py
```

**Code path.**
1. `validate_edit_inputs(src)` → checks readable PNG/JPEG/WebP
2. `images.edit(model=IMAGE_MODEL, image=image_file, prompt=_PROMPT, size="1024x1024", n=1, quality="medium")`
3. `save_generated_image(r, dst)` → writes `edited_product_photo.png`

**What to watch in the output.** Compare `edited_product_photo.png` to source. Note what changed vs what didn't. Logos, text, and small details often change despite "keep unchanged" instructions.

**Exam cues.** Prompt-only edit is full-frame generative transformation. `validate_edit_inputs` checks local format but not all remote API constraints (e.g., size limits, additional format requirements).

**References:** [Image generation how-to (DALL-E)](https://learn.microsoft.com/azure/foundry/openai/how-to/dall-e)

---

### 06 — Masked image edit

**Question answered:** How do you constrain an image edit to a specific region using an alpha-channel mask?

**Background.** A mask PNG with an alpha channel tells the API which pixels are intended to be editable (transparent = editable; opaque = preserve). The constraint is intent, not a pixel lock — generation remains non-deterministic and outside-mask content can still vary slightly. The local validator ensures the mask has the right format before making any API call.

**Before code.** `mask.png` must be the same dimensions as `product_photo.png`, must be PNG with alpha channel, and must have at least one transparent pixel.

```bash
uv run python 03-computer-vision/06_image_masked_edit.py
```

**Code path.**
1. `validate_edit_inputs(src, mask)` → checks both source and mask: same dimensions, PNG with alpha, at least one transparent pixel
2. `images.edit(model=IMAGE_MODEL, image=image_file, mask=mask_file, prompt=_PROMPT, …)`
3. `save_generated_image(r, dst)` → writes `masked_edit_product_photo.png`

**What to watch in the output.** Inspect source, mask, and output together. The generated content should appear in the transparent region of the mask. Check for boundary artifacts and any changes outside the mask area.

**Exam cues.** Mask validation only proves local format geometry and alpha channel. It does not prove semantic placement quality or exact outside-mask preservation. A mask constrains requested change; it is not a pixel lock.

**References:** [Image generation how-to (DALL-E)](https://learn.microsoft.com/azure/foundry/openai/how-to/dall-e)

---

## Stage 3 — Video generation (lessons 07–09)

Sora is an async job API: submit → poll → download. All three steps are visible in lesson 07. Lessons 08–09 add governance gates for reference media and remix — run these as preflight before any billable job.

### 07 — Sora text-to-video

**Question answered:** What does the Sora video generation async lifecycle look like?

**Background.** Sora 2 generates video from a text prompt through an asynchronous job. Unlike synchronous image generation, the video job has three distinct steps: submit, poll for terminal state, then download. This lesson uses the raw `httpx` REST client so all three steps are explicit. Preview availability and region support vary — confirm before committing a design.

```bash
uv run python 03-computer-vision/07_video_generation.py
```

**Code path.**
1. `_token()` → `DefaultAzureCredential().get_token("https://ai.azure.com/.default").token`
2. `POST {AZURE_OPENAI_ENDPOINT}/openai/v1/video/generations/jobs?api-version=preview` → returns job id
3. `_wait_for_job()` → GET polls every 5 s with 300 s deadline; raises on failure/cancellation
4. GET `video/generations/{generation_id}/content/video` → downloads bytes → writes `northwind_video.mp4`

**What to watch in the output.** Job id printed on submit, status updates during polling, "saved: .../northwind_video.mp4" on success. Timeout does not cancel the remote job — reconcile the job id if the script times out.

**Exam cues.** Submit/poll/download is the required async lifecycle, not a single "generate video" call. A 300-second poll timeout does not cancel the remote Sora job. First generation selection is not a quality choice.

**References:** [Sora video generation concepts](https://learn.microsoft.com/azure/foundry/openai/concepts/video-generation)

---

### 08 — Sora reference-media preflight

**Question answered:** What are the requirements and governance gates for reference-image video generation?

**Background.** Sora 2 accepts one JPEG, PNG, or WebP reference image as a first-frame visual anchor. The image must be exactly 1280×720 or 720×1280. Reference media introduces privacy, consent, IP, and source-control risks before a billable generation call — the preflight makes these explicit. Sora 2 currently rejects images containing human faces.

```bash
# No-cloud preflight:
uv run python 03-computer-vision/08_reference_media_preflight.py
# Billable job (only after reviewing rights, privacy, and cost):
uv run python 03-computer-vision/08_reference_media_preflight.py --apply --reference-image <owned-image>
```

**Code path.**
1. Default: `preflight()` → prints requirements; no cloud call, no file inspection
2. `--apply`: `reference_image(path)` → validates existence, suffix, dimensions via Pillow
3. `openai_client().videos.create(model=VIDEO_MODEL, prompt=…, size="1280x720", input_reference=image)`
4. Prints submitted job id and status (does NOT poll/download)

**What to watch in the output.** Default: governance requirements printed. With `--apply`: submitted job id. The lesson does not download the output — retrieve or delete via the Sora video API separately.

**Exam cues.** Passing preflight does not establish rights or policy acceptance. Human faces are rejected by current Sora policy. `--apply` creates a billable preview job.

**References:** [Sora video generation concepts](https://learn.microsoft.com/azure/foundry/openai/concepts/video-generation)

---

### 09 — Sora video remix

**Question answered:** How do you apply a narrow change to an existing Sora-generated video?

**Background.** Sora remix changes an existing generated-video lineage. It accepts a previously completed Sora video ID (not a local file) and applies one narrow prompt change while preserving source structure, motion, and framing. The output is a new async job — not an in-place edit. Source video rights and output retention must be reviewed before submitting.

```bash
# No-cloud preflight:
uv run python 03-computer-vision/09_video_remix.py
# Billable remix (only after reviewing source ID, rights, and cost):
uv run python 03-computer-vision/09_video_remix.py --apply --video-id video_<completed-id>
```

**Code path.**
1. Default: `preflight()` → prints remix requirements; no cloud call
2. `--apply`: validates `--video-id` starts with `video_`
3. `openai_client().videos.remix(video_id=video_id, prompt="Change only the lighting…")`
4. Prints submitted remix job id and status

**What to watch in the output.** Default: governance requirements. With `--apply`: remix job id. The `video_` prefix validation is shallow — it does not prove the ID completed or that the caller is authorized.

**Exam cues.** Remix input is a completed Sora video ID, not a local file. `--apply` creates a new billable job; the lesson does not poll, download, cancel, or delete.

**References:** [Sora video generation concepts](https://learn.microsoft.com/azure/foundry/openai/concepts/video-generation)

---

## Stage 4 — Visual safety and provenance (lessons 10–11)

These lessons address what happens AFTER media is created or received: detecting its origin and defending against content embedded in it. Both start with local preflights; cloud calls require explicit flags.

### 10 — Visual provenance policy

**Question answered:** How do you detect C2PA and Microsoft watermark signals in hosted media?

**Background.** The Content Safety Provenance Detect API checks HTTPS Blob or SAS URIs for supported C2PA metadata and Microsoft AI watermarks. A positive result is an origin signal, not proof of ownership, truth, safety, or trustworthiness. No detected marker does not prove media is human-made or non-AI. Lesson 10 makes this policy boundary explicit.

```bash
# No-cloud preflight:
uv run python 03-computer-vision/10_visual_provenance_policy.py
# Cloud detection (only with owned HTTPS Blob/SAS URI):
uv run python 03-computer-vision/10_visual_provenance_policy.py --run --media-url <https-blob-sas-url>
```

**Code path.**
1. Default: `preflight()` → prints policy statements; no cloud call
2. `--run`: `media_uri(value)` → validates HTTPS + supported extension
3. `submit_detection(client, endpoint, source_uri)` → `POST …/provenance/operations:detect?api-version=2026-07-01-preview` → returns operation id
4. Polls up to 60 × 2 s → prints `outcome` and detected marker `provider`/`model` fields

**What to watch in the output.** Preflight: policy text. With `--run`: `outcome: AI_Generated` or `NOT_DETECTED` and zero or more marker lines. No marker is NOT a negative origin conclusion.

**Exam cues.** Provenance is evidence signal, never a universal trust verdict. API version is `2026-07-01-preview` — verify current supported version before production use.

**References:** [Provenance detection concept](https://learn.microsoft.com/azure/ai-services/content-safety/concepts/provenance-detection) · [Provenance detection how-to](https://learn.microsoft.com/azure/ai-services/content-safety/how-to/how-to-provenance-detection) · [Provenance disclosure guidance](https://learn.microsoft.com/azure/foundry/responsible-ai/content-understanding/provenance-disclosure)

---

### 11 — OCR image-injection safety

**Question answered:** How should text extracted from images be treated before reaching a model?

**Background.** Image text can contain indirect instructions intended to redirect model behavior (indirect prompt injection). OCR does not distinguish trusted user instructions from adversarial document content. The safe path: treat OCR text as untrusted document data, scan it with Prompt Shields before model use, and never paste OCR output into a system prompt. This lesson demonstrates the Prompt Shields `documentsAnalysis` path.

```bash
# No-cloud preflight:
uv run python 03-computer-vision/11_ocr_image_injection_safety.py
# Scan local OCR text file:
uv run python 03-computer-vision/11_ocr_image_injection_safety.py --run --ocr-file <utf8-file>
```

**Code path.**
1. Default: `preflight()` → prints safe-path description; no cloud call
2. `--run`: reads local UTF-8 OCR text file
3. `shield_prompt(content_safety_client(), endpoint, _USER_REQUEST, [ocr_text])` → POST to Prompt Shields
4. Checks `documentsAnalysis[0].attackDetected` → prints True/False and next policy action

**What to watch in the output.** `document attack detected: True` → block or route for human review. `False` → continue treating OCR as untrusted data and applying defense in depth. No detection is not approval.

**Exam cues.** Lesson does not run OCR itself — only scans an existing OCR text file. Never paste OCR output into a system prompt. Prompt Shields is defense-in-depth, not a guarantee that text is benign.

**References:** [Prompt Shields / jailbreak detection](https://learn.microsoft.com/azure/ai-services/content-safety/concepts/jailbreak-detection) · [Content filter Prompt Shields](https://learn.microsoft.com/azure/foundry/openai/concepts/content-filter-prompt-shields)

---

## Stage 5 — Content Understanding (lessons 12–15)

Content Understanding (CU) is an async REST service that fetches media from a hosted URL and returns structured analyzer results. CU cannot access local file paths — the media must be hosted at an HTTPS URL reachable by the CU service (typically an Azure Blob with a short read SAS). Run lesson 12 first to validate your Blob/SAS configuration before lessons 13–15.

### 12 — CU Blob preflight

**Question answered:** Is my Blob, SAS, and identity configuration ready for Content Understanding?

**Background.** CU retrieves media server-side from the URL you provide. A wrong scheme, missing SAS signature, insufficient permissions, or private Blob DNS failure will cause the analyzer to fail — but only at runtime, after a billable operation starts. This preflight checks all locally-detectable issues without making any Azure call.

```bash
# Basic config check:
uv run python 03-computer-vision/12_cu_blob_preflight.py
# Check a specific source URL:
uv run python 03-computer-vision/12_cu_blob_preflight.py --source-url <https-blob-sas-url>
```

**Code path.**
1. `preflight(source_url)` → reads `settings()` for `STORAGE_ACCOUNT`, `STORAGE_CONTAINER`, `CU_ENDPOINT`
2. `source_metadata(source_url)` → parses scheme/host/container/blob path (never prints SAS query string)
3. `validate_source_url(source_url)` → warns about: non-HTTPS, non-Blob host, missing `sig`, missing read `sp=r`, missing expiry `se`

**What to watch in the output.** Configuration status lines, SAS-free source path, and any warnings. Address every warning before running a real CU analysis — each warning is a likely failure mode.

**Exam cues.** Local parser cannot verify SAS signature validity, RBAC, network access, or CU egress. Managed identity for application Blob upload does NOT automatically make CU able to fetch a private Blob URL. Run this lesson before 13–15.

**References:** [Content Understanding quickstart (REST)](https://learn.microsoft.com/azure/ai-services/content-understanding/quickstart/use-rest-api) · [CU secure communications](https://learn.microsoft.com/azure/ai-services/content-understanding/concepts/secure-communications)

---

### 13 — Content Understanding image analysis

**Question answered:** How does CU's `prebuilt-imageSearch` analyzer differ from a multimodal LLM response?

**Background.** `prebuilt-imageSearch` returns a consistent analyzer-shaped result: a Markdown representation of the image content and a `Summary` field. Unlike lesson 01 (free-form LLM prose), CU gives a repeatable structured result designed for searchable-media pipelines. CU retrieves the image server-side — `file://` paths don't work; use `SAMPLE_IMAGE_URL` pointing to an HTTPS Blob SAS URL.

**Before code.** Run lesson 12 preflight. Set `SAMPLE_IMAGE_URL` to a Blob SAS URL of a test image.

```bash
uv run python 03-computer-vision/13_content_understanding_image.py
```

**Code path.**
1. Reads `SAMPLE_IMAGE_URL` from environment; exits with instructions if missing
2. `validate_source_url(image_url)` → validates HTTPS
3. `analyze("prebuilt-imageSearch", image_url)` → POST submit → poll → terminal result
4. Prints `status`, first content `markdown`, and optional `Summary` field

**What to watch in the output.** `status: Succeeded` followed by the Markdown representation and Summary string. Empty contents is valid — it may mean no searchable information was extracted for that image.

**Exam cues.** CU URL submission is NOT Blob upload or search indexing. CU fetches the URL asynchronously. `prebuilt-imageSearch` ≠ `prebuilt-image` (base analyzer for custom). Run lesson 12 first.

**References:** [Content Understanding prebuilt analyzers](https://learn.microsoft.com/azure/ai-services/content-understanding/concepts/prebuilt-analyzers) · [Content Understanding quickstart (REST)](https://learn.microsoft.com/azure/ai-services/content-understanding/quickstart/use-rest-api)

---

### 14 — Content Understanding video analysis

**Question answered:** How does CU's `prebuilt-videoSearch` return video segment summaries?

**Background.** `prebuilt-videoSearch` returns segment-aware results: each content item includes `startTimeMs`, `endTimeMs`, and an optional `Summary` field for that time range. Contrast with `prebuilt-video` which is only a base analyzer for custom analyzers — lesson 14 uses `prebuilt-videoSearch`. Video analysis is async and the video URL must be reachable by CU (Blob SAS is easiest).

**Before code.** Run lesson 12 preflight. Set `SAMPLE_VIDEO_URL` to a Blob SAS URL of an MP4.

```bash
uv run python 03-computer-vision/14_video_analysis.py
```

**Code path.**
1. Reads `SAMPLE_VIDEO_URL` from environment; exits with instructions if missing
2. `validate_source_url(video_url)` → validates HTTPS
3. `analyze("prebuilt-videoSearch", video_url)` → POST submit → poll → terminal result
4. Iterates `result["result"]["contents"]` → prints `[start–end ms] Summary` for each segment

**What to watch in the output.** Segment lines with millisecond time ranges and summaries. A blank summary does not prove no useful information — sampling can miss rapid events or small text.

**Exam cues.** `prebuilt-video` ≠ `prebuilt-videoSearch`. Segment output is partial — not a full transcript, chapter list, or keyframe set. URL submission is not Blob upload.

**References:** [Content Understanding prebuilt analyzers](https://learn.microsoft.com/azure/ai-services/content-understanding/concepts/prebuilt-analyzers) · [Content Understanding quickstart (REST)](https://learn.microsoft.com/azure/ai-services/content-understanding/quickstart/use-rest-api)

---

### 15 — CU visual handoff

**Question answered:** How do you normalize CU output into a bounded, credential-free payload for downstream use?

**Background.** Passing raw CU JSON downstream spreads SAS credentials, unbounded payload size, schema drift, and prompt-injection risk. This lesson normalizes the result: strips SAS query credentials, redacts credential-like strings, caps summary at 400 characters, limits warnings to 10, and limits segments to 20. The `select_analyzer()` function picks `prebuilt-imageSearch` or `prebuilt-videoSearch` automatically from the source file extension.

**Before code.** Run lesson 12 preflight and confirm lessons 13 or 14 work with your source URL.

```bash
# No-cloud preflight (picks analyzer, shows bounds):
uv run python 03-computer-vision/15_cu_visual_handoff.py --source-url <HTTPS_BLOB_SAS_URL>
# Submit and return normalized handoff payload:
uv run python 03-computer-vision/15_cu_visual_handoff.py --apply --source-url <HTTPS_BLOB_SAS_URL>
```

**Code path.**
1. `select_analyzer(source_url)` → picks `prebuilt-imageSearch` or `prebuilt-videoSearch` from extension
2. Preflight: prints chosen analyzer and bound limits; no cloud call
3. `--apply`: `analyze(analyzer, url)` → poll → `normalize_result()` strips SAS, redacts credential-like text, caps summary/warnings/segments
4. Prints formatted JSON: status, analyzer, source metadata (no SAS), warnings, segments, `segments_truncated`

**What to watch in the output.** JSON payload with SAS-free `source` metadata and bounded `segments`. If `segments_truncated: true`, there were more than 20 segments — downstream code must handle partial results.

**Exam cues.** File extension can lie — treat result text as untrusted. Secret regex is defense-in-depth, not a reason to log raw CU data. `--apply` incurs CU operation cost and does not persist operation state.

**References:** [Content Understanding best practices](https://learn.microsoft.com/azure/ai-services/content-understanding/concepts/best-practices) · [Content Understanding prebuilt analyzers](https://learn.microsoft.com/azure/ai-services/content-understanding/concepts/prebuilt-analyzers)

---

## Feature status and hard limits

| Feature | Status | Practical boundary |
|---|---|---|
| Multimodal Responses (image input) | GA | Visual capability varies by deployment; small text and numbers can be misread |
| `images.generate` (DALL-E / gpt-image) | GA | Deployment alias required; not model-family name |
| `images.edit` with prompt only | GA | "Keep unchanged" is intent, not pixel preservation |
| `images.edit` with mask | GA | Mask bounds edit intent; generation remains non-deterministic |
| Sora video generation | Preview | Region/availability limited; async job lifecycle required |
| Sora reference-image input | Preview | Exact 1280×720 or 720×1280; no human faces; owned/consented images only |
| Sora video remix | Preview | Completed Sora ID required; not local file upload |
| Content Safety image analysis | GA | Severity values are 0, 2, 4, 6 — NOT 0–7 |
| Provenance detection | Preview | Supports C2PA and Microsoft watermarks; absence ≠ human-made |
| Prompt Shields | GA | Defense-in-depth signal; not a guarantee text is benign |
| Content Understanding `prebuilt-imageSearch` | GA | Source must be HTTPS URL reachable by CU; not local file |
| Content Understanding `prebuilt-videoSearch` | GA | Segment results are partial; sampling may miss rapid events |

---

## Troubleshooting

| Symptom | Likely cause | Resolution |
|---|---|---|
| `401`/`403` on any call | Wrong endpoint, role, or credential chain | Confirm endpoint surface, `az account show`, workload identity, data-plane role |
| `404 DeploymentNotFound` | Model-family label instead of deployment alias | List deployments in Foundry portal; use configured alias |
| Visual model returns no image content | Deployment not visual-capable | Check `DEFAULT_MODEL` supports vision; gpt-4.1, gpt-4o |
| `validate_edit_inputs` fails | Wrong format, mismatched dimensions, or missing alpha | Use PNG/JPEG/WebP; mask must be PNG with alpha and same dimensions as source |
| Sora job times out | 300 s deadline exceeded or remote job still running | Do NOT resubmit blindly — reconcile existing job id; inspect `failure_reason` |
| Sora reference image rejected | Human faces present or wrong dimensions | Use owned images without faces at exactly 1280×720 or 720×1280 |
| `429` on image/video generation | Quota / capacity exhaustion | Respect `Retry-After`; reduce quality/size only if acceptable; check budget alerts |
| Provenance: no marker detected | Signal absent or media format not supported | Do not infer human origin; record result and apply disclosure policy |
| CU rejects / no result | Missing `SAMPLE_*_URL`, expired SAS, inaccessible URL, wrong API version | Run lesson 12; test connectivity; validate supported `CU_API_VERSION` and analyzer |
| CU poll fails host validation | `Operation-Location` host doesn't match `CU_ENDPOINT` | Treat as security failure; do not follow arbitrary redirect URL |
| Prompt Shields false/negative result | One scan is defense-in-depth, not proof of safety | Layer authorization, validation, and human review; evaluate on representative attacks |

---

## CI/CD and operational release

```text
Define data classification for media (source, generated, OCR, CU output)
    → IaC: resource + RBAC + private endpoints + diagnostic settings
    → media intake: validate type/size/rights/malware scan
    → source store: private Blob + user-delegation read SAS or managed-identity path
    → apply safety/provenance/injection-defense controls by risk level
    → model/generation/CU call with idempotency key, deadline, redacted telemetry
    → output validation + human/policy review gate
    → publish only approved output; retention/deletion and incident workflow
    → evaluate, monitor cost/quota/quality/safety, then release or rollback
```

| Release gate | Minimum evidence |
|---|---|
| Identity | Workload identity; roles scoped to endpoint/action; no user-shared credentials |
| Media rights | Provenance/consent documented before reference media or remix use |
| Content policy | Content Safety thresholds defined; human review path for escalations |
| OCR/injection defense | Prompt Shields + model isolation enforced for document-source content |
| Network | Blob → CU egress path tested from actual runtime; private DNS verified |
| Cost | Image/video/CU budget alerts set; retry bounded with backoff |

---

## Security, networking, and IaC

| Decision | Recommendation | Common pitfall |
|---|---|---|
| SAS credentials | User-delegation SAS, read-only, one blob, HTTPS, short expiry; redact `sig` in logs | Long-lived storage account key SAS or SAS with write/list permissions |
| CU source access | Blob SAS for CU fetch; managed identity for application Blob read/write | Managed identity for application ≠ CU can fetch private Blob URL |
| Blob upload identity | `Storage Blob Data Contributor` at container scope | Account-level permissions or admin role |
| Content Safety role | Cognitive Services User data-plane role at resource scope | Cognitive Services Contributor (control-plane, not inference) |
| Generated content | Human review + policy approval before any distribution | Auto-publishing generated images/video without review |
| OCR text handling | Treat as untrusted document; scan before model; never in system prompt | Pasting OCR output directly into system instructions |
| Provenance disclosure | Record detector version, outcome, policy action; disclose accurately | Treating absent marker as proof of human origin |

---

## Common exam traps

| Claim | Correct interpretation |
|---|---|
| "Data URL and Blob SAS URL are equivalent" | Data URL embeds bytes in the request; SAS URL delegates server-side source retrieval |
| "Image severity uses all values 0–7" | Direct image analysis returns only 0, 2, 4, 6 |
| "Project endpoint can substitute for OpenAI endpoint" | Each has distinct SDK route, API contract, and RBAC scope |
| "Mask guarantees preservation outside transparent pixels" | Bounds intended edit region; generation remains non-deterministic |
| "No provenance marker proves media is human-made" | Absence is not proof of human origin, safety, or ownership |
| "`prebuilt-video` equals `prebuilt-videoSearch`" | Base analyzer vs retrieval-oriented analyzer; use `prebuilt-videoSearch` for lessons 14–15 |
| "CU URL input uploads media" | CU fetches an existing reachable URL; lessons do not upload or index media |
| "Sora returns video synchronously" | Submit job → poll terminal state → retrieve generation; async lifecycle required |
| "Generated alt text solves accessibility" | It is a contextual draft requiring human review; not WCAG conformance |
| "Prompt Shields detection means text is safe" | It is one defense-in-depth signal; apply authorization and isolation regardless |
| "Sora reference preflight establishes rights" | Local type/dimension validation is not consent, ownership, or policy acceptance |
| "Content Safety approves or rejects content" | It provides severity signals; application policy decides block/escalate/allow |

---

## Objective coverage and limits

Domain 3 covers: multimodal image understanding via Responses API; accessibility alt-text and multi-image captioning; two-flow image moderation (direct Content Safety + deployment guardrail); text-to-image generation and both prompt-only and mask-bounded editing; Sora text-to-video async job lifecycle; Sora reference-image and remix governance preflights; visual provenance detection via C2PA/watermark signals; OCR injection defense via Prompt Shields; Content Understanding Blob/SAS preflight; CU `prebuilt-imageSearch` image analysis; CU `prebuilt-videoSearch` video segment analysis; and bounded CU visual handoff with credential stripping.

It does **not** implement: custom CU analyzer creation; full ingestion pipeline with indexing and deletion; image/video accessibility conformance testing; production Sora output lifecycle (download, storage, deletion); Content Safety blocklist or groundedness evaluation; Azure AI Vision OCR (the OCR in lesson 11 is a pre-existing text file); private endpoint configuration for CU or Content Safety; or image/video rights management beyond preflight governance prompts.

---

## References

### Visual understanding and alt text

- [GPT with vision how-to](https://learn.microsoft.com/azure/foundry/openai/how-to/gpt-with-vision)
- [Responses API quickstart](https://learn.microsoft.com/azure/foundry/agents/quickstarts/responses-api)
- [OCR transparency note](https://learn.microsoft.com/azure/foundry/responsible-ai/computer-vision/ocr-transparency-note)

### Image generation and editing

- [Image generation how-to (DALL-E)](https://learn.microsoft.com/azure/foundry/openai/how-to/dall-e)

### Video generation (Sora)

- [Sora video generation concepts](https://learn.microsoft.com/azure/foundry/openai/concepts/video-generation)

### Visual safety and content moderation

- [Content Safety image quickstart](https://learn.microsoft.com/azure/ai-services/content-safety/quickstart-image)
- [Harm categories](https://learn.microsoft.com/azure/ai-services/content-safety/concepts/harm-categories)
- [Provenance detection concept](https://learn.microsoft.com/azure/ai-services/content-safety/concepts/provenance-detection)
- [Provenance detection how-to](https://learn.microsoft.com/azure/ai-services/content-safety/how-to/how-to-provenance-detection)
- [Provenance disclosure guidance](https://learn.microsoft.com/azure/foundry/responsible-ai/content-understanding/provenance-disclosure)
- [Prompt Shields / jailbreak detection](https://learn.microsoft.com/azure/ai-services/content-safety/concepts/jailbreak-detection)
- [Content filter Prompt Shields](https://learn.microsoft.com/azure/foundry/openai/concepts/content-filter-prompt-shields)

### Content Understanding

- [Content Understanding prebuilt analyzers](https://learn.microsoft.com/azure/ai-services/content-understanding/concepts/prebuilt-analyzers)
- [Content Understanding quickstart (REST)](https://learn.microsoft.com/azure/ai-services/content-understanding/quickstart/use-rest-api)
- [Content Understanding best practices](https://learn.microsoft.com/azure/ai-services/content-understanding/concepts/best-practices)
- [CU secure communications](https://learn.microsoft.com/azure/ai-services/content-understanding/concepts/secure-communications)

### Compliance and Responsible AI

- [Image Analysis transparency note](https://learn.microsoft.com/azure/foundry/responsible-ai/computer-vision/image-analysis-transparency-note)
- [Image Analysis characteristics + limitations](https://learn.microsoft.com/azure/foundry/responsible-ai/computer-vision/image-analysis-characteristics-and-limitations)
- [Image Analysis data privacy + security](https://learn.microsoft.com/azure/foundry/responsible-ai/computer-vision/image-analysis-data-privacy-security)
- [Image Analysis integration guidance](https://learn.microsoft.com/azure/foundry/responsible-ai/computer-vision/image-analysis-guidance-for-integration)
- [OCR transparency note](https://learn.microsoft.com/azure/foundry/responsible-ai/computer-vision/ocr-transparency-note)
- [OCR characteristics + limitations](https://learn.microsoft.com/azure/foundry/responsible-ai/computer-vision/ocr-characteristics-and-limitations)
- [OCR data privacy + security](https://learn.microsoft.com/azure/foundry/responsible-ai/computer-vision/ocr-data-privacy-security)
- [OCR integration guidance](https://learn.microsoft.com/azure/foundry/responsible-ai/computer-vision/ocr-guidance-integration-responsible-use)
- [Computer Vision limited access](https://learn.microsoft.com/azure/foundry/responsible-ai/computer-vision/limited-access)
- [Computer Vision limited access (identity)](https://learn.microsoft.com/azure/foundry/responsible-ai/computer-vision/limited-access-identity)
- [Custom Vision transparency note](https://learn.microsoft.com/azure/foundry/responsible-ai/custom-vision/custom-vision-cvs-transparency-note)
- [Custom Vision characteristics + limitations](https://learn.microsoft.com/azure/foundry/responsible-ai/custom-vision/custom-vision-cvs-characteristics-and-limitations)
- [Custom Vision data privacy + security](https://learn.microsoft.com/azure/foundry/responsible-ai/custom-vision/custom-vision-cvs-data-privacy-security)
- [Custom Vision integration guidance](https://learn.microsoft.com/azure/foundry/responsible-ai/custom-vision/custom-vision-cvs-guidance-integration-responsible-use)
- [Face transparency note](https://learn.microsoft.com/azure/foundry/responsible-ai/face/transparency-note)
- [Face characteristics + limitations](https://learn.microsoft.com/azure/foundry/responsible-ai/face/characteristics-and-limitations)
- [Face data privacy + security](https://learn.microsoft.com/azure/foundry/responsible-ai/face/data-privacy-security)
- [Face integration guidance](https://learn.microsoft.com/azure/foundry/responsible-ai/face/guidance-integration-responsible-use)
- [Content Safety transparency note](https://learn.microsoft.com/azure/foundry/responsible-ai/content-safety/transparency-note)
- [Content Safety data privacy](https://learn.microsoft.com/azure/foundry/responsible-ai/content-safety/data-privacy)
- [Content Understanding transparency note](https://learn.microsoft.com/azure/foundry/responsible-ai/content-understanding/transparency-note)
- [Content Understanding data privacy](https://learn.microsoft.com/azure/foundry/responsible-ai/content-understanding/data-privacy)
