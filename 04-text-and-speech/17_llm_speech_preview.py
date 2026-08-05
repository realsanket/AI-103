"""MAI-Transcribe preview — file transcription through the LLM Speech API.

`mai-transcribe-1.5` supports phrase-list entity biasing and verbatim output.
It does not support prompt-tuning or diarization.
"""
import json

import httpx
from azure.identity import DefaultAzureCredential

from _shared.config import SAMPLE_DATA, settings

_SCOPE = "https://cognitiveservices.azure.com/.default"


def _token() -> str:
    return DefaultAzureCredential().get_token(_SCOPE).token


def main() -> None:
    audio = SAMPLE_DATA / "audio" / "conversation.wav"
    url = (
        f"{settings().speech_endpoint}"
        f"/speechtotext/transcriptions:transcribe?api-version=2025-10-15"
    )
    definition = {
        "locales": ["en"],
        "phraseList": {"phrases": ["Northwind Connect", "Sentinel", "Ledger"]},
        "enhancedMode": {"enabled": True, "model": "mai-transcribe-1.5"},
    }
    with audio.open("rb") as f:
        files = {
            "audio": (audio.name, f, "audio/wav"),
            "definition": (None, json.dumps(definition), "application/json"),
        }
        r = httpx.post(url, headers={"Authorization": f"Bearer {_token()}"}, files=files, timeout=180.0)
    r.raise_for_status()
    body = r.json()
    for phrase in body.get("combinedPhrases", []):
        print(phrase.get("text", ""))


if __name__ == "__main__":
    main()
