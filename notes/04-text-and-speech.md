# Domain 4 — Implement Text Analysis Solutions (10–15%)

## Syllabus sections

| Section | Topics |
|---------|--------|
| Language model text analysis | Entity extraction, sentiment/tone, translation, domain customization |
| Speech solutions | STT/TTS for agents, custom speech models, multimodal audio, speech translation |

> **MS Docs source:** `.context/azure-ai-docs/articles/foundry/` (Language/Speech MCP: `foundry/mcp/`) · `.context/azure-ai-docs/articles/ai-services/` (Language, Speech services)

---

# Azure AI Language

## The service tree

```
Azure AI Language
│
├── Language Detection          kind: LanguageDetection
├── Named Entity Recognition    kind: EntityRecognition
├── PII Detection               kind: PiiEntityRecognition
├── Sentiment Analysis          kind: SentimentAnalysis
│     └── Opinion Mining        (same kind, extra param)
├── Key Phrase Extraction       kind: KeyPhraseExtraction
├── Entity Linking              kind: EntityLinking
├── Abstractive Summarization   kind: AbstractiveSummarization
├── Extractive Summarization    kind: ExtractiveSummarization
└── Text Analytics for Health   kind: Healthcare
```

## `kind` field cheat sheet

| Feature | `kind` value |
|---------|-------------|
| Language Detection | `LanguageDetection` |
| Named Entity Recognition | `EntityRecognition` |
| PII Detection | `PiiEntityRecognition` |
| Sentiment Analysis | `SentimentAnalysis` |
| Opinion Mining | `SentimentAnalysis` + `opinionMining: true` |
| Key Phrase Extraction | `KeyPhraseExtraction` |
| Entity Linking | `EntityLinking` |
| Abstractive Summarization | `AbstractiveSummarization` |
| Extractive Summarization | `ExtractiveSummarization` |
| Healthcare Entities | `Healthcare` |

## REST request pattern

```
POST https://<language-resource>.cognitiveservices.azure.com/language/:analyze-text
Authorization: Bearer <token>

{
  "kind": "EntityRecognition",
  "analysisInput": {
    "documents": [
      { "id": "1", "text": "Satya Nadella leads Microsoft in Redmond." }
    ]
  }
}
```

Memory: **All Language features share one endpoint — only `kind` changes.**

## Python SDK pattern

```python
from azure.ai.textanalytics import TextAnalyticsClient

client = TextAnalyticsClient(endpoint, DefaultAzureCredential())

# NER
result = client.recognize_entities(["Satya Nadella leads Microsoft."])

# PII
result = client.recognize_pii_entities(["My SSN is 123-45-6789."])

# Sentiment + Opinion Mining
result = client.analyze_sentiment(["The product is great but delivery was slow."],
                                   show_opinion_mining=True)

# Health
poller = client.begin_analyze_healthcare_entities(["Patient has Type 2 diabetes."])
result = poller.result()
```

---

# Discriminative vs Generative NLP

## Comparison table

| Dimension | Azure Language SDK (Discriminative) | GPT / Responses API (Generative) |
|-----------|-------------------------------------|----------------------------------|
| Model type | Fine-tuned per task | General-purpose LLM |
| Output | Structured (spans, scores, offsets) | Free text or JSON via prompt |
| Categories | Fixed predefined (Person, Org, Location…) | Any you describe in the prompt |
| Novel entities | No | Yes |
| Multi-task in one call | No (one `kind` per call) | Yes (combine NER + sentiment + summary) |
| Compliance-grade PII | Yes (certified redaction) | No |
| Medical entities | Yes (Healthcare kind) | Approximate only |
| Latency | Lower (smaller model) | Higher |
| Cost | Lower | Higher |

## When to pick which

```
Need compliance-grade PII redaction?       → Azure Language PII
Need medical entity extraction?            → Text Analytics for Health
Need NER on standard categories?           → Azure Language NER (faster/cheaper)
Need novel entity types (your domain)?     → GPT prompt
Need multi-task: NER + sentiment + summary?→ GPT prompt (one call)
Need abstractive summary?                  → GPT (better than extractive)
```

