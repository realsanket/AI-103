---
ai-usage: ai-assisted
---

# Domain 3 — Computer vision lessons

Run a lesson from repository root:

```bash
uv run python 03-computer-vision/<lesson>.py
```

These nine runnable lessons use multimodal models, image generation, Sora 2,
Content Safety, and Azure Content Understanding in Foundry Tools. They make
real service requests and, where noted, write files under
`_shared/sample_data/generated/`.

## Lessons

| Lesson | File | What it does |
|---|---|---|
| 01 | `01_multimodal_understanding.py` | Sends a local PNG as a data URL to a multimodal model and prints a summary. |
| 02 | `02_image_generation.py` | Generates `training_image.png` from text. |
| 03 | `03_image_prompt_edit.py` | Prompt-edits `product_photo.png` and writes `edited_product_photo.png`. |
| 04 | `04_image_masked_edit.py` | Uses `mask.png` for a masked edit and writes `masked_edit_product_photo.png`. |
| 05 | `05_video_generation.py` | Creates a text-to-video Sora 2 job, polls it, and downloads `northwind_video.mp4`. |
| 06 | `06_image_moderation.py` | Runs direct image moderation and a multimodal response with deployment guardrails. |
| 07 | `07_alt_text_captions.py` | Produces alt text, an extended description, and a multi-image caption. |
| 08 | `08_content_understanding_image.py` | Sends a reachable image URL to `prebuilt-imageSearch` and prints Markdown plus `Summary`. |
| 09 | `09_video_analysis.py` | Sends a reachable video URL to `prebuilt-videoSearch` and prints segment times plus `Summary`. |

## Resources, authentication, and environment

Run `az login` first. The lessons use `DefaultAzureCredential`; they don't
accept API keys. Configure resource access and model deployments before
running them.

`_shared.config.settings()` validates these baseline values even when one
lesson doesn't directly use every value:

```dotenv
FOUNDRY_ENDPOINT=https://<resource>.services.ai.azure.com
AZURE_OPENAI_ENDPOINT=https://<resource>.openai.azure.com
PROJECT_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<project-name>
DEFAULT_MODEL=<multimodal-deployment>
IMAGE_MODEL=<image-generation-deployment>
VIDEO_MODEL=<Sora-2-deployment>
CU_ENDPOINT=https://<resource>.services.ai.azure.com
CU_API_VERSION=2025-11-01
CONTENT_SAFETY_ENDPOINT=https://<resource>.cognitiveservices.azure.com
```

Use a supported Azure OpenAI region and a deployed Sora 2 model for lesson
05. Sora 2 is preview. The documented keyless prerequisite for its direct API
is the **Cognitive Services User** role. The lesson calls the Azure OpenAI
endpoint directly and requests the `https://ai.azure.com/.default` token
scope; it doesn't use `FOUNDRY_ENDPOINT` for video generation.

Content Understanding is also preview. Give your identity permission to invoke
the configured Content Understanding resource and confirm regional availability
and quota before lessons 08 and 09.

### Blob/SAS inputs for Content Understanding

Lessons 08 and 09 use the CU helper's URL-input contract. It submits one
`inputs` item containing the supplied URL; it does not upload local files.
Set these code-local variables in `.env`:

```dotenv
SAMPLE_IMAGE_URL=<readable-image-URL-or-Blob-SAS-URL>
SAMPLE_VIDEO_URL=<readable-video-URL-or-Blob-SAS-URL>
```

These names aren't present in `.env.example`. Don't invent URLs: upload a
permitted file to storage, then supply its reachable URL. For Azure Blob
Storage, create a read SAS for the individual blob, ensure it remains valid
for the analysis, and ensure the service can reach it. `file://` paths don't
work. The `STORAGE_ACCOUNT`, `STORAGE_CONTAINER`, and
`STORAGE_CONNECTION_STRING` variables do not upload files or create SAS
tokens in this domain.

For lesson 08, use a supported image type (`.jpg`, `.jpeg`, `.jpe`, `.png`,
`.bmp`, `.heif`, or `.heic`) between 50 × 50 and 10,000 × 10,000 pixels.
For lesson 09, this course uses an MP4 URL. CU's URL analysis also supports
other documented video formats, but the video must meet its service limits.

## Safe study order

1. Run 01 and 07 with shipped local images. They don't need Blob storage.
2. Run 06 to inspect direct image moderation and model guardrail behavior.
3. Run 02, 03, and 04 after confirming image-model access. Inspect generated
   files before treating them as usable assets.
4. Run 05 only after confirming Sora 2 preview access in a supported region.
5. Create least-privilege Blob SAS URLs, set `SAMPLE_IMAGE_URL` and
   `SAMPLE_VIDEO_URL`, then run 08 and 09.

## Current API behavior

### Lesson 05: Sora 2 text-to-video

Lesson 05 uses the preview direct endpoints:

```text
POST {AZURE_OPENAI_ENDPOINT}/openai/v1/video/generations/jobs?api-version=preview
GET  {AZURE_OPENAI_ENDPOINT}/openai/v1/video/generations/jobs/{job-id}?api-version=preview
GET  {AZURE_OPENAI_ENDPOINT}/openai/v1/video/generations/{generation-id}/content/video?api-version=preview
```

Its JSON job payload contains `model`, `prompt`, `width: 1280`,
`height: 720`, and `n_seconds: 5`. It polls every five seconds, accepts
`succeeded`, `failed`, and `cancelled` terminal states, then downloads the
first generation after success.

### Lessons 08–09: Content Understanding URL analysis

The shared helper submits a CU analyze request and polls its
`Operation-Location`. `prebuilt-imageSearch` returns a Markdown
representation and fields such as `Summary`. `prebuilt-videoSearch` returns
one or more contents. Each content has `startTimeMs`, `endTimeMs`, Markdown,
and a `fields.Summary.valueString` when available. Lesson 09 reads those
documented field paths.

`prebuilt-video` is a base analyzer for custom analyzers; lesson 09 uses
`prebuilt-videoSearch`.

## Side effects and gaps

- Every lesson invokes remote services. Generation, video processing, Content
  Understanding, and Content Safety can incur usage and quota consumption.
- Lessons 02–05 overwrite their fixed filenames under
  `_shared/sample_data/generated/`. Lesson 05 can run for minutes.
- Lesson 05 is text-to-video only. It has no cancellation, retry, resume, or
  job-cleanup flow.
- Lessons 08 and 09 don't upload data, create SAS tokens, create custom
  analyzers, index results, or retain output. Lesson 08 prints only its first
  content; lesson 09 prints each segment's times and summary, not its complete
  Markdown, key frames, or transcript.
- Image edits follow prompt and mask inputs, but don't guarantee pixel-perfect
  preservation or validate generated output.

## Local references

- [Sora 2 video generation](../.context/azure-ai-docs/articles/foundry/openai/concepts/video-generation.md)
- [Sora 2 REST quickstart](../.context/azure-ai-docs/articles/foundry/openai/includes/video-generation-rest.md)
- [Content Understanding REST quickstart](../.context/azure-ai-docs/articles/ai-services/content-understanding/quickstart/use-rest-api.md)
- [Content Understanding prebuilt analyzers](../.context/azure-ai-docs/articles/ai-services/content-understanding/concepts/prebuilt-analyzers.md)
- [Content Understanding service limits](../.context/azure-ai-docs/articles/ai-services/content-understanding/service-limits.md)
