---
ai-usage: ai-assisted
---

# Domain 2: Implement generative AI and agentic solutions

Run these lessons after Domain 1. They build from Responses API calls through
prompt agents, tool execution, state, evaluation, and framework integrations.
Each Python file is runnable from repository root:

```bash
uv run python 02-generative-ai-and-agents/<lesson>.py
```

This domain creates cloud resources and consumes model tokens. Read [Cloud
state and cost](#cloud-state-and-cost) before running it.

## Prerequisites

Complete these steps in order.

1. Run the repository setup documented in root `README.md`. Don't change
   dependency manifests for an individual lesson.
1. Create a Microsoft Foundry project, deploy a chat model, and deploy an
   embedding model.
1. Run `az login`. Your identity needs access to the Foundry project. Creating
   or managing agents and connections might need additional project permissions.
1. Set these core `.env` values:

   ```text
   FOUNDRY_ENDPOINT=https://<resource>.services.ai.azure.com
   PROJECT_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<project>
   AZURE_OPENAI_ENDPOINT=https://<resource>.openai.azure.com
   DEFAULT_MODEL=<chat-deployment-name>
   EMBEDDING_MODEL=<embedding-deployment-name>
   ```

   `DEFAULT_MODEL` and `EMBEDDING_MODEL` are deployment names, not model family
   labels. Lessons 20–22 use `AZURE_OPENAI_ENDPOINT` for OpenAI-compatible
   LangChain and LangGraph clients. Lesson 22 and the memory store use the
   configured embedding deployment.
1. Optionally set `APPLICATIONINSIGHTS_CONNECTION_STRING` for lesson 21.
1. Install Azure Functions Core Tools only when running the OpenAPI or MCP
   assets. Those assets have their own `requirements.txt` files.

Start with a cheap chat deployment. Run a simple Domain 1 model call before
running tool, agent, or memory lessons.

## Run sequence

Run lessons in this order. Stop after any phase; later phases are independent
unless noted.

| Phase | Lessons | What you run |
|---|---|---|
| Responses API | 01–07 | Basic generation, behavior controls, reasoning, web search, code interpreter, file search, and strict structured output. |
| Prompt agents | 08–13 | Create and invoke an agent, execute function calls in application code, use web search and OpenAPI tools, and continue conversations. Run 08 before 09. Lesson 11 is standalone. |
| Long-term memory | 14 | Preview memory store and memory search tool. Requires both configured chat and embedding deployments. |
| Workflow preview | 15–16 | Structured intake followed by the preview YAML workflow. Run 15 before 16. |
| Orchestration and evaluation | 17–19 | Local Agent Framework run, router-and-specialist pattern, and local SDK evaluation. |
| Framework integrations | 20–22 | LangChain agent, optional Application Insights tracing, and LangGraph with local FAISS retrieval. |

### Tool execution

Lessons 09, 11, and 18 run the application side of function calling. Each
round processes every function call from `response.output`, preserves its
`call_id`, validates JSON arguments, returns an error result for invalid calls,
and continues until the model produces a final response. The model requests a
function; your application executes it.

### OpenAPI Function asset

Lesson 12 reads `azure_functions_orders/northwind_spec.json` and replaces its
placeholder server with `ORDERS_FN_ENDPOINT`.

```bash
cd 02-generative-ai-and-agents/azure_functions_orders
cp local.settings.json.example local.settings.json
func start
curl http://localhost:7071/api/orders
```

This localhost URL only tests the Function. Foundry Agent Service cannot call
your laptop. To run lesson 12, deploy a Function endpoint reachable from Agent
Service and set:

```text
ORDERS_FN_ENDPOINT=https://<your-function-app>.azurewebsites.net
```

The sample's anonymous routes serve static demo data only. Use API-key or
managed-identity authentication for a production backend, configure the same
method in the OpenAPI tool, and grant required access.

### MCP Function asset

`northwind_mcp/` is an independent custom MCP server. No numbered lesson
attaches it. Run it locally only with a local MCP client, or deploy it and add
its reachable `/runtime/webhooks/mcp` URL as a remote MCP server. Configure
Function keys or Microsoft Entra authentication before using it beyond demo
data. See `northwind_mcp/README.md`.

## Current preview status

| Area | Status and lesson impact |
|---|---|
| Memory | Foundry Memory and its memory store APIs are preview. Lesson 14 creates a store and attaches `MemorySearchPreviewTool`; it doesn't depend on a portal toggle. Writes are asynchronous and debounced, so cross-conversation recall isn't guaranteed immediately. |
| Workflows | Foundry workflows are preview and retire on December 1, 2026. Lessons 15–16 preserve a YAML study asset. For new orchestration, use Microsoft Agent Framework. After retirement, deploy workflow code or YAML as a hosted agent instead of relying on the visual designer or in-portal execution. |
| Agent evaluators | Agent evaluators are preview. Lesson 19 runs SDK evaluators locally and doesn't create a portal evaluation or upload a dataset. Tool Call Accuracy needs a full tool trace and tool definitions; its intentionally tool-free sample shows that contract. |
| Hosted agents | Lesson 17 is intentionally local. It uses Agent Framework with `FoundryChatClient`, but doesn't package, deploy, or invoke a hosted agent. A real hosted agent needs its own deployment lifecycle and permissions. |

## Lesson coverage

| # | File | Coverage |
|---:|---|---|
| 01 | `01_first_api_call.py` | Responses API model invocation. |
| 02 | `02_model_behavior.py` | Sampling behavior. |
| 03 | `03_reasoning.py` | Reasoning model request. |
| 04 | `04_web_search_tool.py` | Built-in web search. |
| 05 | `05_code_interpreter.py` | Built-in code interpreter. |
| 06 | `06_file_search_tool.py` | Managed file search and vector store. |
| 07 | `07_structured_output.py` | Strict JSON Schema output. |
| 08 | `08_prompt_agent_create.py` | Prompt agent and function schemas. |
| 09 | `09_prompt_agent_invoke.py` | Conversation and safe function-call loop. |
| 10 | `10_agent_web_search.py` | Prompt agent with web search. |
| 11 | `11_agent_function_tools.py` | End-to-end function-tool agent. |
| 12 | `12_agent_openapi_tools.py` | OpenAPI tool and external Function backend. |
| 13 | `13_conversation_thread.py` | Server-managed conversation history. |
| 14 | `14_foundry_memory.py` | Preview store-backed long-term memory. |
| 15 | `15_workflow_intake.py` | Preview workflow intake schema. |
| 16 | `16_workflow_conditional.py` | Preview YAML branch routing. |
| 17 | `17_hosted_agent_framework.py` | Local Agent Framework application. |
| 18 | `18_multi_agent_coord.py` | Router with specialist agents as tools. |
| 19 | `19_evaluator_task_adherence.py` | Preview local SDK evaluation. |
| 20 | `20_langchain_agent.py` | LangChain OpenAI-compatible client and tools. |
| 21 | `21_langchain_tracing.py` | LangChain tracing when Application Insights is configured. |
| 22 | `22_langgraph_agent.py` | LangGraph, local FAISS, and configured embeddings. |

## Cloud state and cost

These lessons aren't read-only:

- Prompt-agent and workflow lessons create agent versions. Re-running them
  creates more versions.
- File search can create or upload files and vector-store state.
- Lesson 14 creates a memory store, agent version, and long-term memory items.
- Lesson 12 requires a deployed Function App to be reachable. Lesson MCP needs
  its own deployed Function App when used remotely.
- Model calls, built-in tools, memory operations, hosted-agent runtime, Azure
  Functions, Application Insights, and storage can incur charges.

Use separate study names or a disposable project. Review and delete unneeded
agent versions, vector stores and files, memory stores, Function Apps, and
telemetry resources when finished. Do not put keys, tokens, or production data
in `.env`, prompts, tool arguments, or lesson source.

## Troubleshooting

| Symptom | Check |
|---|---|
| Authentication or authorization failure | Run `az login`, verify project access, and confirm all endpoints use the correct subdomain. |
| LangChain or LangGraph request fails | Confirm `AZURE_OPENAI_ENDPOINT`, `DEFAULT_MODEL`, and `EMBEDDING_MODEL`. Do not substitute `FOUNDRY_ENDPOINT` for the OpenAI-compatible client base URL. |
| Lesson 09 function result is rejected | Inspect the printed tool name and JSON arguments. The lesson returns each result with its original call ID. |
| Lesson 12 cannot call orders | Verify deployed `ORDERS_FN_ENDPOINT` is reachable from Agent Service. `localhost` isn't reachable. |
| Lesson 14 doesn't recall data | Confirm compatible chat and embedding deployments. Wait for preview memory updates, then treat recall as model- and retrieval-dependent. |
| Lesson 16 fails | Run 15 first and verify your installed SDK supports the workflow preview surface. |
| Lesson 19 import fails | `azure-ai-evaluation` isn't part of this domain's dependency manifest. Install it in your environment only if you choose to run this optional lesson. |
| Lesson 21 has no cloud traces | Set `APPLICATIONINSIGHTS_CONNECTION_STRING`; without it, the agent still runs without the Azure Monitor tracer. |

## Local references

- [Responses API](../.context/azure-ai-docs/articles/foundry/agents/quickstarts/responses-api.md)
- [Function calling](../.context/azure-ai-docs/articles/foundry/agents/how-to/tools/function-calling.md)
- [OpenAPI tools](../.context/azure-ai-docs/articles/foundry/agents/how-to/tools/openapi.md)
- [Memory usage](../.context/azure-ai-docs/articles/foundry/agents/how-to/memory-usage.md)
- [Workflow retirement](../.context/azure-ai-docs/articles/foundry/agents/concepts/workflow.md)
- [Hosted agents](../.context/azure-ai-docs/articles/foundry/agents/concepts/hosted-agents.md)
- [Agent evaluators](../.context/azure-ai-docs/articles/foundry/concepts/evaluation-evaluators/agent-evaluators.md)