---

# Azure AI Translator

## Service tree

```
Azure AI Translator
│
├── Text Translation          POST /translator/text/translate
├── Document Translation      POST /translator/document/...
├── Transliteration           POST /translator/text/transliterate
├── Dictionary Lookup         POST /translator/text/dictionary/lookup
├── Dictionary Examples       POST /translator/text/dictionary/examples
└── Language Detection        POST /translator/text/detect
```

## Text Translation pattern

```python
from azure.ai.translation.text import TextTranslationClient

client = TextTranslationClient(endpoint, DefaultAzureCredential())
response = client.translate(
    body=[{"text": "Hello world"}],
    to_language=["es", "fr"],       # translate to Spanish AND French
    from_language="en",             # optional; auto-detects if omitted
)
```

## Translator vs Language

| | Azure Translator | Azure Language |
|--|-----------------|----------------|
| Purpose | Change language | Understand text |
| Language detection | Yes (as a feature) | Yes (as a feature) |
| NER, PII, Sentiment | No | Yes |
| Volume document translation | Yes | No |
| Glossary / terminology | Yes (custom translator) | No |

Memory: **Translator changes language; Language understands text.**

---

# Speech Solutions

## STT mode comparison

| Mode | API | When | Lesson |
|------|-----|------|--------|
| **Fast Transcription** | REST (`/speech/recognition/...`) | Single file, sync, fastest | `04/11_stt_fast_file.py` |
| **Real-time STT** | Speech SDK (`SpeechRecognizer`) | Live audio stream | `04/12_stt_real_time.py` |
| **Batch Transcription** | REST async (submit → poll → fetch) | Many files, async processing | `04/13_stt_batch.py` |

## STT pattern comparison

```python
# Fast Transcription (sync, file)
recognizer = SpeechRecognizer(speech_config, AudioConfig(filename="audio.wav"))
result = recognizer.recognize_once_async().get()

# Real-time (stream from mic)
recognizer = SpeechRecognizer(speech_config, AudioConfig(use_default_microphone=True))
recognizer.recognized.connect(callback)
recognizer.start_continuous_recognition()

# Batch (REST async)
# 1. POST to create transcription job
# 2. Poll GET until status == "Succeeded"
# 3. GET results URL and download
```

## TTS mode comparison

| Mode | SSML required | Quality | Lesson |
|------|--------------|---------|--------|
| **Neural** | Optional | High | `04/14_tts_neural.py` |
| **Neural HD** | Required | Highest (HD voice) | `04/15_tts_ssml_hd.py` |

### SSML example (Neural HD)

```xml
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
  <voice name="en-US-AndrewMultilingualNeural">
    <prosody rate="0.9" pitch="+5%">
      Welcome to Northwind support.
    </prosody>
  </voice>
</speak>
```

## Custom Speech Model

```
Train in Speech Studio
        ↓
Deploy custom model → get endpoint GUID
        ↓
Set in code: speech_config.endpoint_id = "your-endpoint-guid"
        ↓
All other code identical to standard STT
```

```python
config = speech_config()           # standard config (keyless)
config.endpoint_id = settings().custom_speech_endpoint_id
# now recognizer uses your custom acoustic/language model
```

Use when: domain jargon, proper nouns, accented speech that standard model misses.

## Speech Translation

```python
from azure.cognitiveservices.speech import translation

config = translation.SpeechTranslationConfig(auth_token=token, region=region)
config.speech_recognition_language = "en-US"
config.add_target_language("es")   # translate to Spanish

recognizer = translation.TranslationRecognizer(config)
result = recognizer.recognize_once_async().get()
# result.translations["es"] → Spanish text
```

Memory: **Speech Translation = `TranslationRecognizer`, NOT Azure Translator.**

---

# Advanced Speech: Voice Live + LLM Speech Preview

## Voice Live

```
Client (WebSocket)
        ↓ audio stream
Voice Live endpoint (wss://...)
        ↓ routes to Prompt Agent
Agent processes, generates response text
        ↓
TTS converts to audio
        ↓ audio stream
Client plays response
```

