# Domain 4 — Implement Text Analysis + Speech Solutions (10–15%)

> Run any lesson: `uv run python 04-text-and-speech/<file>.py`
> Prereqs: `.env` filled, `az login` completed. See root [README.md](../README.md).

19 lessons covering the widest surface area of any domain — three separate
Azure services (Language, Translator, Speech) plus the generative-model
alternatives (LLM prompt for NER / sentiment / translation) plus the
Foundry MCP tools plus Voice Live.

---

## What this domain teaches you

Every way to process **text** and **speech** in Foundry, from two angles:

- **Discriminative** (fine-tuned, cheap, structured) — Azure AI Language
  (NER / PII / sentiment / language detection / summarization / Text
  Analytics for Health), Azure Translator, Speech SDK (STT / TTS / Speech
  Translation), Custom Speech.
- **Generative** (LLM prompt, expensive, flexible) — Responses API with a
  system prompt for the same tasks; audio input via LLM Speech Preview
  (MAI-Transcribe / gpt-4o-transcribe); Voice Live for real-time
  speech-to-speech.

You'll learn WHICH TO PICK for each task — because the exam tests that
choice, not the code.

---

## Text + Speech in 90 seconds

- **Azure AI Language** — one endpoint (`.cognitiveservices.azure.com/language/:analyze-text`),
  many `kind` values (`EntityRecognition`, `PiiEntityRecognition`,
  `SentimentAnalysis`, `LanguageDetection`, `KeyPhraseExtraction`,
  `ExtractiveSummarization`, `AbstractiveSummarization`, `EntityLinking`,
  `Healthcare`). Fine-tuned per task; structured output; compliance-grade
  PII redaction.
- **Azure Translator** — separate REST service. Text translation to 100+
  languages, document translation, transliteration, dictionary lookup.
  Better than LLM for bulk / glossary work.
- **Speech SDK** — three STT modes: **Fast** (sync, one file), **Real-time**
  (streaming from mic/network), **Batch** (async, many files). Two TTS
  modes: **Neural** (default), **Neural HD** (SSML required, best quality).
  Also handles **Speech Translation** via `TranslationRecognizer` (NOT the
  same as Azure Translator).
