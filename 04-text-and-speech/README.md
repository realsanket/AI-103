# Domain 4 — Implement Text Analysis + Speech Solutions (10–15%)

> Run any lesson: `uv run python 04-text-and-speech/<file>.py`
> Prereqs: `.env` filled, `az login` completed. See root [README.md](../README.md).

20 lessons cover three separate services—Azure Language in Foundry Tools
(Language), Azure Translator in Foundry Tools (Translator), and Azure Speech
in Foundry Tools (Speech)—plus LLM alternatives for NER, sentiment, and
translation; a Language MCP example; and Voice Live.

> **Lesson boundary:** these are runnable learning samples, not a production
> architecture, compliance implementation, or accuracy benchmark. They send
> sample content to remote services, print service output, and intentionally
> omit retries, telemetry, policy enforcement, consent, human review, and
> output evaluation. Treat every model result, including a redaction result,
> as output to validate for its intended workflow.

---

## What this domain teaches you

Every way to process **text** and **speech** in Foundry, from two angles:

- **Task-specific** (structured) — Language (NER / PII / sentiment /
  language detection / summarization / Text Analytics for Health), Translator,
  Speech SDK (STT / TTS / Speech Translation), and Custom Speech.
- **Generative** (LLM prompt, expensive, flexible) — Responses API with a
  system prompt for the same tasks; audio input through the LLM Speech API
  (MAI-Transcribe); Voice Live for real-time
  speech-to-speech.

You'll learn WHICH TO PICK for each task — because the exam tests that
choice, not the code.

---

## Text + Speech in 90 seconds

- **Language** — one service endpoint (`.cognitiveservices.azure.com`) with
  task-specific SDK/REST operations,
  many `kind` values (`EntityRecognition`, `PiiEntityRecognition`,
  `SentimentAnalysis`, `LanguageDetection`, `KeyPhraseExtraction`,
  `ExtractiveSummarization`, `AbstractiveSummarization`, `EntityLinking`,
  `Healthcare`). Task-specific models return structured output. PII
  detection returns a redacted copy, but that result alone does not make a
  workflow compliant or safe to disclose.
- **Translator** — separate REST service. Text translation, document
  translation, transliteration, and dictionary operations have different
  contracts. L04 specifically calls Text Translation v3's global
  `/translate` route and reads its list response; it is not a document or
  glossary sample.
- **Speech SDK** — three STT modes: **Fast** (sync, one file), **Real-time**
  (streaming from mic/network), **Batch** (async, many files). Two TTS
  examples: **Neural** (plain text) and **Neural HD with SSML** (voice
  capabilities vary by region).
  Also handles **Speech Translation** via `TranslationRecognizer` (NOT the
  same as Azure Translator).
- **MAI-Transcribe** — preview speech-recognition models available through
  the LLM Speech API. L17 uses `mai-transcribe-1.5` with a phrase list;
  MAI does not support prompt-tuning or diarization.
- **Voice Live** — bidirectional WebSocket for real-time audio. L18 is a
  protocol demo: it sends a prerecorded PCM file and logs events; it does
  not capture microphone input or play returned audio.
- **Custom Speech** — train a model in Speech Studio for domain jargon or
  accents; deploy → get an endpoint GUID; set `endpoint_id` on the
  standard config. Everything else stays the same.

**Beginner shortcut:** *Choose a task-specific service when its supported
input and output contract fits. Choose an LLM for a new schema or combined
reasoning task, then constrain and evaluate it. Speech modes are one-file
sync / stream / batch async—pick by input shape and latency.*

## Read outputs as evidence, not decisions

Use this order before turning a lesson into an application:

1. Define the input boundary: text, audio file, microphone stream, Blob
   container, or WebSocket frames.
1. Select the service by supported feature, locale, region, latency, and
   data-handling requirement—not only apparent output quality.
1. Test representative and adversarial samples. Record false positives,
   false negatives, unsupported languages, and empty/canceled results.
1. Add application controls that these samples lack: authentication,
   authorization, input limits, retries/backoff, audit policy, retention,
   monitoring, escalation, and human review where consequences matter.

For example, L05 masks detected spans, but an undetected identifier can still
remain in `redacted_text`. L10 extracts health concepts; it does not validate
clinical facts, provide medical advice, determine eligibility, or establish a
health-data compliance posture.

---

## Mental model of the 20 lessons

Two phases, each split by service.

```
┌─── Phase 1: TEXT (L01–L10, L20) ───────────────────────────────────────┐
│  Generative (LLM prompt)                                              │
│    L01 NER by prompt                                                  │
│    L02 Sentiment by prompt                                            │
│    L03 Translation by prompt (tone-preserving)                        │
│    L04 Translator REST (bulk / glossary)                              │
│                                                                        │
│  Task-specific (Language)                                             │
│    L05 PII detection + service redaction                              │
│    L06 Language detection                                             │
│    L07 NER prebuilt                                                   │
│    L20 Sentiment + opinion mining (run after L07)                     │
│    L08 List Language MCP tools                                        │
│    L09 Language MCP inside an agent                                   │
│    L10 Text Analytics for Health                                      │
└────────────────────────────────────────────────────────────────────────┘
        ↓ text done — audio next
┌─── Phase 2: SPEECH (L11–L19) ──────────────────────────────────────────┐
│  STT modes                                                             │
│    L11 Fast Transcription (sync, one file)                            │
│    L12 Real-time STT (mic stream)                                     │
│    L13 Batch Transcription (async REST)                               │
│                                                                        │
│  TTS + speech translation                                              │
│    L14 TTS Neural voice                                               │
│    L15 TTS Neural HD with SSML                                         │
│    L16 Speech Translation (TranslationRecognizer)                     │
│                                                                        │
│  LLM audio + real-time agents                                          │
│    L17 MAI-Transcribe 1.5 preview (LLM Speech API)                    │
│    L18 Voice Live (bidirectional WebSocket → Prompt Agent)            │
│    L19 Custom Speech model endpoint                                   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 30-Second Domain 4 Cheat Sheet

```
TEXT — understanding
  Standard NER (Person/Org/Location)?  → Azure Language NER            [L07]
  Novel entity types?                  → GPT prompt NER                [L01]
  Compliance-grade PII redaction?      → Azure Language PII            [L05]
  Sentiment + opinion mining?          → Azure Language Sentiment      [L20]
  Sentiment with rationale?            → GPT prompt                    [L02]
  Medical entities?                    → Text Analytics for Health     [L10]
  Language detection?                  → Azure Language LanguageDetection [L06]
  Summarize (abstractive)?             → GPT prompt (better than extractive)
  Language tools inside an agent?      → Azure Language MCP            [L08, L09]

TEXT — translation
  Bulk / glossary / documents?         → Azure Translator              [L04]
  Tone + register preserved?           → GPT prompt translation        [L03]

SPEECH — input
  One short file synchronously?        → Fast Transcription (REST)     [L11]
  Live audio stream?                   → Real-time STT (SpeechRecognizer) [L12]
  Many files async?                    → Batch Transcription (v3.2)    [L13]
  Domain jargon / accents?             → Custom Speech (endpoint_id)   [L19]
  File + known named entities?         → MAI-Transcribe phrase list    [L17]

SPEECH — output
  Neural voice?                        → SpeechSynthesizer + voice name [L14]
  Neural HD w/ SSML controls?          → SSML + AvaHDNeural voice      [L15]

SPEECH — conversation / translation
  Translate spoken audio?              → TranslationRecognizer          [L16]
  Real-time agent voice conversation?  → Voice Live (WebSocket)        [L18]
```

---

## Prereqs before you run anything

Steps 1–4 come from Domain 1. Steps 5–8 are Domain 4 additions.

1. **Azure subscription** with billing.
2. **Foundry resource** + `az login`.
3. **Roles for the identity used by `az login`:** `Foundry User` for the
   project/agent calls in L09 and L18, and `Cognitive Services User` on the
   resource serving Language, Speech, and Translator requests. Voice Live's
   keyless flow explicitly requires both roles. Role assignment is necessary
   but does not bypass service, model, region, quota, or network restrictions.
4. **`.env` core:** `FOUNDRY_ENDPOINT`, `AZURE_OPENAI_ENDPOINT`, `DEFAULT_MODEL`.
5. **`.env` Domain 4:**
   - `LANGUAGE_ENDPOINT` — Language service, `cognitiveservices.azure.com`.
   - `LANGUAGE_MCP_URL` — `<lang-endpoint>/language/mcp?api-version=2025-11-15-preview`.
   - `SPEECH_ENDPOINT` — Speech, `cognitiveservices.azure.com`.
   - `SPEECH_REGION` — for batch STT (v3.2 REST is region-scoped).
   - `SPEECH_MCP_URL` — `<speech-endpoint>/speech/mcp?api-version=2025-11-15-preview`.
     It is configuration only: none of this domain's scripts reads it.
   - `VOICE_LIVE_ENDPOINT` — `wss://<resource>.services.ai.azure.com/voice-live/realtime`.
   - `CUSTOM_SPEECH_ENDPOINT_ID` — GUID from Speech Studio (only for L19).
