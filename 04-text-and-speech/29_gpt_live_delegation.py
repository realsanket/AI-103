# Run: uv run python 04-text-and-speech/29_gpt_live_delegation.py [--apply]
"""Compare GPT-Live's two delegation modes and drive one delegated turn end-to-end.

When a GPT-Live conversation needs search, deeper reasoning, or an action outside the
spoken exchange, the live model *delegates* that work while the conversation continues.
Two modes, configured once at `session.start` in the `delegation` field:

- Client delegation (`{ type: "client" }` or omitted / null). The service emits
  `session.delegation.created` with `target: "client"` + a delegation `id`. Your
  application does the work and returns the result via `session.commentary.append`
  (spoken) or `session.thinking.append` (quiet), setting `delegation_id` to the id.

- Responses delegation (`{ type: "responses", responses: {...} }`). The service manages
  a Responses API backend with hosted tools (e.g. `web_search`) and its own model. Events
  arrive wrapped in `response.event` envelopes — dispatch on the *nested* `event.type`.
  Client-actionable function calls come out via a nested `response.output_item.done` with
  a `function_call` item; your app runs the tool and submits the result with
  `response.item.create` (item.type=`function_call_output`), then `response.create` to
  continue the backend response.

Preflight prints both delegation config objects verbatim from the how-to doc side by side.
`--apply` opens a session in client delegation mode, injects a `session.commentary.append`
tied to `delegation_id=null` (the general-session delegation slot), and reads events until
close. Full delegated tool loops need audio input to trigger `session.delegation.created`;
mode switch and event routing are provable without audio.

Code path:
  --apply: websockets.connect → session.start (delegation=client)
  → session.commentary.append (delegation_id=null, content="...")
  → wait session.commentary.appended → session.close → drain until session.closed.

What to watch. `session.commentary.appended` proves the client-side commentary path is
wired. To see `session.delegation.created` with `target: "client"` you need real user
speech triggering the delegation — this lesson stops short of that. Switching modes
requires a new session; sparse `session.update` can only patch `delegation.responses`
sub-fields, not the mode itself.

Prerequisites / env vars:
  AZURE_OPENAI_ENDPOINT     — Foundry / Azure OpenAI resource endpoint (https://...)
  AZURE_OPENAI_API_KEY      — API key (omit to use DefaultAzureCredential)
  GPT_LIVE_MODEL            — GPT-Live deployment name (default: gpt-live-1)
  GPT_LIVE_RESPONSES_MODEL  — backend model shown in the Responses config (default: gpt-5.5)
  --apply                   — open WebSocket + run one client-delegation append cycle
"""
import argparse
import json
import os

from _shared.config import load_env


def _live_url(endpoint: str) -> str:
    base = endpoint.rstrip("/").replace("https://", "wss://")
    return f"{base}/openai/v1/live/sessions"


def _client_delegation() -> dict:
    return {"type": "client"}


def _responses_delegation(responses_model: str) -> dict:
    # Mirrors the how-to doc example verbatim: web_search + a client-actionable function.
    return {
        "type": "responses",
        "responses": {
            "model": responses_model,
            "instructions": "Use tools when current information is required.",
            "tools": [
                {"type": "web_search"},
                {
                    "type": "function",
                    "name": "get_weather",
                    "description": "Get current weather for a location.",
                    "parameters": {
                        "type": "object",
                        "properties": {"location": {"type": "string"}},
                        "required": ["location"],
                        "additionalProperties": False,
                    },
                },
            ],
            "tool_choice": "auto",
            "parallel_tool_calls": True,
        },
    }


