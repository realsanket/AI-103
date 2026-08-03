"""Azure Speech SpeechConfig factory — keyless via Entra token when possible.

The Speech SDK supports token-based auth via `SpeechConfig(auth_token=..., region=...)`.
We fetch a Cognitive Services scope token so no long-lived key is stored.
"""
import azure.cognitiveservices.speech as speechsdk
from azure.identity import DefaultAzureCredential
from .config import settings

_SCOPE = "https://cognitiveservices.azure.com/.default"


def _token() -> str:
    return DefaultAzureCredential().get_token(_SCOPE).token


def speech_config() -> speechsdk.SpeechConfig:
    s = settings()
    # SpeechConfig auth_token format for Entra: "aad#<resource_id>#<token>". For most
    # regional endpoints, `auth_token=<bearer>` works when passed with `region=`.
    return speechsdk.SpeechConfig(auth_token=_token(), region=s.speech_region)
