"""Fast transcription — synchronous REST for a single file.

For files under ~2hr / 300MB. Returns transcript in the same call. Uses the
Fast Transcription REST route (`/speechtotext/transcriptions:transcribe`).
"""
from pathlib import Path

import httpx
from azure.identity import DefaultAzureCredential

from _shared.config import SAMPLE_DATA, settings

_SCOPE = "https://cognitiveservices.azure.com/.default"


def _endpoint_base() -> str:
    s = settings()
    # Fast STT lives on `<region>.stt.speech.microsoft.com` OR at the resource endpoint.
    return s.speech_endpoint or f"https://{s.speech_region}.stt.speech.microsoft.com"


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
