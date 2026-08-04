# Domain 2 — Implement Generative AI and Agentic Solutions (30-35%)

Largest exam domain — most files.

## Files

| # | File | Syllabus bullet |
|---|---|---|
| 01 | `01_first_api_call.py` | Deploy and consume LLMs |
| 02 | `02_model_behavior.py` | Tune generation behavior (temperature, top_p) |
| 03 | `03_reasoning.py` | Multi-step reasoning pipeline |
| 04 | `04_web_search_tool.py` | Tool-augmented flows — Web Search |
| 05 | `05_code_interpreter.py` | Tool-augmented flows — Code Interpreter |
| 06 | `06_file_search_tool.py` | Tool-augmented flows — built-in File Search (RAG) |
| 07 | `07_structured_output.py` | Structured JSON outputs (json_schema, strict) |
| 08 | `08_prompt_agent_create.py` | Define agent roles, goals, tool schemas |
| 09 | `09_prompt_agent_invoke.py` | Invoke agent (Responses API + thread) |
| 10 | `10_agent_web_search.py` | Integrate agent tools — Web Search |
| 11 | `11_agent_function_tools.py` | Integrate agent tools — custom functions |
| 12 | `12_agent_openapi_tools.py` | Integrate agent tools — OpenAPI spec (Azure Functions) |
| 13 | `13_conversation_thread.py` | Conversation tracking |
| 14 | `14_foundry_memory.py` | Cross-session memory (Extraction → Consolidation → Retrieval) |
| 15 | `15_workflow_intake.py` | Workflow — intake agent with structured output |
| 16 | `16_workflow_conditional.py` | Workflow — conditional branching |
| 17 | `17_hosted_agent_framework.py` | Hosted agents — Microsoft Agent Framework |
| 18 | `18_multi_agent_coord.py` | Orchestrated multi-agent solutions |
| 19 | `19_evaluator_task_adherence.py` | Agent evaluators — Task Adherence + Tool Call Accuracy |
| 20 | `20_langchain_agent.py` | LangChain agent |
| 21 | `21_langchain_tracing.py` | LangChain + OpenTelemetry tracing |
| 22 | `22_langgraph_agent.py` | LangGraph stateful agent |
| — | `azure_functions_orders/` | OpenAPI-described Function backing tool 12 |
| — | `northwind_mcp/` | Custom MCP server as Azure Function |
| — | `workflows/` | JSON + YAML workflow definitions |

## Run

```bash
python 02-generative-ai-and-agents/01_first_api_call.py
```

For agent files: run `08_prompt_agent_create.py` once (creates the agent version), then `09_prompt_agent_invoke.py` to talk to it.

## Reference docs

- [Foundry Agent Service](../.context/azure-ai-docs/articles/foundry/agents/overview.md)
- [Responses API](../.context/azure-ai-docs/articles/foundry/agents/quickstarts/responses-api.md)
- [Hosted agents](../.context/azure-ai-docs/articles/foundry/agents/concepts/hosted-agents.md)
- [Memory](../.context/azure-ai-docs/articles/foundry/agents/concepts/what-is-memory.md)
- [Workflows / YAML reference](../.context/azure-ai-docs/articles/foundry/agents/concepts/agent-yaml-reference.md)
- [MCP get started](../.context/azure-ai-docs/articles/foundry/mcp/get-started.md)
- [LangChain integration](../.context/azure-ai-docs/articles/foundry/how-to/develop/langchain.md)
