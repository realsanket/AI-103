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

By default the routes use anonymous authentication, only for non-sensitive,
static demonstration data. Do not expose production order data this way.

## Require a function key (lesson 12 `--auth connection`)

1. Set the app setting `ORDERS_REQUIRE_KEY=true`; both routes switch to
   `AuthLevel.FUNCTION` and reject calls without a key.

   ```bash
   az functionapp config appsettings set --name <your-function-app-name> \
     --resource-group <rg> --settings ORDERS_REQUIRE_KEY=true
   ```

2. Copy a function key from the portal (Function App → App keys). Treat it as a
   secret: never commit it or put it in `.env`.
3. In the Foundry project, create a **Custom keys** connection whose key is
   `x-functions-key` and whose value is the function key. Set
   `ORDERS_CONNECTION_NAME` to the connection name.
4. Run `uv run python 02-generative-ai-and-agents/12_agent_openapi_tools.py --auth connection`.
   The lesson adds an `apiKey` security scheme for `x-functions-key` to the spec
   and connects the tool to the connection, so Agent Service sends the header.

For production, prefer managed identity (Entra) authentication where the
backend supports it, and rotate keys through the connection.
