# Domain 4 — Implement Text Analysis + Speech Solutions (10–15%)

> Run any lesson: `uv run python 04-text-and-speech/<file>.py` Prereqs: `.env` filled, `az login` completed. See root [README.md](../README.md).

25 lessons cover three separate services—Azure Language in Foundry Tools (Language), Azure Translator in Foundry Tools (Translator), and Azure Speech in Foundry Tools (Speech)—plus LLM alternatives for NER, sentiment, and translation; a Language MCP example; and Voice Live.

> **Lesson boundary:** these are runnable learning samples, not a production architecture, compliance implementation, or accuracy benchmark. They send sample content to remote services, print service output, and intentionally omit retries, telemetry, policy enforcement, consent, human review, and output evaluation. Treat every model result, including a redaction result, as output to validate for its intended workflow.

---

## What this domain teaches you

Every way to process **text** and **speech** in Foundry, from two angles:

- **Task-specific** (structured) — Language (NER / PII / sentiment /
language detection / summarization / Text Analytics for Health), Translator, Speech SDK (STT / TTS / Speech Translation), and Custom Speech.
- **Generative** (LLM prompt, expensive, flexible) — Responses API with a
system prompt for the same tasks; audio input through the LLM Speech API (MAI-Transcribe); Voice Live for real-time speech-to-speech.

You'll learn WHICH TO PICK for each task — because the exam tests that choice, not the code.

---

## Text + Speech in 90 seconds

- **Language** — one service endpoint (`.cognitiveservices.azure.com`) with
task-specific SDK/REST operations, many `kind` values (`EntityRecognition`, `PiiEntityRecognition`, `SentimentAnalysis`, `LanguageDetection`, `KeyPhraseExtraction`, `ExtractiveSummarization`, `AbstractiveSummarization`, `EntityLinking`, `Healthcare`). Task-specific models return structured output. PII detection returns a redacted copy, but that result alone does not make a workflow compliant or safe to disclose.
- **Translator** — separate REST service. Text translation, document
translation, transliteration, and dictionary operations have different contracts. L04 specifically calls Text Translation v3's global `/translate` route and reads its list response; it is not a document or glossary sample.
- **Speech SDK** — three STT modes: **Fast** (sync, one file), **Real-time**
(streaming from mic/network), **Batch** (async, many files). Two TTS examples: **Neural** (plain text) and **Neural HD with SSML** (voice capabilities vary by region). Also handles **Speech Translation** via `TranslationRecognizer` (NOT the same as Azure Translator).
- **MAI-Transcribe** — preview speech-recognition models available through
the LLM Speech API. L17 uses `mai-transcribe-1.5` with a phrase list; MAI does not support prompt-tuning or diarization.
- **Voice Live** — bidirectional WebSocket for real-time audio. L18 is a
protocol demo: it sends a prerecorded PCM file and logs events; it does not capture microphone input or play returned audio.
- **Custom Speech** — train a model in Speech Studio for domain jargon or
accents; deploy → get an endpoint GUID; set `endpoint_id` on the standard config. Everything else stays the same.

**Beginner shortcut:** *Choose a task-specific service when its supported input and output contract fits. Choose an LLM for a new schema or combined reasoning task, then constrain and evaluate it. Speech modes are one-file sync / stream / batch async—pick by input shape and latency.*

## Read outputs as evidence, not decisions

Use this order before turning a lesson into an application:

1. Define the input boundary: text, audio file, microphone stream, Blob
container, or WebSocket frames.
1. Select the service by supported feature, locale, region, latency, and
data-handling requirement—not only apparent output quality.
1. Test representative and adversarial samples. Record false positives,
false negatives, unsupported languages, and empty/canceled results.
1. Add application controls that these samples lack: authentication,
authorization, input limits, retries/backoff, audit policy, retention, monitoring, escalation, and human review where consequences matter.

For example, L05 masks detected spans, but an undetected identifier can still remain in `redacted_text`. L10 extracts health concepts; it does not validate clinical facts, provide medical advice, determine eligibility, or establish a health-data compliance posture.

---

## Mental model of the 25 lessons

Two phases, each split by service.

```
┌─── Phase 1: TEXT (L01–L10, L20) ───────────────────────────────────────┐
│  Generative (LLM prompt)                                              │
│    L01 NER by prompt                                                  │
│    L02 Sentiment by prompt                                            │
│    L03 Translation by prompt (tone-preserving)                        │
│    L04 Translator Text REST (multiple target languages)               │
│                                                                        │
│  Task-specific (Language)                                             │
│    L05 PII detection + service redaction                              │
│    L06 Language detection                                             │
│    L07 NER prebuilt                                                   │
│    L20 Sentiment + opinion mining (run after L07)                     │
│    L08 List Language MCP tools                                        │
│    L09 Language MCP inside an agent                                   │
│    L10 Text Analytics for Health                                      │
│    L21 Speech MCP preflight/discovery                                 │
│    L22 Translator Entra secure-config preflight                       │
│    L23 Document Translation batch lifecycle                           │
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
│    L24 Voice Live PCM file-to-file flow                               │
│    L25 Monitoring and governance preflight                            │
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
  Text Translation, multiple targets?  → Azure Translator Text         [L04]
  Document Translation batch?          → Azure Translator documents    [L23]
  Tone + register preserved?           → GPT prompt translation        [L03]

SPEECH — input
  One short file synchronously?        → Fast Transcription (REST)     [L11]
  Live audio stream?                   → Real-time STT (SpeechRecognizer) [L12]
  Many files async?                    → Batch Transcription (REST)    [L13]
  Domain jargon / accents?             → Custom Speech (endpoint_id)   [L19]
  File + known named entities?         → MAI-Transcribe phrase list    [L17]

SPEECH — output
  Neural voice?                        → SpeechSynthesizer + voice name [L14]
  Neural HD w/ SSML controls?          → SSML + AvaHDNeural voice      [L15]

SPEECH — conversation / translation
  Translate spoken audio?              → TranslationRecognizer          [L16]
  Real-time agent voice conversation?  → Voice Live (WebSocket)        [L18, L24]
```

---

## Prereqs before you run anything

Steps 1–4 come from Domain 1. Steps 5–8 are Domain 4 additions.

1. **Azure subscription** with billing.
2. **Foundry resource** + `az login`.
3. **Roles for the identity used by `az login`:** `Foundry User` for the
project/agent calls in L09 and L18, and `Cognitive Services User` on the resource serving Language, Speech, and Translator requests. Voice Live's keyless flow explicitly requires both roles. Role assignment is necessary but does not bypass service, model, region, quota, or network restrictions.
4. **`.env` core:** `FOUNDRY_ENDPOINT`, `AZURE_OPENAI_ENDPOINT`, `DEFAULT_MODEL`.
5. **`.env` Domain 4:**
   - `LANGUAGE_ENDPOINT` — Language service, `cognitiveservices.azure.com`.
   - `LANGUAGE_MCP_URL` — `<lang-endpoint>/language/mcp?api-version=2025-11-15-preview`.
   - `TRANSLATOR_RESOURCE_ID` — full Translator resource ARM ID. L04/L22
     send it as `Ocp-Apim-ResourceId` for global-endpoint Entra
     authentication. It is an identifier, not a secret; add it to your
     uncommitted `.env` because older `.env.example` files may omit it.
   - `SPEECH_ENDPOINT` — Speech, `cognitiveservices.azure.com`. SDK STT/TTS
     use this endpoint directly; L11 uses it when set.
   - `SPEECH_REGION` — required by L13/L16 and the regional fallback for
     L11. It must match the Speech resource location.
   - `SPEECH_MCP_URL` — `<speech-endpoint>/speech/mcp?api-version=2025-11-15-preview`.
     L21 reads its presence locally and, only with `--run`, validates the URL
     and discovers tools without invoking one.
   - `VOICE_LIVE_ENDPOINT` — `wss://<resource>.services.ai.azure.com/voice-live/realtime`.
   - `CUSTOM_SPEECH_ENDPOINT_ID` — GUID from Speech Studio (only for L19).
