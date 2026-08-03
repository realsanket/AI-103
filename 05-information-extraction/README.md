# Domain 5 — Implement Information Extraction Solutions (10-15%)

## Files

| # | File | Syllabus bullet |
|---|---|---|
| 01 | `01_search_basic_query.py` | Query an AI Search index (baseline keyword) |
| 02 | `02_search_vector.py` | Configure vector search |
| 03 | `03_search_hybrid_semantic.py` | Configure hybrid + semantic ranking (compared) |
| 04 | `04_search_indexer_setup.py` | Ingest + index via indexer |
| 05 | `05_search_skillset.py` | Enrichment — built-in skills (OCR + split + embed) |
| 06 | `06_search_custom_skill.py` | Enrichment — custom skill via Azure Function |
| 07 | `07_rag_agent_search_tool.py` | Connect retrieval pipeline to an agent tool |
| 08 | `08_rag_client_run.py` | Invoke the RAG agent |
| 09 | `09_cu_prebuilt_read.py` | Content Understanding — prebuilt-read (basic OCR) |
| 10 | `10_cu_prebuilt_layout.py` | Content Understanding — prebuilt-layout (tables/figures) |
| 11 | `11_cu_invoice.py` | Content Understanding — domain-specific analyzer |
| 12 | `12_cu_custom_analyzer.py` | Content Understanding — custom analyzer via baseAnalyzerId |
| 13 | `13_cu_pro_mode.py` | Pro-mode multi-document reasoning |
| 14 | `14_cu_markdown_for_rag.py` | CU → clean Markdown → chunk → index into AI Search |
| 15 | `15_cu_content_agent.py` | Agent using Content Understanding outputs |
| — | `skillset_configs/` | JSON skillset/indexer/index definitions |

## Run

```bash
python 05-information-extraction/01_search_basic_query.py
```

## Reference docs

- Hybrid search: `.context/azure-ai-docs/articles/search/hybrid-search-overview.md`
- Skillsets: `.context/azure-ai-docs/articles/search/cognitive-search-defining-skillset.md`
- Custom skills: `.context/azure-ai-docs/articles/search/cognitive-search-custom-skill-interface.md`
- Agentic knowledge sources: `.context/azure-ai-docs/articles/search/agentic-knowledge-source-overview.md`
- Content Understanding analyzers: `.context/azure-ai-docs/articles/ai-services/content-understanding/concepts/analyzer-reference.md`
- Standard vs Pro mode: `.context/azure-ai-docs/articles/ai-services/content-understanding/concepts/standard-pro-modes.md`
