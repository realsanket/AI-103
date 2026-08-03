# Domain 4 — Implement Text Analysis Solutions (10-15%)

## Files

| # | File | Syllabus bullet |
|---|---|---|
| 01 | `01_llm_ner.py` | Entity extraction via generative prompt |
| 02 | `02_llm_sentiment.py` | Sentiment detection via generative prompt |
| 03 | `03_llm_translation.py` | Translation via LLM prompt |
| 04 | `04_translator_rest.py` | Translation via Azure Translator (REST) — compare with 03 |
| 05 | `05_language_pii.py` | PII detection via Azure AI Language |
| 06 | `06_language_detect.py` | Language detection |
| 07 | `07_language_ner.py` | NER via Azure AI Language (prebuilt) |
| 08 | `08_language_mcp_tools.py` | List Language MCP server tools |
| 09 | `09_language_mcp_agent.py` | Use Language MCP inside an agent turn |
| 10 | `10_health_text_analytics.py` | Text Analytics for Health |
| 11 | `11_stt_fast_file.py` | STT — fast transcription (single file synchronous) |
| 12 | `12_stt_real_time.py` | STT — real-time streaming |
| 13 | `13_stt_batch.py` | STT — batch transcription (async, many files) |
| 14 | `14_tts_neural.py` | TTS — neural voice |
| 15 | `15_tts_ssml_hd.py` | TTS — SSML + Neural HD voice |
| 16 | `16_speech_translation.py` | Speech translation (dedicated) |
| 17 | `17_llm_speech_preview.py` | LLM Speech (preview) — file-based |
| 18 | `18_voice_live_prompt_agent.py` | Voice Live — real-time speech-to-speech agent |

## Run

```bash
python 04-text-and-speech/01_llm_ner.py
```

## Reference docs

- Azure Language: `.context/azure-ai-docs/articles/ai-services/language-service/`
- Language MCP: `.context/azure-ai-docs/articles/foundry/mcp/available-tools.md`
- Speech STT modes: `.context/azure-ai-docs/articles/ai-services/speech-service/concepts/audio-concepts.md`
- Voice Live: `.context/azure-ai-docs/articles/foundry/agents/` (see voice-live docs)
- Translator: `.context/azure-ai-docs/articles/ai-services/translator/`
