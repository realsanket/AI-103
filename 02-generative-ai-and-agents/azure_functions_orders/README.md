# CloudXeus Orders — Azure Function (OpenAPI tool backend)

Backs lesson `12_agent_openapi_tools.py`.

Serves two endpoints described by `cloudxeus_spec.json`:

- `GET /orders` — list orders
- `GET /orders/{order_id}` — fetch by id

The Foundry agent reads the OpenAPI spec, converts each operation to a callable
tool, and decides when to call which — no glue code in the agent.

## Run locally

```bash
cp local.settings.json.example local.settings.json
func start
```

## Deploy

```bash
func azure functionapp publish <your-function-app-name>
```

Then update the `servers.url` in `cloudxeus_spec.json` to your deployed URL.
