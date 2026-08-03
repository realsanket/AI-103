# CloudXeus MCP Server — Azure Function

Hosts a custom MCP server exposing CloudXeus tools (order status, list customer
orders). Any MCP-aware agent — Foundry, Claude Desktop, Cursor — can attach to
it and use the tools without hardcoding a schema.

## Run locally

```bash
cp local.settings.json.example local.settings.json
pip install -r requirements.txt
func start
```

MCP endpoint: `http://localhost:7071/runtime/webhooks/mcp`

## Attach to a Foundry agent

Portal: Add tool → MCP server → paste the deployed URL. See
`../18_multi_agent_coord.py` / `.context/azure-ai-docs/articles/foundry/mcp/`.
