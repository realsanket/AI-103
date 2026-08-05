"""Azure Translator Text v3 REST client using keyless Microsoft Entra auth.

Uses Translator's documented global endpoint. No subscription key is stored.
"""
import httpx
from azure.identity import DefaultAzureCredential

_SCOPE = "https://cognitiveservices.azure.com/.default"
_ENDPOINT = "https://api.cognitive.microsofttranslator.com"
_API_VERSION = "3.0"


def _token() -> str:
    return DefaultAzureCredential().get_token(_SCOPE).token


def translate(
    text: str, targets: list[str], source_language: str = "en"
) -> list[dict]:
    params = [("api-version", _API_VERSION), ("from", source_language)]
    params.extend(("to", target) for target in targets)
    headers = {
        "Authorization": f"Bearer {_token()}",
        "Content-Type": "application/json",
    }
    resp = httpx.post(
        f"{_ENDPOINT}/translate",
        params=params,
        headers=headers,
        json=[{"Text": text}],
        timeout=30.0,
    )
    resp.raise_for_status()
    return resp.json()