6. **Sample audio present:** `_shared/sample_data/audio/` — `conversation.wav`, `northwind_support_message.wav`.
7. **For L12 and L16 only** — allow your terminal or IDE microphone access
in your operating system. L18 doesn't use your microphone.
8. **For L13 (Batch STT)** — create a Blob *container* SAS with **read**
and **list** permissions for only the input container. Set `BATCH_STT_CONTAINER_SAS` only through your shell, Key Vault, or CI secret store; never add it to `.env.example` or source. Make its expiry outlast the batch job, then revoke or let it expire. A SAS is a bearer secret: do not commit it, put it in command history, print it, or attach it to support tickets.
9. **For L19 (Custom Speech)** — train + deploy a model in Speech Studio, paste the endpoint GUID.
10. **For L23 (Document Translation)** — use separate short-lived HTTPS Blob
    SAS URLs: source requires `r` and `l`, target requires `w` and `l`, and every target
    container is unique per batch. Supply `TRANSLATOR_DOCUMENT_KEY` only at
    runtime or through Key Vault-backed configuration; never commit it.

Sanity check: `uv run python 01-plan-and-manage/07_managed_identity_agent.py` must pass. The scripts obtain a Microsoft Entra token through `DefaultAzureCredential`; that credential must resolve to an identity with the roles above. This proves neither Translator resource-ID configuration, Speech regional availability, Blob reachability, nor MCP/Voice Live preview availability.

### Endpoint and role checklist

| Setting or role | Purpose |
|---|---|
| `PROJECT_ENDPOINT` | Prompt Agent creation in L09 and L18. |
| `LANGUAGE_ENDPOINT` | Language SDK lessons L05–L07, L10, and L20. |
| `LANGUAGE_MCP_URL` | Language MCP lessons L08–L09. This endpoint is preview-versioned. |
| `SPEECH_ENDPOINT` and `SPEECH_REGION` | SDK uses endpoint; L13/L16 need region; L11 falls back to regional Fast STT endpoint. |
| `SPEECH_MCP_URL` | Speech MCP endpoint. L21 discovers only after explicit `--run`; preview-versioned. |
| `VOICE_LIVE_ENDPOINT` | WebSocket base URL for L18, without query parameters. |
| `TRANSLATOR_RESOURCE_ID` | Full Translator ARM ID; L04/L22 send it as `Ocp-Apim-ResourceId` with global-endpoint Entra authentication. |
| **Foundry User** | Needed for project and agent operations in L09 and L18. |
| **Cognitive Services User** | Needed for Microsoft Entra access to AI-service data-plane calls. Voice Live documents this role together with **Foundry User**. Assign roles to the identity actually running the command. |

### Portal, CLI, IaC, identity, network, and secret handoff

Use **Foundry/Azure portal** to confirm supported resource, model, locale, voice/style, quota, region, private-endpoint, and preview combinations. Use **Azure CLI** for repeatable identity/resource inspection, never to paste secrets:

```bash
az account show --query "{subscription:id,tenant:tenantId,user:user.name}" -o json
az role assignment list --assignee <principal-object-id> --all -o table
az cognitiveservices account list -g <resource-group> -o table
```

Use reviewed **Bicep/ARM/Terraform** as production source of truth for resource kind/region, tags, diagnostic settings, public-network policy, private endpoints/private DNS, role assignments, Storage lifecycle, Key Vault, and budget/alert resources. Portal exploration and CLI discovery do not replace IaC drift control; IaC does not make an unsupported voice/model/preview available.

Use Azure CLI credentials only on a developer workstation. Deployed code uses managed identity or workload identity; assign smallest data-plane role at resource/project/container scope. A managed identity removes stored login secrets, not role, service authorization, or network work. Use Key Vault references for unavoidable `TRANSLATOR_DOCUMENT_KEY`, certificates, or third-party secrets; grant secret-read access to runtime identity only. Never place those values in source, MCP tool schema, prompts, `.env.example`, telemetry, or support tickets.

For Blob, application upload identity normally needs narrow `Storage Blob Data Contributor`; direct application read needs narrow `Storage Blob Data Reader`; service-fetch flows require their own supported access path. A SAS is bearer delegation, not RBAC: scope one resource/container, HTTPS, minimum permissions and expiry, then redact full query strings. Private endpoint does not grant a role; RBAC does not create route/DNS. Test private DNS, ingress, and egress for Language, Translator, Speech/Voice Live, Storage, Key Vault, Foundry, and Azure Monitor from the actual workload network.

### Cost and feature status

L01–L03 consume model tokens; L04/L22 consume Translator characters when run; L05–L10/L20 consume Language transactions; L11–L17/L19 consume Speech; L13 consumes Speech plus Blob Storage; L18 creates then deletes an agent version and uses Voice Live; L23 can create billable Document Translation batches and Blob output; L24 uses Voice Live. L21/L25 are local by default. The samples do not configure budgets, quotas, diagnostic settings, or alerts. Check pricing, regional/model availability, and quotas before `--run` or `--apply`.

| Feature | Preview or availability status |
|---|---|
| `mai-transcribe-1.5` (L17) | Preview. |
| Language/Speech MCP (L08–L09, L21) | Preview. L08/L09 use Language; L21 discovers Speech tools only after explicit opt-in. |
| Voice Live (L18, L24) | Preview/version-sensitive. L18 selects `DEFAULT_MODEL` through a Prompt Agent; L24 requires explicit `--model`. Verify model, region, and API version `2026-04-10`. |
| Document Translation (L23) | Explicit `--apply`, API-key contract, Blob input/output, and persistent batch/output lifecycle. |
| Azure Language sentiment (L20) | Existing Azure Language feature. Microsoft documents retirement on March 31, 2029; plan new production workloads accordingly. |

### Data, microphone, and network prerequisites

