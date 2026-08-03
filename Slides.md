# AI-103: Developing AI Apps and Agents on Azure

Source: `Slides.pdf` (267 slides). Instructor: Alan Rodrigues, CloudXeus.

---

## Section 1 — Foundation Models, Tools, Developer Workflow

### Generative AI Basics
- Class of AI learns patterns from data, creates new content (text, images, code, audio, video).
- Trained on massive datasets (web, books, code).
- Responds to natural-language prompts.
- Single model performs many tasks without retraining.

### How LLMs Work
- **Tokenisation** — text split into tokens (~¾ word each).
- **Attention** — transformers weigh how each token relates to every other in context window.
- **Next-token prediction** — probability distribution over vocab, sample most likely, repeat.
- **Autoregressive generation** — repeats until stop.

### Key Vocabulary
- **Token** — atomic unit; costs/limits/speeds measured in tokens.
- **Context Window** — max tokens per request (prompt + response).
- **Prompt** — input sent to model.

### GenAI Application Patterns
- Conversational AI (support bots, help desks, doc Q&A)
- Content Generation (drafting, summarizing, reports)
- Code Generation (autocomplete, explanation, tests, refactor)
- Agentic Workflows (tool calling, multi-step actions)
- Reasoning & Analysis (RAG over doc sets)

### LLM vs SLM
**LLMs**
- 100B–trillions of tokens training data; billions–hundreds of billions params.
- Complex reasoning, multi-step problem solving, nuanced writing, code.
- Generalise across diverse tasks with little/no fine-tuning.
- Require significant GPU infra; higher cost per token.
- Accessed via API in Foundry.

**SLMs**
- 1B–14B params (boundary not fixed).
- Curated high-quality training data.
- Excel at narrower task set (coding, reasoning, Q&A).
- Lower cost, faster inference, edge/on-device capable.

### Popular Models
- **LLMs**: GPT-5.5 (frontier, computer-use), Claude Opus 4.8 (1M context, Constitutional AI), Meta Llama 3.3 70B (open-weight serverless), Mistral Large 2 (multilingual), Google Gemma 4 (256K context, multimodal).
- **SLMs**: Phi-4 (14B flagship), Llama 3.2 1B/3B (edge), Mistral 7B (self-host/fine-tune).

### Choose LLM vs SLM
- **LLM**: broad knowledge, multi-step reasoning, multimodal, exploration/prototyping, low-volume/high-value, agentic multi-tool orchestration.
- **SLM**: narrow well-defined task, cost at scale, low latency, offline/constrained.

### Microsoft Foundry
- Azure's single platform for AI apps + agents. At `ai.azure.com`.
- Consolidates: Azure OpenAI Service, Azure AI Studio, Azure ML AI, Cognitive Services.
- Capabilities: **Model Catalog** (1,700+ models), **Playgrounds** (Chat/Agents/Images/Video), **Agent Service**, **Evaluations**, **Fine-tuning** (OpenAI + Phi), **Foundry Tools** (Search, Content Understanding, Speech, Vision), **Observability** (Azure Monitor).

### Deploying Models — Two Dimensions
**Billing**
- **Pay-per-token (Standard)** — no upfront commit.
- **Provisioned (PTU)** — reserved capacity, hourly billing regardless of use.

**Data processing scope**
- **Global** — routed across any region; highest availability, lowest rate, no residency guarantee.
- **Data Zone** — geography-bound (US/EU).
- **Regional** — single region; strictest residency.

**Deployment types**
- **Global Standard** — Microsoft-recommended default. First to get new models. Data at rest stays in region, inference may run anywhere.
- **Standard (Regional)** — inference stays in deploy region; higher per-token cost, lower throughput.
- **Provisioned Throughput (PTU)** — reserved capacity blocks. PTUs are model-independent within region/type. Up to ~70% savings at high volume. Guaranteed rate limits.
- **Serverless API (MaaS)** — Llama, Mistral, Claude (via MaaS), Cohere. No GPUs to manage. Billed via Azure Marketplace for partner models.

### Tools (Model-Level)
- Bridge between text generation and real-world actions.
- Model decides *when* to use, *which* tool, *what* to pass. App executes.
- Cycle: user msg → model evaluates → tool request → app executes → result to model → final answer.

**Built-in tools**
- **Web Search** — real-time internet lookup; overcomes training cutoff.
- **File Search** — private document store search; RAG foundation.
- **Code Interpreter** — Python in isolated sandbox; precise results not approximations.

---

