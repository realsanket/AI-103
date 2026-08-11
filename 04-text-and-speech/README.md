# Domain 4 — Text Analysis and Speech Solutions (10–15%)

> Run any lesson: `uv run python 04-text-and-speech/<file>.py` · Prereqs: `.env` filled, `az login` completed. See root [README.md](../README.md).
> **Scope warning:** these are API exercisers, not production pipelines. Outputs are evidence to validate, not decisions to act on.

---

## What this domain teaches

Three Azure services — **Language**, **Translator**, **Speech** — plus **LLM alternatives** for the same tasks. Lessons progress from prompt-based generative approaches to structured SDK/REST calls, then to advanced MCP integration, Custom Speech, Voice Live, and governance.

```
┌── Stage 1: Generative NLP baseline (01–03) ───────────────────────┐
│  LLM NER · LLM sentiment · LLM translation                        │
│  Why: understand what LLMs can do before you know what to replace  │
└────────────────────────────────────────────────────────────────────┘
         ↓ now compare structured services
┌── Stage 2: Task-specific Language + Translator (04–10, 20) ────────┐
│  Translator REST · PII · language detect · NER · sentiment         │
│  + opinion mining · Language MCP · Text Analytics for Health       │
└────────────────────────────────────────────────────────────────────┘
         ↓ text done — audio begins
┌── Stage 3: Speech to Text — three modes (11–13) ───────────────────┐
│  Fast Transcription · Real-time STT · Batch Transcription          │
└────────────────────────────────────────────────────────────────────┘
┌── Stage 4: Text to Speech + Speech Translation (14–16) ────────────┐
│  Neural voice · SSML + Neural HD · TranslationRecognizer           │
└────────────────────────────────────────────────────────────────────┘
┌── Stage 5: LLM Speech + Voice Live + Custom (17–19) ───────────────┐
│  MAI-Transcribe · Voice Live protocol · Custom Speech endpoint     │
└────────────────────────────────────────────────────────────────────┘
┌── Stage 6: Security, MCP governance, and advanced patterns (21–25)─┐
│  Speech MCP preflight · Translator secure config                   │
│  Document Translation · Voice Live PCM flow · governance preflight │
└────────────────────────────────────────────────────────────────────┘
```

---

## Service mental model

```
TEXT INPUT
  Azure Language  ────── one endpoint, task-specific methods
    recognize_entities()      → NER                [07]
    recognize_pii_entities()  → PII + redacted_text [05]
    detect_language()         → ISO code + confidence [06]
    analyze_sentiment()       → sentiment + opinion mining [20]
    begin_analyze_healthcare_entities() → clinical NER [10]

  Azure Translator ───── separate REST service (not Language)
    /translate                → text translation (multiple targets) [04, 22]
    /translator/document/batches → async document batches [23]

  LLM (Responses API) ── generative alternative
    responses.create()        → NER [01] · sentiment [02] · translation [03]

AUDIO INPUT
  Azure Speech SDK
    SpeechRecognizer          → STT (file/mic) [11, 12, 19]
    TranslationRecognizer     → STT + translate (NOT Translator) [16]
    SpeechSynthesizer         → TTS [14, 15]
  Speech REST
    /speechtotext/transcriptions:transcribe → Fast STT [11, 17]
    /speechtotext/transcriptions            → Batch STT [13]
  Voice Live WebSocket
    wss://.../voice-live/realtime           → real-time audio ↔ agent [18, 24]

MCP (preview)
  /language/mcp               → Language tools for agents [08, 09]
  /speech/mcp                 → Speech tools for agents  [21]
```

---

## Glossary

| Term | Definition |
|------|-----------|
| **Language** | Azure AI Language service. One endpoint, multiple `kind` operations. SDK methods map 1:1 to `kind` values. |
| **`kind` field** | Selects the Language feature per REST call: `EntityRecognition`, `PiiEntityRecognition`, `SentimentAnalysis`, `LanguageDetection`, `Healthcare`, etc. |
| **Discriminative NLP** | Service model trained for one task; returns documented schema with confidence scores. Language SDK uses this path. |
| **Generative NLP** | LLM + prompt; flexible categories; free-form output. Responses API. More expensive; output needs validation. |
| **Opinion Mining** | Sentiment feature that pairs a target noun with its assessments. `analyze_sentiment(..., show_opinion_mining=True)`. Same `kind` as SentimentAnalysis. |
| **Text Analytics for Health** | Extracts clinical entities (medication, dose, condition). Async poller. Not diagnosis; not compliance. |
| **Azure Translator** | Separate REST service. Text Translation (v3 `/translate`), Document Translation, transliteration, dictionary. |
| **Speech SDK** | Python bindings: `SpeechRecognizer` (STT), `SpeechSynthesizer` (TTS), `TranslationRecognizer` (speech translation). |
| **Fast Transcription** | Sync REST: POST one file → transcript in same response. API: `/speechtotext/transcriptions:transcribe?api-version=2025-10-15`. |
| **Batch Transcription** | Async REST for many files in a Blob container. Submit → poll → fetch → cleanup. |
| **Neural voice** | Standard TTS. Name like `en-US-JennyNeural`. Plain text works. |
| **Neural HD voice** | Higher-definition voice. Name contains `HD` (`AvaHDNeural`). SSML unlocks prosody and style. |
| **SSML** | Speech Synthesis Markup Language. XML for TTS: `<voice>`, `<prosody>`, `<break>`, `<mstts:express-as>`. |
| **`TranslationRecognizer`** | Speech SDK class: audio → ASR + translation. NOT the Azure Translator REST service. |
| **MAI-Transcribe** | Preview LLM-based STT model. `mai-transcribe-1.5` via the same Fast Transcription REST route with `enhancedMode`. Supports phrase lists. No prompt-tuning or diarization. |
| **Voice Live** | Real-time bidirectional WebSocket. Audio → agent → synthesized audio. URL: `wss://<resource>.services.ai.azure.com/voice-live/realtime?api-version=2026-04-10`. |
| **Custom Speech** | Train acoustic/language model in Speech Studio; deploy → GUID; set `speech_config.endpoint_id`. Real-time needs the endpoint GUID; batch does not. |
| **Language MCP** | Preview: Language capabilities exposed as MCP tools. `LANGUAGE_MCP_URL`. |
| **Speech MCP** | Preview: Speech capabilities exposed as MCP tools. `SPEECH_MCP_URL`. L21 discovers without invoking. |

---

## Setup

### Environment variables

```env
# Core (from Domain 1)
FOUNDRY_ENDPOINT=https://<project>.services.ai.azure.com/api/projects/<project>
AZURE_OPENAI_ENDPOINT=https://<resource>.openai.azure.com
DEFAULT_MODEL=gpt-4o

# Language
LANGUAGE_ENDPOINT=https://<resource>.cognitiveservices.azure.com
LANGUAGE_MCP_URL=https://<resource>.cognitiveservices.azure.com/language/mcp?api-version=2025-11-15-preview

# Translator
TRANSLATOR_RESOURCE_ID=/subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.CognitiveServices/accounts/<name>

# Speech
SPEECH_ENDPOINT=https://<resource>.cognitiveservices.azure.com
SPEECH_REGION=eastus
SPEECH_MCP_URL=https://<resource>.cognitiveservices.azure.com/speech/mcp?api-version=2025-11-15-preview

# Voice Live
VOICE_LIVE_ENDPOINT=wss://<resource>.services.ai.azure.com/voice-live/realtime

# Custom Speech (lesson 19 only)
CUSTOM_SPEECH_ENDPOINT_ID=<guid-from-speech-studio>
```

`DefaultAzureCredential` resolves to `az login` locally or managed identity in Azure. Required roles:
- **Cognitive Services User** — Language, Translator (global endpoint), Speech data-plane calls
- **Foundry User** — Prompt Agent creation in lessons 09, 18

### Safe run order

1. Run `01-plan-and-manage/07_managed_identity_agent.py` — proves Entra auth works
2. Run lessons 01–03 (LLM only, no new service needed)
3. Set `LANGUAGE_ENDPOINT` → run lessons 05–07, 10, 20
4. Set `LANGUAGE_MCP_URL` → run lesson 08, then 09 (needs Foundry project connection)
5. Set `SPEECH_ENDPOINT` + `SPEECH_REGION` → run lesson 11
6. Run lessons 12, 16 — requires microphone permission
7. Set `BATCH_STT_CONTAINER_SAS` at runtime → run lesson 13 (~30 min)
8. Run lessons 14, 15 (TTS to file)
9. Set `VOICE_LIVE_ENDPOINT` → run lesson 18, then 24 with `--run`
10. Set `CUSTOM_SPEECH_ENDPOINT_ID` → run lesson 19

