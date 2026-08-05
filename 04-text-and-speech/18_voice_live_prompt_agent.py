"""Voice Live for a Foundry Prompt Agent — bidirectional WebSocket session.

Beginner note:
  Voice Live streams mic audio → agent → synthesized audio back, all in one
  WebSocket connection. Preview API; the endpoint shape changed recently.
  Current URL (verified in `ai-services/speech-service/voice-live-how-to.md`):

    wss://<resource>.services.ai.azure.com/voice-live/realtime?api-version=2026-04-10
        &agent_id=<agent-id>
        &project_id=<project-id>

  For non-agent scenarios, pass `model=<name>` instead of `agent_id`+`project_id`.
  Older docs referenced `/voice-live/v1` and `agent_name` — those are outdated.

  This lesson creates the agent inline so it runs cold. Set
  `VOICE_LIVE_ENDPOINT` in `.env` to the base wss URL WITHOUT query params.
"""
import asyncio
import base64
import json

import websockets
from azure.ai.projects.models import PromptAgentDefinition
from azure.identity import DefaultAzureCredential

from _shared.config import SAMPLE_DATA, settings
from _shared.foundry_client import project_client

_SCOPE = "https://cognitiveservices.azure.com/.default"

AGENT_NAME = "northwind-voice-live-agent"

_INSTRUCTIONS = (
    "You are Northwind customer support. The user is talking to you by voice. "
    "Keep answers under two sentences. Speak conversationally."
)


def _ensure_agent(project) -> str:
    """Create the agent inline; return the agent id for the Voice Live URL."""
    agent = project.agents.create_version(
        agent_name=AGENT_NAME,
        definition=PromptAgentDefinition(
            model=settings().default_model,
            instructions=_INSTRUCTIONS,
        ),
    )
    return agent.id


async def _run() -> None:
    project = project_client()
    agent_id = _ensure_agent(project)

    # PROJECT_ENDPOINT ends with `/api/projects/<project-name>` — take the last segment
    s = settings()
    project_name = s.project_endpoint.rstrip("/").split("/")[-1]

    token = DefaultAzureCredential().get_token(_SCOPE).token
    url = (
        f"{s.voice_live_endpoint}"
        f"?api-version=2026-04-10"
        f"&agent_id={agent_id}"
        f"&project_id={project_name}"
    )
    headers = {"Authorization": f"Bearer {token}"}
    print(f"connecting to: {url}")

    audio_bytes = (SAMPLE_DATA / "audio" / "northwind_support_message.wav").read_bytes()
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