## Section 2 — From Prompts to Agents: RAG + Agentic on Foundry

### Agentic AI
- Traditional AI: 1 prompt → 1 response.
- Agentic AI: pursues goal across multi-steps, decides along the way.
- Uses tools, calls services, remembers context, takes actions autonomously.
- Shift: "AI that answers" → "AI that acts".

### Why Now
- LLMs got reliable tool calling + structured output.
- Long context windows hold state.
- **MCP** (Model Context Protocol) standardized agent-tool connections.
- Managed agent infra (Foundry).
- Enterprise demand for coordination reduction.

### Use Cases
- Customer support triage/routing/resolution.
- Retail: recommendations, order tracking, returns.
- Financial: account queries, fraud alerts (human gates on high-value).
- Healthcare: scheduling, symptom triage, med reminders.

### Security Concerns
- Agents operate with real permissions.
- **Over-privileged agents** = major risk. Use least-privilege.
- **Never hardcode credentials** — use managed identity or secure key stores.
- **Prompt injection** — attacker embeds instructions in data agent reads.
- 92% enterprise security pros concerned.

### First Agent — IT Help Desk Scenario
- Repetitive queries (password reset, VPN, install steps, ticket status).
- Agent: accept English → decide tool → call → respond.
- Loop: Receive goal → Reason → Call tool → Observe → Respond.
- Developer never hard-codes which tool — model decides.

### Foundry Agent Service
- Managed platform: build, deploy, scale agents.
- Any framework: OpenAI Agents SDK, LangGraph, Agent Framework, Anthropic SDK.
- Any model from catalog: GPT-4o, Llama, DeepSeek, etc.
- **Responses API** = single entry point.
- Range: no-code portal → fully custom containerized.

### Agent Components
- **Model** — reasoning + language.
- **Instructions** — goals, constraints, behavior.
- **Tools** — data + actions.
- Agents can run without chat interface (event-triggered background).

### Tools in Foundry
- Built-in: Web Search, File Search, Memory (preview), Code Interpreter, MCP servers (remote + custom).
- Custom functions.
- MCP servers addable from Add Tools catalog.
- Custom MCP servers hostable on Azure Functions.

### Enterprise Capabilities
- **Agent identity** — dedicated Microsoft Entra identity per agent.
- **Private networking** — run inside VNet.
- **RBAC** — Entra + Azure RBAC.
- **Content safety** — filters + XPIA (cross-prompt injection) mitigation.
- **BYO resources** — Azure Storage, AI Search, Cosmos DB.

### Publishing + Distribution
- Publish dropdown reveals distribution options.
- Auto-versioned on every save.
- **Routines** = scheduled auto-runs. Needs: Name, Agent, Conversation (optional), Prompt, Trigger.
- **Teams / M365 Copilot** publish — surface as bot in existing tools. Requires admin config.

### Agent Tools (deeper)
- Extend agents beyond text → take action.
- Model decides invocation based on agent instructions.
- Can: web search, run Python, vector search docs, call APIs, browser automation, delegate to other agents.

### Toolbox (Preview)
- Curated tool bundle exposed as single MCP endpoint.
- Attach agent to toolbox instead of individual tools.
- Versioned (test before promote).
- Central auth (Entra ID + OAuth), credential injection, token refresh.

### Hosted Agents
- Custom code, any framework/language, containerized, registered with Foundry.
- Foundry manages: hosting/scaling, endpoint, auth, integration.
- SDK: `agent-framework` package with `FoundryChatClient`, `Agent` class, `project_endpoint` + Azure credentials.
- Choose when: custom orchestration, existing framework migration (LangChain/Semantic Kernel), complex stateful workflows, multi-agent coordination.

### RAG (Retrieval Augmented Generation)
- Solves: LLMs don't know private/fresh data → hallucinations.
- Pattern: combine search + LLM. Responses grounded in your data. Citations to sources.
- Alternative to fine-tuning when adding knowledge (not changing behavior).

**Concepts**
- **Grounding data** — retrieved content reducing guessing.
- **Index** — data structure for fast retrieval.
- **Embeddings** — numeric representations for vector similarity.
- **System prompt** — instructions on using retrieved content.

**Flow**: Retrieve → Augment → Generate (with citations).

**Retrieval modes**
- **Keyword** — exact term match.
- **Semantic** — meaning-based ranking.
- **Vector** — embedding similarity.
- **Hybrid** — keyword + vector (often with semantic ranking).
- **Azure AI Search** = recommended index store for RAG in Foundry.

