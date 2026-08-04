"""Azure Speech SpeechConfig factory — keyless via Entra token, endpoint-based routing."""
import azure.cognitiveservices.speech as speechsdk
from azure.identity import DefaultAzureCredential
from .config import settings

_SCOPE = "https://cognitiveservices.azure.com/.default"


def _token() -> str:
    return DefaultAzureCredential().get_token(_SCOPE).token


def speech_config() -> speechsdk.SpeechConfig:
    s = settings()
    # Endpoint-based auth: same Foundry resource, cognitiveservices subdomain.
    # No SPEECH_REGION needed — the endpoint encodes the resource location.
    return speechsdk.SpeechConfig(auth_token=_token(), endpoint=s.speech_endpoint)
