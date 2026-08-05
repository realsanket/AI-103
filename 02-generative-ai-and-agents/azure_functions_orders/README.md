---
ai-usage: ai-assisted
---

# Northwind Orders — Azure Function (OpenAPI tool backend)

Backs lesson `12_agent_openapi_tools.py`.

Serves two endpoints described by `northwind_spec.json`:

- `GET /orders` — list orders
- `GET /orders/{order_id}` — fetch by id

The Foundry agent reads the OpenAPI spec, converts each operation to a callable
tool, and decides when to call which — no glue code in the agent.

## Run locally

```bash
cp local.settings.json.example local.settings.json
func start
curl http://localhost:7071/api/orders
```

Localhost verifies the Function only. It is not reachable by Foundry Agent
Service, so lesson 12 cannot use `http://localhost:7071`.

## Deploy

```bash
func azure functionapp publish <your-function-app-name>
```

Set `ORDERS_FN_ENDPOINT=https://<your-function-app>.azurewebsites.net` before
running lesson 12. The Function endpoint must be reachable from Agent Service.

This sample sets the Function routes to anonymous authentication only for
non-sensitive, static demonstration data. Do not expose production order data
this way. Protect a production backend and configure matching API-key or
managed-identity authentication for the OpenAPI tool.
