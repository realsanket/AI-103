"""Single source of truth for endpoints/deployment names. Loads .env once."""
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import os
from dotenv import load_dotenv

_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_ENV_FILE)


@dataclass(frozen=True)
class Settings:
    # Foundry / models
    foundry_endpoint: str
    project_endpoint: str
    default_model: str
    reasoning_model: str
    image_model: str
    video_model: str
    embedding_model: str
    model_router_deployment: str
    # Search
    search_endpoint: str
    search_index: str
    search_index_vector: str
    search_indexer: str
    search_skillset: str
    # Language
    language_endpoint: str
    language_mcp_url: str
    # Translator
    translator_endpoint: str
    translator_api_version: str
    # Speech
    speech_region: str
    speech_endpoint: str
    speech_mcp_url: str
    voice_live_endpoint: str
    # Content Understanding
    cu_endpoint: str
    cu_api_version: str
    # Storage
    storage_account: str
    storage_container: str
    storage_connection_string: str
    # Observability
    app_insights_connection_string: str
    # Content Safety
    content_safety_endpoint: str


def _req(key: str) -> str:
    v = os.environ.get(key)
    if not v or v.startswith("<"):
        raise RuntimeError(
            f"Missing env var {key}. Copy .env.example to .env and fill it in."
        )
    return v


def _opt(key: str, default: str = "") -> str:
    v = os.environ.get(key, default)
    return "" if v.startswith("<") else v


@lru_cache
def settings() -> Settings:
    return Settings(
        foundry_endpoint=_req("FOUNDRY_ENDPOINT"),
        project_endpoint=_req("PROJECT_ENDPOINT"),
        default_model=_opt("DEFAULT_MODEL", "gpt-4.1-mini"),
        reasoning_model=_opt("REASONING_MODEL", "o4-mini"),
        image_model=_opt("IMAGE_MODEL", "gpt-image-1"),
        video_model=_opt("VIDEO_MODEL", "sora"),
        embedding_model=_opt("EMBEDDING_MODEL", "text-embedding-3-large"),
        model_router_deployment=_opt("MODEL_ROUTER_DEPLOYMENT", "model-router"),
        search_endpoint=_opt("SEARCH_ENDPOINT"),
        search_index=_opt("SEARCH_INDEX", "cloudxeus-docs"),
        search_index_vector=_opt("SEARCH_INDEX_VECTOR", "cloudxeus-docs-vector"),
        search_indexer=_opt("SEARCH_INDEXER", "cloudxeus-indexer"),
        search_skillset=_opt("SEARCH_SKILLSET", "cloudxeus-skillset"),
        language_endpoint=_opt("LANGUAGE_ENDPOINT"),
        language_mcp_url=_opt("LANGUAGE_MCP_URL"),
        translator_endpoint=_opt("TRANSLATOR_ENDPOINT"),
        translator_api_version=_opt("TRANSLATOR_API_VERSION", "2025-10-01-preview"),
        speech_region=_opt("SPEECH_REGION", "eastus"),
        speech_endpoint=_opt("SPEECH_ENDPOINT"),
        speech_mcp_url=_opt("SPEECH_MCP_URL"),
        voice_live_endpoint=_opt("VOICE_LIVE_ENDPOINT"),
        cu_endpoint=_opt("CU_ENDPOINT"),
        cu_api_version=_opt("CU_API_VERSION", "2025-11-15-preview"),
        storage_account=_opt("STORAGE_ACCOUNT"),
        storage_container=_opt("STORAGE_CONTAINER", "cloudxeus-docs"),
        storage_connection_string=_opt("STORAGE_CONNECTION_STRING"),
        app_insights_connection_string=_opt("APPLICATIONINSIGHTS_CONNECTION_STRING"),
        content_safety_endpoint=_opt("CONTENT_SAFETY_ENDPOINT"),
    )


# Convenience path for sample data — every lesson can `from _shared.config import SAMPLE_DATA`
SAMPLE_DATA = Path(__file__).resolve().parent / "sample_data"
