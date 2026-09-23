# Domain 5 question review

## Per-question lesson map

| Question | Lesson file(s) | Coverage note | Status |
|---:|---|---|---|
| Q2 | [`10_cu_prebuilt_layout.py`](../10_cu_prebuilt_layout.py) | L10 CU layout | Existing |
| Q4 | [`27_agent_azure_ai_search_preflight.py`](../../02-generative-ai-and-agents/27_agent_azure_ai_search_preflight.py), [`20_managed_search_agent_tool.py`](../20_managed_search_agent_tool.py) | L20 managed Search tool and D2 L27 | Existing |
| Q14 | [`24_agentic_knowledge_base.py`](../24_agentic_knowledge_base.py), [`25_agentic_retrieve.py`](../25_agentic_retrieve.py), [`26_agentic_answer_synthesis.py`](../26_agentic_answer_synthesis.py) | L24–26 agentic retrieval | Existing |
| Q15 | — | CU analyzer map | Gap: validate `prebuilt-documentFieldSchema` before code |
| Q21 | [`01_rag_ingestion_contract.py`](01_rag_ingestion_contract.py) | `questions/01_rag_ingestion_contract.py` | New |
| Q28 | [`20_managed_search_agent_tool.py`](../20_managed_search_agent_tool.py) | L20 Search tool index selection | Existing |
| Q31 | [`27_agent_azure_ai_search_preflight.py`](../../02-generative-ai-and-agents/27_agent_azure_ai_search_preflight.py), [`20_managed_search_agent_tool.py`](../20_managed_search_agent_tool.py) | L20 Search connection | Existing |
| Q35 | [`08_rag_client_run.py`](../08_rag_client_run.py) | L08 manual RAG completeness | Existing |
| Q36 | [`11_cu_invoice.py`](../11_cu_invoice.py), [`13_cu_pro_mode.py`](../13_cu_pro_mode.py) | L11/L13 CU standard versus Pro | Existing |
| Q41 | [`12_cu_custom_analyzer.py`](../12_cu_custom_analyzer.py) | L12 custom analyzer | Existing |
| Q46 | [`11_cu_invoice.py`](../11_cu_invoice.py), [`13_cu_pro_mode.py`](../13_cu_pro_mode.py) | L11/L13 CU standard versus Pro | Existing |
| Q55 | [`09_cu_prebuilt_read.py`](../09_cu_prebuilt_read.py) | L09 CU OCR | Existing |
| Q75 | [`08_rbac_role_policies.py`](../../01-plan-and-manage/08_rbac_role_policies.py), [`19_blob_identity_paths.py`](../19_blob_identity_paths.py), [`20_managed_search_agent_tool.py`](../20_managed_search_agent_tool.py) | L20 and D1 L08 Search RBAC | Existing |
| Q77 | [`09_mcp_get_started.py`](../../08-advanced-agents-other/09_mcp_get_started.py) | D8 L09 MCP knowledge tool | Existing |
| Q84 | [`10_cu_prebuilt_layout.py`](../10_cu_prebuilt_layout.py), [`14_cu_markdown_for_rag.py`](../14_cu_markdown_for_rag.py) | L10/L14 layout Markdown RAG | Existing |
| Q87 | [`01_rag_ingestion_contract.py`](01_rag_ingestion_contract.py) | `questions/01_rag_ingestion_contract.py` | New |
| Q88 | [`07_rag_prompt_agent.py`](../07_rag_prompt_agent.py), [`08_rag_client_run.py`](../08_rag_client_run.py) | L07–08 retrieval-context control | Existing |
| Q90 | [`09_cu_prebuilt_read.py`](../09_cu_prebuilt_read.py), [`11_cu_invoice.py`](../11_cu_invoice.py) | L09–11 CU invoice pipeline | Existing |
| Q92 | [`12_cu_custom_analyzer.py`](../12_cu_custom_analyzer.py) | L12 custom CU analyzer | Existing |
| Q94 | [`01_rag_ingestion_contract.py`](01_rag_ingestion_contract.py) | `questions/01_rag_ingestion_contract.py` | New |
| Q114 | — | CU analyzer map | Gap: validate `prebuilt-documentSearch` before code |
| Q116 | [`31_openai_embeddings.py`](../../02-generative-ai-and-agents/31_openai_embeddings.py), [`02_search_vector.py`](../02_search_vector.py) | L02 vector search and D2 L31 | Existing |
| Q118 | [`03_search_hybrid_semantic.py`](../03_search_hybrid_semantic.py) | L03 hybrid/semantic retrieval | Existing |
| Q120 | [`16_cu_multimodal_rag.py`](../16_cu_multimodal_rag.py) | L16 multimodal RAG | Existing |
| Q121 | [`01_rag_ingestion_contract.py`](01_rag_ingestion_contract.py) | `questions/01_rag_ingestion_contract.py` | New |
| Q122 | [`13_cu_pro_mode.py`](../13_cu_pro_mode.py) | L13 CU Pro Mode | Existing |
| Q141 | Adjacent only: [`04_search_indexer_setup.py`](../04_search_indexer_setup.py), [`05_search_skillset.py`](../05_search_skillset.py), [`06_search_custom_skill.py`](../06_search_custom_skill.py) | L04–06 Search enrichment | Gap: knowledge-store projections |
| Q144 | [`28_sharepoint_indexer_acls_preflight.py`](../28_sharepoint_indexer_acls_preflight.py) | L28 ACL/security trimming | Existing |
| Q145 | Adjacent only: [`18_search_monitoring.py`](../18_search_monitoring.py) | L18 monitoring | Gap: query-key rotation runbook |
| Q146 | [`16_cu_multimodal_rag.py`](../16_cu_multimodal_rag.py) | L16 multimodal RAG | Existing; duplicate of Q120 |
| Q170 | [`11_cu_invoice.py`](../11_cu_invoice.py), [`15_cu_content_agent.py`](../15_cu_content_agent.py) | L11/L15 invoice review | Existing |
| Q171 | [`05_search_skillset.py`](../05_search_skillset.py) | L05 split-and-embed skillset | Existing |
| Q172 | [`04_search_indexer_setup.py`](../04_search_indexer_setup.py), [`05_search_skillset.py`](../05_search_skillset.py), [`20_managed_search_agent_tool.py`](../20_managed_search_agent_tool.py) | L04–05/L20 Search RAG | Existing |

The ingestion supplement is an application-level provenance/ACL contract; it does not replace the Search index, data source, skillset, and indexer assets. See [`../../docs/question-coverage.md`](../../docs/question-coverage.md#05---information-extraction).