### OpenAPI Specification
- Note: **OpenAI** = company (GPT); **OpenAPI** = open HTTP API standard (formerly Swagger, unrelated).
- Machine-readable JSON/YAML: endpoints, params, returns, auth.
- Renamed from Swagger 2016. Current: 3.0 / 3.1 (Foundry-accepted).
- For agents: Agent Service reads spec → auto-generates callable tools per operation. Model reads `description` fields → decides invocation. No glue code.

---

## Section 3 — Production-Ready: Memory, Workflows, Monitoring, Safety

### State: Conversations, Session, Memory
**Problem**: LLMs stateless. Three mechanisms at different time scales.

**Conversation History**
- Ordered messages in current conversation.
- Responses API: `client.conversations.create()`, pass `conversation=conversation.id`.
- Lives only for that thread. New conversation = blank slate.
- Solves within-thread recall. Does NOT solve cross-session.

**Session Context (Short-Term)**
- Tracks current session, immediate context.
- Managed by orchestration framework (e.g. Microsoft Agent Framework).
- Working vars, intermediate tool results, running msg thread.
- Gone when session ends. Agent's "RAM".

**Agent Memory (Long-Term)**
- Distilled knowledge across sessions.
- Foundry: **Memory in Foundry Agent Service** — managed, persistent, cross-session/device/workflow.

### Memory Pipeline (not a DB)
- Managed pipeline turning conversations into durable knowledge.
- Stored as items in managed memory store with consolidation + conflict-resolution.
- Three phases: **Extraction → Consolidation → Retrieval**.

**Extraction**
- LLM extracts key info (preferences, facts, context).
- Billable model call. Selective — signal in, noise out.

**Consolidation**
- Dedup: "likes coffee" + "enjoys coffee in the morning" → one item.
- Conflict resolution: newer supersedes older.
- Lean store, not transcript pile.

**Retrieval**
- **Static** — memories injected at conversation start (user profile).
- **Contextual** — retrieved per turn based on latest messages.

### Workflows
- Single agent limits: instructions grow conflicting, no guaranteed order, hard to insert checkpoints, hard to test/version/audit.
- Business processes need deterministic steps; single agent is probabilistic.

**What Workflow Is**
- Declarative predefined step sequence orchestrating agents + business logic.
- Part of Foundry Agent Service, built on Microsoft Agent Framework.
- Two synced views: visual designer + YAML definition (CI/CD friendly).
- Workflow controls *what happens when*; agent controls *how*.

**When to Use**
- Multi-agent orchestration in repeatable process.
- Deterministic step-based execution.
- Conditional branching + shared state without code.
- Human-in-the-loop checkpoints.
- Don't use for: single agent/task, simple tool use.

**Nodes**
- **Agent** — invoke agent from project.
- **Logic** — if/else, go to, for each.
- **Data transformation** — set variable, parse value.
- **Basic chat** — send message, ask question and wait.
- Nodes share state via variables (output → input).

### Quotas, Scaling, Rate Limits, Cost
- **Quota** = allocation of model capacity (TPM tab in Foundry).
- Example: gpt-5.4 Global Standard pool 1M TPM, 500K allocated.
- **Rate limiting %** shows if throttled (429s). 0% = healthy.
- **429 handling**: exponential backoff + jitter, spread across deployments/regions, queue non-immediate, increase TPM on hot deployments.
- **PTU** when transient 429s unacceptable — dedicated capacity, guaranteed rate limits. Quota per subscription/region/deployment type. TPM per PTU varies by model. Each model has minimum PTU.

### Evaluators
- Specialized tool scoring an interaction against criterion.
- Input: query + response + context + ground truth + agent trace → score + reasoning.
- One evaluator, one question.
- Used across lifecycle: pre-deploy test runs, CI/CD gates, production continuous eval.

**Mechanisms**
- **AI-assisted (LLM-as-judge)** — model judges output; you supply judge deployment.
- **NLP metrics** — F1, comparing to ground truth.
- **Hosted safety models** — risk/safety, Microsoft-hosted.

**Categories**
- **General purpose**: Coherence, Fluency.
- **Textual similarity**: Similarity (AI), F1, BLEU, GLEU, ROUGE, METEOR.
- **RAG**: Retrieval, Document Retrieval, Groundedness, Groundedness Pro (preview), Relevance, Response Completeness (preview).
  - Diagnostic split: Retrieval scores search side; Groundedness scores generation side. Completeness = opposite of groundedness (not omitting true things).
