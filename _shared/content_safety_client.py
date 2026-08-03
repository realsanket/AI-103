"""Azure Content Safety — text + image analyze client (keyless)."""
from azure.ai.contentsafety import ContentSafetyClient
from azure.identity import DefaultAzureCredential
from .config import settings


def content_safety_client() -> ContentSafetyClient:
    return ContentSafetyClient(
        endpoint=settings().content_safety_endpoint,
        credential=DefaultAzureCredential(),
    )
