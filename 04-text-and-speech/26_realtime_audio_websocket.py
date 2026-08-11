# Run: uv run python 04-text-and-speech/26_realtime_audio_websocket.py [--apply]
"""Connect to the Azure OpenAI Realtime Audio API via WebSocket and exchange one text turn.

The Realtime API streams bidirectional audio over WebSocket — it is NOT the standard
chat completions path. The model receives PCM16 audio chunks and streams audio + transcript
in real time. This lesson validates the WebSocket connection and sends one text-mode turn
to prove auth works before adding audio I/O. Audio capture/playback requires sounddevice
or pyaudio and is out of scope here.

Default preflight checks env vars and prints the WebSocket URL. --apply opens a WebSocket
session, sends one text input item, reads events until response.done, and closes. The
transcript in the response proves the model is live and reachable.

Code path:
  --apply: websockets.connect(wss://{endpoint}/openai/realtime?deployment={model}&api-version=...)
  → session.update (modalities: text) → conversation.item.create (text input)
  → response.create → read events until response.done → print transcript.

What to watch. Response text from the model proves auth + routing works.
401 = wrong AZURE_OPENAI_API_KEY or missing DefaultAzureCredential.
1006/connection reset = wrong URL format or deployment not realtime-capable.

Prerequisites / env vars:
  AZURE_OPENAI_ENDPOINT  — Azure OpenAI resource endpoint (https://...)
  AZURE_OPENAI_API_KEY   — API key (omit to use DefaultAzureCredential)
  REALTIME_MODEL         — realtime deployment (e.g. gpt-4o-realtime-preview)
  --apply                — open WebSocket and exchange one text turn
"""
import argparse
import json
import os


def _realtime_url(endpoint: str, model: str, api_version: str = "2024-10-01-preview") -> str:
    base = endpoint.rstrip("/").replace("https://", "wss://")
    return f"{base}/openai/realtime?deployment={model}&api-version={api_version}"


def preflight() -> None:
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "")
    model = os.environ.get("REALTIME_MODEL", "gpt-4o-realtime-preview")
    api_key = os.environ.get("AZURE_OPENAI_API_KEY", "")
    print("Realtime Audio WebSocket preflight (no cloud calls).")
    print(f"- AZURE_OPENAI_ENDPOINT: {'configured' if endpoint else 'MISSING'}")
    print(f"- REALTIME_MODEL: {model}")
    print(f"- AZURE_OPENAI_API_KEY: {'configured' if api_key else 'not set (DefaultAzureCredential)'}")
    if endpoint:
        print(f"- WebSocket URL: {_realtime_url(endpoint, model)}")
    print()
    print("Note: Full audio streaming requires sounddevice/pyaudio for mic/speaker.")
    print("This lesson proves auth + text turn only. Add PCM16 chunks for voice pipeline.")
    print("Install websockets: uv add websockets")


def apply() -> None:
    try:
        import websockets  # noqa: F401
    except ImportError:
        raise SystemExit("Install websockets: uv add websockets")

    import asyncio

    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "")
    if not endpoint:
        raise SystemExit("Set AZURE_OPENAI_ENDPOINT to your Azure OpenAI resource endpoint.")
    model = os.environ.get("REALTIME_MODEL", "gpt-4o-realtime-preview")
    api_key = os.environ.get("AZURE_OPENAI_API_KEY", "")
    url = _realtime_url(endpoint, model)

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
            await ws.send(json.dumps({"type": "session.update", "session": {"modalities": ["text"]}}))
            await ws.send(json.dumps({
                "type": "conversation.item.create",
                "item": {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": "Say hello in one sentence."}],
                },
            }))
            await ws.send(json.dumps({"type": "response.create"}))
            parts: list[str] = []
            async for raw in ws:
                event = json.loads(raw)
                etype = event.get("type", "")
                if etype == "response.text.delta":
                    parts.append(event.get("delta", ""))
                elif etype == "response.done":
                    break
            print(f"Response: {''.join(parts)}")

    asyncio.run(run())


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Test Realtime Audio API WebSocket connection.")
    parser.add_argument("--apply", action="store_true", help="Open WebSocket + exchange one text turn.")
    args = parser.parse_args(argv)
    if not args.apply:
        preflight()
        return
    apply()


if __name__ == "__main__":
    main()
