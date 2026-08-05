"""AIProjectClient factory — keyless auth via DefaultAzureCredential (az login)."""
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from .config import settings


def project_client() -> AIProjectClient:
    return AIProjectClient(
        endpoint=settings().require("PROJECT_ENDPOINT"),
        credential=DefaultAzureCredential()
    )
