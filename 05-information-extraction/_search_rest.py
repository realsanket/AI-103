"""Minimal REST deployment helper for JSON AI Search resources."""
import json
from pathlib import Path

import httpx
from azure.identity import DefaultAzureCredential

from _shared.config import settings

_API_VERSION = "2025-09-01"
_SCOPE = "https://search.azure.com/.default"


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
        f"{endpoint}/{resource}/{definition['name']}?api-version={_API_VERSION}",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=definition,
        timeout=60.0,
    )
    response.raise_for_status()