- **Risk & Safety**: Hate/Unfairness, Sexual, Violence, Self-Harm + Protected Materials, Code Vulnerability, Ungrounded Attributes, Prohibited Actions (preview), Sensitive Data Leakage (preview). Output = aggregate defect rate %.
- **Agent (outcome)**: Task Adherence, Task Completion, Intent Resolution, Task Navigation Efficiency.
- **Agent (tool-level)**: Tool Call Accuracy, Tool Selection, Tool Input Accuracy, Tool Output Utilization, Tool Call Success. Need full agent trace.

### Agent Tracing
- Foundry observability platform. Captures inputs, outputs, tool usage, retries, latencies, costs.
- Built on **OpenTelemetry** (open, vendor-neutral).
- Answers "where did this come from?" + "which step slowed/failed?"

**Concepts**
- **Spans** = building blocks; each = single operation with start/end/attributes.
- Spans nest (parent contains children) showing full call stack + order.
- **Attributes** = key-value metadata (params, return values, custom annotations).
- Captures: user in/agent out, tool calls + results, token consumption, duration/latency.

### Prompt Shields
- Detect attempts to manipulate model via adversarial input.
- Part of Foundry guardrails system.
- Two attack types by attacker location:
  - **User prompt attacks** — user tries to bypass system instructions.
  - **Document attacks** — third party hides instructions in ingested content.

**Spotlighting (Preview)**
- Extra defense for document attacks (not replacement).
- Tags ingested docs as lower-trust by base-64 encoding content.
- Model treats encoded as less trustworthy than user/system prompts.

### Model Router
- Deployable model in Foundry sitting in front of pool of LLMs.
- Deploy `model-router` from catalog like any endpoint.
- App sends to single endpoint; router selects best underlying model in real time.
- Response format = standard Chat Completions API. Zero code change.
- `"model"` field in response reveals which was picked.
- Router itself is trained LM (not rules engine). Analyzes: complexity, reasoning demand, task type, token count.
- Doesn't store prompts. Honors access + data zone boundaries.
- **Supported**: OpenAI (gpt-4.1, gpt-4.1-mini/nano, o4-mini, gpt-5, gpt-5-mini/nano); Third-party (DeepSeek-V3.1/V3.2, Llama-4-Maverick-17B, grok-4, grok-4-fast-reasoning); Anthropic (claude-haiku-4-5, claude-sonnet-4-5, claude-opus-4-1, claude-opus-4-6).

---

## Section 4 — Wider Ecosystem: LangChain, LangGraph, MCP

### LangChain
- Built by Harrison Chase (Oct 2022, Robust Intelligence).
- Open-source Python + JS framework for LLM apps.
- Standard interface across providers (OpenAI, Anthropic, Google, Azure, Mistral).
- Abstracts: doc loading, prompt formatting, chaining, retrieval.
- Popularity: launched same month as ChatGPT; 700+ integrations; strong docs; RAG made accessible.

### LangChain Agent Core
- Agent = LM + harness for reasoning + acting.
- `create_agent` builds graph-based runtime via **LangGraph**.
- Graph = nodes (steps) + edges (connections).
- Three node types: **model node** (LLM call), **tools node** (execute tools), **middleware** (shapes behavior).
- Runs until stop: model emits final answer or iteration limit.
- Pattern: **ReAct** — Reason → Act → Observe → Repeat.

### LangGraph
- Low-level orchestration framework for stateful long-running agents.
- Built by LangChain Inc, usable independently.
- Used by Klarna, Uber, JP Morgan.
- Focus: agent orchestration only (not prompts/model wrappers).

**Four capabilities**
- **Persistence** — agents survive failure, resume where left off.
- **Human-in-the-loop** — pause/inspect/modify state.
- **Comprehensive memory** — short-term + long-term cross-session.
- **Streaming** — surface every step in real time.

**State**
- `TypedDict` — typed Python dict.
- Every node reads from + writes to state.
- Common built-in: `MessagesState` with `add_messages` reducer.
- **Reducers**: default overwrites; `add_messages` appends + handles message IDs.

**Nodes**
- Python functions accepting current state → return updated state.
- Node only returns changed fields.
- Special: **START** (entry), **END** (terminal).
- Sync or async.

**Compile**
- Validates structure (no orphans, no missing edges).
- Locks runtime config (checkpointers, breakpoints).
- Returns runnable graph object.

### MCP (Model Context Protocol)
- Problem: M apps × N tools = M×N unique connectors. Custom code per integration.
- **MCP** — open standard by Anthropic (Nov 2024). Converts M×N → M+N.
- Inspired by LSP (Language Server Protocol).
- Open-source day one. Co-governed: Anthropic, OpenAI, Google, Microsoft, AWS, Block, Cloudflare, Bloomberg.

