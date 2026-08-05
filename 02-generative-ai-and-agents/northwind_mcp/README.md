---
ai-usage: ai-assisted
---

# Northwind MCP server — independent Azure Function asset

This project hosts two custom Model Context Protocol (MCP) tools: order status
and customer orders. It is not attached by any numbered lesson. Deploy and
connect it separately when you want to practice custom MCP integration.

## Run locally

```bash
cp local.settings.json.example local.settings.json
pip install -r requirements.txt
func start
```

MCP endpoint: `http://localhost:7071/runtime/webhooks/mcp`

Use the local endpoint only with a local MCP client. Foundry Agent Service
cannot reach your laptop's `localhost`.

## Deploy and connect

1. Deploy the Function App:

   ```bash
   func azure functionapp publish <your-function-app-name>
   ```

1. In Foundry, add a remote MCP server with
   `https://<your-function-app>.azurewebsites.net/runtime/webhooks/mcp`.
   Ensure Agent Service can reach that endpoint.

This sample has no production authentication setup. Configure Function keys or
Microsoft Entra authentication before connecting a non-demo server, then select
the matching authentication method in the MCP connection.
