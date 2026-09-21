# Run: uv run python 04-text-and-speech/28_gpt_live_session.py [--apply]
"""Open a GPT-Live full-duplex voice session over WebSocket and drive one text turn.

GPT-Live is Foundry OpenAI's full-duplex voice model (`gpt-live-1`) — the audio channel
carries data in both directions simultaneously (phone-call model), unlike the turn-based
Realtime Audio API in lesson 26. Session lifecycle differs: the client sends `session.start`
with a strict config object (`model`, `instructions`, `audio.output.voice`, `delegation`),
waits for `session.started`, exchanges events, then sends `session.close` and reads until
`session.closed` carries final cumulative usage.

This lesson validates the WebSocket handshake and session config against a live endpoint
without streaming audio: the audio pipeline requires 24 kHz mono PCM16 base64 frames plus
mic/speaker I/O (sounddevice / pyaudio) which is out of scope. Instead, `--apply` opens the
session, injects a `session.thinking.append` context event (a supported non-audio input),
reads the resulting event stream until `session.closed`, and prints event types + final
usage. Delegation is set to `null` which the service resolves to client delegation.

Code path:
  --apply: websockets.connect(wss://{endpoint}/openai/v1/live/sessions)
  → session.start (model=gpt-live-1, delegation=null) → wait session.started
  → session.thinking.append (delegation_id=null, content="...")
  → collect events until session.closed → print event summary + usage.

What to watch. `session.started` with the session id proves auth + model routing.
`session.thinking.appended` acknowledges the context injection (does NOT prove the model
consumed it — full-duplex means speech and context run independently). `session.closed`
carries the authoritative final `usage`; a transport close without it leaves usage
unconfirmed. 401 = wrong AZURE_OPENAI_API_KEY or missing DefaultAzureCredential.
404 / 1006 = endpoint doesn't host a `gpt-live-1` deployment.

Prerequisites / env vars:
  AZURE_OPENAI_ENDPOINT  — Foundry / Azure OpenAI resource endpoint (https://...)
  AZURE_OPENAI_API_KEY   — API key (omit to use DefaultAzureCredential)
  GPT_LIVE_MODEL         — GPT-Live deployment name (default: gpt-live-1)
  --apply                — open WebSocket and drive one text-context turn
"""
import argparse
import json
import os


def _live_url(endpoint: str) -> str:
    base = endpoint.rstrip("/").replace("https://", "wss://")
    return f"{base}/openai/v1/live/sessions"


def _session_config(model: str) -> dict:
    # Mirrors the how-to doc verbatim: strict object, delegation omitted/null = client mode.
    return {
        "model": model,
        "instructions": "Be concise and ask before taking an external action.",
        "audio": {"output": {"voice": "marin"}},
        "delegation": None,
    }


def preflight() -> None:
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "")
    model = os.environ.get("GPT_LIVE_MODEL", "gpt-live-1")
    api_key = os.environ.get("AZURE_OPENAI_API_KEY", "")
    print("GPT-Live session preflight (no cloud calls).")
    print(f"- AZURE_OPENAI_ENDPOINT: {'configured' if endpoint else 'MISSING'}")
    print(f"- GPT_LIVE_MODEL: {model}")
    print(f"- AZURE_OPENAI_API_KEY: {'configured' if api_key else 'not set (DefaultAzureCredential)'}")
    if endpoint:
        print(f"- WebSocket URL: {_live_url(endpoint)}")
    print()
    print("Session config that --apply will send in session.start:")
    print(json.dumps(_session_config(model), indent=2))
    print()
    print("Notes:")
    print("- Full audio path needs 24 kHz mono PCM16 base64 frames on session.input_audio.append.")
    print("- This lesson only proves the session lifecycle: start -> thinking.append -> close.")
    print("- Delegation=null resolves to client delegation server-side (see lesson 29).")
    print("- Install websockets: uv add websockets")


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
                "session": _session_config(model),
            }))

            session_id: str | None = None
            event_counts: dict[str, int] = {}
            usage: dict | None = None
            closed_reason: str | None = None
            sent_context = False

            async for raw in ws:
                event = json.loads(raw)
                etype = event.get("type", "")
                event_counts[etype] = event_counts.get(etype, 0) + 1

                if etype == "session.started":
                    session_id = event.get("session", {}).get("id")
                    print(f"session.started id={session_id}")
                    # Inject one context event to prove the non-audio input path works.
                    await ws.send(json.dumps({
                        "type": "session.thinking.append",
                        "event_id": "event_context_1",
                        "delegation_id": None,
                        "content": "The caller has confirmed their identity.",
                    }))
                    sent_context = True
                elif etype == "session.thinking.appended":
                    print("session.thinking.appended (context accepted for injection)")
                    # Nothing else to drive from the client without audio; close cleanly.
                    await ws.send(json.dumps({"type": "session.close", "event_id": "event_close"}))
                elif etype == "session.usage.updated":
                    usage = event.get("usage")
                elif etype == "session.closed":
                    usage = event.get("usage", usage)
                    closed_reason = event.get("reason")
                    break
                elif etype == "error":
                    print(f"error: {event.get('error')}")
                    break

            print()
            print("Event summary:")
            for name, count in sorted(event_counts.items()):
                print(f"  {name}: {count}")
            print(f"context injected: {sent_context}")
            print(f"close reason: {closed_reason}")
            print(f"final usage: {usage}")

    asyncio.run(run())


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Drive one GPT-Live session lifecycle over WebSocket.")
    parser.add_argument("--apply", action="store_true", help="Open WebSocket + run one session.start/close cycle.")
    args = parser.parse_args(argv)
    if not args.apply:
        preflight()
        return
    apply()


if __name__ == "__main__":
    main()