**Three Roles**
- **Host** — AI app user interacts with (Claude Desktop, Foundry Agent Service, Cursor).
- **Client** — inside host, manages 1:1 connection to one server.
- **Server** — external program exposing tools/data/templates.
- Host can run multiple clients (one per server). Model never talks to server directly; client brokers.

**Three Primitives**
- **Tools** — executable functions (API calls, DB writes, computation). Model-controlled.
- **Resources** — read-only data (files, records, live data). App-controlled.
- **Prompts** — reusable instruction templates. User-controlled.
- Every server declares primitives at handshake. Agent discovers tools at runtime — no hardcoding.

---

## Section 5 — Computer Vision Solutions

### Prompt Shields for Documents (Indirect Prompt Injection)
**Scenario**: OCR on uploaded images, extracted text appended to prompt as context. Embedded text in image can carry hidden instructions. Model can't distinguish data from commands.

**Two Attack Models**
- **User Prompt attacks** — user is attacker, overrides system rules directly.
- **Document attacks** — third party is attacker; instructions smuggled via documents, emails, web pages, OCR text.

**Document Attack Details**
- Entry: third-party content.
- Method: model misinterprets content as instruction not data.
- Objective: attacker gains control/access without touching user prompt.
- Result: model executes unintended commands from context.

**Why OCR Scenario**
- OCR output appended "as additional context" — structurally identical to retrieved doc / pasted email.
- User never typed the injection; arrived via image pixels.
- Textbook **indirect injection** case for Prompt Shields for Documents.
- Image moderation, protected material detection, User Prompt shields solve *different* problems.

---

## Section 6 — Text Analysis Solutions

### Language Model Text Analysis
**Two paths**
- **Discriminative** — narrow-trained model per task (NER, sentiment, translation) via Foundry Tools (Azure Language, Azure Translator).
- **Generative** — general model (GPT-5.4) instructed via prompt. Flexible, schema-free, multi-task per call.

**Tasks**
- **Entity Extraction** — Azure Language NER (prebuilt/custom) vs GPT prompt (any field, incl. concepts no prebuilt saw, e.g. "CloudXeus SLA tier + breach penalty").
- **Topics + Summaries** — Azure Language dedicated feature (conversation, call-center variants) vs GPT via prompt wording.
- **Structured JSON Output** — "respond in JSON" is advisory only. **Structured Outputs** on Responses API (`text.format`, `type: "json_schema"`, `strict: true`) constrain token generation itself. Mechanically guaranteed schema match.
- **Sentiment + Tone** — Azure Language sentiment (pos/neg/neutral/mixed) + opinion mining (aspect-linked). Tone (formality/emotion/urgency) = generative only. Generative advantage: single-call multi-return. Discriminative: benchmarked confidence scores.
- **Translation** — Azure Translator (large lang coverage, doc translation, custom terminology, predictable per-char pricing) vs GPT (contextual, idiom/tone/domain jargon; no glossary tooling).

### Azure AI Language
- NLP service via REST, SDKs, Foundry portal no-code, MCP server.
- Rebranded "Azure Language in Foundry Tools".
- Two tiers: **Core** (active dev, new projects) + **Legacy** (stable, supported, not investment focus).

**Core**
- **PII detection** — identify + redact PII; preview anonymization with synthetic replacement.
- **Language detection** — language + dialect.
- **NER** — prebuilt (fixed categories) + custom (train your own).
- **Text Analytics for Health** — medical extraction (conditions, meds, dosages).

**Legacy**
- Key phrase extraction (no training).
- Sentiment analysis + opinion mining.
- Summarization (extractive + abstractive + conversation/call-center variants).
- Entity linking (disambiguate + link to Wikipedia).

**Azure Language Agents (in Foundry portal)**
- **Intent Routing agent** — CLU (intent classification) + Custom Question Answering; deterministic routing with RAG fallback.
- **Exact Question Answering agent** — no-code verbatim FAQ from CQA knowledge base; consistent auditable answers.

### Azure Language MCP Server
- Open protocol for AI agent tool discovery + call.
- Three roles: Host (Foundry), Client (in host), Server (exposes tools).
- Dynamic tool discovery: agent queries server at runtime — not hardcoded.

**How Agent Picks Tool**
- User prompt → model reads tool catalog + descriptions → picks tool(s) → call via MCP server → structured results back → natural response.
- No routing logic to write. Single prompt can trigger multiple tool calls in one turn (e.g. lang detection + NER together).