def preflight() -> None:
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "")
    model = os.environ.get("GPT_LIVE_MODEL", "gpt-live-1")
    responses_model = os.environ.get("GPT_LIVE_RESPONSES_MODEL", "gpt-5.5")
    api_key = os.environ.get("AZURE_OPENAI_API_KEY", "")
    print("GPT-Live delegation preflight (no cloud calls).")
    print(f"- AZURE_OPENAI_ENDPOINT: {'configured' if endpoint else 'MISSING'}")
    print(f"- GPT_LIVE_MODEL: {model}")
    print(f"- GPT_LIVE_RESPONSES_MODEL: {responses_model}")
    print(f"- AZURE_OPENAI_API_KEY: {'configured' if api_key else 'not set (DefaultAzureCredential)'}")
    if endpoint:
        print(f"- WebSocket URL: {_live_url(endpoint)}")
    print()
    print("Client delegation config:")
    print(json.dumps({"delegation": _client_delegation()}, indent=2))
    print()
    print("Responses delegation config:")
    print(json.dumps({"delegation": _responses_delegation(responses_model)}, indent=2))
    print()
    print("Handoff shape by mode:")
    print("  client    -> session.delegation.created (target=client, id)")
    print("               reply with session.commentary.append or session.thinking.append")
    print("               (set delegation_id = that id)")
    print("  responses -> session.delegation.created (target=responses, response_id)")
    print("               events wrapped in response.event; dispatch on nested event.type;")
    print("               for function_call items, submit response.item.create then response.create")
    print()
    print("--apply runs one client-delegation append against the general session slot.")


def apply() -> None:
    try:
        import websockets  # noqa: F401
    except ImportError:
        raise SystemExit("Install websockets: uv add websockets")

    import asyncio

    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "")
    if not endpoint:
        raise SystemExit("Set AZURE_OPENAI_ENDPOINT to your Foundry / Azure OpenAI resource endpoint.")
    model = os.environ.get("GPT_LIVE_MODEL", "gpt-live-1")
    api_key = os.environ.get("AZURE_OPENAI_API_KEY", "")
    url = _live_url(endpoint)

    async def run() -> None:
        import websockets

        headers: dict[str, str] = {}
        if api_key:
            headers["api-key"] = api_key
        else:
            from azure.identity import DefaultAzureCredential
            token = DefaultAzureCredential().get_token("https://cognitiveservices.azure.com/.default").token
            headers["Authorization"] = f"Bearer {token}"

        print(f"Connecting: {url}")
        async with websockets.connect(url, additional_headers=headers) as ws:
            await ws.send(json.dumps({
                "type": "session.start",
                "event_id": "event_start",
                "session": {
                    "model": model,
                    "instructions": "Be concise. Ask before external actions.",
                    "delegation": _client_delegation(),
                },
            }))

            event_counts: dict[str, int] = {}
            usage: dict | None = None

            async for raw in ws:
                event = json.loads(raw)
                etype = event.get("type", "")
                event_counts[etype] = event_counts.get(etype, 0) + 1

                if etype == "session.started":
                    print(f"session.started id={event.get('session', {}).get('id')} "
                          f"delegation={event.get('session', {}).get('delegation')}")
                    # Append content the model can say aloud. delegation_id=null = general
                    # session slot, not tied to a specific delegation. A real client
                    # delegation reply would use the id from session.delegation.created.
                    await ws.send(json.dumps({
                        "type": "session.commentary.append",
                        "event_id": "event_commentary_1",
                        "delegation_id": None,
                        "content": "The scheduled maintenance window is 22:00 to 23:00 UTC tonight.",
                    }))
                elif etype == "session.commentary.appended":
                    print(f"session.commentary.appended start_ms={event.get('start_ms')} "
                          f"end_ms={event.get('end_ms')}")
                    await ws.send(json.dumps({"type": "session.close", "event_id": "event_close"}))
                elif etype == "session.usage.updated":
                    usage = event.get("usage")
                elif etype == "session.closed":
                    usage = event.get("usage", usage)
                    print(f"session.closed reason={event.get('reason')}")
                    break
                elif etype == "error":
                    print(f"error: {event.get('error')}")
                    break

            print()
            print("Event summary:")
            for name, count in sorted(event_counts.items()):
                print(f"  {name}: {count}")
            print(f"final usage: {usage}")

    asyncio.run(run())


def main(argv: list[str] | None = None) -> None:
    load_env()
    parser = argparse.ArgumentParser(description="Compare + drive GPT-Live delegation modes.")
    parser.add_argument("--apply", action="store_true", help="Open WebSocket + run one client-delegation cycle.")
    args = parser.parse_args(argv)
    if not args.apply:
        preflight()
        return
    apply()


if __name__ == "__main__":
    main()
