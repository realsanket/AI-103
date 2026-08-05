"""OpenAI client pointing at Azure OpenAI — keyless via Entra bearer token.

Uses AZURE_OPENAI_ENDPOINT (openai.azure.com subdomain), NOT the Foundry
services.ai.azure.com endpoint. The two subdomains serve different SDKs:
  - openai.azure.com  → OpenAI Python SDK (Chat Completions, Responses, Embeddings)
  - services.ai.azure.com → Foundry SDK (agents, projects, connections)
"""
from openai import OpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from .config import settings

_SCOPE = "https://ai.azure.com/.default"


def azure_openai_token_provider():
    """Return a callable that obtains a fresh Entra token for Azure OpenAI."""
    return get_bearer_token_provider(DefaultAzureCredential(), _SCOPE)


def openai_client() -> OpenAI:
    return OpenAI(
        base_url=f"{settings().require('AZURE_OPENAI_ENDPOINT')}/openai/v1",
        api_key=azure_openai_token_provider(),
    )