### Costs and side effects

| Lesson(s) | What it writes / costs |
|-----------|----------------------|
| 01–03 | Model tokens |
| 04, 22 | Translator characters (when run) |
| 05–07, 10, 20 | Language transactions |
| 08 | Language MCP network + token |
| 09 | Agent version created + Language MCP + model tokens (agent version stays until deleted manually) |
| 11, 12, 17 | Speech recognition |
| 13 | Speech batch + Blob read; job + results deleted in `finally` — copy output first |
| 14, 15 | TTS synthesis → WAV written to `_shared/sample_data/generated/` |
| 16 | Speech translation |
| 18 | Agent version created + Voice Live + model tokens; version deleted in `finally` |
| 19 | Speech recognition via custom endpoint |
| 23 | Document Translation batch billable on `--apply`; Blob output persists until storage lifecycle removes it |
| 24 | Voice Live + model tokens on `--run`; `.pcm` file written |
| 21, 25 | No cloud calls by default |

---

## Decision tables

### Discriminative vs Generative NLP

| Dimension | Azure Language (discriminative) | Responses API (generative) |
|-----------|--------------------------------|---------------------------|
| Output | Structured spans + confidence | Free text or JSON |
| Categories | Fixed prebuilt | Anything you describe |
| Novel entity types | ✘ | ✔ |
| Multi-task per call | ✘ (one `kind`) | ✔ |
| Latency | Lower | Higher |
| Cost | Lower | Higher |

**Pick by task:**
- Prebuilt PII categories + redacted text → Language PII (05), then validate
- Prebuilt clinical entities → Text Analytics for Health (10)
- Standard NER at volume → Language NER (07, cheaper)
- Novel entity types → GPT prompt (01)
- Multi-task in one call → GPT prompt (01 or 02)

### Translation comparison

| | Azure Translator (04) | GPT prompt (03) | TranslationRecognizer (16) |
|--|-----------------------|-----------------|---------------------------|
| Input | Text | Text | Audio (mic/stream) |
| Output | Text | Text | Text (translated) |
| Best for | Multi-target, predictable pricing | Tone + register preservation | Live spoken translation |
| Doc translation | Use Document Translation API (23) | ✘ | ✘ |

### STT mode selection

```
Audio input?
  ├── Single file, sync → Fast Transcription [11]
  ├── Live mic/network stream → Real-time STT [12]
  ├── Many files async → Batch Transcription [13]
  ├── Translate audio → TranslationRecognizer [16]
  ├── Known named entities → MAI-Transcribe phrase list [17]
  ├── Real-time agent conversation → Voice Live [18, 24]
  └── Domain jargon/accents → Custom Speech endpoint [19]
```

### TTS selection

```
Audio output?
  ├── Standard quality, plain text → Neural voice [14]
  └── Best quality + prosody control → Neural HD + SSML [15]
```

---

## Lesson map

| # | File | Runnable objective | Status |
|---|------|-------------------|--------|
| 01 | `01_llm_ner.py` | NER via LLM prompt — novel entity categories | Generative; validate JSON output |
| 02 | `02_llm_sentiment.py` | Per-topic sentiment + rationale via LLM | Generative; output is free text |
| 03 | `03_llm_translation.py` | Tone-preserving translation via LLM | Generative; compare with 04 |
| 04 | `04_translator_rest.py` | Text Translation v3 REST (multi-target) | Requires Translator ARM ID + role |
| 05 | `05_language_pii.py` | PII detection + service redaction | Prebuilt categories only |
| 06 | `06_language_detect.py` | Language identification + confidence | Low confidence on short text |
| 07 | `07_language_ner.py` | Prebuilt NER — fixed categories + confidence | Fixed schema; compare with 01 |
| 20 | `20_language_sentiment.py` | Sentiment + opinion mining (structured) | Retirement March 2029 |
| 08 | `08_language_mcp_tools.py` | Discover Language MCP tool contracts | Preview; discovery only |
| 09 | `09_language_mcp_agent.py` | Language MCP tools inside a Foundry agent | Preview; needs project connection |
| 10 | `10_health_text_analytics.py` | Clinical entity extraction (async) | Not diagnosis; approved process needed |
| 11 | `11_stt_fast_file.py` | Fast Transcription — one file, sync REST | api-version=2025-10-15 |
| 12 | `12_stt_real_time.py` | Real-time STT from microphone | Requires mic permission |
| 13 | `13_stt_batch.py` | Batch Transcription — async, many files | Needs container SAS; ~30 min |
| 14 | `14_tts_neural.py` | TTS — neural voice to WAV | Check voice availability in region |
| 15 | `15_tts_ssml_hd.py` | TTS — SSML + Neural HD voice | HD voice must be available in region |
| 16 | `16_speech_translation.py` | Speech translation from mic | Requires mic; uses SPEECH_REGION |
| 17 | `17_llm_speech_preview.py` | MAI-Transcribe 1.5 + phrase list | Preview; check regional availability |
| 18 | `18_voice_live_prompt_agent.py` | Voice Live WebSocket protocol demo | Preview; protocol only, no audio playback |
| 19 | `19_custom_speech_model.py` | Custom Speech deployed endpoint | Needs model GUID from Speech Studio |
| 21 | `21_speech_mcp_preflight.py` | Speech MCP preflight + opt-in discovery | Preview; `--run` lists tools only |
| 22 | `22_translator_secure_config.py` | Translator Entra keyless auth + guard | `--run` for cloud call |
| 23 | `23_translator_batch_operations.py` | Document Translation lifecycle | `--apply` for cloud; persistent output |
| 24 | `24_voice_live_audio_flow.py` | Voice Live PCM file-to-file flow | `--run` for cloud; raw .pcm output |
| 25 | `25_text_speech_governance_preflight.py` | Monitoring + governance config check | No cloud calls; config check only |

---

## Stage 1 — Generative NLP Baseline (lessons 01–03)

These three lessons establish what LLMs can do for text analysis before comparing structured services. Run them first — they only need `DEFAULT_MODEL` and confirm your LLM endpoint works.

### 01 — LLM NER (generative path)

**Question answered:** How do you extract entity types that Azure Language NER doesn't know about?

**Background.** Azure Language's prebuilt NER covers fixed categories (Person, Organization, Location, DateTime...). A support ticket may contain domain-specific concepts like `ticket_id`, `sla_tier`, or `monetary_amount` — none of which the prebuilt model knows. The generative path: describe the categories in a system prompt and have the LLM return JSON. Flexible, but output must be schema-validated before automation.

```bash
uv run python 04-text-and-speech/01_llm_ner.py
```

**Code path.**
1. `openai_client()` → `responses.create()` with `_SYSTEM` (category definitions) + `_TICKET` as user message
2. `output_text` printed — intended to be JSON; validate before parsing

**What to watch.** Entities including `Sarah Chen` (person), `Acme Logistics` (organization), `TKT-1042` (ticket_id), `Gold` (sla_tier), `$500` (monetary_amount). If the model adds prose around the JSON, tighten the system prompt.

**Exam cues.** LLM NER = flexible categories, expensive, output needs validation. Language NER = fixed categories, cheap, structured. Both solve entity extraction differently.