Real-time, bidirectional. Agent modality — the agent "hears" and "speaks".

## LLM Speech Preview (MAI-Transcribe)

```python
result = client.responses.create(
    model="gpt-4o-audio-preview",
    input=[{
        "type": "audio",
        "audio": {"url": audio_url}   # or base64
    }],
    instructions="Transcribe and answer the question in the audio.",
)
# → transcript + LLM response in one call
```

Difference from Voice Live: **LLM Speech Preview = file in → response out** (batch-style); **Voice Live = real-time stream** (conversational).

---

# Language + Speech MCP Tools

## Endpoint patterns

| Service | MCP Endpoint |
|---------|-------------|
| Azure Language | `https://<foundry>.cognitiveservices.azure.com/language/mcp?api-version=2025-11-15-preview` |
| Azure Speech | `https://<foundry>.cognitiveservices.azure.com/speech/mcp?api-version=2025-11-15-preview` |

## Use in an agent

```python
mcp_tool = McpTool(server_label="language-mcp", server_url=settings().language_mcp_url)
# agent can now call language NER, PII, sentiment etc. via MCP
```

---

# Text Analysis Decision Tree

```
Text input — what do you need?
        │
        ├── Change language?
        │     ├── Documents / bulk / glossary? → Azure Translator
        │     └── Tone/idiom/context?          → GPT translation
        │
        ├── Detect language?           → Language (LanguageDetection) or Translator /detect
        │
        ├── Extract entities?
        │     ├── Standard categories (Person, Org, Location)?  → Language NER
        │     └── Novel / domain-specific categories?           → GPT prompt
        │
        ├── Detect PII? (compliance-grade) → Language PII
        │
        ├── Sentiment + opinion?       → Language SentimentAnalysis + opinionMining
        │
        ├── Medical entities?          → Text Analytics for Health
        │
        └── Summarize?
              ├── Extractive (exact sentences)? → Language ExtractiveSummarization
              └── Abstractive (paraphrase)?     → GPT prompt

Audio input — what do you need?
        │
        ├── Single file sync?          → Fast Transcription (STT)
        ├── Live stream?               → Real-time STT (SDK)
        ├── Many files async?          → Batch Transcription (REST)
        ├── Translate speech?          → TranslationRecognizer (Speech SDK)
        ├── Agent voice conversation?  → Voice Live (WebSocket)
        ├── Audio + LLM in one call?   → LLM Speech Preview
        └── Domain vocab / accents?    → Custom Speech (endpoint_id)
```

---

# Common Exam Traps

| Trap | Truth |
|------|-------|
| "Opinion Mining uses a different `kind` from Sentiment Analysis" | ❌ — same `kind: SentimentAnalysis`, just pass `show_opinion_mining=True` |
| "Fast Transcription is the same as real-time STT" | ❌ — fast = file sync; real-time = live stream via SDK |
| "Neural HD voice works without SSML" | ❌ — Neural HD **requires** SSML; plain Neural doesn't |
| "`TranslationRecognizer` is Azure Translator" | ❌ — TranslationRecognizer is the Speech SDK class; Azure Translator is a separate REST service |
| "Language MCP and Speech MCP have the same endpoint pattern" | ❌ — different paths: `/language/mcp` vs `/speech/mcp` |
| "GPT does compliance-grade PII redaction" | ❌ — Azure Language PII is certified; GPT is approximate |

---

# 30-Second Domain 4 Trick

```
Text to understand?        → Azure Language SDK (kind field)
Text to translate?         → Azure Translator (volume) or GPT (tone)
Text from patient notes?   → Text Analytics for Health
Need structured JSON?      → GPT + json_schema strict mode

Short audio file?          → Fast Transcription (sync)
Live audio stream?         → Real-time STT (SpeechRecognizer)
Batch audio files?         → Batch Transcription (REST async)
Translate spoken audio?    → TranslationRecognizer (Speech SDK)
Agent talks to user?       → Voice Live (real-time WebSocket)
Custom domain vocab?       → Custom Speech (endpoint_id)
```
