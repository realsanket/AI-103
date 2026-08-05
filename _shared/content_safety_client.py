"""Azure Content Safety — text/image analyze + blocklist clients (keyless)."""
import json

from azure.ai.contentsafety import BlocklistClient, ContentSafetyClient
from azure.core.rest import HttpRequest
from azure.identity import DefaultAzureCredential
from .config import settings


def content_safety_client() -> ContentSafetyClient:
    return ContentSafetyClient(
        endpoint=settings().require("CONTENT_SAFETY_ENDPOINT"),
        credential=DefaultAzureCredential(),
    )


def blocklist_client() -> BlocklistClient:
    return BlocklistClient(
        endpoint=settings().require("CONTENT_SAFETY_ENDPOINT"),
        credential=DefaultAzureCredential(),
    )


def shield_prompt(
    client: ContentSafetyClient, endpoint: str, user_prompt: str, documents: list[str]
) -> dict:
    """Call Prompt Shields with documented input limits before sending content."""
    if len(user_prompt) > 10_000:
        raise ValueError("Prompt Shields userPrompt is limited to 10,000 characters.")
    if len(documents) > 5 or sum(map(len, documents)) > 10_000:
        raise ValueError(
            "Prompt Shields accepts at most five documents and 10,000 total characters."
        )

    request = HttpRequest(
        method="POST",
        url=f"{endpoint}/contentsafety/text:shieldPrompt?api-version=2024-09-01",
        headers={"Content-Type": "application/json"},
        content=json.dumps({"userPrompt": user_prompt, "documents": documents}).encode(),
    )
    return client.send_request(request).json()