**Endpoint**
- Remote: `https://{foundry-resource-name}.cognitiveservices.azure.com/language/mcp?api-version=2025-11-15-preview`
- `{foundry-resource-name}` = Foundry / Azure Language resource name (configured once).
- Local MCP server variant exists for dev / network-restricted environments.

### Speech & Voice Arc — Five Pillars
- **Speech to Text** — audio → text (real-time / fast / batch).
- **Text to Speech** — text → audio (standard / neural HD / custom voices / avatars).
- **Speech Translation** — dedicated real-time (speech-to-speech + speech-to-text).
- **LLM Speech (preview)** — LLM-enhanced file transcription + translation.
- **Voice Live API** — single real-time API fusing STT + TTS + turn-taking + generative model.
- Customization layer: Custom Speech, Custom Voice, Custom Avatar.

### STT — Three Modes
- **Real-time** — streaming; interim + final results. Live captioning, dictation, agent assist.
- **Fast** — synchronous REST: submit file, get transcript in same request. Faster than real-time playback length. Hard ceiling <5hr / <500MB (MS guidance: <2hr / <300MB). Display form only.
- **Batch** — async; multiple files or Blob container. Best-effort scheduling: peak wait up to 30min to start, up to 24hr complete. Region processes serially. MS guidance: ~1000 files/request, spread across hours.

**Decision Matrix**
- Real-time — result while audio still happening.
- Fast — one file, need it synchronously, ≤2hr / 300MB.
- Batch — many files or one long file, no rush, lowest cost/min.

### TTS
- **Standard neural voices** — 100+ languages, 24/48 kHz.
- **Neural HD voices** — LLM-based; read semantic content, detect emotion cues, adjust tone/style, keep persona.
- **SSML** — markup for pitch, rate, pauses, pronunciation, multi-voice.

### Speech Translation (Classic)
- Real-time multilingual (speech-to-speech + speech-to-text).
- Dedicated translation model (not LLM). Long-standing low-latency path.
- Scenarios: multilingual calls, meetings, e-commerce/e-sports streams.
- Video Translation = end-to-end localization pipeline with GPT-assisted editing.

### LLM Speech (Preview)
- LLM enhances speech model for transcription + translation of audio *files*.
- Adds: deeper contextual understanding, broader multilingual, prompt-tuning.
- File-based, not real-time. For meeting notes, call-center assist, voicemail, captions.
- Choose underlying model as request property (e.g. MAI-Transcribe).

### Voice Live API
- One API: STT + TTS + turn detection + interruption + avatars in single real-time session.
- Choose generative model: GPT-Realtime, GPT-5, GPT-4.1, Phi, BYO deployed Foundry model.
- WebSocket-based.
- Two shapes:
  - **Voice Live for Foundry Prompt Agents** — GA, minimal ops overhead.
  - **Hosted Agents with Voice Live** — preview, BYO orchestration (Agent Framework, LangChain) hosted on Foundry Agent Service. WebSocket/WebRTC.

### Customization Stack
- **Custom Speech** — adapt STT accuracy: acoustic + language + pronunciation data. Models/endpoints have lifecycle expiry.
- **Custom Voice** — two tracks:
  - **Professional Voice** — studio recordings, longer fine-tuning, limited-access approval.
  - **Personal Voice** — zero-shot cloning from short sample; used in Voice Live + Live Interpreter.
- **Custom Avatar** — Photo Avatar (instant from one image) + full custom video avatar (recorded video, longer training).

### Azure Speech MCP Server
- Exposes Azure AI Speech as agent tools.
- Agent uses STT for audio input, TTS for spoken output.
- Model reasons; Speech does specialized audio processing.
- Audio via file locations / URLs the service accesses securely.
- Architecture: user → Foundry agent → model decides → Speech MCP server → Azure AI Speech → Azure Storage for I/O files.

### Voice Live vs Traditional Flow
- Traditional: record → transcribe → send to model → generate → synthesize (feels slow).
- Voice Live: streaming interaction, audio flows during session. Low latency, continuous.
- Fit: customer support, voice assistants, coaching, accessibility, conversational kiosks.

