"""Azure Content Safety — text/image analyze + blocklist clients (keyless)."""
from azure.ai.contentsafety import BlocklistClient, ContentSafetyClient
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
