# Run: uv run python 04-text-and-speech/17_llm_speech_preview.py
"""MAI-Transcribe 1.5 preview — file transcription with phrase-list entity biasing.

mai-transcribe-1.5 is an LLM-based speech recognition model available through the
same Fast Transcription REST route. It improves recognition of named entities you
supply in a phraseList. It does NOT support prompt-tuning, diarization, or
transcribeStyle configuration (in the checked-in request). A phrase list is NOT the
same as Custom Speech training — it biases recognition without a model retraining cycle.

Code path:
  Build definition dict with locales, phraseList.phrases, and enhancedMode enabled
  with model=mai-transcribe-1.5. POST multipart to
  /speechtotext/transcriptions:transcribe?api-version=2025-10-15 with Bearer token.
  Print returned transcript.

What to watch: "Northwind Connect" and other listed phrases should be recognized
accurately if the audio contains them. A 404 means model or API version mismatch;
verify regional preview availability.

Prerequisites / env vars:
  SPEECH_ENDPOINT — Speech resource endpoint (cognitiveservices.azure.com)
  _shared/sample_data/audio/conversation.wav must exist
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