- Use synthetic or authorized test data. Audio, transcripts, medical text,
names, email addresses, and SAS URLs can be sensitive.
- L12 and L16 open the operating system's **default microphone**. Grant
microphone permission to the terminal or IDE only after confirming the selected device and local recording policy. Stop the process when testing ends. L18 reads a bundled WAV; it does not open a microphone.
- The samples call public service endpoints. Private endpoints, firewalls,
DNS, and regional restrictions can block them. Do not weaken network controls only to make a lesson run.
- L13 places input media behind a container SAS. Blob access is separate from
service authorization. Scope its permissions, expiry, and storage lifecycle independently.
- Review service logging and retention settings before using live data.
Custom Speech endpoint logging is optional in the service; L19 neither configures nor audits it.

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
| **Batch Transcription** | Async REST for many files. L13 submits → polls with `Retry-After`/bounded backoff → fetches result files → deletes service job/results. |
| **Neural voice** | Standard TTS. Voice name like `en-US-JennyNeural`. Plain text works. |
| **Neural HD voice** | A higher-definition Speech voice. L15 uses SSML to request pauses, rate, and style. Voice availability, styles, and regions vary; test a selected voice before relying on it. |
| **SSML** | Speech Synthesis Markup Language. XML dialect for TTS controls: `<voice>`, `<prosody>`, `<break>`, `<mstts:express-as>`. |
| **`TranslationRecognizer`** | Speech SDK class that recognizes speech AND translates in one call. NOT the same as Azure Translator (that's a REST service). |
| **MAI-Transcribe** | Preview speech-recognition models in the LLM Speech API. L17 uses `mai-transcribe-1.5`; it supports phrase lists and transcript style, not prompt-tuning or diarization. |
| **LLM Speech API** | Speech API used by MAI-Transcribe. L17 is a file-transcription example. |
| **Voice Live** | Real-time bidirectional WebSocket API. `wss://<resource>.services.ai.azure.com/voice-live/realtime?api-version=2026-04-10`. |
| **Custom Speech** | Train an acoustic/language model in Speech Studio; deploy → endpoint GUID; set `speech_config.endpoint_id`. |
| **Language MCP** | Foundry MCP endpoint exposing Language features as agent tools. |
| **Speech MCP** | Preview MCP endpoint. L21 defaults to a local preflight; `--run` lists runtime tools but invokes none. |

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
| L04/L22: `TRANSLATOR_RESOURCE_ID` error or `401` | Missing/malformed ARM ID, wrong Translator resource, role, or propagation | Set full `/subscriptions/.../providers/Microsoft.CognitiveServices/accounts/...` ID for the Translator resource; verify documented data-plane role and wait for propagation. |
| L12 exits with a traceback after Ctrl+C | The lesson prints “press Ctrl+C” but has no `KeyboardInterrupt` cleanup | Stop from an SDK event in the sample, or add `try`/`finally` and call `stop_continuous_recognition()` before using it interactively. |
| L13 appears to delete results | L13 intentionally deletes job in `finally` | Copy approved output to governed storage before completion; reconcile remote job after local interruption. |
| L18 creates another agent version each run | It creates one fresh version to show cold-start agent setup | `finally` deletes it. Monitor failed/interrupted runs and use a version/reuse lifecycle in production. |
| L21 rejects MCP URL | URL is not HTTPS, is localhost, or lacks `api-version` | Use documented reachable HTTPS endpoint and keep discovery behind explicit `--run`. |
| L23 rejects source/target | Missing SAS permission or unsafe URL | Source must contain `sp=r` and `l`; target `sp=w` and `l`; use scoped short-lived HTTPS Blob SAS and never print them. |
| L24 rejects audio/output | Input is not mono PCM16 16/24 kHz WAV, output exists, or output is not `.pcm` | Convert audio; choose a new output path. Raw output needs sample rate/format metadata to play. |

## Known code and documentation mismatches

This table records current behavior without changing lesson code.

| Area | Code contract | Documentation-aligned reality |
|---|---|---|
| L04 Translator authentication | `_shared/translator_client.py` obtains an Entra token, validates `TRANSLATOR_RESOURCE_ID`, and sends it as `Ocp-Apim-ResourceId` to global Text Translation v3. | This now matches documented global-endpoint Entra authentication. It still needs the correct Translator ARM ID, data-plane RBAC, endpoint reachability, and approved text. |
| L04 Translator scope | L04 submits plain text to `/translate` and prints `result[0]["translations"]`. | It does not demonstrate glossary use, document translation, Custom Translator, or newer Translator APIs. |
| L05 PII | L05 asks the Text Analytics SDK for text PII and prints entities plus `redacted_text`. | It is a synchronous text example only. It does not cover conversation PII, document PII, entity policy tuning, missed detections, audit policy, or a compliance guarantee. |
| L08–L09/L21 MCP | L08 discovers Language tools, L09 registers Language MCP on a Prompt Agent, and L21 locally preflights or explicitly lists Speech MCP tools. | Preview endpoints and schemas change. Discovery does not authorize tool execution; L21 invokes no tool. Tool names returned at runtime are authoritative. |
| L09 MCP connection | L09 creates an `MCPTool` from a URL and creates an agent version. | Local Language MCP guidance requires a configured Foundry project connection for agent authentication. The lesson does not create or validate that connection, so a successful L08 direct call does not prove L09 is configured. |
| L11 Fast STT | L11 uploads one WAV using multipart form data and returns the first `combinedPhrases` text, or `""`. | It has no MIME sniffing, chunking, retry, alternate transcript selection, or verified limit enforcement. Service limits and supported codecs remain deployment/API-version dependent. |
| L12 real-time STT | L12 requests the default microphone and starts continuous recognition. | It prints only final events and lacks partial-result handling, reconnect/retry, device selection, `KeyboardInterrupt` cleanup, consent UI, and persisted transcript handling. |
| L13 batch STT | L13 uses `/speechtotext/transcriptions?api-version=2024-11-15`, honors `Retry-After` or bounded 60–600 second backoff, prints result files, and deletes the job in `finally`. | Speech jobs are best-effort and can queue. The cleanup deletes service-managed results, so copy approved output to governed storage first. Production still needs durable job state, retries, access control, and reconciliation after interrupted clients. |
| L15 TTS | L15 sends one fixed SSML document to `en-US-AvaHDNeural`. | It does not verify that this voice, its `friendly` style, or HD support is available in the configured region. Invalid SSML or unsupported voice/style fails at runtime. |
| L17 MAI-Transcribe | L17 requests preview `mai-transcribe-1.5` with a phrase list. | The code does not set `transcribeStyle`, test locale/model availability, evaluate accuracy, or provide diarization. Phrase lists and transcript style are only documented for `mai-transcribe-1.5`; they are not prompt tuning. |
| L18 Voice Live | L18 creates an active Prompt Agent using `DEFAULT_MODEL`, sends one prerecorded PCM16 buffer, logs events, and deletes that agent version in `finally`. | It has no microphone capture, frame pacing, audio-delta decode/playback, WebRTC client, cancellation, or reconnect. It is protocol-only, not an end-to-end voice app. |
| L23 Document Translation | L23 is local until `--apply`; then it submits, inspects, or cancels one batch using runtime-only key plus source/target Blob SAS URLs. | It validates URL shape/permissions, not SAS validity, blob content, or business authorization. Keep operation URL and output lifecycle in a secure job store; target output persists until your storage lifecycle removes it. |
| L24 Voice Live audio | L24 is local until `--run`; it validates PCM WAV, chunks input, collects `response.audio.delta`, and writes new raw `.pcm` output. | It has no microphone/speaker, transcript persistence, cancellation, paced streaming, reconnect, or consent UX. Output is raw PCM, not a WAV file. |
| L25 governance | L25 reads four local configuration flags only. | It neither tests connectivity nor configures Monitor, Policy, RBAC, networking, retention, or alerts. |
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
| 21 | `21_speech_mcp_preflight.py` | Local Speech MCP preflight; opt-in tool discovery only |
| 22 | `22_translator_secure_config.py` | Local Translator Entra preflight; opt-in reviewed-text translation |
| 23 | `23_translator_batch_operations.py` | Explicit Document Translation submit, inspect, or cancel lifecycle |
| 24 | `24_voice_live_audio_flow.py` | Explicit Voice Live PCM file-to-file audio flow |
| 25 | `25_text_speech_governance_preflight.py` | Local monitoring and governance configuration preflight |

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

### Official Microsoft references

Validate API version, model/voice/locale/region support, limits, pricing, and preview status at release time:

- [Azure Language overview](https://learn.microsoft.com/azure/ai-services/language-service/overview)
- [Language Foundry tools and agents](https://learn.microsoft.com/azure/ai-services/language-service/concepts/foundry-tools-agents)
- [Translator overview](https://learn.microsoft.com/azure/ai-services/translator/translator-overview)
- [Translator Microsoft Entra authentication](https://learn.microsoft.com/azure/ai-services/translator/how-to/microsoft-entra-id-auth)
- [Document Translation overview](https://learn.microsoft.com/azure/ai-services/translator/document-translation/overview)
- [Speech service overview](https://learn.microsoft.com/azure/ai-services/speech-service/overview)
- [Speech-to-text overview](https://learn.microsoft.com/azure/ai-services/speech-service/speech-to-text)
- [Text-to-speech overview](https://learn.microsoft.com/azure/ai-services/speech-service/text-to-speech)
- [Voice Live how-to](https://learn.microsoft.com/azure/ai-services/speech-service/voice-live-how-to)
- [Custom Speech overview](https://learn.microsoft.com/azure/ai-services/speech-service/custom-speech-overview)
- [Azure Storage SAS overview](https://learn.microsoft.com/azure/storage/common/storage-sas-overview)
- [Blob data-access RBAC](https://learn.microsoft.com/azure/storage/blobs/assign-azure-role-data-access)
- [Managed identities](https://learn.microsoft.com/entra/identity/managed-identities-azure-resources/overview)
- [Azure Key Vault overview](https://learn.microsoft.com/azure/key-vault/general/overview)
- [Azure Private Endpoint overview](https://learn.microsoft.com/azure/private-link/private-endpoint-overview)
- [Application Insights overview](https://learn.microsoft.com/azure/azure-monitor/app/app-insights-overview)

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
| Best for | Text translation to selected target languages | Tone / register preserved | Live speech translation |
| SDK | `azure.ai.translation.text` | `openai.responses.create` | `speechsdk.translation.TranslationRecognizer` |
| Sync/Async | Sync | Sync | Recognize-once or continuous |

**Memory:** *Azure Translator = REST text translation. GPT translation = idiom + tone. TranslationRecognizer = SPEECH not text.*

---

## Speech decision tree

```
Audio input — what do you need?
    │
    ├── Single file, sync?                → Fast Transcription (L11)
    ├── Live stream (mic/network)?        → Real-time STT (L12)
    ├── Many files, async batch?          → Batch Transcription REST (L13)
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

## 25-lab implementation contract

Every row supplies the compact **what/why → prereqs/code path → output → use, security, cost, and production boundary** that applies while reading the deeper lesson walkthrough. “Do not use” means the runnable sample does not prove that broader scenario.

| Lab | What / why | Prereqs and code path → expected output | Use, security, cost, and production boundary |
|---:|---|---|---|
| 01 | Prompt-defined NER for novel business categories. | `DEFAULT_MODEL`; `openai_client()` → `responses.create()` → `output_text` intended as JSON. | Use flexible extraction; do not use unvalidated prose as machine data. Model tokens; schema-validate, evaluate hallucinations, redact telemetry. |
| 02 | Prompt-defined topic sentiment/rationale. | Model deployment; ticket + system instruction → Responses output. | Use explanations/custom topic grouping; do not use as sentiment ground truth. Model tokens; test bias/language coverage and avoid sensitive ticket logs. |
| 03 | Tone-preserving text translation. | Model deployment; source plus target-language system prompt → formatted model text. | Use nuanced, reviewed low-volume text; do not use bulk/document translation. Token cost; validate terminology, privacy, locale, and human-review high-impact output. |
| 04 | Text Translation v3 for repeated target languages. | `TRANSLATOR_RESOURCE_ID`, Entra role; token + ARM-ID header → global `/translate` → `[to] text`. | Use plain-text translation; do not use documents/glossary implementation. Character cost; redact text, use managed identity, validate locale/output and network/RBAC. |
| 05 | Prebuilt text PII spans and masked copy. | `LANGUAGE_ENDPOINT`; `recognize_pii_entities()` → entities/`redacted_text`. | Use detection as a privacy signal; do not use as compliance certification or document/conversation PII path. Transaction cost; test misses, minimize retention/access, never disclose raw input. |
| 06 | Detect primary language before routing. | Language endpoint; `detect_language()` → name/code/confidence. | Use route selection; do not use low-confidence short text as fact. Transaction cost; define unknown threshold, fallback, and privacy-aware logging. |
| 07 | Prebuilt NER with fixed categories/confidence. | Language endpoint; `recognize_entities()` → category/subcategory/confidence. | Use high-volume standard NER; do not use it for unsupported custom labels. Transaction cost; validate errors, confidence thresholds, locale, and Custom NER evaluation. |
| 08 | Discover Language MCP tool contract. | Versioned `LANGUAGE_MCP_URL`, Entra; streamable HTTP initialize → `list_tools()`. | Use tool inventory; do not use discovery as invocation authorization. Preview/network cost; allowlist tools, review server retention/DNS/RBAC. |
| 09 | Give a Prompt Agent Language MCP tools. | L08 plus Foundry connection/project role/model; `MCPTool` → agent version → Responses agent reference. | Use agent-selected Language capabilities; do not use model tool choice as authorization. Agent/model cost; validate connection, tool data boundary, approvals, cleanup/version lifecycle. |
| 10 | Extract health entities asynchronously. | Language endpoint; `begin_analyze_healthcare_entities()` → poller result/entities. | Use extraction aid; do not use diagnosis/clinical decision. Transaction cost; approved health-data process, minimum access/retention, human clinical validation. |
| 11 | One-file synchronous Fast STT. | WAV, endpoint or valid region fallback, Entra; multipart POST → first phrase/empty string. | Use short file request/response; do not use streaming/large-file pipeline. Speech cost; validate MIME/limits, retry classified failures, protect transcript/audio. |
| 12 | Continuous microphone STT. | Speech endpoint, microphone permission; `SpeechRecognizer` events → final text. | Use live captions/dictation prototype; do not use unattended production capture. Speech cost; capture consent, device choice, partials/reconnect/interrupt cleanup and transcript policy. |
| 13 | Async container batch STT. | Region, read/list container SAS; submit → poll with backoff → download → delete job/results. | Use bounded backlog processing; do not use without durable state/output copy. Speech/Blob cost; least SAS, storage lifecycle, reconcile interruption and queue/throttle. |
| 14 | Plain-text neural TTS to WAV. | Speech endpoint; voice config → synthesizer → generated WAV or cleanup. | Use standard voice prototype; do not use a voice-availability or acceptance guarantee. Speech cost; verify result/voice locale, protect generated audio, handle retries/errors. |
| 15 | SSML/HD voice control. | L14 plus supported voice/style; SSML → synthesizer → generated WAV or cleanup. | Use prosody/style experiments; do not use invalid XML/unsupported style in production. Speech cost; validate SSML/locale, accessibility, review spoken output. |
| 16 | Recognize and translate one spoken utterance. | Region, microphone, Entra; `TranslationRecognizer` → source/French text. | Use speech-to-text translation; do not use it as Azure Translator text API. Speech cost; consent, locale/target validation, continuous/reconnect design. |
| 17 | Preview MAI file transcription with phrase biasing. | Speech endpoint/WAV/preview support; multipart Fast route + `enhancedMode` → phrases. | Use known-term transcription evaluation; do not use phrase list as tuning/diarization. Preview Speech cost; test region/model/accuracy and protect audio/transcript. |
| 18 | Voice Live with a temporary Prompt Agent. | Project + Voice Live endpoint/model/roles; agent readiness → PCM append/commit → events → delete version. | Use protocol demonstration; do not use as full voice client. Agent/Voice Live cost; consent, cleanup, frame pacing, playback/reconnect, redacted telemetry. |
| 19 | Route SDK STT to deployed Custom Speech endpoint. | Speech endpoint, model GUID, test WAV; set `endpoint_id` → one result. | Use domain-model consumption; do not use as training/quality evidence. Speech cost; train/test WER, deployment/logging lifecycle, secure audio and rotate endpoint. |
| 20 | Sentiment plus target/assessment pairs. | Language endpoint; `analyze_sentiment(... opinion_mining=True)` → document/sentence/opinions. | Use structured opinions; do not use as a personnel/customer decision. Transaction cost; test domain/language bias and retirement/migration plan. |
| 21 | Speech MCP preflight/discovery. | Configured URL; local preflight reads it, or `--run` validates URL and uses an Entra session → tool list. | Use contract inventory; do not use discovery as tool approval. Preview/network cost; allowlist, backend authorization, private DNS/egress review. |
| 22 | Guarded keyless Translator Text request. | ARM ID/role/reviewed text; local preflight or shared client → translations. | Use reviewed text; do not use documents or secret text. Character cost; managed identity, Key Vault for exceptions, residency/output review. |
| 23 | Document Translation submit/inspect/cancel. | Endpoint, runtime key, source `r`/`l` and target `w`/`l` SAS; `--apply` → operation status/URL. | Use owned document batches; do not use as a storage or polling system. Batch/Blob cost; secret SAS/key, target lifecycle, job persistence, private network. |
| 24 | Voice Live PCM WAV to raw PCM. | WSS endpoint, supported model, valid WAV/new output; chunk/decode deltas → `.pcm`. | Use protocol smoke test; do not use as microphone/playback client. Voice cost; consent, codec metadata, session bounds, reconnect/cancel and retention. |
| 25 | Local configuration governance reminder. | None; `settings()` flags → `No cloud calls made.` | Use release preflight; do not use as health/compliance proof. Configure Monitor/IaC/RBAC/network/retention/budgets separately. |

---

# Lesson 01 — LLM NER (Generative Path)

**You'll learn:** entity extraction via a system prompt on the Responses API; the free-form counterpart to L07's discriminative Language SDK path. **Prereqs:** `DEFAULT_MODEL` deployed. **Time:** ~5 min.

**Concept:** Describe the entity categories you want in a system prompt; the model is asked to return JSON. It is flexible on categories your data cares about (`ticket_id`, `sla_tier`, `monetary_amount` — none of which Azure Language's prebuilt NER knows).

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

**Expected output:** model text that is intended to be JSON with an entity list (Sarah Chen / Acme Logistics / TKT-1042 / Gold / Northwind Connect / $500) and topics. Parse it only after validating it.

**Key points:**
- The current code asks for JSON in prose only. For a machine consumer, add a
response schema and validate the parsed result; see Domain 2 L07. Do not assume prompt wording alone guarantees valid JSON.
- LLM NER can invent categories your data doesn't have. Great for novelty;
validate it before automating a consequence.
- Compare with L07 — same ticket, a fixed service schema and confidence
signals rather than prompt-defined categories.

---

# Lesson 02 — LLM Sentiment (Generative)

**You'll learn:** per-topic sentiment + overall tone from a prompt; the LLM alternative to Azure Language Sentiment. **Prereqs:** L01 works. **Time:** ~5 min.

**Concept:** Ask the model to break a message into concerns/topics and score each one (sentiment + intensity + rationale). Something Azure Language's Sentiment Analysis + Opinion Mining does structurally — but the LLM version can explain its reasoning in prose.

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

**Expected output:** several per-topic entries (SLA breach → frustrated, Marcus's help → grateful) + an overall tone.

**Key points:**
- Use Azure Language `SentimentAnalysis` + `opinionMining=true` for cost + structured spans; use LLM for explainability.
- Prompt matters — the system prompt is where you enforce the output shape.

---

# Lesson 03 — LLM Translation

**You'll learn:** LLM translation that preserves tone and register; a soft alternative to Azure Translator when nuance matters. **Prereqs:** L01 works. **Time:** ~5 min.

**Concept:** Ask the model to translate while keeping tone/register (formal, urgent, casual). Contrast with L04's deterministic Translator Text REST request for selected target languages.

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
- LLM handles idioms and register; L04 demonstrates deterministic Text Translation output.
- Prompt-force the output format — no "Sure, here's the translation..." preamble.

---

# Lesson 04 — Azure Translator (REST)

**You'll learn:** read a Translator Text v3 REST response containing multiple targets. **Prereqs:** Translator resource, `az login` (or workload/managed identity), the appropriate Translator/Cognitive Services data role, and full `TRANSLATOR_RESOURCE_ID` in `.env`. No `TRANSLATOR_ENDPOINT` setting is used: the helper calls the documented global route with Entra bearer token plus `Ocp-Apim-ResourceId`. **Time:** ~5 min.

**Concept:** Translator is a separate REST service. The shared helper POSTs `[{"Text": text}]` to the global `/translate` endpoint with `api-version=3.0`, one `from` parameter, and repeated `to` parameters. A successful response is a list: each input item contains its `translations` list. The script does not implement glossary, document translation, or custom translation configuration.

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
- The shared helper validates the full Translator ARM ID before sending it in
`Ocp-Apim-ResourceId`; do not put keys in this sample.
- The response is a list, so read `result[0]["translations"]`; its language
key is `to`, not `language`.
- For document-level translation (PDF, DOCX), use the **Document Translation** API on the same service.
- **Speech Translation is NOT Azure Translator** — different service (see L16).

---

# Lesson 05 — Azure Language — PII Detection

**You'll learn:** text PII detection plus service-produced redaction through the Language SDK. **Prereqs:** `LANGUAGE_ENDPOINT` in `.env`. **Time:** ~5 min.

**Concept:** `recognize_pii_entities` returns both:
- `entities` — spans with category (Person / Email / Phone / SSN / ...) + confidence,
- `redacted_text` — the original text with PII masked.

This is a prebuilt detection feature, not a full privacy/compliance control. GPT can also miss or alter sensitive content; neither sample substitutes for data governance, evaluation, and human review.

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
sensitive data is absent. Do not label it “safe” without measuring detection quality and applying your retention/access policies.
- For domain-specific identifiers, evaluate a custom NER model or a
purpose-built rule/model pipeline. An LLM can help classify novel patterns, but it does not provide a compliance guarantee.

---

# Lesson 06 — Language Detection

**You'll learn:** identify a document's primary language and confidence score; useful as a router step before invoking language-specific tools. **Prereqs:** L05 works. **Time:** ~3 min.

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

**You'll learn:** prebuilt NER with fixed categories, confidence scores per entity, and optional subcategories (Person → EMPLOYEE, Location → CITY, ...). **Prereqs:** L05 works. **Time:** ~5 min.

**Concept:** `recognize_entities()` returns categorized entities with subcategories and confidence. Contrast with L01's LLM path: this gives a documented fixed schema; L01 can request novel categories. Confidence is a model signal, not an audit conclusion or accuracy guarantee.

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

**You'll learn:** return document and sentence sentiment, then associate an opinion assessment with its target. Run this after L07, before the MCP lessons. **Prereqs:** `LANGUAGE_ENDPOINT` in `.env`. **Time:** ~5 min.

**Concept:** `analyze_sentiment(..., show_opinion_mining=True)` returns positive, neutral, negative, or mixed document and sentence labels with confidence scores. Opinion mining adds targets and assessments; for example, it can associate `frustrating` with `onboarding process`.

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

**Expected output:** sentence sentiment plus target/assessment pairs, such as `onboarding process (negative): frustrating (negative)`.

**Key points:**
- Opinion mining is enabled by `show_opinion_mining=True`; it isn't a
separate Language task.
- This feature has a published retirement date of March 31, 2029. Prefer
Foundry models for new production workloads.
- L02 remains useful when you need free-form rationale or custom topic
grouping rather than fixed sentiment results.

---

# Lesson 08 — List Language MCP Tools

**You'll learn:** discover the tools exposed by the Azure Language MCP server; the exam expects you to know MCP is available for Language + Speech. **Prereqs:** `LANGUAGE_MCP_URL` in `.env`; `mcp` Python package installed. Language MCP is preview. L08 makes a direct authenticated client call; it does not prove that a Foundry project has the connection required by L09. **Time:** ~5 min.

**Concept:** The repository configures Language and Speech MCP URLs, but this lesson discovers **Language** only. Language MCP is a preview endpoint that exposes Language capabilities as agent tools. It reduces custom REST plumbing for an MCP-compatible consumer; it does not remove authentication, authorization, data-sharing review, or preview risk.

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
supplies a different `/speech/mcp` URL, but this directory does not verify its authentication or tool list.
- Use MCP when the tool consumer is another agent or an off-Azure client.

---

# Lesson 09 — Language MCP Inside a Foundry Agent

**You'll learn:** attach the Language MCP server to a Prompt Agent as an `McpTool`; let the model pick which language tool to invoke per turn. **Prereqs:** L08 works; configure the Foundry project connection required for Language MCP authentication. The code does not create that connection. **Time:** ~5 min.

**Concept:** Same MCP endpoint, but wrapped as an `McpTool` on a registered agent. The agent's system prompt tells it which class of questions map to which tool.

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

**You'll learn:** extract clinical entities (medication, dosage, condition, symptom) and inspect returned normalized text when present. **Prereqs:** L05 works. **Time:** ~5 min.

**Concept:** `begin_analyze_healthcare_entities` is async (poller-based). Returns clinical entities with `category`, `confidence_score`, and sometimes `normalized_text`. It is an extraction aid, not a diagnosis, coding decision, or clinical validation workflow. Handle health data only under an approved privacy, access, and human-review process.

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

**You'll learn:** synchronous transcription of a single audio file via the Fast Transcription REST endpoint. **Prereqs:** `SPEECH_ENDPOINT` in `.env` or a valid matching `SPEECH_REGION` for regional fallback; `_shared/sample_data/audio/conversation.wav` present. **Time:** ~5 min.

**Concept:** POST an audio file to `/speechtotext/transcriptions:transcribe?api-version=2025-10-15` with a JSON `definition` describing locales. Response is the transcript in one call. Limits: ~2 hr / 300 MB per file.

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
- **API version:** `2025-10-15`. `_endpoint_base()` uses configured Speech
endpoint or safely derives `https://<region>.stt.speech.microsoft.com`.
- `definition` is multipart JSON — locales, diarization flags, custom endpoint id all go here.
- Fast Transcription does NOT support real-time streaming — use L12 for that.

---

# Lesson 12 — Real-Time STT (Streaming)

**You'll learn:** continuous recognition from the default microphone via the Speech SDK's `SpeechRecognizer`. **Prereqs:** `SPEECH_ENDPOINT`; microphone access on your machine. `SPEECH_REGION` is not read by this script. **Time:** ~5 min.

**Concept:** `SpeechRecognizer` with `AudioConfig(use_default_microphone=True)` subscribes to `recognized` events. `start_continuous_recognition()` runs until you call `stop_continuous_recognition()`. Good for meeting transcription, live captions, dictation.

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

**You'll learn:** submit many audio files at once via the async Speech REST endpoint; poll until done; list and download each transcription JSON file. **Prereqs:** `SPEECH_REGION` in `.env`; runtime-only `BATCH_STT_CONTAINER_SAS` set to a Blob container SAS with read and list permissions. **Time:** ~30 min (batch runs in the background, region-serial).

**Concept:** Three steps:
1. POST `/speechtotext/transcriptions?api-version=2024-11-15` with the
container SAS + config.
2. Poll `GET <returned job URL>` until `status = Succeeded`.
3. GET the `links.files` URL, select files where `kind` is `Transcription`,
then GET each file's `links.contentUrl`.

Use for backlogs, weekly archives, and work with no interactive caller. Batch scheduling is best effort: files in a job can process concurrently, but jobs can queue. Spread submissions and do not infer throughput from this single-job sample.

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
    r = httpx.post(
        f"{_base_url()}/speechtotext/transcriptions?api-version=2024-11-15",
        headers=_headers(), json=body,
    )
    return r.json()["self"]

def _wait(job_url: str) -> dict:
    attempt = 0
    while True:
        response = httpx.get(job_url, headers=_headers())
        body = response.json()
        if body["status"] in ("Succeeded", "Failed", "Cancelled"):
            return body
        delay = _poll_delay(response.headers, attempt)
        print(f"status={body['status']} — waiting {delay}s")
        time.sleep(delay)
        attempt += 1

def _print_transcripts(files_url: str) -> None:
    files = httpx.get(files_url, headers=_headers()).json()
    for item in files["values"]:
        if item["kind"] != "Transcription":
            continue
        result = httpx.get(item["links"]["contentUrl"]).json()
        print(item["name"], result["combinedRecognizedPhrases"])
```

**Expected output:** job URL, `status=Running — waiting <60–600>s` polls, then one printed transcription per result file. The `finally` block deletes the remote job and its service-managed results.

**Key points:**
- The current script uses `api-version=2024-11-15`, not the older v3.2 route.
- `diarizationEnabled` requests per-speaker labels ("Speaker 1", "Speaker 2")
in the transcript; validate supported configuration and output for your locale and audio.
- `links.files` is an index, not a transcript. Download each
`kind: Transcription` item's `links.contentUrl`.
- `_poll_delay()` honors `Retry-After` and otherwise uses bounded exponential
delay. Copy approved results before cleanup; a production job must persist its state and reconcile client interruption.
- Batch does not need a custom endpoint even when using a Custom Speech model (unlike real-time).

---

# Lesson 14 — TTS Neural Voice

**You'll learn:** synthesize speech with a neural voice — plain text in, WAV out. **Prereqs:** `SPEECH_ENDPOINT` in `.env`. **Time:** ~3 min.

**Concept:** `SpeechSynthesizer` writes audio to a file or stream. `speech_synthesis_voice_name` picks the voice. Plain text works for the selected neural voice; voice inventory and availability vary by locale and region.

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

**You'll learn:** send SSML to a selected Neural HD voice and use `<prosody>`, `<break>`, and `<mstts:express-as style="friendly">` for control. **Prereqs:** L14 works. **Time:** ~5 min.

**Concept:** The lesson's HD voice and expressive controls are requested in SSML. SSML lets you control selected words, break points, rate, and style. Quality, supported styles, and regional availability are properties to check for the selected voice, not guarantees from this sample.

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

**You'll learn:** `TranslationRecognizer` recognizes speech AND translates in one call. Different service from Azure Translator. **Prereqs:** `SPEECH_REGION` in `.env`; mic access. **Time:** ~5 min.

**Concept:** `speechsdk.translation.TranslationRecognizer` uses the Speech SDK for continuous or one-shot translation from audio. Set the source language, add one or more `target_language`s, invoke; result carries the recognized source text AND every requested translation.

**Code:**

```python
# 16_speech_translation.py (excerpt)
token = DefaultAzureCredential().get_token(_SCOPE).token
cfg = speechsdk.translation.SpeechTranslationConfig(
    auth_token=token, region=speech_region()
)
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

**You'll learn:** file transcription with `mai-transcribe-1.5` through the LLM Speech API, including phrase-list entity biasing. **Prereqs:** `SPEECH_ENDPOINT` in `.env`; sample audio. **Time:** ~10 min.

**Concept:** MAI-Transcribe is a preview speech-recognition model. L17 uses the `mai-transcribe-1.5` enhanced mode on the same REST route as Fast Transcription. The model supports a phrase list to bias named entities and can support `transcribeStyle`; the checked-in request does not set a style. It doesn't support prompt-tuning or diarization.

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

**Expected output:** transcript with phrase-list terms such as `Northwind Connect` recognized accurately when the audio contains them.

**Key points:**
- This lesson uses REST API version `2025-10-15`; verify regional model
availability and the current preview contract before depending on it.
- `mai-transcribe-1.5` is preview-only. Confirm model and regional
availability before relying on it.
- A phrase list isn't a prompt and doesn't replace Custom Speech training.

---

# Lesson 18 — Voice Live protocol demo for a Prompt Agent

**You'll learn:** connect a WebSocket to a Foundry Prompt Agent, send prerecorded PCM audio, and inspect Voice Live events. **Prereqs:** `VOICE_LIVE_ENDPOINT` in `.env`; `PROJECT_ENDPOINT` in `.env`. **Time:** ~15 min.

**Concept:** Voice Live can stream audio to an agent and return audio deltas. This lesson is deliberately protocol-only: it sends the bundled 16-kHz mono PCM16 sample, prints events, and stops at `response.done`. It does **not** capture microphone input, decode `response.audio.delta`, or play audio. It creates a Prompt Agent whose model is `DEFAULT_MODEL`; it is therefore not accurate to describe this request as model-free.

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
    agent = _ensure_agent(project)        # inline create — no portal setup

    project_name = settings().project_endpoint.rstrip("/").split("/")[-1]
    token = DefaultAzureCredential().get_token(_SCOPE).token
    url = (
        f"{settings().voice_live_endpoint}"
        f"?api-version=2026-04-10&agent_id={agent.id}&project_id={project_name}"
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
    finally:
        project.agents.delete_version(agent.name, agent.version)
```

**Expected output:** several WebSocket events (`session.created`, `input_audio_buffer.committed`, `response.audio.delta`, `response.done`). Audio deltas are logged only; no sound plays.

**Key points:**
- **URL correction:** `/voice-live/realtime?api-version=2026-04-10`; params `agent_id` + `project_id` (not `agent_name`).
- For non-agent scenarios pass a supported `model` query parameter instead of
the agent parameters. Confirm model/region support; this README does not claim a particular model is available.
- Two subdomain options: `services.ai.azure.com` (current) or `cognitiveservices.azure.com` (older resources).
- `websockets` 15 uses `additional_headers`, not `extra_headers`.
- The temporary agent version is deleted in `finally`; still inventory
interrupted runs and use a controlled version/reuse/cleanup policy.
- Build a microphone capture, PCM framing, audio-delta decoding, and output
playback loop before describing an application as end-to-end voice.

---

# Lesson 19 — Custom Speech Model

**You'll learn:** point the Speech SDK at a Custom Speech model you've trained in Speech Studio — same code, one extra config line. **Prereqs:** trained + deployed Custom Speech model; `CUSTOM_SPEECH_ENDPOINT_ID` in `.env` (GUID). **Time:** ~5 min (assuming model already deployed; training itself is separate).

**Concept:** Setting `speech_config.endpoint_id = "<guid>"` routes recognition to your custom acoustic/language model. Every other SDK call is identical to standard STT. Use for domain jargon, accented speech, unusual product names.

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
    result = recognizer.recognize_once_async().get()
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return result.text
    return f"[recognition did not complete: {result.reason}]"
```

**Expected output:** one recognition result routed to the configured endpoint. It might improve domain-specific terms, but this sample has no base-model comparison or word-error-rate measurement and cannot demonstrate improvement.

**Key points:**
- Batch Transcription does NOT need a custom endpoint even when using your custom model — you reference the model directly in the batch request.
- MAI-Transcribe phrase lists (L17) can improve recognition of known terms
without training.
- Custom Speech has three stages: **train** (Speech Studio, needs labeled
data) → **test** (for example, word error rate against a held-out set) → **deploy** (get endpoint GUID). L19 implements only the final consume step.

---

# Lesson 21 — Speech MCP preflight and discovery

Run local-only preflight:

```bash
uv run python 04-text-and-speech/21_speech_mcp_preflight.py
```

Discover tools only after review:

```bash
uv run python 04-text-and-speech/21_speech_mcp_preflight.py --run
```

**What and why.** MCP exposes remote Speech capabilities as tools for an MCP-compatible client. It can reduce one-off REST adapters, but it does not make remote tools trusted, authorized, stable, or free. This lesson makes the safe first step explicit: default mode makes no network call; `--run` only lists tool metadata and never invokes a tool.

**Prereqs.** Set `SPEECH_MCP_URL` to documented HTTPS endpoint including `api-version`; use an Entra identity with the documented least-privilege Speech/Cognitive Services data role. Preview availability, region, project connection requirements, DNS, firewall, and service support remain separate checks. Do not use localhost as a stand-in for a remote client path.

**Code path and output.** `preflight()` reads configuration only. With `--run`, `speech_mcp_url()` rejects non-HTTPS, localhost, and unversioned URLs; `DefaultAzureCredential` obtains a Cognitive Services token; streamable HTTP initializes `ClientSession`; `list_tools()` prints each name and description. Expected output is `Discovered N Speech MCP tool(s); none invoked.`

**Use / do not use.** Use to inventory an approved preview server before an agent/tool integration. Do not use it as a permission check, a production health probe, or unattended approval for a discovered tool.

**Security, cost, production pitfalls.** Treat server descriptions and tool results as untrusted input. Allowlist operation names, validate arguments, reauthorize against end-user identity in the backend, bound time/result size, and require approval for side effects. Discovery can incur service/network usage; invoked tools may incur Speech/model costs. Pin and regression-test the preview contract, test private DNS/egress from actual runtime, and log only redacted correlation metadata.

**AI-103/interview takeaway.** MCP standardizes tool transport; it does not replace RBAC, application authorization, network reachability, or tool policy.

---

# Lesson 22 — Translator secure configuration

```bash
uv run python 04-text-and-speech/22_translator_secure_config.py
uv run python 04-text-and-speech/22_translator_secure_config.py \
  --run --text "Approved sample." --source en --targets fr,ja
```

**What and why.** This is a guarded Text Translation v3 entry point for reviewed text. It demonstrates keyless global-endpoint Microsoft Entra authentication through the shared Translator client and keeps routine translation separate from L23's document-batch/key contract.

**Prereqs.** `az login` locally or managed/workload identity in Azure; `TRANSLATOR_RESOURCE_ID` set to the full Translator ARM ID; appropriate Translator/Cognitive Services data role; and reviewed text only. The global endpoint uses the resource ID header so identity is routed to the intended Translator resource. A custom domain, private endpoint, or residency requirement may require a different supported design; validate current service documentation first.

**Code path and output.** Default `preflight()` prints `No cloud calls made.` With `--run`, `_language_tags()` limits source/target input to language-tag syntax, then `translate()` receives text, target list, and source tag. The shared client requests an Entra token, validates ARM-ID shape, POSTs `/translate?api-version=3.0` with repeated `to` parameters and `Ocp-Apim-ResourceId`, then prints `[fr] ...` and `[ja] ...`.

**Use / do not use.** Use for controlled plain-text translation and a keyless-auth smoke path. Do not use for documents, glossaries, keys in source, sensitive text without data approval, or a claim that translation is semantically/culturally correct.

**Security, cost, production pitfalls.** Translator charges by characters. Redact payloads from logs/traces, use managed identity where supported, keep role scope narrow, and place exceptional secrets in Key Vault—not source or environment files. Validate source/target locale behavior, terminology, unsupported languages, rate limits, output quality, residency, private DNS, and retention. Human-review regulated, legal, medical, safety-critical, or customer-facing translations.

**AI-103/interview takeaway.** Entra token is insufficient for global Translator endpoint: documented global flow also requires the target resource ARM ID in `Ocp-Apim-ResourceId`.

---

# Lesson 23 — Document Translation batch operations

Preflight first:

```bash
uv run python 04-text-and-speech/23_translator_batch_operations.py
```

Apply only in a reviewed nonproduction environment:

```bash
TRANSLATOR_DOCUMENT_KEY='<runtime-only-secret>' \
uv run python 04-text-and-speech/23_translator_batch_operations.py --apply \
  --endpoint https://<translator>.cognitiveservices.azure.com \
  --source-url '<read-sas>' --target-url '<write-sas>' --language fr
```

**What and why.** L23 manages Document Translation lifecycle: submit a Blob-to-Blob batch, inspect its `operation-location`, or cancel it. Document Translation is not L04 with a larger string: it has source/target storage, asynchronous state, output-retention, and API-key requirements.

**Prereqs.** Use a supported Translator resource endpoint; source and target HTTPS Blob SAS URLs; `r` and `l` permissions on source and `w` and `l` on target; a unique target container for every batch; and `TRANSLATOR_DOCUMENT_KEY` supplied only at runtime or retrieved from Key Vault. Read current document translation requirements for file types, regions, managed identity alternatives, and limits. This lesson's `2026-03-01` request contract explicitly uses the document API key; do not confuse it with L04's Entra Text Translation client.

**Code path and output.** Default `preflight()` makes no request. `--apply` validates the HTTPS/SAS shape without printing credentials. Submission builds `inputs[].source.sourceUrl` and `targets[].targetUrl/language`, POSTs `/translator/document/batches?api-version=2026-03-01`, and prints the returned `operation-location`. Later `--operation-url` GETs status; adding `--cancel` DELETEs it. The client rejects an operation URL on another host.

**Use / do not use.** Use for controlled document batches with a durable job owner. Do not use it as a text-translation shortcut, an automatic completion poller, an output-content reviewer, or a storage lifecycle manager.

**Security, cost, production pitfalls.** Both SAS URLs and key are bearer secrets: do not put them in shell history, CI logs, tickets, or telemetry. Use per-batch containers, short expiry, HTTPS, least privileges, storage encryption/retention rules, private DNS/egress tests, and Key Vault access through managed identity. Batch submission/output is billable and persists in Blob; retain operation ID securely, poll with backoff, handle terminal `Succeeded`/`Failed`/`Cancelled`/`ValidationFailed`, validate output and cleanup it according to policy.

**AI-103/interview takeaway.** SAS grants delegated Blob access, not Translator authorization; managed identity/RBAC and network design for application, Translator, and Storage remain independent boundaries.

---

# Lesson 24 — Voice Live PCM file-to-file flow

```bash
uv run python 04-text-and-speech/24_voice_live_audio_flow.py
uv run python 04-text-and-speech/24_voice_live_audio_flow.py --run \
  --model <supported-deployment> \
  --audio _shared/sample_data/audio/northwind_support_message.wav \
  --output 04-text-and-speech/voice-response.pcm
```

**What and why.** L24 turns prerecorded audio into Voice Live request frames and writes returned audio deltas as raw PCM. Unlike L18's Prompt-Agent protocol example, it uses `model=<name>` query parameter and demonstrates input chunking plus `response.audio.delta` decoding. It remains file-to-file: no microphone capture, browser/WebRTC transport, transcript store, or speaker playback.

**Prereqs.** `VOICE_LIVE_ENDPOINT` must be `wss://...`; select a model supported by Voice Live in resource/region; authenticate with Entra `https://ai.azure.com/.default` scope and matching narrow roles; provide a new writable `.pcm` output path; and use authorized mono, 16-bit PCM WAV at 16 or 24 kHz. Confirm consent, retention, and voice/model availability before streaming real audio.

**Code path and output.** Default `preflight()` has no cloud call and can locally validate audio. `pcm_wav()` enforces channel, sample width, and rate; `voice_live_url()` overwrites query with API version/model; `session_update()` requests PCM16 input/output and selected voice. `run()` obtains a token, opens WebSocket with `additional_headers`, base64-sends 256 KiB chunks, commits/creates response, decodes each audio delta, and refuses to overwrite existing output. Expected output: `Saved <N> PCM bytes to <path>.`

**Use / do not use.** Use as a bounded protocol smoke test and to learn audio frame contracts. Do not use as a production voice client, a WAV exporter, or evidence that real-time latency, interruption, accessibility, or transcription requirements are met.

**Security, cost, production pitfalls.** Audio/transcripts can be sensitive. Do not log base64, tokens, endpoints with secrets, or returned audio; use managed identity, scoped roles, consent, retention/deletion, and redacted telemetry. Voice Live/model use is billable; cap session duration/output, handle error/cancel/reconnect/timeout, pace frames, preserve codec metadata, and test private network DNS/egress from runtime. Wrap PCM with correct format metadata before playback.

**AI-103/interview takeaway.** A WebSocket stream requires explicit audio format, frame lifecycle, identity, model/agent selection, output handling, and cost/privacy controls—not only a speech recognizer.

---

# Lesson 25 — Monitoring and governance preflight

```bash
uv run python 04-text-and-speech/25_text_speech_governance_preflight.py
```

**What and why.** This no-cloud-call preflight exposes whether local Application Insights, Speech, Voice Live, and Speech MCP settings exist. It is a release-review reminder that observability, privacy, network, RBAC, retention, and cost are distinct from one successful API call.

**Prereqs and code path.** None beyond runnable repository environment. `preflight()` reads `settings()` and returns four booleans; `main()` prints them plus monitoring/governance handoff. Expected output starts `Text and speech monitoring/governance preflight. No cloud calls made.`

**Use / do not use.** Use before a production review or CI preflight. Do not use as connectivity, authorization, policy, compliance, private-DNS, or health proof; it changes no Azure setting.

**Security, cost, production pitfalls.** Create diagnostic settings, budget alerts, policy, private endpoints/DNS, role assignments, Key Vault secret references, retention/deletion rules, and alert ownership through reviewed portal change control or IaC—not this script. Export correlation ID, service, region, deployment/model/analyzer version, operation state, latency, throttle/error class, and cost estimate; never raw prompts, translations, audio, transcripts, SAS URLs, tokens, or keys without explicit approved governance. Alert on 401/403/404/429, batch terminal failure, anomalous access, latency, spend, and retention failure.

**AI-103/interview takeaway.** Monitoring measures behavior; it does not grant access, prove correctness, or make data handling compliant.

---

## Coverage gaps and best next lessons

The 25 scripts demonstrate narrow API paths. Local Foundry documentation identifies these high-value additions; they are **not** claimed as implemented by this directory.

| Priority | Missing lesson | Why it matters | Local source |
|---|---|---|---|
| 1 | Translator authentication integration test | L04/L22 now send `Ocp-Apim-ResourceId`; they still need a controlled live test for ARM-ID, RBAC, custom-domain/global routing, error classification, and redacted telemetry. | [Translator Entra authentication](../.context/azure-ai-docs/articles/ai-services/translator/how-to/microsoft-entra-id-auth.md) |
| 2 | Conversation and document PII | L05 covers only synchronous strings. Contact-center transcripts and native documents require different PII input models and workflows. | [Conversation PII](../.context/azure-ai-docs/articles/ai-services/language-service/personally-identifiable-information/conversation-pii-overview.md), [Document PII](../.context/azure-ai-docs/articles/ai-services/language-service/personally-identifiable-information/document-based-pii-overview.md) |
| 3 | Custom NER training and evaluation | L01 prompt NER and L07 prebuilt NER leave out the supported middle path: labeled domain categories with held-out evaluation. | [Custom NER](../.context/azure-ai-docs/articles/ai-services/language-service/custom-named-entity-recognition/overview.md) |
| 4 | Runtime phrase-list accuracy | L17 has the MAI-specific phrase list, but no lesson shows the standard Speech runtime phrase list for Fast, real-time, or Voice Live, nor its limit that batch transcription does not support. | [Phrase lists](../.context/azure-ai-docs/articles/ai-services/speech-service/improve-accuracy-phrase-list.md) |
| 5 | Speech MCP approved invocation | L21 safely discovers runtime tools but intentionally invokes none. Add execution only after tool allowlists, approval, authorization, network, retention, and preview-contract review. | [Language tools and agents](../.context/azure-ai-docs/articles/ai-services/language-service/concepts/foundry-tools-agents.md) |
| 6 | Real-time audio source and reliability | L12 teaches only a default mic. A practical lesson needs `PushAudioInputStream`/`PullAudioInputStream`, audio format validation, reconnect behavior, and cancellation. | [Audio input streams](../.context/azure-ai-docs/articles/ai-services/speech-service/how-to-use-audio-input-streams.md) |
| 7 | Voice Live client delivery | L18 proves a small WebSocket exchange, not a voice client. A next lesson should use the recommended browser/mobile transport where appropriate, add consent, frame pacing, playback, interruption, and failure handling. | [Voice Live WebRTC](../.context/azure-ai-docs/articles/ai-services/speech-service/voice-live-webrtc.md), [Voice Live customization](../.context/azure-ai-docs/articles/ai-services/speech-service/voice-live-how-to-customize.md) |
| 8 | Current Translator API comparison | L04 deliberately stays on Text Translation v3. A separate lesson can compare the newer GA API only after choosing its contract and migration path. | [Text Translation 2026-06-06 REST guide](../.context/azure-ai-docs/articles/ai-services/translator/text-translation/2026-06-06/rest-api-guide.md) |

Also absent: schema-constrained LLM output and evaluation for L01–L03, batch-job durability and cleanup for L13, TTS voice/style availability checks, Custom Speech train/test lifecycle automation, and an end-to-end transcript-to-PII privacy pipeline. Add these as separate lessons rather than quietly treating these short samples as coverage.

---

# Common Exam Traps

| Trap | Truth |
|------|-------|
| "Opinion Mining uses a different `kind`" | ❌ — same `kind: SentimentAnalysis`, just pass `show_opinion_mining=True` |
| "Fast Transcription is the same as real-time STT" | ❌ — Fast = one file sync; real-time = live stream |
| "Neural HD works without SSML" | ❌ — Neural HD **requires** SSML for the good stuff; plain Neural doesn't |
| "`TranslationRecognizer` is Azure Translator" | ❌ — `TranslationRecognizer` is the Speech SDK; Azure Translator is a separate REST service |
| "L08 proves Speech MCP works too" | ❌ — L08 discovers Language only. L21 can list Speech tools, but neither discovery authorizes invocation. |
| "A redaction result proves the data is safe" | ❌ — both missed detections and application handling remain your responsibility |
| "Voice Live uses `/voice-live/v1`" | ❌ — current URL is `/voice-live/realtime?api-version=2026-04-10` |
| "Voice Live takes `agent_name`" | ❌ — takes `agent_id` + `project_id` query params (or `model` for non-agent) |
| "Fast STT api-version is `2024-11-15`" | ❌ — current `2025-10-15` |
| "MAI-Transcribe supports prompt-tuning" | ❌ — `mai-transcribe-1.5` supports phrase lists and transcript style, not prompt-tuning or diarization |
| "Custom Speech works for batch by default" | ✔ — batch can use a custom model without deploying an endpoint. Real-time DOES need the endpoint. |
| "Extractive and Abstractive summarization are the same kind" | ❌ — separate `kind` values (`ExtractiveSummarization` / `AbstractiveSummarization`) |

---

> The 30-second cheat sheet lives at the [top of this README](#30-second-domain-4-cheat-sheet) — scroll up any time an exam question makes you second-guess which lesson covers it.
