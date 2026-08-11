# Run: uv run python 04-text-and-speech/18_voice_live_prompt_agent.py
"""Voice Live WebSocket protocol demo — PCM audio to a Foundry Prompt Agent.

Voice Live is a real-time bidirectional WebSocket API that streams audio to an
agent and receives synthesized audio responses. This lesson is a protocol demo
only: it sends prerecorded PCM16 audio and logs response events. It does NOT
capture a microphone, decode audio deltas, or play audio. The Prompt Agent is
created inline (no portal setup needed). For the file-to-file flow with audio
output, see 24_voice_live_audio_flow.py.

Current URL shape (api-version=2026-04-10):
  wss://<resource>.services.ai.azure.com/voice-live/realtime
      ?api-version=2026-04-10&agent_id=<agent-id>&project_id=<project-name>
  Older docs used /voice-live/v1 and agent_name — those are outdated.

Code path:
  _ensure_agent() → create Prompt Agent version with DEFAULT_MODEL.
  websockets.connect() with additional_headers (Entra Bearer token, scope ai.azure.com).
  Send session.update, input_audio_buffer.append (base64 PCM16), commit, response.create.
  Iterate events until response.done. finally: delete agent version.

What to watch: session.created, input_audio_buffer.committed, response.audio.delta
(base64, not played), response.done. Audio deltas are logged only; no sound plays.

Prerequisites / env vars:
  VOICE_LIVE_ENDPOINT — wss://<resource>.services.ai.azure.com/voice-live/realtime (no query)
  PROJECT_ENDPOINT    — Foundry project endpoint
  DEFAULT_MODEL       — deployed chat model supported by Voice Live
"""
import asyncio
import base64
import json
import time
import wave

import websockets
from azure.ai.projects.models import PromptAgentDefinition
from azure.identity import DefaultAzureCredential

from _shared.config import SAMPLE_DATA, settings
from _shared.foundry_client import active_agent_reference, project_client

_SCOPE = "https://ai.azure.com/.default"

AGENT_NAME = "northwind-voice-live-agent"

_INSTRUCTIONS = (
    "You are Northwind customer support. The user is talking to you by voice. "
    "Keep answers under two sentences. Speak conversationally."
)


def _ensure_agent(project):
    """Create one agent version and wait until it can serve Voice Live."""
    agent = project.agents.create_version(
        agent_name=AGENT_NAME,
        definition=PromptAgentDefinition(
            model=settings().default_model,
            instructions=_INSTRUCTIONS,
        ),
    )
    deadline = time.monotonic() + 60
    while True:
        status = str(getattr(getattr(agent, "status", "active"), "value", getattr(agent, "status", "active"))).lower()
        if status == "active":
            active_agent_reference(agent)
            return agent
        if status in {"failed", "deleting", "deleted"}:
            raise RuntimeError(f"Voice Live agent {agent.name!r} is {status!r}.")
        if time.monotonic() >= deadline:
            raise TimeoutError(f"Voice Live agent {agent.name!r} did not become active within 60 seconds.")
        time.sleep(2)
        agent = project.agents.get_version(agent.name, agent.version)


def _read_pcm16_mono(audio_path) -> bytes:
    with wave.open(str(audio_path), "rb") as audio:
        if audio.getnchannels() != 1 or audio.getsampwidth() != 2 or audio.getframerate() != 16000:
            raise ValueError("Voice Live demo input must be 16-kHz, mono, 16-bit PCM WAV.")
        return audio.readframes(audio.getnframes())


async def _run() -> None:
    project = project_client()
    agent = _ensure_agent(project)

    # PROJECT_ENDPOINT ends with `/api/projects/<project-name>` — take the last segment
    s = settings()
    project_name = s.require("PROJECT_ENDPOINT").rstrip("/").split("/")[-1]

    token = DefaultAzureCredential().get_token(_SCOPE).token
    url = (
        f"{s.require('VOICE_LIVE_ENDPOINT').rstrip('/')}"
        f"?api-version=2026-04-10"
        f"&agent_id={agent.id}"
        f"&project_id={project_name}"
    )
    headers = {"Authorization": f"Bearer {token}"}
    print(f"connecting to: {url}")

    audio_bytes = _read_pcm16_mono(SAMPLE_DATA / "audio" / "northwind_support_message.wav")
    b64_audio = base64.b64encode(audio_bytes).decode("ascii")

    try:
        async with websockets.connect(url, additional_headers=headers) as ws:
            await ws.send(json.dumps({
                "type": "session.update",
                "session": {"input_audio_sampling_rate": 16000},
            }))
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
    finally:
        project.agents.delete_version(agent.name, agent.version)


def main() -> None:
    asyncio.run(_run())


if __name__ == "__main__":
    main()
