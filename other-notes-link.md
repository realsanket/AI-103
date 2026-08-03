https://learn.microsoft.com/en-us/azure/ai-services/content-safety/

Here's a **revision sheet** for the major **Microsoft Foundry (Azure AI Services)** families. This groups the services by what they do, the common REST endpoint pattern, and the major sub-features. The table is based on the current Microsoft Foundry/Azure AI Services documentation. ([Microsoft Learn][1])

| Service Family                     | Purpose                                       | Major Features / Subtypes                                                                                                                                                                                                                                                              | Typical Endpoint Pattern                  |
| ---------------------------------- | --------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------- |
| **Azure AI Language**              | Analyze and understand text                   | Language Detection, Named Entity Recognition (NER), PII Detection/Redaction, Sentiment Analysis, Opinion Mining, Key Phrase Extraction, Entity Linking, Summarization, Text Classification, Conversational Language Understanding (CLU), Question Answering, Healthcare Text Analytics | `/language/:analyze-text` (most features) |
| **Azure AI Translator**            | Translate languages                           | Text Translation, Document Translation, Transliteration, Dictionary Lookup, Dictionary Examples, Language Detection                                                                                                                                                                    | `/translator/text/...`                    |
| **Azure AI Speech**                | Voice AI                                      | Speech-to-Text, Real-time Speech Recognition, Text-to-Speech, Speech Translation, Speaker Recognition, Voice Live API, Custom Speech, Custom Voice, Avatar                                                                                                                             | `/speech/...` or Speech SDK               |
| **Azure AI Vision**                | Analyze images/videos                         | OCR (Read), Image Analysis, Object Detection, Captioning, Dense Captions, Smart Cropping, Face Detection (limited), Video analysis                                                                                                                                                     | `/vision/...`                             |
| **Azure AI Document Intelligence** | Extract structured information from documents | Read OCR, Layout Analysis, Invoices, Receipts, ID Documents, Business Cards, Contracts, Tax Forms, Custom Extraction Models, Classification                                                                                                                                            | `/documentintelligence/...`               |
| **Azure Content Understanding**    | Understand multimodal content                 | Document Understanding, Image Understanding, Audio Understanding, Video Understanding, Custom field extraction                                                                                                                                                                         | `/contentunderstanding/...`               |
| **Azure AI Search**                | Search + RAG                                  | Full-text Search, Vector Search, Hybrid Search, Semantic Ranking, AI Enrichment                                                                                                                                                                                                        | `/indexes/...`                            |
| **Azure AI Content Safety**        | Detect unsafe content                         | Text Moderation, Image Moderation, Prompt Shield, Jailbreak Detection, Protected Material Detection, Groundedness Detection                                                                                                                                                            | `/contentsafety/...`                      |

---

# Azure AI Language (Most Important for NLP)

These features all belong to **Azure AI Language**. Most of them share the **same REST endpoint**, with the operation selected by the `"kind"` field in the request body. ([Microsoft Learn][2])

| Feature                  | What it does                                       | `kind`                                                 |
| ------------------------ | -------------------------------------------------- | ------------------------------------------------------ |
| Language Detection       | Detect input language                              | `LanguageDetection`                                    |
| Named Entity Recognition | Extract people, organizations, places, dates, etc. | `EntityRecognition`                                    |
| PII Detection            | Detect SSNs, emails, phone numbers, etc.           | `PiiEntityRecognition`                                 |
| Sentiment Analysis       | Positive/Negative/Neutral sentiment                | `SentimentAnalysis`                                    |
| Opinion Mining           | Opinion targets and sentiment                      | `SentimentAnalysis` (with opinion mining options)      |
| Key Phrase Extraction    | Extract important phrases                          | `KeyPhraseExtraction`                                  |
| Entity Linking           | Link entities to Wikipedia                         | `EntityLinking`                                        |
| Summarization            | Summarize documents or conversations               | `AbstractiveSummarization` / `ExtractiveSummarization` |
| Healthcare               | Extract medical entities                           | `Healthcare`                                           |

Typical request pattern:

```text
POST /language/:analyze-text
```

```json
{
  "kind": "...",
  "analysisInput": {
    "documents": [...]
  }
}
```

---

# Azure AI Translator

Translator uses a **different API family** from Language.

| Feature              | Endpoint                               |
| -------------------- | -------------------------------------- |
| Text Translation     | `/translator/text/translate`           |
| Document Translation | `/translator/document/...`             |
| Transliteration      | `/translator/text/transliterate`       |
| Dictionary Lookup    | `/translator/text/dictionary/lookup`   |
| Dictionary Examples  | `/translator/text/dictionary/examples` |
| Detect Language      | `/translator/text/detect`              |

Request pattern:

