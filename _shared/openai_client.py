"""OpenAI client pointing at Foundry — keyless via Entra bearer token.

Uses OpenAI Python SDK against Foundry `/openai/v1` surface. This is the same
Responses API the Foundry Agent Service exposes; keeps sample code portable
between direct model calls and agent turns.
"""
from openai import OpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from .config import settings

_SCOPE = "https://cognitiveservices.azure.com/.default"


def openai_client() -> OpenAI:
    token_provider = get_bearer_token_provider(DefaultAzureCredential(), _SCOPE)
    return OpenAI(
        base_url=f"{settings().foundry_endpoint}/openai/v1",
        api_key=token_provider(),
    )
