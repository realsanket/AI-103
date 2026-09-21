"""Minimal REST deployment helper for JSON AI Search resources."""
import json
from pathlib import Path

import httpx
from azure.identity import DefaultAzureCredential

from _shared.config import settings

_API_VERSION = "2026-04-01"
_PREVIEW_API_VERSION = "2026-08-01-preview"
_SCOPE = "https://search.azure.com/.default"


def _endpoint() -> str:
    endpoint = settings().search_endpoint
    if not endpoint:
        raise RuntimeError("Missing env var SEARCH_ENDPOINT.")
    return endpoint.rstrip("/")


def _token() -> str:
    return DefaultAzureCredential().get_token(_SCOPE).token


def put_named(resource: str, name: str, body: dict, api_version: str = _API_VERSION) -> dict:
    """PUT /<resource>/<name>?api-version=... Returns response JSON when present."""
    response = httpx.put(
        f"{_endpoint()}/{resource}/{name}?api-version={api_version}",
        headers={"Authorization": f"Bearer {_token()}", "Content-Type": "application/json"},
        json=body,
        timeout=120.0,
    )
    response.raise_for_status()
    return response.json() if response.content else {}


def post(path: str, body: dict, api_version: str = _PREVIEW_API_VERSION) -> dict:
    """POST /<path>?api-version=... Used for the knowledge-base retrieve action."""
    response = httpx.post(
        f"{_endpoint()}/{path}?api-version={api_version}",
        headers={"Authorization": f"Bearer {_token()}", "Content-Type": "application/json"},
        json=body,
        timeout=120.0,
    )
    response.raise_for_status()
    return response.json() if response.content else {}


def load_definition(path: Path) -> dict:
    """Load a JSON resource and resolve its documented configuration placeholders."""
    s = settings()
    values = {
        "AZURE_OPENAI_ENDPOINT": s.azure_openai_endpoint,
        "EMBEDDING_MODEL": s.embedding_model,
        "AZURE_RESOURCE_GROUP": s.azure_resource_group,
        "AZURE_SUBSCRIPTION_ID": s.azure_subscription_id,
        "SEARCH_INDEXER": s.search_indexer,
        "SEARCH_INDEX_VECTOR": s.search_index_vector,
        "SEARCH_SKILLSET": s.search_skillset,
        "STORAGE_ACCOUNT": s.storage_account,
        "STORAGE_CONTAINER": s.storage_container,
    }
    text = path.read_text()
    for name, value in values.items():
        marker = f"${{{name}}}"
        if marker in text:
            if not value:
                raise RuntimeError(f"Missing env var {name} required by {path.name}.")
            text = text.replace(marker, value)
    return json.loads(text)


def put(resource: str, definition: dict) -> None:
    """Create or replace one Search resource using its REST JSON shape."""
    endpoint = settings().search_endpoint
    if not endpoint:
        raise RuntimeError("Missing env var SEARCH_ENDPOINT.")
    token = DefaultAzureCredential().get_token(_SCOPE).token
    response = httpx.put(
        f"{endpoint.rstrip('/')}/{resource}/{definition['name']}?api-version={_API_VERSION}",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=definition,
        timeout=60.0,
    )
    response.raise_for_status()