```text
POST /translator/text/translate
```

```json
{
    "inputs":[...]
}
```

---

# Azure AI Speech

Speech APIs are organized around voice and audio processing. ([Microsoft Learn][1])

| Feature             | Purpose                            |
| ------------------- | ---------------------------------- |
| Speech-to-Text      | Audio → Text                       |
| Text-to-Speech      | Text → Audio                       |
| Speech Translation  | Audio → Translated Text            |
| Voice Live          | Real-time conversational voice API |
| Avatar              | Animated speaking avatar           |
| Speaker Recognition | Verify or identify speakers        |
| Custom Speech       | Train recognition for your domain  |
| Custom Voice        | Build a custom synthetic voice     |

---

# Azure AI Vision

| Feature          | Purpose                            |
| ---------------- | ---------------------------------- |
| OCR (Read)       | Extract text from images/PDFs      |
| Image Analysis   | Tags, captions, objects            |
| Object Detection | Detect objects with bounding boxes |
| Captioning       | Generate image descriptions        |
| Dense Captioning | Describe multiple regions          |
| Smart Crop       | AI-based cropping                  |

---

# Azure AI Document Intelligence

| Feature           | Purpose                      |
| ----------------- | ---------------------------- |
| Read              | OCR                          |
| Layout            | Paragraphs, tables, headings |
| Invoice           | Extract invoice fields       |
| Receipt           | Extract receipt data         |
| ID Document       | Passport, driver's license   |
| Business Card     | Contact information          |
| Contract          | Contract fields              |
| Tax Forms         | Tax document extraction      |
| Custom Extraction | Train on your own forms      |
| Classification    | Classify document types      |

---

# Azure Content Understanding

This is Microsoft's newer multimodal service for extracting structured information from documents, images, audio, and video. ([Microsoft Learn][1])

| Feature                | Purpose                      |
| ---------------------- | ---------------------------- |
| Read                   | OCR                          |
| Layout                 | Document structure           |
| Document Understanding | Extract business fields      |
| Image Understanding    | Structured image insights    |
| Audio Understanding    | Analyze spoken/audio content |
| Video Understanding    | Analyze video content        |

---

# Which service should I use?

| If you want...                             | Use                                                             |
| ------------------------------------------ | --------------------------------------------------------------- |
| Translate text                             | Azure AI Translator                                             |
| Detect language                            | Azure AI Language *(or Translator if translation-related)*      |
| Extract people/organizations               | Azure AI Language (NER)                                         |
| Detect sentiment                           | Azure AI Language                                               |
| Extract key phrases                        | Azure AI Language                                               |
| Remove PII                                 | Azure AI Language                                               |
| Summarize text                             | Azure AI Language                                               |
| Speech → Text                              | Azure AI Speech                                                 |
| Text → Speech                              | Azure AI Speech                                                 |
| Translate speech                           | Azure AI Speech                                                 |
| OCR from PDFs                              | Azure AI Document Intelligence (Read) or Azure AI Vision (Read) |
| Extract invoice/receipt fields             | Azure AI Document Intelligence                                  |
| Analyze images                             | Azure AI Vision                                                 |
| Analyze mixed documents/images/audio/video | Azure Content Understanding                                     |
| Build vector/RAG search                    | Azure AI Search                                                 |

## REST patterns to memorize

| Service                   | Common REST pattern                          |
| ------------------------- | -------------------------------------------- |
| **Language**              | `POST /language/:analyze-text`               |
| **Translator**            | `POST /translator/text/...`                  |
| **Speech**                | `POST /speech/...` (or Speech SDK/WebSocket) |
| **Vision**                | `POST /vision/...`                           |
| **Document Intelligence** | `POST /documentintelligence/...`             |
| **Content Understanding** | `POST /contentunderstanding/...`             |
| **Content Safety**        | `POST /contentsafety/...`                    |
| **Azure AI Search**       | `POST /indexes/...` or `/docs/search`        |

This "cheat sheet" is a good mental model: first identify the **service family** (Language, Translator, Speech, Vision, etc.), then learn that family's endpoint pattern and request format. Within a family—especially **Azure AI Language**—many features differ only by a field such as `"kind"` rather than requiring a completely different API. ([Microsoft Learn][2])

[1]: https://learn.microsoft.com/en-us/azure/ai-services/what-are-ai-services?utm_source=chatgpt.com "What are Foundry Tools? - Foundry Tools | Microsoft Learn"
[2]: https://learn.microsoft.com/en-gb/azure/ai-services/language-service/overview?utm_source=chatgpt.com "What is Azure Language in Foundry Tools - Foundry Tools | Microsoft Learn"



A good way to memorize this is to **group by the type of input** rather than trying to remember eight separate services. Your uploaded revision sheet already organizes the services by family. 

