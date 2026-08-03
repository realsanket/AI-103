"""Azure Translator via Foundry Tools — REST-only surface (no dedicated SDK for this route).

We use httpx + Entra bearer token so no subscription key is stored.
"""
import httpx
from azure.identity import DefaultAzureCredential
from .config import settings

_SCOPE = "https://cognitiveservices.azure.com/.default"


def _token() -> str:
    return DefaultAzureCredential().get_token(_SCOPE).token


def translate(text: str, targets: list[str], source_language: str = "en") -> dict:
    s = settings()
    url = f"{s.translator_endpoint}/translator/text/translate?api-version={s.translator_api_version}"
    headers = {
        "Authorization": f"Bearer {_token()}",
        "Content-Type": "application/json",
    }
    body = {
        "inputs": [
            {
                "Text": text,
                "language": source_language,
                "targets": [{"language": t} for t in targets],
            }
        ]
    }
    resp = httpx.post(url, headers=headers, json=body, timeout=30.0)
    resp.raise_for_status()
    return resp.json()