### Speech Translation vs LLM Speech
- **Speech Translation** — convert spoken input to another language. Best when main task = translation. Stays close to what speaker said.
- **LLM Speech** — voice conversation powered by generative model. Best for understanding + reasoning + responding. Voice Live = real-time speech-to-speech example.
- **Choose Speech Translation** when: real-time spoken translation, captions, translated meetings, interpreter-style, no open-ended reasoning.
- **Choose LLM Speech** when: voice conversation with intelligent assistant, follow-ups, reasoning, tool usage, live low-latency, text-agent → voice-first.

---

## Section 7 — Information Extraction Solutions

### Azure Content Understanding
- Converts documents / images / audio / video → structured information.
- Foundry Tool for intelligent AI workflows.
- Uses **analyzers** = config defining content type + data extracted + output format.
- Output supports automation, search, RAG, agent reasoning.

**Business Problem**
- Info trapped in unstructured PDFs, scans, images, recordings, videos.
- Apps need structured values (names, dates, totals, tables, categories, IDs).
- Manual review is slow / inconsistent / doesn't scale.
- Agents + RAG need clean grounded input, not raw messy files.
- Content Understanding = bridge between raw content + AI-ready structured data.

**Processable Content**
- **Documents** — OCR, layout, tables, fields, sections, figures, Markdown.
- **Images** — visual characteristics, descriptions, objects, diagrams, screenshots.
- **Audio** — transcripts, speakers, timing, summaries, extracted fields.
- **Videos** — transcripts, key frames, timing, scene segments, visual context.

### Analyzers (Core Concept)
- Reusable config defining processing for content type.
- Specifies: modality (doc/image/audio/video/multimodal), info to extract (fields/tables/summaries/transcripts/segments), output structure (JSON/Markdown).
- Prebuilt for common scenarios or custom for org-specific.

### Document Analysis
**Capabilities**
- OCR — readable text from digital/scanned PDFs, forms, receipts, images.
- Layout — pages, paragraphs, headings, sections, tables, reading order.
- Field extraction — invoice #, customer, due date, line items, totals, contract dates.
- Figure/table extraction — preserves visual + tabular info.
- Markdown output — cleaner rep for agents, indexes, RAG.

**Analyzer Categories**
- **Content extraction analyzers** — OCR + layout, basic to rich structure.
- **Base analyzers** — foundation for custom analyzers.
- **Domain-specific** — invoices, receipts, IDs, tax forms, contracts, mortgage.
- **Custom** — your schema when prebuilt doesn't match.

**Key Prebuilt Analyzers**
- **prebuilt-read** — basic OCR, text elements (words, paragraphs). Can extract formulas, barcodes. Lightweight. No detailed layout.
- **prebuilt-layout** — text + layout (words, paragraphs, tables, figures, sections). Reading order, formatting, charts/diagrams/pictures/icons, hyperlinks, annotations (highlights/underlines/strikethroughs). Use when structure matters but no fixed schema.
- **prebuilt-document** — base for custom document analyzers. Use as parent via `baseAnalyzerId`. Foundation for org-specific fields.

**Domain-Specific**
- Financial: invoices, receipts, credit card statements, credit memos, bank checks, US bank statements.
- Identity: passports, driver licenses, ID cards, residency permits, SSN cards, PAN, Aadhaar.
- Legal, procurement, tax, mortgage, utility, pay stub.

### Visual Understanding (Image Analyzers)
- Convert visual content to structured machine-readable info.
- Business info in screenshots, charts, diagrams, product photos, scanned visuals.
- Extract fields per schema (not just NL description).
- Output for agents, search, review workflows, reporting.

**Image Analyzers**
- **Base image analyzer** — foundation for custom.
- **Image search analyzer** — descriptions + structured outputs for image retrieval.
- **Custom image analyzers** — specific fields per image type.
- Same pattern: submit → wait → read structured result.

**Scenarios**
- Support: screenshots → error messages, UI areas, products, next steps.
- Retail: product images → item type, condition, packaging, color, branding.
- Operations: inspection photos → issues, safety concerns, damaged assets, missing equipment.
- Training: diagrams/slides/charts → searchable + summarizable by agents.

### Standard Mode vs Pro Mode
**Standard mode**
- Default. Focused extraction from single content items.
- Lower cost + latency.
- Supports docs, images, audio, video, text.
- Uses schemas to extract fields (names, dates, totals, categories, summaries).
- Best for most demos, labs, production extraction.
- **Examples**: invoice fields, image description, audio transcript+summary, video segments/chapters, RAG ingestion → Markdown chunks.
- **Flow**: pick analyzer → submit one item → CU extracts → app reads structured result → store/search/agent.

