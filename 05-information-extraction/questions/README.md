# Domain 5 question review

## Per-question lesson map

| Question | Lesson file(s) | Coverage note | Status |
|---:|---|---|---|
| Q2 | [`10_cu_prebuilt_layout.py`](../10_cu_prebuilt_layout.py) | L10 CU layout | Existing |
| Q4 | [`27_agent_azure_ai_search_preflight.py`](../../02-generative-ai-and-agents/27_agent_azure_ai_search_preflight.py), [`20_managed_search_agent_tool.py`](../20_managed_search_agent_tool.py) | L20 managed Search tool and D2 L27 | Existing |
| Q14 | [`24_agentic_knowledge_base.py`](../24_agentic_knowledge_base.py), [`25_agentic_retrieve.py`](../25_agentic_retrieve.py), [`26_agentic_answer_synthesis.py`](../26_agentic_answer_synthesis.py) | L24–26 agentic retrieval | Existing |
| Q15 | [`12_cu_custom_analyzer.py`](../12_cu_custom_analyzer.py) | L12 `--propose-schema` runs `prebuilt-documentFieldSchema` | Existing |
| Q21 | [`01_rag_ingestion_contract.py`](01_rag_ingestion_contract.py), [`14_cu_markdown_for_rag.py`](../14_cu_markdown_for_rag.py) | `questions/01_rag_ingestion_contract.py` plus L14 structure-aware chunks | Existing |
| Q28 | [`20_managed_search_agent_tool.py`](../20_managed_search_agent_tool.py) | L20 Search tool index selection | Existing |
| Q31 | [`27_agent_azure_ai_search_preflight.py`](../../02-generative-ai-and-agents/27_agent_azure_ai_search_preflight.py), [`20_managed_search_agent_tool.py`](../20_managed_search_agent_tool.py) | L20 Search connection | Existing |
| Q35 | [`08_rag_client_run.py`](../08_rag_client_run.py) | L08 manual RAG completeness | Existing |
| Q36 | Adjacent only: [`11_cu_invoice.py`](../11_cu_invoice.py), [`13_cu_cross_document_validation.py`](../13_cu_cross_document_validation.py) | L11 single-file standard analyzer, L13 GA cross-document replacement | Compatibility: CU Pro mode (`2025-05-01-preview`) retired July 15, 2026 |
| Q41 | [`12_cu_custom_analyzer.py`](../12_cu_custom_analyzer.py) | L12 custom analyzer | Existing |
| Q46 | Adjacent only: [`11_cu_invoice.py`](../11_cu_invoice.py), [`13_cu_cross_document_validation.py`](../13_cu_cross_document_validation.py) | L11 single-file standard analyzer, L13 GA cross-document replacement | Compatibility: CU Pro mode (`2025-05-01-preview`) retired July 15, 2026 |
| Q55 | [`09_cu_prebuilt_read.py`](../09_cu_prebuilt_read.py) | L09 CU OCR | Existing |
| Q84 | [`10_cu_prebuilt_layout.py`](../10_cu_prebuilt_layout.py), [`14_cu_markdown_for_rag.py`](../14_cu_markdown_for_rag.py) | L10/L14 layout Markdown RAG | Existing |
| Q87 | [`12_cu_custom_analyzer.py`](../12_cu_custom_analyzer.py) | L12 `estimateFieldSourceAndConfidence` plus confidence-based review routing | Existing |
| Q88 | [`07_rag_prompt_agent.py`](../07_rag_prompt_agent.py), [`08_rag_client_run.py`](../08_rag_client_run.py) | L07–08 retrieval-context control | Existing |
| Q90 | [`09_cu_prebuilt_read.py`](../09_cu_prebuilt_read.py), [`11_cu_invoice.py`](../11_cu_invoice.py) | L09–11 CU invoice pipeline | Existing |
| Q92 | [`12_cu_custom_analyzer.py`](../12_cu_custom_analyzer.py) | L12 custom CU analyzer | Existing |
| Q94 | [`29_search_ocr_knowledge_store.py`](../29_search_ocr_knowledge_store.py) | L29 indexer `imageAction: generateNormalizedImages` feeds the OCR skill | Existing |
| Q114 | [`14_cu_markdown_for_rag.py`](../14_cu_markdown_for_rag.py) | L14 `--analyzer prebuilt-documentSearch` RAG Markdown | Existing |
| Q116 | [`31_openai_embeddings.py`](../../02-generative-ai-and-agents/31_openai_embeddings.py), [`02_search_vector.py`](../02_search_vector.py) | L02 vector search and D2 L31 | Existing |
| Q118 | [`03_search_hybrid_semantic.py`](../03_search_hybrid_semantic.py) | L03 hybrid/semantic retrieval | Existing |
| Q120 | [`30_search_cu_skill_citations.py`](../30_search_cu_skill_citations.py), [`16_cu_multimodal_rag.py`](../16_cu_multimodal_rag.py) | L30 Content Understanding skill with `locationMetadata` polygons and cross-page tables; L16 multimodal RAG | Existing |
| Q121 | [`29_search_ocr_knowledge_store.py`](../29_search_ocr_knowledge_store.py) | L29 OCR skill reads scanned-image text; Text Merge adds it to the indexed field | Existing |
| Q122 | Adjacent only: [`13_cu_cross_document_validation.py`](../13_cu_cross_document_validation.py) | L13 per-document extraction plus app-side consistency check | Compatibility: CU Pro mode (`2025-05-01-preview`) retired July 15, 2026 |
| Q141 | [`29_search_ocr_knowledge_store.py`](../29_search_ocr_knowledge_store.py) | L29 knowledge store: object projection for JSON, table projections for extracted text | Existing |
| Q144 | [`28_sharepoint_indexer_acls_preflight.py`](../28_sharepoint_indexer_acls_preflight.py) | L28 ACL/security trimming | Existing |
| Q145 | Adjacent only: [`18_search_monitoring.py`](../18_search_monitoring.py) | L18 monitoring | Gap: query-key rotation runbook |
| Q146 | [`30_search_cu_skill_citations.py`](../30_search_cu_skill_citations.py), [`16_cu_multimodal_rag.py`](../16_cu_multimodal_rag.py) | Duplicate of Q120: L30 Content Understanding skill in the skillset; L16 multimodal RAG | Existing |
| Q170 | [`11_cu_invoice.py`](../11_cu_invoice.py), [`15_cu_content_agent.py`](../15_cu_content_agent.py) | L11/L15 invoice review | Existing |
| Q171 | [`05_search_skillset.py`](../05_search_skillset.py) | L05 split-and-embed skillset | Existing |
| Q172 | [`04_search_indexer_setup.py`](../04_search_indexer_setup.py), [`05_search_skillset.py`](../05_search_skillset.py), [`20_managed_search_agent_tool.py`](../20_managed_search_agent_tool.py) | L04–05/L20 Search RAG | Existing |

The ingestion supplement is an application-level provenance/ACL contract; it does not replace the Search index, data source, skillset, and indexer assets. See [`../../docs/question-coverage.md`](../../docs/question-coverage.md#05---information-extraction).