**References:** [Azure AI Language overview](https://learn.microsoft.com/azure/ai-services/language-service/overview) · [Named entity recognition overview](https://learn.microsoft.com/azure/ai-services/language-service/named-entity-recognition/overview)

---

### 02 — LLM Sentiment (generative path)

**Question answered:** When does the LLM approach beat Azure Language Sentiment?

**Background.** Azure Language Sentiment returns structured labels and, with opinion mining, target+assessment pairs. The LLM alternative adds free-form rationale and custom topic grouping in one call — useful when you need to explain why a segment is negative, not just that it is. Compare with lesson 20 for the structured alternative.

```bash
uv run python 04-text-and-speech/02_llm_sentiment.py
```

**Code path.**
1. `responses.create()` with system instruction: identify concerns/topics, rate sentiment + intensity + rationale, assess overall tone
2. `output_text` printed as prose

**What to watch.** Two or more concern blocks: SLA breach → frustrated with rationale, Marcus's support → grateful. Overall tone assessment. If merged into one block, the per-topic instruction isn't landing.

**Exam cues.** LLM: rationale, custom grouping, higher cost. Language Sentiment: fixed labels, structured spans, lower cost.

**References:** [Sentiment analysis overview](https://learn.microsoft.com/azure/ai-services/language-service/sentiment-opinion-mining/overview)

---

### 03 — LLM Translation (tone-preserving)

**Question answered:** When should you use an LLM for translation instead of Azure Translator?

**Background.** Azure Translator produces flat literal output optimized for correctness and language coverage. For customer-facing text where urgency, register, and idiom matter, the LLM path preserves those qualities. Not for bulk or document translation — use lesson 04 or 23 for those.

```bash
uv run python 04-text-and-speech/03_llm_translation.py
```

**Code path.**
1. `translate(text, target_language)` builds a system prompt requesting tone-preserving translation
2. `responses.create()` → output formatted as `SOURCE LANGUAGE: ... TRANSLATION: ...`
3. `main()` runs French and Japanese

**What to watch.** The translations should feel urgent, not bureaucratic. If they sound flat, strengthen the register instruction or add a few-shot example.

**Exam cues.** GPT translation = idiom+register. Azure Translator = bulk/document. TranslationRecognizer = speech input (not text).

**References:** [Azure AI Language supported languages](https://learn.microsoft.com/azure/ai-services/language-service/concepts/language-support) · [Azure Translator overview](https://learn.microsoft.com/azure/ai-services/translator/overview)

---

## Stage 2 — Task-specific Language + Translator (lessons 04–10, 20)

Structured services for text analysis. Each lesson calls a specific Language SDK method or Translator endpoint and returns a documented schema with confidence scores.

### 04 — Azure Translator Text REST

**Question answered:** How do you translate text to multiple target languages in one call using Azure Translator?

**Background.** Azure Translator is a separate REST service — not part of Azure Language. One POST to the global `/translate` endpoint with repeated `to` parameters returns translations for all target languages simultaneously. Billing is per character. Does NOT handle documents (use Document Translation API), glossary, or tone preservation. The shared helper sends `Ocp-Apim-ResourceId` with the full Translator ARM ID for Entra authentication at the global endpoint.

```bash
uv run python 04-text-and-speech/04_translator_rest.py
```

**Code path.**
1. `translate(text, targets=["fr", "ja", "es"], source_language="en")` → POST to global `/translate?api-version=3.0`
2. Response: list of per-input items, each with `translations` list — key is `to`, not `language`
3. Print `[{to}] {text}` per target

**What to watch.** Three lines, one per language code. A 401 means `TRANSLATOR_RESOURCE_ID` is missing, malformed, or the identity lacks the documented Translator data-plane role.

**Exam cues.** Response shape: `result[0]["translations"]` — outer list = inputs, inner = targets. `to` key not `language`. Document Translation is a different API.

**References:** [Translator Text overview](https://learn.microsoft.com/azure/ai-services/translator/overview) · [Translator Microsoft Entra auth](https://learn.microsoft.com/azure/ai-services/translator/how-to/microsoft-entra-id-auth)

---

### 05 — Azure Language — PII Detection

**Question answered:** How do you detect and redact PII spans from text using the Language service?

**Background.** `recognize_pii_entities()` returns two things: entity spans with category (Person, Email, PhoneNumber, SSN...) and confidence score, plus `redacted_text` with detected spans masked. This is a privacy signal, not a compliance certification. Missed detections remain in `redacted_text`. Does NOT cover conversation PII or document (native file format) PII — those require different API calls.

```bash
uv run python 04-text-and-speech/05_language_pii.py
```

**Code path.**
1. `language_client()` → `recognize_pii_entities(_DOCS, language="en")`
2. For each doc: print `redacted_text` and each entity with `[category] 'text' (confidence)`

**What to watch.** Sarah Chen masked, email masked, phone masked. TKT-1042 is NOT masked — ticket IDs aren't a prebuilt PII category. That's expected.

**Exam cues.** PII output is a signal, not proof of data safety. `redacted_text` still needs application-level handling. Category list is fixed; custom categories require Custom NER.

**References:** [PII detection overview](https://learn.microsoft.com/azure/ai-services/language-service/personally-identifiable-information/overview) · [Azure AI Language overview](https://learn.microsoft.com/azure/ai-services/language-service/overview)

---

### 06 — Language Detection

**Question answered:** How do you detect a document's language and confidence before routing it?

**Background.** `detect_language()` returns `primary_language` with `iso6391_name` (2-letter ISO code) and `confidence_score`. It's a routing primitive — detect first, dispatch to the right Translator locale or Language model. Short or ambiguous text ("OK") gives low confidence; treat < 0.5 as unknown in production and define a fallback path.

```bash
uv run python 04-text-and-speech/06_language_detect.py
```

**Code path.**
1. `language_client()` → `detect_language(_DOCS)` with four test strings
2. Print language name, ISO code, and confidence per document

**What to watch.** English ~0.99, French ~0.99, Japanese ~0.99. "OK" → low confidence (ambiguous). The last doc intentionally shows the failure case.

**Exam cues.** `primary_language.iso6391_name` is the 2-letter code. Low confidence is expected on short inputs. Translator also has language detection (`/translator/text/detect`) — same idea, different service.

**References:** [Language detection overview](https://learn.microsoft.com/azure/ai-services/language-service/language-detection/overview) · [Azure AI Language overview](https://learn.microsoft.com/azure/ai-services/language-service/overview)

---

### 07 — Azure Language NER (discriminative)

**Question answered:** How do you extract entities with fixed categories and auditable confidence scores?

**Background.** `recognize_entities()` returns fixed-schema categorized entities (Person, Organization, Location, DateTime, Quantity, Product...) with optional subcategories (Person/Employee, Location/City) and per-entity confidence scores. Compare with lesson 01: same ticket, fixed schema vs prompt-defined categories. Confidence scores are model signals, not audit conclusions.

```bash
uv run python 04-text-and-speech/07_language_ner.py
```

**Code path.**
1. `language_client()` → `recognize_entities(_DOCS, language="en")`
2. Print `[Category / Subcategory] 'text' (confidence)` per entity

**What to watch.** `[Person] 'Sarah Chen' (0.99)`, `[Organization] 'Acme Logistics' (0.98)`, `[Quantity/Duration] '4 hour'`. Subcategory is optional — check for `None`.

**Exam cues.** Prebuilt categories are FIXED. For custom labels (ticket_id, sla_tier), use Custom NER or the LLM path (lesson 01). Confidence is not a guarantee.

**References:** [Named entity recognition overview](https://learn.microsoft.com/azure/ai-services/language-service/named-entity-recognition/overview) · [Custom NER overview](https://learn.microsoft.com/azure/ai-services/language-service/custom-named-entity-recognition/overview)

---

### 20 — Azure Language Sentiment + Opinion Mining

**Question answered:** How do you get structured per-sentence sentiment and associate assessments with their targets?

**Background.** `analyze_sentiment(..., show_opinion_mining=True)` returns document-level sentiment (positive/negative/neutral/mixed), per-sentence sentiment, and opinion mining — target+assessment pairs that link descriptors to their subjects (e.g., "frustrating" → "onboarding process"). This is the structured alternative to lesson 02's LLM approach. Retirement: March 31, 2029 — prefer Foundry models for new production workloads.

```bash
uv run python 04-text-and-speech/20_language_sentiment.py
```

**Code path.**
1. `language_client()` → `analyze_sentiment(_DOCS, language="en", show_opinion_mining=True)`
2. Print document sentiment, per-sentence sentiment, then `mined_opinions` — each with `target.text` (sentiment) and assessments

**What to watch.** Document → "mixed". Per sentence: "reliable" → positive, "frustrating" → negative. Opinion mining: `onboarding process (negative): frustrating (negative)`.

**Exam cues.** Opinion mining does NOT use a different `kind` — it's the same `SentimentAnalysis` kind with `opinionMining=true`. Compare to lesson 02 which gives free-form rationale.

**References:** [Sentiment + opinion mining overview](https://learn.microsoft.com/azure/ai-services/language-service/sentiment-opinion-mining/overview)

---

### 08 — Language MCP Tool Discovery

**Question answered:** What tools does the Azure Language MCP server expose, and how do you discover them?

**Background.** The Language MCP server exposes Language SDK capabilities (NER, PII, sentiment, language detection, key phrases, summarization) as MCP tools that any MCP-compatible agent or client can call. This lesson performs discovery only — it lists tool names and descriptions without invoking a tool. L08 proves the MCP endpoint is reachable and authenticated; it does NOT prove that a Foundry project connection is configured for L09.

```bash
uv run python 04-text-and-speech/08_language_mcp_tools.py
```

**Code path.**
1. `DefaultAzureCredential` → Cognitive Services token → httpx.AsyncClient with Bearer header
2. `streamable_http_client(language_mcp_url)` → `ClientSession.initialize()` → `list_tools()`
3. Print tool name and description for each tool

**What to watch.** A list of MCP tools (NER, PII detection, sentiment analysis, language detection, etc.). Tool names are authoritative at runtime — preview contracts can change.

**Exam cues.** L08 discovers Language MCP only. L21 discovers Speech MCP. Discovery does not authorize tool invocation. MCP standardizes transport; it does not remove auth, RBAC, or network requirements.

**References:** [Language Foundry tools and agents](https://learn.microsoft.com/azure/ai-services/language-service/concepts/foundry-tools-agents) · [Azure AI Language overview](https://learn.microsoft.com/azure/ai-services/language-service/overview)

---

### 09 — Language MCP Agent

**Question answered:** How do you attach the Language MCP server to a Foundry Prompt Agent so the model picks the right Language tool per question?

**Background.** Same Language MCP endpoint as L08, but wrapped as `MCPTool` on a registered Prompt Agent. The agent's system prompt declares what tasks map to which tool type; the model decides tool selection at runtime. Requires a Foundry project connection that authorizes Language MCP for agent authentication — L08's direct call success does NOT prove this connection exists.

```bash
uv run python 04-text-and-speech/09_language_mcp_agent.py
```

**Code path.**
1. `project_client()` → `MCPTool(server_url, server_label="azure_language")`
2. `agents.create_version()` with `PromptAgentDefinition` (model + instructions + tools)
3. `project.get_openai_client()` → `responses.create()` with `agent_reference` in extra_body
4. Print response

**What to watch.** Response identifies Japanese as the language and Sarah Chen as a person — agent called Language MCP tools under the hood. Check Foundry trace for tool calls if available.

**Exam cues.** `MCPTool` is the Azure Projects SDK construct for a remote MCP server. No hardcoded routing — model decides. `agents.create_version()` creates a new version; clean up agent versions in production.

**References:** [Language Foundry tools and agents](https://learn.microsoft.com/azure/ai-services/language-service/concepts/foundry-tools-agents) · [Azure AI Foundry agents](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/azure-ai-speech)

---

### 10 — Text Analytics for Health

**Question answered:** How do you extract clinical entities from unstructured medical text?

**Background.** `begin_analyze_healthcare_entities()` extracts clinical concepts: MedicationName, Dosage, RouteOfAdministration, Diagnosis, SymptomOrSign, ExaminationName, and more. Many entities include `normalized_text` mapping to UMLS codes — critical for downstream analytics. The API is async (poller-based). This is an extraction aid only — NOT diagnosis, clinical decision support, or a compliance control. Health data requires approved privacy, access, and human-review processes.

```bash
uv run python 04-text-and-speech/10_health_text_analytics.py
```

**Code path.**
1. `language_client()` → `begin_analyze_healthcare_entities(_CLINICAL, language="en")` → `poller.result()`
2. For each entity: print `[category] 'text' conf=... norm=...`

**What to watch.** `[SymptomOrSign] 'dry cough'`, `[Diagnosis] 'hypertension'`, `[MedicationName] 'lisinopril'` with dosage linked. `normalized_text` field links to UMLS concepts when available.

**Exam cues.** Always `.result()` on the poller — it's async internally. Healthcare extraction ≠ diagnosis or coding. UMLS normalization is for analytics, not clinical validation.

**References:** [Text Analytics for Health overview](https://learn.microsoft.com/azure/ai-services/language-service/text-analytics-for-health/overview) · [Health entity categories](https://learn.microsoft.com/azure/ai-services/language-service/text-analytics-for-health/concepts/health-entity-categories)

---

## Stage 3 — Speech to Text: Three Modes (lessons 11–13)

Three distinct STT paths. Pick by input shape and latency requirements.

### 11 — Fast Transcription (sync REST)

**Question answered:** How do you synchronously transcribe a single audio file to text?

**Background.** Fast Transcription is the one-file synchronous path: POST audio + JSON definition, get transcript in the same HTTP response. No polling, no background job. Limit: ~2 hr / 300 MB per file. For live streaming use lesson 12; for many files async use lesson 13.

```bash
uv run python 04-text-and-speech/11_stt_fast_file.py
```

**Code path.**
1. `_endpoint_base()` returns configured `speech_endpoint` or derives regional URL from `SPEECH_REGION`
2. `transcribe()` opens WAV, POSTs multipart with Bearer token and JSON definition
3. Returns `r.json()["combinedPhrases"][0]["text"]`

**What to watch.** Transcript of `conversation.wav`. Empty string means `combinedPhrases` was empty — check locale and audio codec. 404 means wrong API version; this repo uses `2025-10-15`.

**Exam cues.** API: `/speechtotext/transcriptions:transcribe` (NOT the batch endpoint). `definition` is multipart JSON. Fast Transcription = sync one-file; Real-time = streaming; Batch = async many-files.

**References:** [Fast transcription how-to](https://learn.microsoft.com/azure/ai-services/speech-service/fast-transcription-create) · [Speech-to-text overview](https://learn.microsoft.com/azure/ai-services/speech-service/speech-to-text)

---

### 12 — Real-Time STT (microphone streaming)

**Question answered:** How do you continuously recognize speech from a live microphone stream?

**Background.** `SpeechRecognizer` with `AudioConfig(use_default_microphone=True)` streams audio to the Speech service in real time. Events: `recognizing` (partial, not wired here) and `recognized` (final). `start_continuous_recognition()` runs until `stop_continuous_recognition()` is called. For network audio (not mic) use `PushAudioInputStream`.

```bash
uv run python 04-text-and-speech/12_stt_real_time.py
```

**Code path.**
1. `speech_config()` + `AudioConfig(use_default_microphone=True)` → `SpeechRecognizer`
2. Connect `recognized` → print, `session_stopped/canceled` → stop
3. `start_continuous_recognition()` → spin on `done["stop"]`

**What to watch.** Your spoken words printed as recognized phrases. No Ctrl+C cleanup — add `try/finally` calling `stop_continuous_recognition()` for interactive use.

**Exam cues.** `recognized` events = final; `recognizing` = partial. Both need to be subscribed to for real use. Mic access must be granted to terminal/IDE.

**References:** [Get started with STT](https://learn.microsoft.com/azure/ai-services/speech-service/get-started-speech-to-text) · [Speech-to-text overview](https://learn.microsoft.com/azure/ai-services/speech-service/speech-to-text)

---

### 13 — Batch Transcription (async REST)

**Question answered:** How do you transcribe many audio files asynchronously from Blob storage?

**Background.** POST a Blob container SAS URL to `/speechtotext/transcriptions?api-version=2024-11-15`. The service processes all files asynchronously; jobs can queue. Poll until `status` is `Succeeded`/`Failed`/`Cancelled`, honoring `Retry-After` or bounded 60–600s backoff. The `finally` block deletes the remote job and service-managed results — copy output to governed storage first.

```bash
uv run python 04-text-and-speech/13_stt_batch.py
```

**Code path.**
1. `_submit(container_sas_url)` → POST config with `contentContainerUrl`, `diarizationEnabled`, `wordLevelTimestampsEnabled` → returns `self` URL
2. `_wait(job_url)` → GET + backoff until terminal status
3. `_print_transcripts(files_url)` → GET `links.files` → filter `kind=Transcription` → GET each `contentUrl`
4. `finally`: DELETE job URL

**What to watch.** Job URL printed, then status polls, then transcript phrases. Save the job URL externally — if the client is interrupted before `finally`, the job remains running.

**Exam cues.** Batch API version: `2024-11-15`. Diarization = per-speaker labels. Batch does NOT need a custom endpoint GUID even with a custom model — reference model in request body. Copy results before `finally` deletes them.

**References:** [Batch transcription overview](https://learn.microsoft.com/azure/ai-services/speech-service/batch-transcription) · [Create batch transcription](https://learn.microsoft.com/azure/ai-services/speech-service/batch-transcription-create)

---

## Stage 4 — Text to Speech + Speech Translation (lessons 14–16)

Audio output and speech-to-translated-text in one call.

### 14 — TTS Neural Voice

**Question answered:** How do you synthesize speech from plain text using a neural voice?

**Background.** `SpeechSynthesizer` converts text to audio and writes to a file or stream. Set `speech_synthesis_voice_name` to select the voice. Voice inventory and availability vary by locale and region — verify before depending on a specific voice. For prosody control (pauses, pitch, style), use SSML with a Neural HD voice (lesson 15).

```bash
uv run python 04-text-and-speech/14_tts_neural.py
```

**Code path.**
1. `speech_config()` → set `speech_synthesis_voice_name = "en-US-JennyNeural"`
2. `AudioOutputConfig(filename=str(_OUTPUT))` → `SpeechSynthesizer`
3. `speak_text_async(_TEXT).get()` → check `ResultReason` → print OK or cleanup on failure

**What to watch.** `OK — synthesized to .../northwind_support_message.wav`. Listen — JennyNeural sounds professional. If flat, that's the plain-text ceiling; switch to lesson 15 for prosody.

**Exam cues.** Voice name format: `<locale>-<Name>Neural`. `AudioOutputConfig` accepts filename, byte stream, or default speaker. Neural HD requires SSML for expressive features.

**References:** [Text-to-speech overview](https://learn.microsoft.com/azure/ai-services/speech-service/text-to-speech) · [Speech SDK text-to-speech](https://learn.microsoft.com/azure/ai-services/speech-service/rest-text-to-speech)

---

### 15 — TTS SSML + Neural HD Voice

**Question answered:** How do you control prosody, pauses, and expressive style in TTS?

**Background.** Neural HD voices (name contains `HD`: `AvaHDNeural`, `AndrewMultilingualNeural`) support expressive styles and higher-definition audio. Plain text works but SSML unlocks `<prosody rate>`, `<break>`, and `<mstts:express-as style>`. SSML is XML-strict — invalid markup fails the whole call. Voice availability and supported styles vary by region; test before depending on a specific voice/style combination.

```bash
uv run python 04-text-and-speech/15_tts_ssml_hd.py
```

**Code path.**
1. `speech_config()` + `AudioOutputConfig` → `SpeechSynthesizer`
2. `speak_ssml_async(_SSML).get()` — SSML specifies AvaHDNeural, `express-as style=friendly`, 200ms break, `prosody rate=-5%`
3. Check `ResultReason` → print OK or cleanup

**What to watch.** Listen to `northwind_hd_announcement.wav` — pause after "Northwind" and slightly slower delivery. If it sounds flat, check that the SSML was sent correctly (not as plain text).

**Exam cues.** HD voice names contain `HD`. `<mstts:express-as>` styles differ per voice. SSML is XML; whitespace and namespace matter. Neural HD needs SSML for the best quality — plain text works but wastes HD capability.

**References:** [Text-to-speech overview](https://learn.microsoft.com/azure/ai-services/speech-service/text-to-speech) · [SSML documentation](https://learn.microsoft.com/azure/ai-services/speech-service/speech-synthesis-markup)

---

### 16 — Speech Translation

**Question answered:** How do you transcribe and translate spoken audio in one SDK call?

**Background.** `TranslationRecognizer` is NOT the same as Azure Translator (the REST text service). It handles the full pipeline: audio → ASR → translation in one streaming call. `recognize_once_async()` for a single utterance; subscribe to `recognized` events for continuous. Add multiple target languages with `add_target_language()`. Uses `SPEECH_REGION` (not just endpoint).

```bash
uv run python 04-text-and-speech/16_speech_translation.py
```

**Code path.**
1. `DefaultAzureCredential` → Cognitive Services token → `SpeechTranslationConfig(auth_token, region)`
2. `cfg.speech_recognition_language = "en-US"` + `cfg.add_target_language("fr")`
3. `TranslationRecognizer` → `recognize_once_async().get()`
4. Print `result.text` (English) and `result.translations["fr"]` (French)

**What to watch.** Two output blocks: English source and French translation. If `result.reason != TranslatedSpeech`, print `result.reason` to diagnose.

**Exam cues.** `TranslationRecognizer` ≠ Azure Translator REST API — the exam tests this distinction explicitly. Add multiple targets with repeated `add_target_language()` calls. Speech Translation requires `SPEECH_REGION`, not just `SPEECH_ENDPOINT`.

**References:** [Speech translation overview](https://learn.microsoft.com/azure/ai-services/speech-service/speech-translation) · [Get started with speech translation](https://learn.microsoft.com/azure/ai-services/speech-service/get-started-speech-translation)

---

## Stage 5 — LLM Speech + Voice Live + Custom Speech (lessons 17–19)

Advanced speech paths: LLM-based transcription, real-time agent voice, and custom acoustic models.

### 17 — MAI-Transcribe 1.5 Preview

**Question answered:** How do you use an LLM-based speech model with phrase-list entity biasing?

**Background.** `mai-transcribe-1.5` is a preview LLM-based STT model available through the same Fast Transcription REST route as lesson 11, via `enhancedMode`. It improves recognition of domain-specific terms (product names, proper nouns) supplied in `phraseList.phrases`. A phrase list is NOT the same as Custom Speech training — no model retraining, just inference-time biasing. Does NOT support prompt-tuning or diarization.

```bash
uv run python 04-text-and-speech/17_llm_speech_preview.py
```

**Code path.**
1. Build `definition` dict with `locales`, `phraseList.phrases`, and `enhancedMode: {enabled: true, model: "mai-transcribe-1.5"}`
2. POST multipart to `/speechtotext/transcriptions:transcribe?api-version=2025-10-15`
3. Print transcript

**What to watch.** "Northwind Connect" and other listed phrases recognized accurately if present in audio. 404 = model or API version unavailable in region — verify preview availability.

**Exam cues.** MAI-Transcribe uses the Fast Transcription endpoint, not a separate route. Phrase lists ≠ prompt-tuning ≠ diarization. Preview: confirm regional and model availability before depending on it.

**References:** [MAI-Transcribe model](https://learn.microsoft.com/azure/ai-services/speech-service/mai-transcribe) · [Fast transcription how-to](https://learn.microsoft.com/azure/ai-services/speech-service/fast-transcription-create)

---

### 18 — Voice Live WebSocket Protocol Demo

**Question answered:** How does the Voice Live WebSocket protocol work with a Foundry Prompt Agent?

**Background.** Voice Live is a bidirectional WebSocket API: send audio frames, receive synthesized audio responses from an agent. This lesson is a protocol demo — it sends prerecorded PCM16 audio and logs response events. It does NOT capture microphone, decode audio deltas, or play audio. The Prompt Agent is created inline so no portal setup is needed. For the file-to-file flow with audio output, see lesson 24.

Current URL: `wss://<resource>.services.ai.azure.com/voice-live/realtime?api-version=2026-04-10&agent_id=<id>&project_id=<name>`

```bash
uv run python 04-text-and-speech/18_voice_live_prompt_agent.py
```

**Code path.**
1. `_ensure_agent()` creates a Prompt Agent version with `DEFAULT_MODEL`
2. `websockets.connect(url, additional_headers={"Authorization": ...})`
3. Send `session.update`, `input_audio_buffer.append` (base64 PCM16), `commit`, `response.create`
4. Iterate events until `response.done`; `finally` deletes agent version

**What to watch.** Events: `session.created`, `input_audio_buffer.committed`, `response.audio.delta` (base64, logged not played), `response.done`. No audio plays.

**Exam cues.** URL is `/voice-live/realtime` not `/voice-live/v1`. Query params: `agent_id` + `project_id` (not `agent_name`). For non-agent use: pass `model` query param instead. `websockets` 15 uses `additional_headers`, not `extra_headers`.

**References:** [Voice Live how-to](https://learn.microsoft.com/azure/ai-services/speech-service/voice-live-how-to) · [Voice Live API reference 2026-04-10](https://learn.microsoft.com/azure/ai-services/speech-service/voice-live-api-reference-2026-04-10)

---

### 19 — Custom Speech Model Endpoint

**Question answered:** How do you route real-time STT to a trained and deployed custom acoustic model?

**Background.** Custom Speech lets you train on domain vocabulary (product names, jargon, accented speech) and deploy a custom model via Speech Studio. The consumption step is simple: set `speech_config.endpoint_id = "<guid>"` and every other SDK call is identical to standard STT. Note: Batch Transcription references a custom model in the request body — it does NOT need the endpoint GUID. Only real-time and Fast Transcription require the endpoint GUID. This lesson does NOT train or evaluate — it implements the consume step only.

```bash
uv run python 04-text-and-speech/19_custom_speech_model.py
```

**Code path.**
1. Check `custom_speech_endpoint_id` is set; raise `SystemExit` with guidance if missing
2. `speech_config()` → `config.endpoint_id = s.custom_speech_endpoint_id`
3. `SpeechRecognizer` with audio file → `recognize_once_async().get()` → print result

**What to watch.** Transcript via custom model. This lesson cannot prove the custom model is more accurate — that requires a held-out test set and word-error-rate comparison.

**Exam cues.** One extra line compared to standard STT: `config.endpoint_id`. Batch transcription uses a custom model without endpoint GUID (reference model in batch request body). Real-time DOES need the GUID.

**References:** [Custom Speech overview](https://learn.microsoft.com/azure/ai-services/speech-service/custom-speech-overview) · [Deploy a custom speech model](https://learn.microsoft.com/azure/ai-services/speech-service/how-to-custom-speech-deploy-model)

---

## Stage 6 — Governance, Security, and Advanced Patterns (lessons 21–25)

Safety guards, secure configuration, and operational awareness for production-grade text and speech workloads.

### 21 — Speech MCP Preflight

**Question answered:** How do you safely discover what Speech MCP tools are available before any integration?

**Background.** The Speech MCP server (preview) exposes Speech capabilities as MCP tools. This lesson defaults to a local preflight (no network call); `--run` validates the URL and lists tool contracts without invoking a tool. MCP standardizes tool transport — it does not replace RBAC, application authorization, network reachability, or tool allowlisting.

```bash
uv run python 04-text-and-speech/21_speech_mcp_preflight.py
uv run python 04-text-and-speech/21_speech_mcp_preflight.py --run
```

**Code path.**
1. Default: `preflight()` reads `SPEECH_MCP_URL` from settings — no cloud call
2. `--run`: `speech_mcp_url()` validates HTTPS, rejects localhost and unversioned URLs → Cognitive Services token → `streamable_http_client` → `list_tools()`
3. Print tool names

**What to watch.** Local: config presence. With `--run`: `Discovered N Speech MCP tool(s); none invoked.`

**Exam cues.** Discovery ≠ invocation authorization. L08 discovers Language MCP; L21 discovers Speech MCP. Preview endpoint — pin and regression-test the contract.

**References:** [Voice Live MCP server](https://learn.microsoft.com/azure/ai-services/speech-service/how-to-voice-live-mcp-server) · [Language Foundry tools and agents](https://learn.microsoft.com/azure/ai-services/language-service/concepts/foundry-tools-agents)

---

### 22 — Translator Secure Configuration

**Question answered:** How do you use Azure Translator with keyless Entra authentication and input validation guards?

**Background.** Extends lesson 04 with an explicit preflight guard: default run makes no cloud call; `--run` requires `--text`, `--source`, and `--targets` to be provided explicitly. Uses the same shared Translator client (Entra + ARM ID). Keeps routine translation separate from lesson 23's document-batch/key contract.

```bash
uv run python 04-text-and-speech/22_translator_secure_config.py
uv run python 04-text-and-speech/22_translator_secure_config.py \
  --run --text "Approved sample." --source en --targets fr,ja
```

**Code path.**
1. No flags: `preflight()` prints `No cloud calls made.`
2. `--run`: `_language_tags()` validates language tag syntax → `translate()` via shared client → print translations

**What to watch.** Without flags: preflight message. With flags: `[fr] ...` and `[ja] ...` translations.

**Exam cues.** Global Translator endpoint requires both Entra token AND `TRANSLATOR_RESOURCE_ID` in `Ocp-Apim-ResourceId` header. Token alone is not enough.

**References:** [Translator Microsoft Entra auth](https://learn.microsoft.com/azure/ai-services/translator/how-to/microsoft-entra-id-auth) · [Translator secure deployment](https://learn.microsoft.com/azure/ai-services/translator/secure-deployment)

---

### 23 — Document Translation Batch Operations

**Question answered:** How do you submit, inspect, and cancel an async Document Translation batch?

**Background.** Document Translation is a separate API from Text Translation (lesson 04). It requires a Translator API key (not Entra), source and target Blob SAS URLs, and a unique target container per batch. Submitted output persists in Blob until your storage lifecycle removes it. This lesson defaults to local-only; `--apply` triggers the cloud call.

```bash
uv run python 04-text-and-speech/23_translator_batch_operations.py
TRANSLATOR_DOCUMENT_KEY='<runtime-only>' uv run python 04-text-and-speech/23_translator_batch_operations.py \
  --apply --endpoint https://<resource>.cognitiveservices.azure.com \
  --source-url '<read-sas>' --target-url '<write-sas>' --language fr
```

**Code path.**
1. No flags: `preflight()` — no cloud call
2. `--apply`: validate HTTPS/SAS shape → POST `/translator/document/batches?api-version=2026-03-01` → print `operation-location`
3. `--operation-url`: GET status; `--cancel`: DELETE

**What to watch.** `operation-location` URL on submit. Status transitions: `Running` → `Succeeded`/`Failed`. Output persists in Blob — lifecycle it.

**Exam cues.** SAS grants Blob access, not Translator authorization — these are independent boundaries. Source SAS needs read+list; target needs write+list. Every target container must be unique per batch.

**References:** [Document Translation overview](https://learn.microsoft.com/azure/ai-services/translator/document-translation/overview) · [Translator overview](https://learn.microsoft.com/azure/ai-services/translator/overview)

---

### 24 — Voice Live PCM File-to-File Flow

**Question answered:** How do you stream a WAV file through Voice Live and capture the audio response?

**Background.** Builds on lesson 18 (protocol demo). Where L18 creates a Prompt Agent, L24 uses `model=<name>` query parameter directly. It validates PCM WAV format, chunks the input, decodes `response.audio.delta` (base64 PCM), and writes raw `.pcm` output. File-to-file only — no microphone capture, speaker playback, or WebRTC transport. Raw `.pcm` needs correct codec metadata to play back.

```bash
uv run python 04-text-and-speech/24_voice_live_audio_flow.py
uv run python 04-text-and-speech/24_voice_live_audio_flow.py --run \
  --model <deployment> \
  --audio _shared/sample_data/audio/northwind_support_message.wav \
  --output 04-text-and-speech/voice-response.pcm
```

**Code path.**
1. No flags: local preflight + WAV validation only
2. `--run`: `pcm_wav()` enforces mono, 16-bit, 16/24 kHz; `voice_live_url()` builds URL with `api-version` and `model`
3. `session_update()` requests PCM16 I/O; WebSocket + Entra Bearer
4. Base64-send 256 KiB chunks, commit, create response → decode each `response.audio.delta` → write `.pcm`

**What to watch.** `Saved <N> PCM bytes to <path>`. Raw `.pcm` needs format metadata (sample rate, channels, bit depth) to play back in a media player.

**Exam cues.** `model` query param for non-agent Voice Live; `agent_id`+`project_id` for agent mode (lesson 18). Output is raw PCM, not WAV — wrap with format metadata before playback.

**References:** [Voice Live how-to](https://learn.microsoft.com/azure/ai-services/speech-service/voice-live-how-to) · [Voice Live API reference 2026-04-10](https://learn.microsoft.com/azure/ai-services/speech-service/voice-live-api-reference-2026-04-10) · [Voice Live customization](https://learn.microsoft.com/azure/ai-services/speech-service/voice-live-how-to-customize)

---

### 25 — Monitoring and Governance Preflight

**Question answered:** Which monitoring and governance settings must be configured before deploying text and speech workloads?

**Background.** A no-cloud-call preflight that checks whether `APP_INSIGHTS_CONNECTION_STRING`, `SPEECH_ENDPOINT`, `VOICE_LIVE_ENDPOINT`, and `SPEECH_MCP_URL` are configured. It is a release-review reminder that observability, privacy, network, RBAC, retention, and cost are separate from making one successful API call. Configure Monitor, Policy, private endpoints, role assignments, and budget alerts through reviewed IaC — not this script.

```bash
uv run python 04-text-and-speech/25_text_speech_governance_preflight.py
```

**Code path.**
1. `preflight()` reads four `settings()` fields → returns dict of booleans
2. `main()` prints each flag and a monitoring/governance reminder

**What to watch.** A list of configured/missing flags. Expected: `No cloud calls made.` The script makes no Azure call — it only inspects local config.

**Exam cues.** Monitoring measures behavior; it does not grant access, prove correctness, or make data handling compliant. Preflight ≠ health probe. IaC controls RBAC, networking, and retention — not this script.

**References:** [Azure Monitor overview](https://learn.microsoft.com/azure/azure-monitor/overview) · [Translator secure deployment](https://learn.microsoft.com/azure/ai-services/translator/secure-deployment) · [Speech service data privacy](https://learn.microsoft.com/azure/foundry/responsible-ai/speech-service/speech-to-text/data-privacy-security)

---

## Feature status and hard limits

| Feature | Status | Practical boundary |
|---------|--------|--------------------|
| `mai-transcribe-1.5` (L17) | Preview | Regional availability varies; confirm before depending |
| Language MCP (L08–L09) | Preview | Endpoint contract can change; discovery ≠ invocation auth |
| Speech MCP (L21) | Preview | L21 discovers tools only; none invoked |
| Voice Live (L18, L24) | Preview, version-sensitive | API version `2026-04-10`; model/region availability varies |
| Document Translation (L23) | GA | API key required; Blob output persists; per-batch unique target container |
| Language Sentiment (L20) | GA | Retirement: March 31, 2029 |
| Opinion Mining (L20) | GA | Same `kind` as Sentiment; `opinionMining=true` |

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| L11/L17: 404 on Fast STT | Wrong API version | Use `api-version=2025-10-15` |
| L17: 404 on MAI-Transcribe | Model or region not available | Verify `mai-transcribe-1.5` preview availability in your region |
| L18: `TypeError` on `extra_headers` | `websockets` 15 changed API | Use `additional_headers` |
| L18/L24: WebSocket 404 or 401 | Wrong URL path or missing query params | `/voice-live/realtime?api-version=2026-04-10` + correct `agent_id/model` |
| L13: 401 on batch submit | Region mismatch | `SPEECH_REGION` must match Speech resource location |
| L13: `SystemExit: Set BATCH_STT_CONTAINER_SAS` | Env var missing | Generate container SAS with read + list; set at runtime only |
| L15: HD voice sounds flat | Sent plain text, not SSML | Use `speak_ssml_async()` with correct SSML document |
| L19: `SystemExit: Set CUSTOM_SPEECH_ENDPOINT_ID` | No custom model deployed | Speech Studio → Custom Speech → train + deploy → paste GUID |
| L04/L22: 401 or ARM ID error | Missing or malformed `TRANSLATOR_RESOURCE_ID` | Set full `/subscriptions/.../providers/Microsoft.CognitiveServices/accounts/<name>` |
| L12: hangs after Ctrl+C | No interrupt cleanup | Add `try/finally` calling `stop_continuous_recognition()` |
| L23: rejects source/target | Missing SAS permissions | Source: `r`+`l`; target: `w`+`l`; use HTTPS Blob SAS |
| L24: rejects audio | Not mono PCM16 WAV at 16/24 kHz | Convert audio first |

---

## CI/CD and operational release

```
Plan → Code → Test → Review → Stage → Release
  │              │       │        │       │
  │         lesson       │    IaC PR   gate on:
  │         syntax    doc        │     ├── Fast STT smoke
  │         check   tests    policy    ├── TTS output exists
  │                               │    ├── Preflight (L25) clean
  │                               └──  └── Budget alert configured
  └── RBAC, endpoints, keys in Key Vault
```

**What to version:** API versions (`2025-10-15`, `2026-04-10`), model names, voice names, locale strings, custom model GUIDs, MCP API versions. Pin these in config — they change with preview updates.

**Release gates:** L25 preflight must show all four settings configured. `az role assignment list` confirms identity has Cognitive Services User and Foundry User. Batch container SAS expiry must outlast the job.

---

## Security, networking, and IaC

| Decision | Recommendation | Common pitfall |
|----------|---------------|---------------|
| Auth for Language/Speech | `DefaultAzureCredential` → managed identity in Azure | Do not use subscription keys in app code |
| Auth for Translator Text | Entra token + `TRANSLATOR_RESOURCE_ID` ARM ID header | Entra token alone is insufficient at global endpoint |
| Auth for Document Translation | API key at runtime via Key Vault; never commit | Confusing with Text Translation Entra path |
| Blob SAS for batch/docs | Scoped HTTPS SAS, min permissions, short expiry | Do not put SAS in `.env.example`, logs, or CI variables |
| Private endpoint | Test private DNS, ingress/egress for Language, Translator, Speech, Storage from actual workload network | Private endpoint does not grant a role |
| Microphone (L12, L16) | Grant to terminal/IDE only; stop process after testing | Do not leave continuous capture running unattended |
| MCP endpoints | Allowlist tool names, validate arguments, require approval for side effects | Discovery ≠ invocation authorization |

---

## Common exam traps

| Claim | Correct interpretation |
|-------|----------------------|
| "Opinion Mining uses a different `kind`" | ❌ — same `kind: SentimentAnalysis`, pass `show_opinion_mining=True` |
| "Fast Transcription = real-time STT" | ❌ — Fast = one file sync; real-time = live streaming `SpeechRecognizer` |
| "Neural HD works fine with plain text" | ⚠️ — works, but SSML is required for prosody/style controls |
| "`TranslationRecognizer` = Azure Translator" | ❌ — `TranslationRecognizer` is Speech SDK; Azure Translator is a separate REST service |
| "L08 proves Speech MCP works too" | ❌ — L08 discovers Language MCP only; L21 discovers Speech MCP |
| "Redaction result means data is safe" | ❌ — missed detections remain; application handling is your responsibility |
| "Voice Live URL is `/voice-live/v1`" | ❌ — current: `/voice-live/realtime?api-version=2026-04-10` |
| "Voice Live takes `agent_name`" | ❌ — takes `agent_id` + `project_id` (or `model` for non-agent) |
| "Fast STT api-version is `2024-11-15`" | ❌ — current: `2025-10-15` |
| "MAI-Transcribe supports diarization" | ❌ — supports phrase lists and verbatim style; no diarization |
| "Custom Speech needs endpoint GUID for batch" | ❌ — Batch transcription references model in request body; only real-time needs GUID |
| "Extractive and Abstractive summarization use the same kind" | ❌ — separate `kind` values: `ExtractiveSummarization` / `AbstractiveSummarization` |

---

## Objective coverage and limits

Domain 4 covers **language model text analysis** (entity extraction, sentiment, translation, PII, health extraction, language detection, MCP integration) and **speech solutions** (STT in three modes, TTS in two modes, speech translation, MAI-Transcribe, Voice Live, Custom Speech).

Not covered: Custom NER training lifecycle, conversation PII, document-format PII, standard Speech SDK phrase lists for Fast/real-time/Voice Live (only MAI-specific phrase list shown), end-to-end Voice Live client with microphone and speaker playback, WebRTC transport, batch transcription durability patterns, and TTS voice availability automation. These gaps are noted in the lesson table — do not assume these samples prove those scenarios.

---

## References

### Azure AI Language
- [Azure AI Language overview](https://learn.microsoft.com/azure/ai-services/language-service/overview)
- [Named entity recognition overview](https://learn.microsoft.com/azure/ai-services/language-service/named-entity-recognition/overview)
- [Custom NER overview](https://learn.microsoft.com/azure/ai-services/language-service/custom-named-entity-recognition/overview)
- [PII detection overview](https://learn.microsoft.com/azure/ai-services/language-service/personally-identifiable-information/overview)
- [Language detection overview](https://learn.microsoft.com/azure/ai-services/language-service/language-detection/overview)
- [Sentiment + opinion mining overview](https://learn.microsoft.com/azure/ai-services/language-service/sentiment-opinion-mining/overview)
- [Text Analytics for Health overview](https://learn.microsoft.com/azure/ai-services/language-service/text-analytics-for-health/overview)
- [Health entity categories](https://learn.microsoft.com/azure/ai-services/language-service/text-analytics-for-health/concepts/health-entity-categories)
- [Language Foundry tools and agents (MCP)](https://learn.microsoft.com/azure/ai-services/language-service/concepts/foundry-tools-agents)

### Azure Translator
- [Translator overview](https://learn.microsoft.com/azure/ai-services/translator/overview)
- [Translator Microsoft Entra authentication](https://learn.microsoft.com/azure/ai-services/translator/how-to/microsoft-entra-id-auth)
- [Translator secure deployment](https://learn.microsoft.com/azure/ai-services/translator/secure-deployment)
- [Document Translation overview](https://learn.microsoft.com/azure/ai-services/translator/document-translation/overview)

### Azure Speech — STT
- [Speech-to-text overview](https://learn.microsoft.com/azure/ai-services/speech-service/speech-to-text)
- [Get started with STT](https://learn.microsoft.com/azure/ai-services/speech-service/get-started-speech-to-text)
- [Fast transcription how-to](https://learn.microsoft.com/azure/ai-services/speech-service/fast-transcription-create)
- [Batch transcription overview](https://learn.microsoft.com/azure/ai-services/speech-service/batch-transcription)
- [Create batch transcription](https://learn.microsoft.com/azure/ai-services/speech-service/batch-transcription-create)
- [MAI-Transcribe model](https://learn.microsoft.com/azure/ai-services/speech-service/mai-transcribe)
- [Custom Speech overview](https://learn.microsoft.com/azure/ai-services/speech-service/custom-speech-overview)
- [Deploy a custom speech model](https://learn.microsoft.com/azure/ai-services/speech-service/how-to-custom-speech-deploy-model)

### Azure Speech — TTS + Translation
- [Text-to-speech overview](https://learn.microsoft.com/azure/ai-services/speech-service/text-to-speech)
- [Speech translation overview](https://learn.microsoft.com/azure/ai-services/speech-service/speech-translation)
- [Get started with speech translation](https://learn.microsoft.com/azure/ai-services/speech-service/get-started-speech-translation)

### Voice Live
- [Voice Live how-to](https://learn.microsoft.com/azure/ai-services/speech-service/voice-live-how-to)
- [Voice Live API reference 2026-04-10](https://learn.microsoft.com/azure/ai-services/speech-service/voice-live-api-reference-2026-04-10)
- [Voice Live customization](https://learn.microsoft.com/azure/ai-services/speech-service/voice-live-how-to-customize)
- [Voice Live MCP server](https://learn.microsoft.com/azure/ai-services/speech-service/how-to-voice-live-mcp-server)
- [Build a voice agent (Foundry)](https://learn.microsoft.com/azure/foundry/agents/how-to/build-voice-agent)

### Security and operations
- [Azure Monitor overview](https://learn.microsoft.com/azure/azure-monitor/overview)
- [Speech service data privacy](https://learn.microsoft.com/azure/foundry/responsible-ai/speech-service/speech-to-text/data-privacy-security)
- [TTS responsible AI transparency](https://learn.microsoft.com/azure/foundry/responsible-ai/speech-service/text-to-speech/transparency-note)
- [Managed identities overview](https://learn.microsoft.com/entra/identity/managed-identities-azure-resources/overview)
- [Azure Key Vault overview](https://learn.microsoft.com/azure/key-vault/general/overview)

### Compliance and Responsible AI

**Language Service:**
- [Language Service transparency note](https://learn.microsoft.com/azure/foundry/responsible-ai/language-service/transparency-note)
- [Language Service data privacy](https://learn.microsoft.com/azure/foundry/responsible-ai/language-service/data-privacy)
- [Language Service integration guidance](https://learn.microsoft.com/azure/foundry/responsible-ai/language-service/guidance-integration-responsible-use)
- [Sentiment analysis transparency](https://learn.microsoft.com/azure/foundry/responsible-ai/language-service/transparency-note-sentiment-analysis)
- [Named Entity Recognition transparency](https://learn.microsoft.com/azure/foundry/responsible-ai/language-service/transparency-note-named-entity-recognition)
- [PII transparency](https://learn.microsoft.com/azure/foundry/responsible-ai/language-service/transparency-note-personally-identifiable-information)
- [Language detection transparency](https://learn.microsoft.com/azure/foundry/responsible-ai/language-service/transparency-note-language-detection)
- [Key phrase extraction transparency](https://learn.microsoft.com/azure/foundry/responsible-ai/language-service/transparency-note-key-phrase-extraction)
- [Text Analytics for Health transparency](https://learn.microsoft.com/azure/foundry/responsible-ai/language-service/transparency-note-health)
- [Extractive summarization transparency](https://learn.microsoft.com/azure/foundry/responsible-ai/language-service/transparency-note-extractive-summarization)
- [Summarization characteristics + limitations](https://learn.microsoft.com/azure/foundry/responsible-ai/language-service/characteristics-and-limitations-summarization)
- [CLU transparency note](https://learn.microsoft.com/azure/foundry/responsible-ai/clu/clu-transparency-note)
- [CLU characteristics + limitations](https://learn.microsoft.com/azure/foundry/responsible-ai/clu/clu-characteristics-and-limitations)
- [CLU data privacy + security](https://learn.microsoft.com/azure/foundry/responsible-ai/clu/clu-data-privacy-security)
- [CLU integration guidance](https://learn.microsoft.com/azure/foundry/responsible-ai/clu/clu-guidance-integration-responsible-use)

**Speech Service:**
- [Speech-to-Text transparency note](https://learn.microsoft.com/azure/foundry/responsible-ai/speech-service/speech-to-text/transparency-note)
- [Text-to-Speech transparency note](https://learn.microsoft.com/azure/foundry/responsible-ai/speech-service/text-to-speech/transparency-note)
- [TTS data privacy + security](https://learn.microsoft.com/azure/foundry/responsible-ai/speech-service/text-to-speech/data-privacy-security)
- [TTS limited access](https://learn.microsoft.com/azure/foundry/responsible-ai/speech-service/text-to-speech/limited-access)
- [TTS disclosure guidelines](https://learn.microsoft.com/azure/foundry/responsible-ai/speech-service/text-to-speech/concepts-disclosure-guidelines)
- [TTS disclosure patterns](https://learn.microsoft.com/azure/foundry/responsible-ai/speech-service/text-to-speech/concepts-disclosure-patterns)
- [TTS avatar disclosure guidelines](https://learn.microsoft.com/azure/foundry/responsible-ai/speech-service/text-to-speech/concepts-disclosure-guidelines-avatar)
- [TTS avatar disclosure patterns](https://learn.microsoft.com/azure/foundry/responsible-ai/speech-service/text-to-speech/concepts-disclosure-patterns-avatar)
- [TTS voice talent disclosure](https://learn.microsoft.com/azure/foundry/responsible-ai/speech-service/text-to-speech/disclosure-voice-talent)
- [Voice Live transparency note](https://learn.microsoft.com/azure/foundry/responsible-ai/speech-service/voice-live/transparency-note)
- [Voice Live data privacy + security](https://learn.microsoft.com/azure/foundry/responsible-ai/speech-service/voice-live/data-privacy-security)
- [Embedded speech limited access](https://learn.microsoft.com/azure/foundry/responsible-ai/speech-service/embedded-speech/limited-access-embedded-speech)
- [Pronunciation assessment transparency](https://learn.microsoft.com/azure/foundry/responsible-ai/speech-service/pronunciation-assessment/transparency-note-pronunciation-assessment)
- [Pronunciation assessment characteristics + limitations](https://learn.microsoft.com/azure/foundry/responsible-ai/speech-service/pronunciation-assessment/characteristics-and-limitations-pronunciation-assessment)

**Translator:**
- [Translator transparency note](https://learn.microsoft.com/azure/foundry/responsible-ai/translator/transparency-note)
- [Translator Pro transparency note](https://learn.microsoft.com/azure/foundry/responsible-ai/translator/translator-pro-transparency-note)
- [Translator data privacy + security](https://learn.microsoft.com/azure/foundry/responsible-ai/translator/data-privacy-security)
