"""LLM Speech (preview) — file-based transcription with prompt-tuning.

Adds contextual understanding + broader multilingual + prompt-tuning over the
classic Speech STT models. File-based only (not real-time). MAI-Transcribe is
Microsoft's own; other models can be selected per request.
"""
import httpx
from azure.identity import DefaultAzureCredential

from _shared.config import SAMPLE_DATA, settings

_SCOPE = "https://cognitiveservices.azure.com/.default"


def _token() -> str:
    return DefaultAzureCredential().get_token(_SCOPE).token


def main() -> None:
    audio = SAMPLE_DATA / "audio" / "conversation.wav"
    # Verified against ai-services/speech-service/mai-transcribe.md — api-version=2025-10-15
    # Endpoint is the resource endpoint (cognitiveservices subdomain), not region-specific.
    url = (
        f"{settings().speech_endpoint}"
        f"/speechtotext/transcriptions:transcribe?api-version=2025-10-15"
    )
    with audio.open("rb") as f:
        files = {
            "audio": (audio.name, f, "audio/wav"),
            "definition": (
                None,
                '{"model":"mai-transcribe","locales":["en-US"],'
                '"prompt":"Northwind product names include Connect, Sentinel, Ledger. '
                'Use exact spellings."}',
                "application/json",
            ),
        }
        r = httpx.post(url, headers={"Authorization": f"Bearer {_token()}"}, files=files, timeout=180.0)
    r.raise_for_status()
    body = r.json()
    for phrase in body.get("combinedPhrases", []):
        print(phrase.get("text", ""))


if __name__ == "__main__":
    main()
