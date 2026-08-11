# Run: uv run python 04-text-and-speech/11_stt_fast_file.py
"""Fast Transcription — synchronous REST for a single audio file.

Fast Transcription is the one-file synchronous STT path. POST audio + a JSON
definition to /speechtotext/transcriptions:transcribe and get the transcript back
in the same response. Limit: ~2 hr / 300 MB per file. Use Real-time STT (12) for
live streaming; use Batch Transcription (13) for many files without a waiting user.

Code path:
  _endpoint_base() returns configured speech_endpoint or derives regional URL.
  transcribe() opens the WAV, POSTs multipart with auth Bearer token and JSON
  definition → r.json()["combinedPhrases"][0]["text"].

What to watch: the printed transcript of conversation.wav. An empty string means
combinedPhrases was empty — check locale and audio codec. A 404 means the API
version is wrong; this repo uses 2025-10-15.

Prerequisites / env vars:
  SPEECH_ENDPOINT — Speech resource endpoint (cognitiveservices.azure.com), OR
  SPEECH_REGION   — falls back to regional stt.speech.microsoft.com endpoint
"""
from pathlib import Path

import httpx
from azure.identity import DefaultAzureCredential

from _shared.config import SAMPLE_DATA, settings
from _shared.speech_config import speech_region

_SCOPE = "https://cognitiveservices.azure.com/.default"


def _endpoint_base() -> str:
    s = settings()
    # Fast STT lives on `<region>.stt.speech.microsoft.com` OR at the resource endpoint.
    return s.speech_endpoint or f"https://{speech_region()}.stt.speech.microsoft.com"


def transcribe(audio_path: Path, locale: str = "en-US") -> str:
    token = DefaultAzureCredential().get_token(_SCOPE).token
    url = f"{_endpoint_base()}/speechtotext/transcriptions:transcribe?api-version=2025-10-15"
    with audio_path.open("rb") as f:
        files = {
            "audio": (audio_path.name, f, "audio/wav"),
            "definition": (None, '{"locales":["' + locale + '"]}', "application/json"),
        }
        r = httpx.post(url, headers={"Authorization": f"Bearer {token}"}, files=files, timeout=120.0)
    r.raise_for_status()
    body = r.json()
    phrases = body.get("combinedPhrases", [])
    return phrases[0]["text"] if phrases else ""


def main() -> None:
    audio = SAMPLE_DATA / "audio" / "conversation.wav"
    print(transcribe(audio))


if __name__ == "__main__":
    main()