**Pro mode**
- Advanced multi-step reasoning + complex decision-making.
- Multiple input documents analyzed together.
- Uses reference data during analyzer creation for linking, validation, enrichment.
- For cross-document relationships, not just single-file fields.
- **Examples**: mortgage review (compare borrower info across app/pay stubs/statements/closing), onboarding package validation, insurance claim review (claim/policy/estimates/evidence), compliance review, vendor approval.

**Standard vs Pro**
- Standard = single item structured extract; multi-modality.
- Pro = reasoning across related docs + reference data; **currently document-focused**.
- Standard = lower latency/cost/complexity.
- Default: Standard unless multi-doc reasoning required.

### Azure AI Search for RAG
**Why**
- LLMs don't know your latest docs/policies/manuals/tickets.
- RAG retrieves relevant business content before generation.
- Azure AI Search = common retrieval layer.
- Model = reasoning layer, not database.
- Answer quality depends on retrieval quality.

**Where AI Search Fits**
- Source: Blob Storage, file repos, KBs, web content, doc stores.
- AI Search: processes → searchable index (text fields, metadata, optional vectors).
- User Q → app queries AI Search → results into prompt as grounding → model answers grounded.

**Raw Content → Searchable**
- Ingest raw files → transform to searchable docs in AI Search index.
- **Indexers** — automate reading from data sources + loading.
- During indexing: extract text, capture metadata, prep for search.
- **Skillsets** — apply AI enrichment (OCR, lang detection, entity recognition, translation, image analysis).

**Search Options for Grounding**
- **Keyword** — exact terms, product names, error codes, IDs.
- **Vector** — embedding similarity even when wording differs.
- **Semantic ranking** — rerank by meaning.
- **Hybrid** — full-text + vector in single query.
- Real RAG often: **hybrid + semantic ranking** (exact + meaning-based).

### AI Enrichment + Skillsets
**Why Enrichment**
- Basic indexing extracts text + metadata. Real content has more.
- Docs include scans, images, tables, mixed languages, technical terms, entities, layout.
- Enrichment adds processing during indexing.
- Extracts text from images, detects language, identifies entities, splits docs, translates, generates embeddings.

**Skillset**
- Collection of skills in AI Search indexing pipeline.
- Skill = specific transform (OCR, lang detection, key phrase, NER, translation, text split, embedding).
- Attached to indexer; runs when indexer processes source data.
- Inputs/outputs: output of one skill → input of next.
- Enriched output mapped into index fields.

**Built-in vs Custom Skills**
- **Built-in** — MS-provided: OCR, NER, key phrase, lang detection, translation, image analysis.
- **Custom** — call your external logic (Azure Function, API, ML endpoint).
- Both can participate in same skillset.

**Common Enrichment**
- OCR — visible text from images searchable.
- Entity recognition — people, orgs, locations, dates, quantities.
- Key phrase — main topics.
- **Text split** — long content into chunks (critical for RAG + vector).
- **Embedding** — vector representations for semantic similarity.

**Why Skillsets Matter for RAG**
- Retrieval quality drives RAG.
- OCR includes scanned/image info.
- Text splitting = smaller retrieval units.
- Embeddings enable vector search.
- Well-designed skillset → better grounding, less irrelevant retrieval.

### Connecting AI Search to an Agent
**From Search Index to Agent Knowledge**
- AI Search stores prepared knowledge; not conversational alone.
- Foundry agent uses AI Search as tool to retrieve before generation.
- User Q → agent decides knowledge needed → search tool call → results = grounding context → grounded answer.

**Agent Connection**
- Tells Foundry agent which search service + index.
- Agent doesn't browse Blob directly; queries prepared AI Search index.
- Index can hold basic content, enriched content, OCR text, metadata, chunks, or vectors.
- Agent returns grounded response, often with citations.

**Runtime Flow**
- User Q ("Does CloudXeus provide weekend support?") → agent evaluates → AI Search tool → search returns passages/fields → agent adds to reasoning context → conversational grounded answer.

**Agent Tool vs Manual RAG**
- Manual: app code calls Search → builds prompt → calls model.
- Agent tool: search attached to agent, used as part of tool workflow.
- Less orchestration code for simple grounding.
- Agent combines search with code execution, OpenAPI tools, workflow tools, custom tools.
- Useful when needing both knowledge retrieval + action.

**Prerequisites**
- AI Search service with populated index.
- Retrievable fields with grounding text (`content`, `merged_content`, `chunk`).
- Foundry project connected to AI Search (supported auth).
- Agent configured with AI Search tool + correct index.
- Agent instructions telling model when to use search + how to answer from retrieved.