# 🧠 The Azure AI House

Imagine a house with **8 rooms**.

```
                    Azure AI House
                          │
 ┌────────────────────────────────────────────────────┐
 │                                                    │
 │  📝 Text        🌍 Language      🎤 Voice           │
 │  Language       Translator       Speech            │
 │                                                    │
 │  🖼️ Images      📄 Documents     🎬 Mixed Content   │
 │  Vision         Document Int.   Content Understand │
 │                                                    │
 │  🔍 Search      🛡️ Safety                          │
 │  AI Search      Content Safety                     │
 └────────────────────────────────────────────────────┘
```

---

# Step 1: Remember the Input

Ask yourself:

> **"What am I giving Azure?"**

| Input                                   | Service               | Think...                     |
| --------------------------------------- | --------------------- | ---------------------------- |
| 📝 Text                                 | Language              | Understand text              |
| 🌍 Text                                 | Translator            | Change language              |
| 🎤 Audio                                | Speech                | Understand or generate voice |
| 🖼️ Image                               | Vision                | Understand pictures          |
| 📄 PDF/Form                             | Document Intelligence | Extract structured fields    |
| 🎬 Mixed (image + audio + docs + video) | Content Understanding | Understand everything        |
| 📚 Documents                            | AI Search             | Find information             |
| 🚫 Harmful text/images                  | Content Safety        | Check if safe                |

---

# Step 2: Learn the Families

## 📝 Language = Understand text

Think:

```
Read text
      ↓
Understand it
```

Everything is about **understanding**.

```
Language
│
├── Detect Language
├── NER
├── PII
├── Sentiment
├── Key Phrases
├── Summarization
├── Entity Linking
├── Healthcare
```

Memory sentence:

> **Language reads and understands text.**

---

## 🌍 Translator = Change language

```
English
     ↓
Spanish
```

Only translation-related tasks.

```
Translator
│
├── Translate
├── Document Translate
├── Dictionary
├── Transliteration
```

Memory:

> **Translator changes languages.**

---

## 🎤 Speech = Voice

```
Voice
 ↓
Text

Text
 ↓
Voice
```

Everything starts with sound.

```
Speech
│
├── STT
├── TTS
├── Speech Translation
├── Avatar
├── Voice Live
├── Speaker Recognition
```

Memory:

> **Speech hears and speaks.**

---

## 🖼️ Vision = Images

```
Picture
     ↓
Understand
```

```
Vision
│
├── OCR
├── Caption
├── Detect Objects
├── Tags
```

Memory:

> **Vision sees.**

---

## 📄 Document Intelligence

Think

```
Invoice

Passport

Receipt

Contract
```

↓

Extract fields.

Memory:

> **Document Intelligence reads business documents.**

---

## 🎬 Content Understanding

Think

```
PDF

Image

Video

Audio

All together
```

↓

One AI.

Memory:

> **Content Understanding understands everything.**

---

## 🔍 AI Search

```
Millions of documents

↓

Find answer
```

Memory:

> **Search finds knowledge.**

---

## 🛡️ Content Safety

```
Text

↓

Safe?
```

Memory:

> **Content Safety protects AI.**

---

# Step 3: REST Endpoints

Don't memorize every endpoint.

Memorize the **first word**.

| Family                | Endpoint Starts With    |
| --------------------- | ----------------------- |
| Language              | `/language`             |
| Translator            | `/translator`           |
| Speech                | `/speech`               |
| Vision                | `/vision`               |
| Document Intelligence | `/documentintelligence` |
| Content Understanding | `/contentunderstanding` |
| Search                | `/indexes`              |
| Content Safety        | `/contentsafety`        |

Notice the pattern:

```
Family name
↓

Endpoint name
```

Most endpoints literally use the service name.

---

# Step 4: One-line Story

```
📝 Language
Understand text

🌍 Translator
Change language

🎤 Speech
Voice ↔ Text

🖼️ Vision
Understand images

📄 Document Intelligence
Extract fields from documents

🎬 Content Understanding
Understand any media

🔍 Search
Find knowledge

🛡️ Content Safety
Keep AI safe
```

---

# 🚀 30-Second Interview Trick

When asked **"Which Azure AI service would you use?"**, think in this order:

```
What is my input?

Text?
    ↓ Language

Need another language?
    ↓ Translator

Voice?
    ↓ Speech

Image?
    ↓ Vision

Invoice/Receipt/PDF?
    ↓ Document Intelligence

Mixed media?
    ↓ Content Understanding

Need RAG/Search?
    ↓ AI Search

Need moderation?
    ↓ Content Safety
```

If you can remember **the input type first**, choosing the correct Azure AI service becomes much easier than trying to memorize a long list of names.