6. **Sample audio present:** `_shared/sample_data/audio/` — `conversation.wav`, `northwind_support_message.wav`.
7. **For L12 and L16 only** — allow your terminal or IDE microphone access
   in your operating system. L18 doesn't use your microphone.
8. **For L13 (Batch STT)** — create a Blob *container* SAS with **read**
   and **list** permissions for only the input container. Set
   `BATCH_STT_CONTAINER_SAS` only in your shell or uncommitted `.env`; make
   its expiry outlast the batch job, then revoke or let it expire. A SAS is a
   bearer secret: do not commit it, put it in command history, print it, or
   attach it to support tickets.
9. **For L19 (Custom Speech)** — train + deploy a model in Speech Studio, paste the endpoint GUID.

Sanity check: `uv run python 01-plan-and-manage/07_managed_identity_agent.py`
must pass. The scripts obtain a Microsoft Entra token through
`DefaultAzureCredential`; that credential must resolve to an identity with
the roles above. This does **not** prove every Domain 4 route is configured:
L04's current global Translator request lacks the resource-identity header
required by Translator's documented Entra global-endpoint flow. See
[known code/documentation mismatches](#known-code-and-documentation-mismatches).

### Endpoint and role checklist

| Setting or role | Purpose |
|---|---|
| `PROJECT_ENDPOINT` | Prompt Agent creation in L09 and L18. |
| `LANGUAGE_ENDPOINT` | Language SDK lessons L05–L07, L10, and L20. |
| `LANGUAGE_MCP_URL` | Language MCP lessons L08–L09. This endpoint is preview-versioned. |
| `SPEECH_ENDPOINT` and `SPEECH_REGION` | Speech REST/SDK lessons. Batch uses the region-scoped REST endpoint. |
| `SPEECH_MCP_URL` | Speech MCP endpoint. This endpoint is preview-versioned. |
| `VOICE_LIVE_ENDPOINT` | WebSocket base URL for L18, without query parameters. |
| Azure Translator Text v3 | L04's helper calls `https://api.cognitive.microsofttranslator.com/translate` with `api-version=3.0`; it has no `TRANSLATOR_ENDPOINT` or resource-ID setting. The documented Entra global route also requires `Ocp-Apim-ResourceId`, which this helper cannot send. |
| **Foundry User** | Needed for project and agent operations in L09 and L18. |
| **Cognitive Services User** | Needed for Microsoft Entra access to AI-service data-plane calls. Voice Live documents this role together with **Foundry User**. Assign roles to the identity actually running the command. |

### Cost and feature status

Every lesson makes a remote call and can incur charges. L01–L03 consume model
tokens; L04 consumes Translator characters; L05–L10 and L20 consume Language
transactions; L11–L17 and L19 consume Speech; L13 also uses Blob Storage; and
L18 creates an agent version and uses Voice Live. The samples do not set
spending caps, quotas, cleanup automation, or cost alerts. Check pricing,
regional availability, model availability, and quotas before running them.

| Feature | Preview or availability status |
|---|---|
| `mai-transcribe-1.5` (L17) | Preview. |
| Language MCP (L08–L09) | Preview. L08 and L09 use Language MCP only. `SPEECH_MCP_URL` is configured but has no lesson in this directory. |
| Voice Live (L18) | Protocol-only sample. It selects the Prompt Agent's `DEFAULT_MODEL` indirectly; verify that model, region, API version `2026-04-10`, and Voice Live status before use. |
| Azure Language sentiment (L20) | Existing Azure Language feature. Microsoft documents retirement on March 31, 2029; plan new production workloads accordingly. |

### Data, microphone, and network prerequisites

- Use synthetic or authorized test data. Audio, transcripts, medical text,
  names, email addresses, and SAS URLs can be sensitive.
- L12 and L16 open the operating system's **default microphone**. Grant
  microphone permission to the terminal or IDE only after confirming the
  selected device and local recording policy. Stop the process when testing
  ends. L18 reads a bundled WAV; it does not open a microphone.
- The samples call public service endpoints. Private endpoints, firewalls,
  DNS, and regional restrictions can block them. Do not weaken network
  controls only to make a lesson run.
- L13 places input media behind a container SAS. Blob access is separate from
  service authorization. Scope its permissions, expiry, and storage
  lifecycle independently.
- Review service logging and retention settings before using live data.
  Custom Speech endpoint logging is optional in the service; L19 neither
  configures nor audits it.

---

## Glossary — Domain 4 terms

| Term | Beginner definition |
|------|--------------------|
| **Language** | Task-specific service for text tasks. The SDK exposes feature-specific methods; the REST API uses task `kind` values. |
| **`kind` field** | Selects the Language feature per call — `EntityRecognition`, `PiiEntityRecognition`, `SentimentAnalysis`, ... |
| **Task-specific NLP** | A service model designed for a defined task that returns a documented schema. Language SDK examples use this path. |
| **Generative NLP** | LLM + prompt. Free-form output; multi-task in one call. Responses API. |
| **Opinion Mining** | Sentiment feature that pairs a target with its aspect. `SentimentAnalysis` + `opinionMining=true`. |
| **Extractive summarization** | Picks the most salient sentences verbatim from the source. Azure Language. |
| **Abstractive summarization** | Paraphrases the source into a new summary. Azure Language OR GPT (usually better). |
| **Entity Linking** | Maps entities to Wikipedia URLs / knowledge base ids. Azure Language. |
| **Text Analytics for Health** | Extracts clinical entities (medication, dose, condition). Async: `begin_analyze_healthcare_entities`. |
| **Azure Translator** | Separate REST service for translation. `text/translate`, `document/translate`, `transliterate`, `dictionary/*`. |
| **Speech SDK** | Python bindings: `SpeechRecognizer` (STT), `SpeechSynthesizer` (TTS), `TranslationRecognizer` (speech translation). |
| **Fast Transcription** | Sync REST: `/speechtotext/transcriptions:transcribe?api-version=2025-10-15`. One file, ~2 hr / 300 MB limit. |
| **Real-time STT** | Speech SDK streaming from mic or network. Continuous recognition. |
| **Batch Transcription** | Async REST v3.2 for many files. Submit → poll → fetch results URL. |
| **Neural voice** | Standard TTS. Voice name like `en-US-JennyNeural`. Plain text works. |
| **Neural HD voice** | A higher-definition Speech voice. L15 uses SSML to request pauses, rate, and style. Voice availability, styles, and regions vary; test a selected voice before relying on it. |
| **SSML** | Speech Synthesis Markup Language. XML dialect for TTS controls: `<voice>`, `<prosody>`, `<break>`, `<mstts:express-as>`. |
| **`TranslationRecognizer`** | Speech SDK class that recognizes speech AND translates in one call. NOT the same as Azure Translator (that's a REST service). |
| **MAI-Transcribe** | Preview speech-recognition models in the LLM Speech API. L17 uses `mai-transcribe-1.5`; it supports phrase lists and transcript style, not prompt-tuning or diarization. |
| **LLM Speech API** | Speech API used by MAI-Transcribe. L17 is a file-transcription example. |
| **Voice Live** | Real-time bidirectional WebSocket API. `wss://<resource>.services.ai.azure.com/voice-live/realtime?api-version=2026-04-10`. |
| **Custom Speech** | Train an acoustic/language model in Speech Studio; deploy → endpoint GUID; set `speech_config.endpoint_id`. |
| **Language MCP** | Foundry MCP endpoint exposing Language features as agent tools. |
| **Speech MCP** | A separately configured MCP URL in `.env`. This directory does not call or discover it, so treat its availability and tool contract as preview-dependent and verify them separately. |

---

## Common first-run failures

| Symptom | Root cause | Fix |
|---------|-----------|-----|
| L11: `404` on Fast STT | Old API version | Use `api-version=2025-10-15` (this repo fixed) |
| L17: `404` on MAI-Transcribe | Wrong endpoint, API version, model, or region | Use the Speech resource endpoint, `api-version=2025-10-15`, and preview-supported `mai-transcribe-1.5` availability |
| L18: `TypeError` for `extra_headers` | Current lockfile uses `websockets` 15 | Use `additional_headers` |
| L18: WebSocket 404 or 401 | Old URL path or missing agent query parameters | Use `/voice-live/realtime?api-version=2026-04-10&agent_id=...&project_id=...` |
| L18: `Agent not found` | Old README referenced `northwind-support` agent | L18 now creates the agent inline |
| L13: `401` on batch submit | Region mismatch — Speech resource in region X, `SPEECH_REGION` = Y | Match region to the resource |
| L13: `SystemExit: Set BATCH_STT_CONTAINER_SAS` | env var missing | Generate a container SAS with read and list permissions |
| L15: Neural HD reads text flatly | Missing SSML — you sent plain text | Pass SSML (see L15 code); HD voices need it |
| L19: `SystemExit: Set CUSTOM_SPEECH_ENDPOINT_ID` | No custom model deployed | Speech Studio → Custom Speech → train + deploy, paste GUID |
| L03: Translator has better output than L03 | Volume translation; use L04 | L03 = tone-preserving; L04 = bulk-optimal. Both are correct. |
| L04: `401` or authorization error | The helper sends an Entra token to Translator's global endpoint without `Ocp-Apim-ResourceId` | This is a code/documentation mismatch. The documented global Entra request needs that header; use a custom-domain route or update the helper before treating L04 as runnable. |
| L12 exits with a traceback after Ctrl+C | The lesson prints “press Ctrl+C” but has no `KeyboardInterrupt` cleanup | Stop from an SDK event in the sample, or add `try`/`finally` and call `stop_continuous_recognition()` before using it interactively. |
| L13 polls more often than current guidance | The code sleeps 30 seconds; local Speech guidance recommends no more than once per minute, ideally less frequently | Do not copy its polling cadence into a batch system. Use backoff and a longer interval. |
| L18 creates another agent version each run | `_ensure_agent()` calls `create_version()` on every execution | Expect project clutter and billed activity. The sample contains no reuse or cleanup path. |

## Known code and documentation mismatches

This table records current behavior without changing lesson code.

| Area | Code contract | Documentation-aligned reality |
|---|---|---|
| L04 Translator authentication | `_shared/translator_client.py` calls the global v3 endpoint with a bearer token and no resource identifier. | Translator's documented Microsoft Entra flow for the global endpoint requires `Ocp-Apim-ResourceId`. The helper has no setting or header for it, so L04's keyless call can fail. The README does not claim it is production-ready. |
| L04 Translator scope | L04 submits plain text to `/translate` and prints `result[0]["translations"]`. | It does not demonstrate glossary use, document translation, Custom Translator, or newer Translator APIs. “Bulk / glossary” is a selection hint, not a capability implemented by the script. |
| L05 PII | L05 asks the Text Analytics SDK for text PII and prints entities plus `redacted_text`. | It is a synchronous text example only. It does not cover conversation PII, document PII, entity policy tuning, missed detections, audit policy, or a compliance guarantee. |
| L08–L09 MCP | L08 discovers Language MCP tools; L09 gives a `MCPTool` to a Prompt Agent. | `SPEECH_MCP_URL` is never read, no Speech MCP call exists, and preview endpoints can change. Tool names returned by discovery are authoritative; the README does not promise a fixed list. |
| L09 MCP connection | L09 creates an `MCPTool` from a URL and creates an agent version. | Local Language MCP guidance requires a configured Foundry project connection for agent authentication. The lesson does not create or validate that connection, so a successful L08 direct call does not prove L09 is configured. |
| L11 Fast STT | L11 uploads one WAV using multipart form data and returns the first `combinedPhrases` text, or `""`. | It has no MIME sniffing, chunking, retry, alternate transcript selection, or verified limit enforcement. Service limits and supported codecs remain deployment/API-version dependent. |
| L12 real-time STT | L12 requests the default microphone and starts continuous recognition. | It prints only final events and lacks partial-result handling, reconnect/retry, device selection, `KeyboardInterrupt` cleanup, consent UI, and persisted transcript handling. |
| L13 batch STT | L13 submits one container SAS, polls every 30 seconds, then downloads result URLs. | The Speech guidance says jobs are best-effort: files within a job can run concurrently, while job scheduling can queue. Use a longer polling interval and build durable job state, retries, storage access controls, and cleanup outside this sample. |
| L15 TTS | L15 sends one fixed SSML document to `en-US-AvaHDNeural`. | It does not verify that this voice, its `friendly` style, or HD support is available in the configured region. Invalid SSML or unsupported voice/style fails at runtime. |
| L17 MAI-Transcribe | L17 requests preview `mai-transcribe-1.5` with a phrase list. | The code does not set `transcribeStyle`, test locale/model availability, evaluate accuracy, or provide diarization. Phrase lists and transcript style are only documented for `mai-transcribe-1.5`; they are not prompt tuning. |
| L18 Voice Live | L18 creates a Prompt Agent using `DEFAULT_MODEL`, sends one complete prerecorded PCM16 buffer, logs events, and stops. | The code *does* select a model indirectly through the agent, contrary to older README wording that it selected none. It has no microphone capture, frame pacing, audio-delta decode/playback, WebRTC client, cancellation, reconnect, or agent cleanup. It is protocol-only, not an end-to-end voice app. |
| L19 Custom Speech | L19 sets an existing deployment GUID as `speech_config.endpoint_id`, recognizes one file, then prints a result. | It does not create training data, train, test word error rate, deploy, rotate expired endpoints, or configure logging. A successful call does not prove the custom model improves recognition. |

---

## Files

| # | File | Syllabus bullet |
|---|---|---|
| 01 | `01_llm_ner.py` | Entity extraction via generative prompt |
| 02 | `02_llm_sentiment.py` | Sentiment + tone via generative prompt |
| 03 | `03_llm_translation.py` | Translation via LLM prompt (tone-preserving) |
| 04 | `04_translator_rest.py` | Translation via Azure Translator Text v3 REST |
| 05 | `05_language_pii.py` | Text PII detection + redaction via Language |
| 06 | `06_language_detect.py` | Language detection via Language |
| 07 | `07_language_ner.py` | Prebuilt NER via Language |
| 20 | `20_language_sentiment.py` | Sentiment analysis + opinion mining via Language |
| 08 | `08_language_mcp_tools.py` | Discover Language MCP tools |
| 09 | `09_language_mcp_agent.py` | Use Language MCP inside a Foundry agent |
| 10 | `10_health_text_analytics.py` | Text Analytics for Health |
| 11 | `11_stt_fast_file.py` | STT — Fast Transcription (single file, sync) |
| 12 | `12_stt_real_time.py` | STT — real-time streaming from mic |
| 13 | `13_stt_batch.py` | STT — Batch Transcription (async, many files) |
| 14 | `14_tts_neural.py` | TTS — neural voice |
| 15 | `15_tts_ssml_hd.py` | TTS — SSML + Neural HD voice |
| 16 | `16_speech_translation.py` | Speech Translation (`TranslationRecognizer`) |
| 17 | `17_llm_speech_preview.py` | MAI-Transcribe 1.5 preview via LLM Speech API |
| 18 | `18_voice_live_prompt_agent.py` | Voice Live WebSocket protocol demo; no microphone capture or audio playback |
| 19 | `19_custom_speech_model.py` | Custom Speech — deployed model endpoint |

## Reference docs

- [Azure Language service overview](../.context/azure-ai-docs/articles/ai-services/language-service/overview.md)
- [Language MCP tools and agents (preview)](../.context/azure-ai-docs/articles/ai-services/language-service/concepts/foundry-tools-agents.md)
- [Speech service overview](../.context/azure-ai-docs/articles/ai-services/speech-service/overview.md)
- [Fast Transcription REST](../.context/azure-ai-docs/articles/ai-services/speech-service/fast-transcription-create.md)
- [Batch Transcription REST](../.context/azure-ai-docs/articles/ai-services/speech-service/batch-transcription.md)
- [MAI-Transcribe model](../.context/azure-ai-docs/articles/ai-services/speech-service/mai-transcribe.md)
- [Voice Live how-to](../.context/azure-ai-docs/articles/ai-services/speech-service/voice-live-how-to.md)
- [Custom Speech deploy](../.context/azure-ai-docs/articles/ai-services/speech-service/how-to-custom-speech-deploy-model.md)
- [Azure Translator overview](../.context/azure-ai-docs/articles/ai-services/translator/overview.md)

---

## Syllabus sections

| Section | Topics |
|---------|--------|
| Language model text analysis | Entity extraction, sentiment/tone, translation, domain customization |
| Speech solutions | STT/TTS for agents, custom speech models, multimodal audio, speech translation |

---

## Language tasks and REST `kind` values

```
Language REST analysis operations (the Python SDK presents methods such as
`recognize_entities()` and `analyze_sentiment()`)
│
├── LanguageDetection          — primary language + confidence
├── EntityRecognition          — Person / Org / Location / Date / Product ...
├── PiiEntityRecognition       — SSN / email / phone / redact
├── SentimentAnalysis          — pos / neg / neutral / mixed (+ opinion mining)
├── KeyPhraseExtraction        — nouny phrases summarizing the doc
├── EntityLinking              — link entities to Wikipedia/KB
├── AbstractiveSummarization   — paraphrase (async, longer docs)
├── ExtractiveSummarization    — pick key sentences (async)
└── Healthcare                 — clinical entities (async)
```

**Python SDK pattern (shared across all):**

```python
from azure.ai.textanalytics import TextAnalyticsClient
client = TextAnalyticsClient(endpoint, DefaultAzureCredential())

client.recognize_entities(["Satya Nadella leads Microsoft."])
client.recognize_pii_entities(["My SSN is 123-45-6789."])
client.detect_language(["Bonjour tout le monde."])
client.analyze_sentiment(["Great product, slow delivery."], show_opinion_mining=True)

# Async features return a poller
poller = client.begin_analyze_healthcare_entities(["Patient on lisinopril 10mg daily."])
result = poller.result()
```

**Memory:** *All Language features share one endpoint — the `kind` selects the feature.*

---

## Discriminative vs Generative NLP

| Dimension | Azure Language (discriminative) | GPT / Responses API (generative) |
|-----------|-------------------------------|----------------------------------|
| Model type | Fine-tuned per task | General-purpose LLM |
| Output | Structured (spans, offsets, confidence) | Free text or JSON |
| Categories | Fixed predefined | Any you describe in the prompt |
| Novel entities | ✘ | ✔ |
| Multi-task per call | ✘ (one `kind`) | ✔ (NER + sentiment + summary together) |
| PII output | Prebuilt categories and redacted text | Prompt-defined result |
| Medical entities | Prebuilt health extraction | Prompt-defined result |
| Latency | Lower | Higher |
| Cost | Lower | Higher |

**Pick by task:**

```
Need prebuilt PII categories/redacted text? → Language PII, then validate
Need prebuilt medical extraction?        → Text Analytics for Health, then validate
Standard-category NER on volume?        → Azure Language NER (cheaper/faster)
Novel entity types (your domain)?       → GPT prompt
Multi-task: NER + sentiment + summary?  → GPT prompt (one call)
Abstractive summary?                    → GPT (usually beats Azure abstractive)
```

---

## Azure Translator vs Speech Translation vs GPT Translation

Three separate paths — each for different scenarios.

| | Azure Translator (L04) | GPT Translation (L03) | Speech Translation (L16) |
|--|-----------------------|-----------------------|--------------------------|
| Input | Text | Text | Audio (mic/stream) |
| Output | Text | Text | Text (translated) |
| Best for | Bulk, glossary, 100+ languages | Tone / register preserved | Live speech translation |
| SDK | `azure.ai.translation.text` | `openai.responses.create` | `speechsdk.translation.TranslationRecognizer` |
| Sync/Async | Sync | Sync | Recognize-once or continuous |

**Memory:** *Azure Translator = REST + volume + glossary. GPT translation = idiom + tone. TranslationRecognizer = SPEECH not text.*

---

## Speech decision tree

```
Audio input — what do you need?
    │
    ├── Single file, sync?                → Fast Transcription (L11)
    ├── Live stream (mic/network)?        → Real-time STT (L12)
    ├── Many files, async batch?          → Batch Transcription v3.2 (L13)
    ├── Translate spoken audio?           → TranslationRecognizer (L16)
    ├── File + known named entities?      → MAI-Transcribe phrase list (L17)
    ├── Agent voice conversation?         → Voice Live WebSocket (L18)
    └── Domain vocab / accents?           → Custom Speech endpoint (L19)

Audio output — what do you need?
    │
    ├── Standard TTS?                     → Neural voice (L14)
    └── Best quality + prosody control?   → Neural HD + SSML (L15)
```

---

# Lesson 01 — LLM NER (Generative Path)

**You'll learn:** entity extraction via a system prompt on the Responses API; the free-form counterpart to L07's discriminative Language SDK path.
**Prereqs:** `DEFAULT_MODEL` deployed.
**Time:** ~5 min.

**Concept:** Describe the entity categories you want in a system prompt;
the model is asked to return JSON. It is flexible on
categories your data cares about (`ticket_id`, `sla_tier`,
`monetary_amount` — none of which Azure Language's prebuilt NER knows).

**Code:**

```python
# 01_llm_ner.py (excerpt)
_SYSTEM = """
You are a text analysis engine for Northwind support tickets.
Read the ticket text and respond with ONLY a JSON object containing:
- "entities": list of objects with "text" and "category"
  (categories: person, organization, date, product, ticket_id, sla_tier, monetary_amount)
- "topics": list of short topic labels
Respond with JSON only. No other text.
"""

r = client.responses.create(
    model=settings().default_model,
    input=[
        {"type": "message", "role": "system", "content": _SYSTEM},
        {"type": "message", "role": "user", "content": _TICKET},
    ],
)
print(r.output_text)
```

**Expected output:** model text that is intended to be JSON with an entity list
(Sarah Chen / Acme Logistics / TKT-1042 / Gold / Northwind Connect / $500)
and topics. Parse it only after validating it.

**Key points:**
- The current code asks for JSON in prose only. For a machine consumer, add a
  response schema and validate the parsed result; see Domain 2 L07. Do not
  assume prompt wording alone guarantees valid JSON.
- LLM NER can invent categories your data doesn't have. Great for novelty;
  validate it before automating a consequence.
- Compare with L07 — same ticket, a fixed service schema and confidence
  signals rather than prompt-defined categories.

---

# Lesson 02 — LLM Sentiment (Generative)

**You'll learn:** per-topic sentiment + overall tone from a prompt; the LLM alternative to Azure Language Sentiment.
**Prereqs:** L01 works.
**Time:** ~5 min.

**Concept:** Ask the model to break a message into concerns/topics and
score each one (sentiment + intensity + rationale). Something Azure
Language's Sentiment Analysis + Opinion Mining does structurally — but
the LLM version can explain its reasoning in prose.

**Code:**

```python
# 02_llm_sentiment.py (excerpt)
_SYSTEM = """
You are a sentiment and tone analysis engine for Northwind support tickets.
Identify each distinct concern or topic raised in the text, and for each one
report the sentiment, an intensity score, and a short rationale.
Separately, assess the overall tone of the message as a whole.
"""
r = client.responses.create(model=settings().default_model, input=[...])
print(r.output_text)
```

**Expected output:** several per-topic entries (SLA breach → frustrated,
Marcus's help → grateful) + an overall tone.

**Key points:**
- Use Azure Language `SentimentAnalysis` + `opinionMining=true` for cost + structured spans; use LLM for explainability.
- Prompt matters — the system prompt is where you enforce the output shape.

---

# Lesson 03 — LLM Translation

**You'll learn:** LLM translation that preserves tone and register; a soft alternative to Azure Translator when nuance matters.
**Prereqs:** L01 works.
**Time:** ~5 min.

**Concept:** Ask the model to translate while keeping tone/register
(formal, urgent, casual). Contrast with L04's Translator REST, which is
better for bulk + glossary consistency but flatter tonally.

**Code:**

```python
# 03_llm_translation.py (excerpt)
def translate(text: str, target_language: str) -> str:
    system_prompt = f"""
You are a professional translator. Translate the user's text into
{target_language}. Preserve the original line breaks and formatting.
Preserve the tone and register of the original (formal, urgent, casual)
rather than producing a flat literal translation.
Respond in exactly this format, no extra commentary:
SOURCE LANGUAGE: <detected source language>
TRANSLATION: <the translated text>
"""
    r = client.responses.create(model=settings().default_model, input=[
        {"type": "message", "role": "system", "content": system_prompt},
        {"type": "message", "role": "user", "content": text},
    ])
    return r.output_text
```

**Expected output:** each target language block prints `SOURCE LANGUAGE:` + `TRANSLATION:`.

**Key points:**
- LLM handles idioms + register better than Translator; Translator handles bulk + glossary better.
- Prompt-force the output format — no "Sure, here's the translation..." preamble.

---

# Lesson 04 — Azure Translator (REST)

**You'll learn:** read a Translator Text v3 REST response containing multiple
targets.
**Prereqs:** a Translator resource, `az login`, and a corrected authentication
path. No `TRANSLATOR_ENDPOINT` setting is used. **Important:** the checked-in
keyless helper lacks the `Ocp-Apim-ResourceId` header required by the documented
global Microsoft Entra route, so do not expect this lesson to authenticate
unchanged.
**Time:** ~5 min.

**Concept:** Translator is a separate REST service. The shared helper POSTs
`[{"Text": text}]` to the global `/translate` endpoint with `api-version=3.0`,
one `from` parameter, and repeated `to` parameters. A successful response is
a list: each input item contains its `translations` list. The script does not
implement glossary, document translation, or custom translation configuration.

**Code:**

```python
# 04_translator_rest.py
from _shared.translator_client import translate


def main() -> None:
    text = (
        "Our VPN keeps dropping every 10 minutes since the last update. "
        "This is affecting our whole sales team."
    )
    result = translate(text, targets=["fr", "ja", "es"], source_language="en")
    for translation in result[0]["translations"]:
        print(f"[{translation['to']}] {translation['text']}")
```

**Expected output:** three lines, one per target language.

**Key points:**
- `targets=[...]` becomes repeated `to` query parameters in one v3 request.
- The response is a list, so read `result[0]["translations"]`; its language
  key is `to`, not `language`.
- For document-level translation (PDF, DOCX), use the **Document Translation** API on the same service.
- **Speech Translation is NOT Azure Translator** — different service (see L16).

---

# Lesson 05 — Azure Language — PII Detection

**You'll learn:** text PII detection plus service-produced redaction through
the Language SDK.
**Prereqs:** `LANGUAGE_ENDPOINT` in `.env`.
**Time:** ~5 min.

**Concept:** `recognize_pii_entities` returns both:
- `entities` — spans with category (Person / Email / Phone / SSN / ...) + confidence,
- `redacted_text` — the original text with PII masked.

This is a prebuilt detection feature, not a full privacy/compliance control.
GPT can also miss or alter sensitive content; neither sample substitutes for
data governance, evaluation, and human review.

**Code:**

```python
# 05_language_pii.py
from _shared.language_client import language_client

_DOCS = [
    "Hi, this is Sarah Chen from Acme Logistics. You can reach me at "
    "sarah.chen@acmelogistics.com or call 312-555-1234 regarding ticket TKT-1042.",
]

def main() -> None:
    client = language_client()
    response = client.recognize_pii_entities(_DOCS, language="en")
    for idx, doc in enumerate(response):
        if doc.is_error:
            print(f"Document {idx + 1} failed: {doc.error.code}")
            continue
        print(f"--- Document {idx + 1} ---")
        print(f"Redacted: {doc.redacted_text}")
        for e in doc.entities:
            print(f"  [{e.category}] '{e.text}'  ({e.confidence_score:.2f})")
```

**Expected output:** the doc with PII masked (`Sarah Chen` → `**********`, email + phone masked), plus a table of detected entities with confidence.

**Key points:**
- `redacted_text` is a service-produced masked copy, not proof that all
  sensitive data is absent. Do not label it “safe” without measuring
  detection quality and applying your retention/access policies.
- For domain-specific identifiers, evaluate a custom NER model or a
  purpose-built rule/model pipeline. An LLM can help classify novel patterns,
  but it does not provide a compliance guarantee.

---

# Lesson 06 — Language Detection

**You'll learn:** identify a document's primary language and confidence score; useful as a router step before invoking language-specific tools.
**Prereqs:** L05 works.
**Time:** ~3 min.

**Concept:** `detect_language()` returns `primary_language` with `iso6391_name` (2-letter code) + `confidence_score`. Good for routing: detect first, then dispatch to a Translator/summarizer/etc.

**Code:**

```python
# 06_language_detect.py
from _shared.language_client import language_client

_DOCS = [
    "Hi, this is Sarah Chen from Acme Logistics regarding ticket TKT-1042.",
    "Bonjour, je vous écris au sujet du ticket TKT-1042 concernant notre VPN.",
    "こんにちは、TKT-1042のチケットについてVPNの問題をご連絡しています。",
    "OK",
]

def main() -> None:
    client = language_client()
    for idx, doc in enumerate(client.detect_language(_DOCS)):
        if doc.is_error:
            print(f"Document {idx + 1} failed: {doc.error.code}")
            continue
        primary = doc.primary_language
        print(f"{_DOCS[idx]!r}: {primary.name} ({primary.iso6391_name})")
```

**Expected output:** English / French / Japanese / (ambiguous, low confidence) for the four docs.

**Key points:**
- Short docs ("OK") give low confidence — treat < 0.5 as "unknown" in production.
- Translator also has language detection (`/translator/text/detect`) — same idea, different service.

---

# Lesson 07 — Azure Language — NER (Discriminative)

**You'll learn:** prebuilt NER with fixed categories, confidence scores per
entity, and optional subcategories (Person → EMPLOYEE, Location → CITY, ...).
**Prereqs:** L05 works.
**Time:** ~5 min.

**Concept:** `recognize_entities()` returns categorized entities with
subcategories and confidence. Contrast with L01's LLM path: this gives a
documented fixed schema; L01 can request novel categories. Confidence is a
model signal, not an audit conclusion or accuracy guarantee.

**Code:**

```python
# 07_language_ner.py
def main() -> None:
    client = language_client()
    for idx, doc in enumerate(client.recognize_entities(_DOCS, language="en")):
        if doc.is_error:
            print(f"Document {idx + 1} failed: {doc.error.code}")
            continue
        for e in doc.entities:
            subcat = f" / {e.subcategory}" if e.subcategory else ""
            print(f"  [{e.category}{subcat}] '{e.text}'  ({e.confidence_score:.2f})")
```

**Expected output:** entries like `[Person] 'Sarah Chen' (0.99)`, `[Organization] 'Acme Logistics' (0.98)`, `[Quantity] '4 hour' (0.95)`, ...

**Key points:**
- Prebuilt categories are FIXED — for custom types build a **Custom NER** model (portal + labeled data).
- Subcategory is not always populated — check for `None`.

---

# Lesson 20 — Azure Language sentiment + opinion mining

**You'll learn:** return document and sentence sentiment, then associate an
opinion assessment with its target. Run this after L07, before the MCP
lessons.
**Prereqs:** `LANGUAGE_ENDPOINT` in `.env`.
**Time:** ~5 min.

**Concept:** `analyze_sentiment(..., show_opinion_mining=True)` returns
positive, neutral, negative, or mixed document and sentence labels with
confidence scores. Opinion mining adds targets and assessments; for example,
it can associate `frustrating` with `onboarding process`.

**Code:**

```python
# 20_language_sentiment.py
response = client.analyze_sentiment(
    _DOCS, language="en", show_opinion_mining=True
)
for idx, doc in enumerate(response):
    if doc.is_error:
        print(f"Document {idx + 1} failed: {doc.error.code}")
        continue
    print(f"--- Document {idx + 1}: {doc.sentiment} ---")
    for sentence in doc.sentences:
        print(f"  [{sentence.sentiment}] {sentence.text}")
        for opinion in sentence.mined_opinions:
            target = opinion.target
            assessments = ", ".join(
                f"{assessment.text} ({assessment.sentiment})"
                for assessment in opinion.assessments
            )
            print(f"    {target.text} ({target.sentiment}): {assessments}")
```

**Expected output:** sentence sentiment plus target/assessment pairs, such
as `onboarding process (negative): frustrating (negative)`.

**Key points:**
- Opinion mining is enabled by `show_opinion_mining=True`; it isn't a
  separate Language task.
- This feature has a published retirement date of March 31, 2029. Prefer
  Foundry models for new production workloads.
- L02 remains useful when you need free-form rationale or custom topic
  grouping rather than fixed sentiment results.

---

# Lesson 08 — List Language MCP Tools

**You'll learn:** discover the tools exposed by the Azure Language MCP server; the exam expects you to know MCP is available for Language + Speech.
**Prereqs:** `LANGUAGE_MCP_URL` in `.env`; `mcp` Python package installed.
Language MCP is preview. L08 makes a direct authenticated client call; it does
not prove that a Foundry project has the connection required by L09.
**Time:** ~5 min.

**Concept:** The repository configures Language and Speech MCP URLs, but this
lesson discovers **Language** only. Language MCP is a preview endpoint that
exposes Language capabilities as agent tools. It reduces custom REST plumbing
for an MCP-compatible consumer; it does not remove authentication,
authorization, data-sharing review, or preview risk.

**Endpoints:**

| Service | MCP URL |
|---------|---------|
| Language | `https://<foundry>.cognitiveservices.azure.com/language/mcp?api-version=2025-11-15-preview` |
| Speech | `https://<foundry>.cognitiveservices.azure.com/speech/mcp?api-version=2025-11-15-preview` |

**Code:**

```python
# 08_language_mcp_tools.py (excerpt)
async def _list_tools() -> None:
    token = DefaultAzureCredential().get_token(_SCOPE).token
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(headers=headers, timeout=...) as http:
        async with streamable_http_client(url=settings().language_mcp_url, http_client=http) as (r, w, _):
            async with ClientSession(r, w) as session:
                await session.initialize()
                result = await session.list_tools()
                for t in result.tools:
                    print(f"• {t.name}\n  {t.description}\n")
```

**Expected output:** a list of tools — NER, PII, sentiment, language detection, key phrases, summarization — each with a short description.

**Key points:**
- L08 obtains an Entra bearer token and uses `/language/mcp`. The repository
  supplies a different `/speech/mcp` URL, but this directory does not verify
  its authentication or tool list.
- Use MCP when the tool consumer is another agent or an off-Azure client.

---

# Lesson 09 — Language MCP Inside a Foundry Agent

**You'll learn:** attach the Language MCP server to a Prompt Agent as an `McpTool`; let the model pick which language tool to invoke per turn.
**Prereqs:** L08 works; configure the Foundry project connection required for
Language MCP authentication. The code does not create that connection.
**Time:** ~5 min.

**Concept:** Same MCP endpoint, but wrapped as an `McpTool` on a
registered agent. The agent's system prompt tells it which class of
questions map to which tool.

**Code:**

```python
# 09_language_mcp_agent.py (excerpt)
tool = MCPTool(server_url=settings().language_mcp_url, server_label="azure_language")
agent = project.agents.create_version(
    agent_name=AGENT_NAME,
    definition=PromptAgentDefinition(
        model=settings().default_model,
        instructions="You analyze customer support text using the Azure Language MCP tools. "
                     "Pick the right tool per user question — do not answer from memory.",
        tools=[tool],
    ),
)
r = openai.responses.create(
    input="Analyze this message. What language is it in, and who is mentioned?\n\n"
          "こんにちは、Sarah Chenです。TKT-1042の件でVPNの問題を報告しています。",
    extra_body={"agent_reference": {"type": "agent_reference", "name": agent.name, "version": agent.version}},
)
```

**Expected output:** an answer that identifies Japanese as the language and Sarah Chen as a mentioned person — with the agent having called MCP tools under the hood.

**Key points:**
- `MCPTool` is the current Azure Projects SDK construct for a remote MCP server.
- No hardcoded routing — the model decides which tool to invoke based on the user's question.

---

# Lesson 10 — Text Analytics for Health

**You'll learn:** extract clinical entities (medication, dosage, condition,
symptom) and inspect returned normalized text when present.
**Prereqs:** L05 works.
**Time:** ~5 min.

**Concept:** `begin_analyze_healthcare_entities` is async (poller-based).
Returns clinical entities with `category`, `confidence_score`, and sometimes
`normalized_text`. It is an extraction aid, not a diagnosis, coding decision,
or clinical validation workflow. Handle health data only under an approved
privacy, access, and human-review process.

**Code:**

```python
# 10_health_text_analytics.py
def main() -> None:
    client = language_client()
    poller = client.begin_analyze_healthcare_entities([
        "Patient presents with a persistent dry cough and shortness of breath for 5 days. "
        "PMH: hypertension controlled on lisinopril 10mg daily. "
        "Prescribed amoxicillin 500mg TID for 7 days."
    ], language="en")
    result = poller.result()
    for doc in (r for r in result if not r.is_error):
        for e in doc.entities:
            print(f"  [{e.category}] '{e.text}'  conf={e.confidence_score:.2f}  norm={getattr(e, 'normalized_text', None)}")
```

**Expected output:** entities like `[SymptomOrSign] 'dry cough'`, `[MedicationName] 'lisinopril'` with dosage/route linked, `[Diagnosis] 'hypertension'`.

**Key points:**
- Async — always `.result()` on the poller.
- Normalized text links to UMLS concepts — invaluable for downstream analytics.

---

# Lesson 11 — STT Fast Transcription (Sync REST)

**You'll learn:** synchronous transcription of a single audio file via the Fast Transcription REST endpoint.
**Prereqs:** `SPEECH_ENDPOINT` in `.env`; `_shared/sample_data/audio/conversation.wav` present.
**Time:** ~5 min.

**Concept:** POST an audio file to `/speechtotext/transcriptions:transcribe?api-version=2025-10-15`
with a JSON `definition` describing locales. Response is the transcript in one call. Limits: ~2 hr / 300 MB per file.

**Code:**

```python
# 11_stt_fast_file.py (excerpt)
def transcribe(audio_path: Path, locale: str = "en-US") -> str:
    token = DefaultAzureCredential().get_token(_SCOPE).token
    url = f"{_endpoint_base()}/speechtotext/transcriptions:transcribe?api-version=2025-10-15"
    with audio_path.open("rb") as f:
        files = {
            "audio": (audio_path.name, f, "audio/wav"),
            "definition": (None, '{"locales":["' + locale + '"]}', "application/json"),
        }
        r = httpx.post(url, headers={"Authorization": f"Bearer {token}"}, files=files, timeout=120.0)
    r.raise_for_status()
    return r.json()["combinedPhrases"][0]["text"]
```

**Expected output:** the transcript of the sample WAV.

**Key points:**
- **API version fix:** `2025-10-15` (older `2024-11-15` still works but is deprecated).
- `definition` is multipart JSON — locales, diarization flags, custom endpoint id all go here.
- Fast Transcription does NOT support real-time streaming — use L12 for that.

---

# Lesson 12 — Real-Time STT (Streaming)

**You'll learn:** continuous recognition from the default microphone via the Speech SDK's `SpeechRecognizer`.
**Prereqs:** `SPEECH_ENDPOINT`; microphone access on your machine.
`SPEECH_REGION` is not read by this script.
**Time:** ~5 min.

**Concept:** `SpeechRecognizer` with `AudioConfig(use_default_microphone=True)`
subscribes to `recognized` events. `start_continuous_recognition()` runs
until you call `stop_continuous_recognition()`. Good for meeting
transcription, live captions, dictation.

**Code:**

```python
# 12_stt_real_time.py
audio = speechsdk.audio.AudioConfig(use_default_microphone=True)
recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config(), audio_config=audio)

recognizer.recognized.connect(lambda evt: print(evt.result.text))
recognizer.session_stopped.connect(stop_cb)
recognizer.canceled.connect(stop_cb)

recognizer.start_continuous_recognition()
print("Listening — press Ctrl+C to stop.")
```

**Expected output:** whatever you say, live, as recognized phrases.

**Key points:**
- Different subscription events: `recognizing` (partial), `recognized` (final), `session_stopped`, `canceled`. Wire what you need.
- For network-source audio (not mic) use `PushAudioInputStream` or `PullAudioInputStream`.
- This sample does not handle Ctrl+C with `try`/`finally`; see
  [known code and documentation mismatches](#known-code-and-documentation-mismatches).

---

# Lesson 13 — Batch Transcription (Async REST)

**You'll learn:** submit many audio files at once via the async v3.2 REST
endpoint; poll until done; list and download each transcription JSON file.
**Prereqs:** `SPEECH_REGION` in `.env`; `BATCH_STT_CONTAINER_SAS` set to a
Blob container SAS with read and list permissions.
**Time:** ~30 min (batch runs in the background, region-serial).

**Concept:** Three steps:
1. POST `/speechtotext/v3.2/transcriptions` with the container SAS + config.
2. Poll `GET <returned job URL>` until `status = Succeeded`.
3. GET the `links.files` URL, select files where `kind` is `Transcription`,
   then GET each file's `links.contentUrl`.

Use for backlogs, weekly archives, and work with no interactive caller.
Batch scheduling is best effort: files in a job can process concurrently, but
jobs can queue. Spread submissions and do not infer throughput from this
single-job sample.

**Code:**

```python
# 13_stt_batch.py (excerpt)
def _submit(container_sas_url: str) -> str:
    body = {
        "displayName": "northwind-support-calls-batch",
        "locale": "en-US",
        "contentContainerUrl": container_sas_url,
        "properties": {
            "diarizationEnabled": True,
            "wordLevelTimestampsEnabled": True,
            "timeToLiveHours": 48,
        },
    }
    r = httpx.post(f"{_base_url()}/speechtotext/v3.2/transcriptions", headers=_headers(), json=body)
    return r.json()["self"]

def _wait(job_url: str) -> dict:
    while True:
        body = httpx.get(job_url, headers=_headers()).json()
        if body["status"] in ("Succeeded", "Failed"):
            return body
        time.sleep(30)

def _print_transcripts(files_url: str) -> None:
    files = httpx.get(files_url, headers=_headers()).json()
    for item in files["values"]:
        if item["kind"] != "Transcription":
            continue
        result = httpx.get(item["links"]["contentUrl"]).json()
        print(item["name"], result["combinedRecognizedPhrases"])
```

**Expected output:** job URL, several `status=Running — waiting 30s` polls,
then one downloaded `Transcription` JSON result per successfully processed
audio file.

**Key points:**
- v3.2 is the current stable API version.
- `diarizationEnabled` requests per-speaker labels ("Speaker 1", "Speaker 2")
  in the transcript; validate supported configuration and output for your
  locale and audio.
- `links.files` is an index, not a transcript. Download each
  `kind: Transcription` item's `links.contentUrl`.
- Batch does not need a custom endpoint even when using a Custom Speech model (unlike real-time).

---

# Lesson 14 — TTS Neural Voice

**You'll learn:** synthesize speech with a neural voice — plain text in, WAV out.
**Prereqs:** `SPEECH_ENDPOINT` in `.env`.
**Time:** ~3 min.

**Concept:** `SpeechSynthesizer` writes audio to a file or stream.
`speech_synthesis_voice_name` picks the voice. Plain text works for the
selected neural voice; voice inventory and availability vary by locale and
region.

**Code:**

```python
# 14_tts_neural.py
cfg = speech_config()
cfg.speech_synthesis_voice_name = "en-US-JennyNeural"
audio_out = speechsdk.audio.AudioOutputConfig(filename=str(_OUTPUT))
synth = speechsdk.SpeechSynthesizer(speech_config=cfg, audio_config=audio_out)
result = synth.speak_text_async(_TEXT).get()
```

**Expected output:** `OK — synthesized to .../northwind_support_message.wav`.

**Key points:**
- Voice names encode language + name + tier: `en-US-JennyNeural`, `ja-JP-NanamiNeural`, etc.
- For prosody control (pitch, rate, pauses, emotion) use SSML (L15).
- `AudioOutputConfig` accepts a filename, byte stream, or default speaker.

---

# Lesson 15 — TTS with SSML + Neural HD

**You'll learn:** send SSML to a selected Neural HD voice and use
`<prosody>`, `<break>`, and `<mstts:express-as style="friendly">` for control.
**Prereqs:** L14 works.
**Time:** ~5 min.

**Concept:** The lesson's HD voice and expressive controls are requested in
SSML. SSML lets you control selected words, break points, rate, and style.
Quality, supported styles, and regional availability are properties to check
for the selected voice, not guarantees from this sample.

**Code:**

```python
# 15_tts_ssml_hd.py (SSML excerpt)
_SSML = """
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis"
       xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US">
  <voice name="en-US-AvaHDNeural">
    <mstts:express-as style="friendly">
      Hello, and thank you for contacting <break time="200ms"/> Northwind.
    </mstts:express-as>
    <break time="400ms"/>
    <prosody rate="-5%">
      Your support request has been received. A specialist will contact you shortly.
    </prosody>
  </voice>
</speak>
"""
synth.speak_ssml_async(_SSML).get()
```

**Expected output:** `OK — synthesized to .../northwind_hd_announcement.wav`. Listen — pauses + slightly slower rate + friendly tone should be audible.

**Key points:**
- HD voice names contain `HD` (`AvaHDNeural`, `AndrewMultilingualNeural`).
- `<mstts:express-as>` styles differ per voice — check the docs for what each voice supports.
- SSML is XML-strict — bad markup fails the whole call.

---

# Lesson 16 — Speech Translation

**You'll learn:** `TranslationRecognizer` recognizes speech AND translates in one call. Different service from Azure Translator.
**Prereqs:** `SPEECH_REGION` in `.env`; mic access.
**Time:** ~5 min.

**Concept:** `speechsdk.translation.TranslationRecognizer` uses the Speech
SDK for continuous or one-shot translation from audio. Set the source
language, add one or more `target_language`s, invoke; result carries
the recognized source text AND every requested translation.

**Code:**

```python
# 16_speech_translation.py (excerpt)
token = DefaultAzureCredential().get_token(_SCOPE).token
cfg = speechsdk.translation.SpeechTranslationConfig(auth_token=token, region=settings().speech_region)
cfg.speech_recognition_language = "en-US"
cfg.add_target_language("fr")

audio = speechsdk.audio.AudioConfig(use_default_microphone=True)
recognizer = speechsdk.translation.TranslationRecognizer(translation_config=cfg, audio_config=audio)
result = recognizer.recognize_once_async().get()

if result.reason == speechsdk.ResultReason.TranslatedSpeech:
    print(result.text)                      # source (English)
    print(result.translations["fr"])        # translated (French)
```

**Expected output:** recognized English text + French translation of a single spoken utterance.

**Key points:**
- **Not Azure Translator.** Different service, different SDK. The exam loves this trap.
- Add multiple targets before `recognize` to translate to many languages simultaneously.
- Continuous variant: subscribe to `recognized` events like L12.

---

# Lesson 17 — MAI-Transcribe 1.5 preview

**You'll learn:** file transcription with `mai-transcribe-1.5` through the
LLM Speech API, including phrase-list entity biasing.
**Prereqs:** `SPEECH_ENDPOINT` in `.env`; sample audio.
**Time:** ~10 min.

**Concept:** MAI-Transcribe is a preview speech-recognition model. L17 uses
the `mai-transcribe-1.5` enhanced mode on the same REST route as Fast
Transcription. The model supports a phrase list to bias named entities and
can support `transcribeStyle`; the checked-in request does not set a style.
It doesn't support prompt-tuning or diarization.

**Code:**

```python
# 17_llm_speech_preview.py (excerpt)
definition = {
    "locales": ["en"],
    "phraseList": {"phrases": ["Northwind Connect", "Sentinel", "Ledger"]},
    "enhancedMode": {"enabled": True, "model": "mai-transcribe-1.5"},
}
url = (
    f"{settings().speech_endpoint}"
    "/speechtotext/transcriptions:transcribe?api-version=2025-10-15"
)
with audio.open("rb") as f:
    files = {
        "audio": (audio.name, f, "audio/wav"),
        "definition": (None, json.dumps(definition), "application/json"),
    }
    r = httpx.post(url, headers={"Authorization": f"Bearer {_token()}"}, files=files, timeout=180.0)
```

**Expected output:** transcript with phrase-list terms such as `Northwind
Connect` recognized accurately when the audio contains them.

**Key points:**
- This lesson uses REST API version `2025-10-15`; verify regional model
  availability and the current preview contract before depending on it.
- `mai-transcribe-1.5` is preview-only. Confirm model and regional
  availability before relying on it.
- A phrase list isn't a prompt and doesn't replace Custom Speech training.

---

# Lesson 18 — Voice Live protocol demo for a Prompt Agent

**You'll learn:** connect a WebSocket to a Foundry Prompt Agent, send
prerecorded PCM audio, and inspect Voice Live events.
**Prereqs:** `VOICE_LIVE_ENDPOINT` in `.env`; `PROJECT_ENDPOINT` in `.env`.
**Time:** ~15 min.

**Concept:** Voice Live can stream audio to an agent and return audio deltas.
This lesson is deliberately protocol-only: it sends the bundled 16-kHz mono
PCM16 sample, prints events, and stops at `response.done`. It does **not**
capture microphone input, decode `response.audio.delta`, or play audio.
It creates a Prompt Agent whose model is `DEFAULT_MODEL`; it is therefore not
accurate to describe this request as model-free.

Current URL (verified in `speech-service/voice-live-how-to.md`):

```
wss://<resource>.services.ai.azure.com/voice-live/realtime
    ?api-version=2026-04-10
    &agent_id=<agent-id>
    &project_id=<project-name>
```

Older docs referenced `/voice-live/v1` and `agent_name` — outdated.

**Code:**

```python
# 18_voice_live_prompt_agent.py (excerpt)
async def _run() -> None:
    project = project_client()
    agent_id = _ensure_agent(project)     # inline create — no portal setup

    project_name = settings().project_endpoint.rstrip("/").split("/")[-1]
    token = DefaultAzureCredential().get_token(_SCOPE).token
    url = (
        f"{settings().voice_live_endpoint}"
        f"?api-version=2026-04-10&agent_id={agent_id}&project_id={project_name}"
    )
    headers = {"Authorization": f"Bearer {token}"}

    async with websockets.connect(url, additional_headers=headers) as ws:
        await ws.send(json.dumps({
            "type": "session.update",
            "session": {"input_audio_sampling_rate": 16000},
        }))
        await ws.send(json.dumps({"type": "input_audio_buffer.append", "audio": b64_audio}))
        await ws.send(json.dumps({"type": "input_audio_buffer.commit"}))
        await ws.send(json.dumps({"type": "response.create"}))
        async for msg in ws:
            event = json.loads(msg)
            if event.get("type") == "response.done":
                break
```

**Expected output:** several WebSocket events (`session.created`,
`input_audio_buffer.committed`, `response.audio.delta`, `response.done`).
Audio deltas are logged only; no sound plays.

**Key points:**
- **URL correction:** `/voice-live/realtime?api-version=2026-04-10`; params `agent_id` + `project_id` (not `agent_name`).
- For non-agent scenarios pass a supported `model` query parameter instead of
  the agent parameters. Confirm model/region support; this README does not
  claim a particular model is available.
- Two subdomain options: `services.ai.azure.com` (current) or `cognitiveservices.azure.com` (older resources).
- `websockets` 15 uses `additional_headers`, not `extra_headers`.
- Build a microphone capture, PCM framing, audio-delta decoding, and output
  playback loop before describing an application as end-to-end voice.

---

# Lesson 19 — Custom Speech Model

**You'll learn:** point the Speech SDK at a Custom Speech model you've trained in Speech Studio — same code, one extra config line.
**Prereqs:** trained + deployed Custom Speech model; `CUSTOM_SPEECH_ENDPOINT_ID` in `.env` (GUID).
**Time:** ~5 min (assuming model already deployed; training itself is separate).

**Concept:** Setting `speech_config.endpoint_id = "<guid>"` routes
recognition to your custom acoustic/language model. Every other SDK
call is identical to standard STT. Use for domain jargon, accented
speech, unusual product names.

**Code:**

```python
# 19_custom_speech_model.py (excerpt)
def recognize_with_custom_model(audio_path: str) -> str:
    s = settings()
    if not s.custom_speech_endpoint_id:
        raise SystemExit("Set CUSTOM_SPEECH_ENDPOINT_ID to your deployment GUID.")
    config = speech_config()
    config.endpoint_id = s.custom_speech_endpoint_id
    recognizer = speechsdk.SpeechRecognizer(
        speech_config=config,
        audio_config=speechsdk.audio.AudioConfig(filename=audio_path),
    )
    return recognizer.recognize_once_async().get().text
```

**Expected output:** one recognition result routed to the configured endpoint.
It might improve domain-specific terms, but this sample has no base-model
comparison or word-error-rate measurement and cannot demonstrate improvement.

**Key points:**
- Batch Transcription does NOT need a custom endpoint even when using your custom model — you reference the model directly in the batch request.
- MAI-Transcribe phrase lists (L17) can improve recognition of known terms
  without training.
- Custom Speech has three stages: **train** (Speech Studio, needs labeled
  data) → **test** (for example, word error rate against a held-out set) →
  **deploy** (get endpoint GUID). L19 implements only the final consume step.

---

## Coverage gaps and best next lessons

The 20 scripts demonstrate narrow API paths. Local Foundry documentation
identifies these high-value additions; they are **not** claimed as implemented
by this directory.

| Priority | Missing lesson | Why it matters | Local source |
|---|---|---|---|
| 1 | Fix and test Translator Microsoft Entra authentication | L04 currently cannot send the required resource ID for the documented global endpoint. A lesson should compare global + `Ocp-Apim-ResourceId` with the custom-domain route, then test response/error handling. | [Translator Entra authentication](../.context/azure-ai-docs/articles/ai-services/translator/how-to/microsoft-entra-id-auth.md) |
| 2 | Conversation and document PII | L05 covers only synchronous strings. Contact-center transcripts and native documents require different PII input models and workflows. | [Conversation PII](../.context/azure-ai-docs/articles/ai-services/language-service/personally-identifiable-information/conversation-pii-overview.md), [Document PII](../.context/azure-ai-docs/articles/ai-services/language-service/personally-identifiable-information/document-based-pii-overview.md) |
| 3 | Custom NER training and evaluation | L01 prompt NER and L07 prebuilt NER leave out the supported middle path: labeled domain categories with held-out evaluation. | [Custom NER](../.context/azure-ai-docs/articles/ai-services/language-service/custom-named-entity-recognition/overview.md) |
| 4 | Runtime phrase-list accuracy | L17 has the MAI-specific phrase list, but no lesson shows the standard Speech runtime phrase list for Fast, real-time, or Voice Live, nor its limit that batch transcription does not support. | [Phrase lists](../.context/azure-ai-docs/articles/ai-services/speech-service/improve-accuracy-phrase-list.md) |
| 5 | Speech MCP discovery/use | Configuration exposes `SPEECH_MCP_URL`, but no lesson tests it. Add it only after confirming its preview contract and tool list at runtime. Language MCP itself is explicitly preview. | [Language tools and agents](../.context/azure-ai-docs/articles/ai-services/language-service/concepts/foundry-tools-agents.md) |
| 6 | Real-time audio source and reliability | L12 teaches only a default mic. A practical lesson needs `PushAudioInputStream`/`PullAudioInputStream`, audio format validation, reconnect behavior, and cancellation. | [Audio input streams](../.context/azure-ai-docs/articles/ai-services/speech-service/how-to-use-audio-input-streams.md) |
| 7 | Voice Live client delivery | L18 proves a small WebSocket exchange, not a voice client. A next lesson should use the recommended browser/mobile transport where appropriate, add consent, frame pacing, playback, interruption, and failure handling. | [Voice Live WebRTC](../.context/azure-ai-docs/articles/ai-services/speech-service/voice-live-webrtc.md), [Voice Live customization](../.context/azure-ai-docs/articles/ai-services/speech-service/voice-live-how-to-customize.md) |
| 8 | Current Translator API comparison | L04 deliberately stays on Text Translation v3. A separate lesson can compare the newer GA API only after choosing its contract and migration path. | [Text Translation 2026-06-06 REST guide](../.context/azure-ai-docs/articles/ai-services/translator/text-translation/2026-06-06/rest-api-guide.md) |

Also absent: schema-constrained LLM output and evaluation for L01–L03,
batch-job durability and cleanup for L13, TTS voice/style availability checks,
Custom Speech train/test lifecycle automation, and an end-to-end
transcript-to-PII privacy pipeline. Add these as separate lessons rather than
quietly treating these short samples as coverage.

---

# Common Exam Traps

| Trap | Truth |
|------|-------|
| "Opinion Mining uses a different `kind`" | ❌ — same `kind: SentimentAnalysis`, just pass `show_opinion_mining=True` |
| "Fast Transcription is the same as real-time STT" | ❌ — Fast = one file sync; real-time = live stream |
| "Neural HD works without SSML" | ❌ — Neural HD **requires** SSML for the good stuff; plain Neural doesn't |
| "`TranslationRecognizer` is Azure Translator" | ❌ — `TranslationRecognizer` is the Speech SDK; Azure Translator is a separate REST service |
| "L08 proves Speech MCP works too" | ❌ — L08 discovers Language MCP only; `SPEECH_MCP_URL` is unused in this directory |
| "A redaction result proves the data is safe" | ❌ — both missed detections and application handling remain your responsibility |
| "Voice Live uses `/voice-live/v1`" | ❌ — current URL is `/voice-live/realtime?api-version=2026-04-10` |
| "Voice Live takes `agent_name`" | ❌ — takes `agent_id` + `project_id` query params (or `model` for non-agent) |
| "Fast STT api-version is `2024-11-15`" | ❌ — current `2025-10-15` |
| "MAI-Transcribe supports prompt-tuning" | ❌ — `mai-transcribe-1.5` supports phrase lists and transcript style, not prompt-tuning or diarization |
| "Custom Speech works for batch by default" | ✔ — batch can use a custom model without deploying an endpoint. Real-time DOES need the endpoint. |
| "Extractive and Abstractive summarization are the same kind" | ❌ — separate `kind` values (`ExtractiveSummarization` / `AbstractiveSummarization`) |

---

> The 30-second cheat sheet lives at the [top of this README](#30-second-domain-4-cheat-sheet)
> — scroll up any time an exam question makes you second-guess which lesson covers it.
