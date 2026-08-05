"""Azure Translator Text v3 REST client using keyless Microsoft Entra auth.

Uses Translator's documented global endpoint. No subscription key is stored.
"""
import httpx
from azure.identity import DefaultAzureCredential
from .config import settings

_SCOPE = "https://cognitiveservices.azure.com/.default"
_ENDPOINT = "https://api.cognitive.microsofttranslator.com"
_API_VERSION = "3.0"


def _token() -> str:
    return DefaultAzureCredential().get_token(_SCOPE).token


def _resource_id() -> str:
    resource_id = settings().require("TRANSLATOR_RESOURCE_ID")
    parts = resource_id.strip("/").split("/")
    if (
        len(parts) != 8
        or parts[0].lower() != "subscriptions"
        or parts[2].lower() != "resourcegroups"
        or parts[4].lower() != "providers"
        or parts[5].lower() != "microsoft.cognitiveservices"
        or parts[6].lower() != "accounts"
        or not all(parts[index] for index in (1, 3, 7))
    ):
        raise ValueError(
            "TRANSLATOR_RESOURCE_ID must be the Translator resource ARM ID: "
            "/subscriptions/<id>/resourceGroups/<name>/providers/"
            "Microsoft.CognitiveServices/accounts/<name>."
        )
    return resource_id


def translate(
    text: str, targets: list[str], source_language: str = "en"
) -> list[dict]:
    params = [("api-version", _API_VERSION), ("from", source_language)]
    params.extend(("to", target) for target in targets)
    headers = {
        "Authorization": f"Bearer {_token()}",
        "Ocp-Apim-ResourceId": _resource_id(),
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
