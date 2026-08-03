"""Voice Live for a Foundry Prompt Agent — bidirectional WebSocket session.

Streams mic audio → agent → synthesized audio back, in one continuous session.
Uses Voice Live's simplified surface for Prompt Agents (GA); Hosted Agents
+ Voice Live is a separate preview shape.

This lesson connects and exchanges one round-trip; extend for a full session
in your own app.
"""
import asyncio
import base64
import json

import websockets
from azure.identity import DefaultAzureCredential

from _shared.config import SAMPLE_DATA, settings

_SCOPE = "https://cognitiveservices.azure.com/.default"

AGENT_NAME = "cloudxeus-support"


async def _run() -> None:
    token = DefaultAzureCredential().get_token(_SCOPE).token
    url = (
        f"{settings().voice_live_endpoint}?agent_name={AGENT_NAME}"
        f"&api-version=2025-11-15-preview"
    )
    headers = {"Authorization": f"Bearer {token}"}

    audio_bytes = (SAMPLE_DATA / "audio" / "cloudxeus_support_message.wav").read_bytes()
    b64_audio = base64.b64encode(audio_bytes).decode("ascii")

    async with websockets.connect(url, extra_headers=headers) as ws:
        await ws.send(json.dumps({
            "type": "input_audio_buffer.append",
            "audio": b64_audio,
        }))
        await ws.send(json.dumps({"type": "input_audio_buffer.commit"}))
        await ws.send(json.dumps({"type": "response.create"}))

        async for msg in ws:
            event = json.loads(msg)
            print(event.get("type"), "→", str(event)[:160])
            if event.get("type") == "response.done":
                break


def main() -> None:
    asyncio.run(_run())


if __name__ == "__main__":
    main()
