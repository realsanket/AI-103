"""Azure Speech SpeechConfig factory — keyless via Entra token, endpoint-based routing."""
from pathlib import Path
import re

import azure.cognitiveservices.speech as speechsdk
from azure.identity import DefaultAzureCredential
from .config import settings

_SCOPE = "https://cognitiveservices.azure.com/.default"
_REGION = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


def _token() -> str:
    return DefaultAzureCredential().get_token(_SCOPE).token


def speech_region() -> str:
    """Return a region safe to interpolate into a regional Speech hostname."""
    region = settings().speech_region.strip().lower()
    if not _REGION.fullmatch(region):
        raise ValueError("SPEECH_REGION must contain only lowercase letters, digits, and hyphens.")
    return region


def prepare_audio_output(path: Path) -> Path:
    """Create output directory and remove stale audio before synthesis."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.unlink(missing_ok=True)
    return path


def speech_config() -> speechsdk.SpeechConfig:
    s = settings()
    # Endpoint-based auth: same Foundry resource, cognitiveservices subdomain.
    # No SPEECH_REGION needed — the endpoint encodes the resource location.
    return speechsdk.SpeechConfig(
        auth_token=_token(), endpoint=s.require("SPEECH_ENDPOINT")
    )