- **MAI-Transcribe / LLM Speech Preview** — file-based transcription that
  goes through an LLM. Prompt-tunable ("Northwind product names include
  Connect, Sentinel — spell them like that"). Preview.
- **Voice Live** — bidirectional WebSocket. Mic in → agent thinks → TTS
  out. Real-time conversation. Preview.
- **Custom Speech** — train a model in Speech Studio for domain jargon or
  accents; deploy → get an endpoint GUID; set `endpoint_id` on the
  standard config. Everything else stays the same.

**Beginner shortcut:** *Discriminative for cost + certified categories.
Generative for novel entity types and multi-task calls. Speech modes are
one-file sync / stream / batch async — pick by input shape.*

---

## Mental model of the 19 lessons

Two phases, each split by service.

```
┌─── Phase 1: TEXT (L01–L10) ────────────────────────────────────────────┐
│  Generative (LLM prompt)                                              │
│    L01 NER by prompt                                                  │
│    L02 Sentiment by prompt                                            │
│    L03 Translation by prompt (tone-preserving)                        │
│    L04 Translator REST (bulk / glossary)                              │
│                                                                        │
│  Discriminative (Azure AI Language)                                   │
│    L05 PII detection (compliance-grade)                               │
│    L06 Language detection                                             │
│    L07 NER prebuilt                                                   │
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
│    L15 TTS Neural HD (SSML required)                                  │
│    L16 Speech Translation (TranslationRecognizer)                     │
│                                                                        │
│  LLM audio + real-time agents                                          │
│    L17 LLM Speech Preview (MAI-Transcribe file-based)                 │
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
  Sentiment + opinion mining?          → Azure Language Sentiment      (SDK)
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
  File + prompt-tuning?                → LLM Speech Preview (MAI)      [L17]

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
3. **`Foundry User` role** on the Foundry resource.
4. **`.env` core:** `FOUNDRY_ENDPOINT`, `AZURE_OPENAI_ENDPOINT`, `DEFAULT_MODEL`.
5. **`.env` Domain 4:**
   - `LANGUAGE_ENDPOINT` — Language service, `cognitiveservices.azure.com`.
   - `LANGUAGE_MCP_URL` — `<lang-endpoint>/language/mcp?api-version=2025-11-15-preview`.
   - `TRANSLATOR_ENDPOINT` — Translator via Foundry Tools (`services.ai.azure.com` subdomain).
   - `SPEECH_ENDPOINT` — Speech, `cognitiveservices.azure.com`.
   - `SPEECH_REGION` — for batch STT (v3.2 REST is region-scoped).
   - `SPEECH_MCP_URL` — `<speech-endpoint>/speech/mcp?api-version=2025-11-15-preview`.
   - `VOICE_LIVE_ENDPOINT` — `wss://<resource>.services.ai.azure.com/voice-live/realtime`.
   - `CUSTOM_SPEECH_ENDPOINT_ID` — GUID from Speech Studio (only for L19).
6. **Sample audio present:** `_shared/sample_data/audio/` — `conversation.wav`, `northwind_support_message.wav`.
7. **For L13 (Batch STT)** — a Blob container SAS URL exposing WAV files; export `BATCH_STT_CONTAINER_SAS`.
8. **For L19 (Custom Speech)** — train + deploy a model in Speech Studio, paste the endpoint GUID.

Sanity check: `uv run python 01-plan-and-manage/07_managed_identity_agent.py`
must pass. Language / Speech / Translator all use the same Foundry
principal via `DefaultAzureCredential`.

---

## Glossary — Domain 4 terms

| Term | Beginner definition |
|------|--------------------|
| **Azure AI Language** | Fine-tuned service for text tasks. One endpoint, many `kind` values. |
| **`kind` field** | Selects the Language feature per call — `EntityRecognition`, `PiiEntityRecognition`, `SentimentAnalysis`, ... |
| **Discriminative NLP** | Task-specific fine-tuned model with structured output. Azure Language SDK. |
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
| **Neural HD voice** | Best TTS quality; **requires SSML** to unlock the prosody controls. `en-US-AvaHDNeural`, `en-US-AndrewMultilingualNeural`. |
| **SSML** | Speech Synthesis Markup Language. XML dialect for TTS controls: `<voice>`, `<prosody>`, `<break>`, `<mstts:express-as>`. |
| **`TranslationRecognizer`** | Speech SDK class that recognizes speech AND translates in one call. NOT the same as Azure Translator (that's a REST service). |
| **MAI-Transcribe** | Microsoft's LLM-based transcription model. Prompt-tunable. File-based only. |
| **LLM Speech Preview** | Umbrella name for LLM-based STT — includes MAI-Transcribe, gpt-4o-transcribe. |
| **Voice Live** | Real-time bidirectional WebSocket API. `wss://<resource>.services.ai.azure.com/voice-live/realtime?api-version=2026-04-10`. |
| **Custom Speech** | Train an acoustic/language model in Speech Studio; deploy → endpoint GUID; set `speech_config.endpoint_id`. |
| **Language MCP** | Foundry MCP endpoint exposing Language features as agent tools. |
| **Speech MCP** | Same, for Speech features. |

---

## Common first-run failures

| Symptom | Root cause | Fix |
|---------|-----------|-----|
| L11: `404` on Fast STT | Old API version | Use `api-version=2025-10-15` (this repo fixed) |
| L17: `404` on MAI-Transcribe | Wrong subdomain or old API version | Use `SPEECH_ENDPOINT` (resource endpoint) + `api-version=2025-10-15` |
| L18: WebSocket 404 or 401 | Old URL path `/voice-live/v1` or missing `agent_id`/`project_id` | Use `/voice-live/realtime?api-version=2026-04-10&agent_id=...&project_id=...` (this repo fixed) |
| L18: `Agent not found` | Old README referenced `northwind-support` agent | L18 now creates the agent inline |
| L13: `401` on batch submit | Region mismatch — Speech resource in region X, `SPEECH_REGION` = Y | Match region to the resource |
| L13: `SystemExit: Set BATCH_STT_CONTAINER_SAS` | env var missing | Generate a Blob container SAS with the WAV files |
| L15: Neural HD reads text flatly | Missing SSML — you sent plain text | Pass SSML (see L15 code); HD voices need it |
| L19: `SystemExit: Set CUSTOM_SPEECH_ENDPOINT_ID` | No custom model deployed | Speech Studio → Custom Speech → train + deploy, paste GUID |
| L03: Translator has better output than L03 | Volume translation; use L04 | L03 = tone-preserving; L04 = bulk-optimal. Both are correct. |

---

## Files

| # | File | Syllabus bullet |
|---|---|---|
| 01 | `01_llm_ner.py` | Entity extraction via generative prompt |
| 02 | `02_llm_sentiment.py` | Sentiment + tone via generative prompt |
| 03 | `03_llm_translation.py` | Translation via LLM prompt (tone-preserving) |
| 04 | `04_translator_rest.py` | Translation via Azure Translator (Foundry Tools REST) |
| 05 | `05_language_pii.py` | PII detection + redaction via Azure AI Language |
| 06 | `06_language_detect.py` | Language detection via Azure AI Language |
| 07 | `07_language_ner.py` | NER via Azure AI Language (prebuilt, discriminative) |
| 08 | `08_language_mcp_tools.py` | Discover Language MCP tools |
| 09 | `09_language_mcp_agent.py` | Use Language MCP inside a Foundry agent |
| 10 | `10_health_text_analytics.py` | Text Analytics for Health |
| 11 | `11_stt_fast_file.py` | STT — Fast Transcription (single file, sync) |
| 12 | `12_stt_real_time.py` | STT — real-time streaming from mic |
| 13 | `13_stt_batch.py` | STT — Batch Transcription (async, many files) |
| 14 | `14_tts_neural.py` | TTS — neural voice |
| 15 | `15_tts_ssml_hd.py` | TTS — SSML + Neural HD voice |
| 16 | `16_speech_translation.py` | Speech Translation (`TranslationRecognizer`) |
| 17 | `17_llm_speech_preview.py` | LLM Speech Preview (MAI-Transcribe, file-based) |
| 18 | `18_voice_live_prompt_agent.py` | Voice Live — real-time speech-to-speech agent |
| 19 | `19_custom_speech_model.py` | Custom Speech — deployed model endpoint |

## Reference docs

- [Azure Language service overview](../.context/azure-ai-docs/articles/ai-services/language-service/overview.md)
- [Language / Speech MCP tools](../.context/azure-ai-docs/articles/foundry/mcp/available-tools.md)
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

## Azure AI Language — one endpoint, many `kind` values

```
Azure AI Language (all through /language/:analyze-text)
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
| Compliance-grade PII | ✔ (certified redaction) | ✘ (approximate only) |
| Medical entities | ✔ (`Healthcare` kind) | ✘ (approximate only) |
| Latency | Lower | Higher |
| Cost | Lower | Higher |

**Pick by task:**

```
Compliance-grade PII redaction?         → Azure Language PII
Medical entity extraction?              → Text Analytics for Health
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
    ├── File + prompt tuning?             → LLM Speech Preview / MAI-Transcribe (L17)
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
the model returns JSON. Not certified for compliance, but flexible on
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

**Expected output:** JSON with entity list (Sarah Chen / Acme Logistics /
TKT-1042 / Gold / Northwind Connect / $500) + topics.

**Key points:**
- For guaranteed JSON, wrap this in `text.format = json_schema` + `strict=True` (Domain 2 L07).
- LLM NER can invent categories your data doesn't have. Great for novelty; risky for compliance.
- Compare with L07 — same ticket, structured output from a certified model.

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

**You'll learn:** call Azure Translator via the Foundry Tools REST endpoint; multiple targets in one call.
**Prereqs:** `TRANSLATOR_ENDPOINT` in `.env` (Foundry `services.ai.azure.com` subdomain).
**Time:** ~5 min.

**Concept:** Translator is a separate REST service purpose-built for
translation at volume. One call → multiple target languages. Supports
custom glossaries and Custom Translator for domain-tuned MT.

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
    for t in result["value"][0]["translations"]:
        print(f"[{t['language']}] {t['text']}")
```

**Expected output:** three lines, one per target language.

**Key points:**
- `targets=[...]` — one call, many languages, saved cost vs N calls.
- For document-level translation (PDF, DOCX), use the **Document Translation** API on the same service.
- **Speech Translation is NOT Azure Translator** — different service (see L16).

---

# Lesson 05 — Azure Language — PII Detection

**You'll learn:** compliance-grade PII detection + auto-redaction via Azure AI Language; the certified alternative to LLM-based redaction.
**Prereqs:** `LANGUAGE_ENDPOINT` in `.env`.
**Time:** ~5 min.

**Concept:** `recognize_pii_entities` returns both:
- `entities` — spans with category (Person / Email / Phone / SSN / ...) + confidence,
- `redacted_text` — the original text with PII masked.

Certified for compliance in most sectors. GPT can approximate but shouldn't be trusted for regulated data.

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
    for idx, doc in enumerate(r for r in response if not r.is_error):
        print(f"--- Document {idx + 1} ---")
        print(f"Redacted: {doc.redacted_text}")
        for e in doc.entities:
            print(f"  [{e.category}] '{e.text}'  ({e.confidence_score:.2f})")
```

**Expected output:** the doc with PII masked (`Sarah Chen` → `**********`, email + phone masked), plus a table of detected entities with confidence.

**Key points:**
- `redacted_text` gives you a compliance-safe copy to log/store.
- For domain-specific PII (customer ids, internal identifiers), stack a custom Language model on top OR use GPT for the domain-specific parts.

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
    for idx, doc in enumerate(r for r in client.detect_language(_DOCS) if not r.is_error):
        primary = doc.primary_language
        print(f"  {primary.name} ({primary.iso6391_name})  conf={primary.confidence_score:.2f}")
```

**Expected output:** English / French / Japanese / (ambiguous, low confidence) for the four docs.

**Key points:**
- Short docs ("OK") give low confidence — treat < 0.5 as "unknown" in production.
- Translator also has language detection (`/translator/text/detect`) — same idea, different service.

---

# Lesson 07 — Azure Language — NER (Discriminative)

**You'll learn:** prebuilt NER with certified categories, confidence scores per entity, and subcategories (Person → EMPLOYEE, Location → CITY, ...).
**Prereqs:** L05 works.
**Time:** ~5 min.

**Concept:** `recognize_entities()` returns categorized entities with
subcategories and confidence. Contrast with L01's LLM path: this gives
you scores you can defend in audit; L01 gives you novel categories.

**Code:**

```python
# 07_language_ner.py
def main() -> None:
    client = language_client()
    for idx, doc in enumerate(r for r in client.recognize_entities(_DOCS, language="en") if not r.is_error):
        for e in doc.entities:
            subcat = f" / {e.subcategory}" if e.subcategory else ""
            print(f"  [{e.category}{subcat}] '{e.text}'  ({e.confidence_score:.2f})")
```

**Expected output:** entries like `[Person] 'Sarah Chen' (0.99)`, `[Organization] 'Acme Logistics' (0.98)`, `[Quantity] '4 hour' (0.95)`, ...

**Key points:**
- Prebuilt categories are FIXED — for custom types build a **Custom NER** model (portal + labeled data).
- Subcategory is not always populated — check for `None`.

---

# Lesson 08 — List Language MCP Tools

**You'll learn:** discover the tools exposed by the Azure Language MCP server; the exam expects you to know MCP is available for Language + Speech.
**Prereqs:** `LANGUAGE_MCP_URL` in `.env`; `mcp` Python package installed.
**Time:** ~5 min.

**Concept:** Foundry ships MCP endpoints for Azure Language and Azure
Speech. They expose the service features as MCP tools so any agent
(Foundry Prompt Agent, Claude Desktop, etc.) can consume them without
custom REST plumbing.

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
- Language MCP + Speech MCP use different URL paths but the same auth (Entra bearer).
- Use MCP when the tool consumer is another agent or an off-Azure client.

---

# Lesson 09 — Language MCP Inside a Foundry Agent

**You'll learn:** attach the Language MCP server to a Prompt Agent as an `McpTool`; let the model pick which language tool to invoke per turn.
**Prereqs:** L08 works.
**Time:** ~5 min.

**Concept:** Same MCP endpoint, but wrapped as an `McpTool` on a
registered agent. The agent's system prompt tells it which class of
questions map to which tool.

**Code:**

```python
# 09_language_mcp_agent.py (excerpt)
tool = McpTool(server_url=settings().language_mcp_url, server_label="azure_language")
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
- `McpTool` is the same construct used for any MCP server (Domain 2's Toolbox produces one too).
- No hardcoded routing — the model decides which tool to invoke based on the user's question.

---

# Lesson 10 — Text Analytics for Health

**You'll learn:** extract clinical entities (medication, dosage, condition, symptom) with normalization to standard vocabularies (UMLS, RxNorm).
**Prereqs:** L05 works.
**Time:** ~5 min.

**Concept:** `begin_analyze_healthcare_entities` is async (poller-based).
Returns clinical entities with `category`, `confidence_score`, and
sometimes `normalized_text` (link to a standard code). Certified for
healthcare data pipelines; GPT is approximate at best here.

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
**Prereqs:** `SPEECH_ENDPOINT` + `SPEECH_REGION`; mic access on your machine.
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
- Real-time IS higher-latency than Fast Transcription for equivalent one-shot input — pick by use case.

---

# Lesson 13 — Batch Transcription (Async REST)

**You'll learn:** submit many audio files at once via the async v3.2 REST endpoint; poll until done; fetch a results URL.
**Prereqs:** `SPEECH_REGION` in `.env`; `BATCH_STT_CONTAINER_SAS` env var pointing at a Blob container of WAV files.
**Time:** ~30 min (batch runs in the background, region-serial).

**Concept:** Three steps:
1. POST `/speechtotext/v3.2/transcriptions` with the container SAS + config.
2. Poll `GET <returned job URL>` until `status = Succeeded`.
3. GET the `links.files` URL to enumerate transcript files.

Use for backlogs, weekly archives, anything not user-facing. Batch processes serially per region — spread submissions.

**Code:**

```python
# 13_stt_batch.py (excerpt)
def _submit(container_sas_url: str) -> str:
    body = {
        "displayName": "northwind-support-calls-batch",
        "locale": "en-US",
        "contentContainerUrl": container_sas_url,
        "properties": {"diarizationEnabled": True, "wordLevelTimestampsEnabled": True},
    }
    r = httpx.post(f"{_base_url()}/speechtotext/v3.2/transcriptions", headers=_headers(), json=body)
    return r.json()["self"]

def _wait(job_url: str) -> dict:
    while True:
        body = httpx.get(job_url, headers=_headers()).json()
        if body["status"] in ("Succeeded", "Failed"):
            return body
        time.sleep(30)
```

**Expected output:** job URL, several `status=Running — waiting 30s` polls, then a `done: Succeeded. Fetch transcripts at ...` message.

**Key points:**
- v3.2 is the current stable API version.
- `diarizationEnabled` = per-speaker labels ("Speaker 1", "Speaker 2") in the transcript.
- Batch does not need a custom endpoint even when using a Custom Speech model (unlike real-time).

---

# Lesson 14 — TTS Neural Voice

**You'll learn:** synthesize speech with a neural voice — plain text in, WAV out.
**Prereqs:** `SPEECH_ENDPOINT` in `.env`.
**Time:** ~3 min.

**Concept:** `SpeechSynthesizer` writes audio to a file or stream.
`speech_synthesis_voice_name` picks the voice; 500+ voices in 140+ languages. Plain text works; no SSML needed.

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

**You'll learn:** Neural HD voices unlock the best quality but **require SSML**; use `<prosody>`, `<break>`, `<mstts:express-as style="friendly">` for control.
**Prereqs:** L14 works.
**Time:** ~5 min.

**Concept:** Neural HD voices are trained differently — they read
semantic content and emotional cues better than plain Neural. But they
only expose the good stuff via SSML — plain text falls back to a flat
read. SSML lets you nudge specific words for pronunciation, break
points, emphasis, and speaking style.

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

# Lesson 17 — LLM Speech Preview (MAI-Transcribe)

**You'll learn:** file-based transcription that goes through an LLM (MAI-Transcribe) — prompt-tunable, better for domain jargon and mixed-language audio.
**Prereqs:** `SPEECH_ENDPOINT` in `.env`; sample audio.
**Time:** ~10 min (LLM transcription is slower).

**Concept:** `mai-transcribe` is Microsoft's LLM-based transcription
model. Same REST route as Fast Transcription
(`/speechtotext/transcriptions:transcribe`) with `"model": "mai-transcribe"`
and an optional `"prompt"` to bias vocabulary. Preview.

**Code:**

```python
# 17_llm_speech_preview.py (excerpt)
url = f"{settings().speech_endpoint}/speechtotext/transcriptions:transcribe?api-version=2025-10-15"
with audio.open("rb") as f:
    files = {
        "audio": (audio.name, f, "audio/wav"),
        "definition": (None,
            '{"model":"mai-transcribe","locales":["en-US"],'
            '"prompt":"Northwind product names include Connect, Sentinel, Ledger. Use exact spellings."}',
            "application/json"),
    }
    r = httpx.post(url, headers={"Authorization": f"Bearer {_token()}"}, files=files, timeout=180.0)
```

**Expected output:** transcript that respects the prompt hints (spells "Connect" correctly rather than "Konnect", etc.).

**Key points:**
- **API version fix:** `2025-10-15` (older `2025-11-15-preview` was wrong).
- Also available: `gpt-4o-transcribe`, `gpt-4o-mini-transcribe`, `whisper-1` for different quality/cost points.
- Prompt-tuning is the "custom speech for people who don't want to train a model" — cheaper than L19.

---

# Lesson 18 — Voice Live for a Prompt Agent

**You'll learn:** real-time speech-to-speech conversation with a Foundry Prompt Agent via a WebSocket; agent inline-created so it runs cold.
**Prereqs:** `VOICE_LIVE_ENDPOINT` in `.env`; `PROJECT_ENDPOINT` in `.env`.
**Time:** ~15 min.

**Concept:** Voice Live streams:
- Client → WebSocket → send mic audio buffers.
- Voice Live routes to a Prompt Agent (transcribes → agent thinks → TTS).
- WebSocket → Client → receive audio deltas.

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

    async with websockets.connect(url, extra_headers=headers) as ws:
        await ws.send(json.dumps({"type": "input_audio_buffer.append", "audio": b64_audio}))
        await ws.send(json.dumps({"type": "input_audio_buffer.commit"}))
        await ws.send(json.dumps({"type": "response.create"}))
        async for msg in ws:
            event = json.loads(msg)
            if event.get("type") == "response.done":
                break
```

**Expected output:** several WebSocket events (`session.created`,
`input_audio_buffer.committed`, `response.audio.delta`, `response.done`)
scrolling as the agent transcribes → responds → speaks.

**Key points:**
- **URL correction:** `/voice-live/realtime?api-version=2026-04-10`; params `agent_id` + `project_id` (not `agent_name`).
- For non-agent scenarios pass `model=gpt-realtime` instead of the agent params.
- Two subdomain options: `services.ai.azure.com` (current) or `cognitiveservices.azure.com` (older resources).
- Voice Live for Prompt Agents is GA-ish (preview); for Hosted Agents the shape differs.

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

**Expected output:** transcript that gets domain-specific words correct where the base model would guess.

**Key points:**
- Batch Transcription does NOT need a custom endpoint even when using your custom model — you reference the model directly in the batch request.
- MAI-Transcribe with a prompt (L17) is a lightweight alternative — no training needed.
- Custom Speech has three stages: **train** (Speech Studio, needs labeled data) → **test** (word error rate) → **deploy** (get endpoint GUID).

---

# Common Exam Traps

| Trap | Truth |
|------|-------|
| "Opinion Mining uses a different `kind`" | ❌ — same `kind: SentimentAnalysis`, just pass `show_opinion_mining=True` |
| "Fast Transcription is the same as real-time STT" | ❌ — Fast = one file sync; real-time = live stream |
| "Neural HD works without SSML" | ❌ — Neural HD **requires** SSML for the good stuff; plain Neural doesn't |
| "`TranslationRecognizer` is Azure Translator" | ❌ — `TranslationRecognizer` is the Speech SDK; Azure Translator is a separate REST service |
| "Language MCP + Speech MCP share one URL path" | ❌ — different paths: `/language/mcp` vs `/speech/mcp` |
| "GPT does compliance-grade PII redaction" | ❌ — Azure Language PII is certified; GPT is approximate |
| "Voice Live uses `/voice-live/v1`" | ❌ — current URL is `/voice-live/realtime?api-version=2026-04-10` |
| "Voice Live takes `agent_name`" | ❌ — takes `agent_id` + `project_id` query params (or `model` for non-agent) |
| "Fast STT api-version is `2024-11-15`" | ❌ — current `2025-10-15` |
| "MAI-Transcribe replaces the Speech SDK" | ❌ — MAI is file-based only; SDK covers real-time + mic + streaming |
| "Custom Speech works for batch by default" | ✔ — batch can use a custom model without deploying an endpoint. Real-time DOES need the endpoint. |
| "Extractive and Abstractive summarization are the same kind" | ❌ — separate `kind` values (`ExtractiveSummarization` / `AbstractiveSummarization`) |

---

> The 30-second cheat sheet lives at the [top of this README](#30-second-domain-4-cheat-sheet)
> — scroll up any time an exam question makes you second-guess which lesson covers it.
