"""OpenAI client pointing at Azure OpenAI — keyless via Entra bearer token.

Uses AZURE_OPENAI_ENDPOINT (openai.azure.com subdomain), NOT the Foundry
services.ai.azure.com endpoint. The two subdomains serve different SDKs:
  - openai.azure.com  → OpenAI Python SDK (Chat Completions, Responses, Embeddings)
  - services.ai.azure.com → Foundry SDK (agents, projects, connections)
"""
from openai import OpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from .config import settings

_SCOPE = "https://cognitiveservices.azure.com/.default"


def openai_client() -> OpenAI:
    token_provider = get_bearer_token_provider(DefaultAzureCredential(), _SCOPE)
    return OpenAI(
        base_url=f"{settings().azure_openai_endpoint}/openai/v1",
        api_key=token_provider(),
    )
