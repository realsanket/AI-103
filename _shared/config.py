"""Single source of truth for endpoints/deployment names. Loads .env once."""
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import json
import os
from dotenv import load_dotenv

_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_ENV_FILE)


@dataclass(frozen=True)
class Settings:
    # Foundry / models
    foundry_endpoint: str
    azure_openai_endpoint: str
    project_endpoint: str
    default_model: str
    reasoning_model: str
    image_model: str
    video_model: str
    embedding_model: str
    model_router_deployment: str
    deployment_name: str
    deployment_model_name: str
    deployment_model_version: str
    # Search
    search_endpoint: str
    search_index: str
    search_index_vector: str
    search_indexer: str
    search_skillset: str
    # Language
    language_endpoint: str
    language_mcp_url: str
    translator_resource_id: str
    # Speech
    speech_region: str
    speech_endpoint: str
    speech_mcp_url: str
    voice_live_endpoint: str
    custom_speech_endpoint_id: str
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
    provenance_source_url: str
    # RBAC / resource identifiers
    azure_subscription_id: str
    azure_resource_group: str

    def require(self, env_var: str) -> str:
        value = getattr(self, env_var.lower())
        if value:
            return value
        raise RuntimeError(
            f"Missing env var {env_var}. Copy .env.example to .env and fill it in."
        )


def to_plain_dict(value) -> dict:
    """Normalize SDK model objects/mappings into plain dicts for printing."""
    if value is None:
        return {}
    if isinstance(value, dict):
        return value
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if hasattr(value, "to_dict"):
        return value.to_dict()
    try:
        return dict(value)
    except Exception:
        return {}


def format_content_filter_summary(result: dict, indent: str = "  ") -> str:
    """Return a readable multi-line summary for content-filter details."""
    if not result:
        return f"{indent}No content filter details returned."

    ordered = ["violence", "hate", "sexual", "self_harm", "jailbreak"]
    keys = ordered + sorted(k for k in result.keys() if k not in ordered)
    lines = [f"{indent}Content filter summary:"]

    for key in keys:
        details = result.get(key)
        if not details:
            continue
        if not isinstance(details, dict):
            lines.append(f"{indent}  - {key:<10}: {details}")
            continue

        severity = details.get("severity", "n/a")
        filtered = details.get("filtered", "n/a")
        detected = details.get("detected", "n/a")
        line = (
            f"{indent}  - {key:<10} severity={severity:<6} "
            f"filtered={str(filtered):<5} detected={str(detected):<5}"
        )
        lines.append(line)

    return "\n".join(lines)


def preview_text(text: str, max_len: int = 180) -> str:
    """Normalize whitespace and truncate long user-visible text for console output."""
    cleaned = " ".join(str(text).split())
    return cleaned if len(cleaned) <= max_len else cleaned[: max_len - 3] + "..."


def format_json_preview(value, indent: str = "  ", max_chars: int = 1000) -> str:
    """Return compact pretty JSON text with indentation and optional truncation."""
    payload = json.dumps(value, indent=2, ensure_ascii=True)
    if max_chars > 0 and len(payload) > max_chars:
        payload = payload[:max_chars] + "..."
    return "\n".join(f"{indent}{line}" for line in payload.splitlines())


def format_hit_categories(
    sub_categories: list[dict], field: str, limit: int = 10
) -> str:
    """List sub-category names where a boolean field is true."""
    hits = [s.get("sub_category", "unknown") for s in sub_categories if s.get(field)]
    if not hits:
        return "none"
    shown = ", ".join(hits[:limit])
    more = len(hits) - limit
    return f"{shown} (+{more} more)" if more > 0 else shown


def _opt(key: str, default: str = "") -> str:
    v = os.environ.get(key, default)
    return "" if v.startswith("<") else v


@lru_cache
def settings() -> Settings:
    return Settings(
        foundry_endpoint=_opt("FOUNDRY_ENDPOINT").rstrip("/"),
        azure_openai_endpoint=_opt("AZURE_OPENAI_ENDPOINT").rstrip("/"),
        project_endpoint=_opt("PROJECT_ENDPOINT"),
        default_model=_opt("DEFAULT_MODEL", "gpt-4.1-mini"),
        reasoning_model=_opt("REASONING_MODEL", "o4-mini"),
        image_model=_opt("IMAGE_MODEL", "gpt-image-1"),
        video_model=_opt("VIDEO_MODEL", "sora"),
        embedding_model=_opt("EMBEDDING_MODEL", "text-embedding-3-large"),
        model_router_deployment=_opt("MODEL_ROUTER_DEPLOYMENT", "model-router"),
        deployment_name=_opt("DEPLOYMENT_NAME"),
        deployment_model_name=_opt("DEPLOYMENT_MODEL_NAME"),
        deployment_model_version=_opt("DEPLOYMENT_MODEL_VERSION"),
        search_endpoint=_opt("SEARCH_ENDPOINT"),
        search_index=_opt("SEARCH_INDEX", "northwind-docs"),
        search_index_vector=_opt("SEARCH_INDEX_VECTOR", "northwind-docs-vector"),
        search_indexer=_opt("SEARCH_INDEXER", "northwind-indexer"),
        search_skillset=_opt("SEARCH_SKILLSET", "northwind-skillset"),
        language_endpoint=_opt("LANGUAGE_ENDPOINT"),
        language_mcp_url=_opt("LANGUAGE_MCP_URL"),
        translator_resource_id=_opt("TRANSLATOR_RESOURCE_ID"),
        speech_region=_opt("SPEECH_REGION", "eastus"),
        speech_endpoint=_opt("SPEECH_ENDPOINT"),
        speech_mcp_url=_opt("SPEECH_MCP_URL"),
        voice_live_endpoint=_opt("VOICE_LIVE_ENDPOINT"),
        custom_speech_endpoint_id=_opt("CUSTOM_SPEECH_ENDPOINT_ID"),
        cu_endpoint=_opt("CU_ENDPOINT"),
        cu_api_version=_opt("CU_API_VERSION", "2025-11-01"),
        storage_account=_opt("STORAGE_ACCOUNT"),
        storage_container=_opt("STORAGE_CONTAINER", "northwind-docs"),
        storage_connection_string=_opt("STORAGE_CONNECTION_STRING"),
        app_insights_connection_string=_opt("APPLICATIONINSIGHTS_CONNECTION_STRING"),
        content_safety_endpoint=_opt("CONTENT_SAFETY_ENDPOINT"),
        provenance_source_url=_opt("PROVENANCE_SOURCE_URL"),
        azure_subscription_id=_opt("AZURE_SUBSCRIPTION_ID"),
        azure_resource_group=_opt("AZURE_RESOURCE_GROUP"),
    )


# Convenience path for sample data — every lesson can `from _shared.config import SAMPLE_DATA`
SAMPLE_DATA = Path(__file__).resolve().parent / "sample_data"


# ---------------------------------------------------------------------------
# Per-lesson override helpers — reusable across all lessons
# ---------------------------------------------------------------------------

def add_lesson_overrides(parser) -> None:
    """Add --project-endpoint, --api-key, --chat-model, --embedding-model to any argparse parser.

    Lessons that need to target a different Foundry project or model deployment
    (e.g. testing a preview feature in a specific region) call this once and then
    pass args to resolve_models() and _shared.foundry_client.resolve_project_client().

    --api-key uses AzureKeyCredential instead of DefaultAzureCredential. Useful when
    server-side LROs (e.g. begin_update_memories) need key-based auth to call the model.
    """
    parser.add_argument(
        "--project-endpoint",
        default=None,
        metavar="URL",
        help="Override PROJECT_ENDPOINT for this run only "
             "(falls back to PROJECT_ENDPOINT env var).",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        metavar="KEY",
        help="Use AzureKeyCredential instead of DefaultAzureCredential. "
             "Pass the resource API key shown in the Foundry portal. "
             "Never commit this value — pass via shell only.",
    )
    parser.add_argument(
        "--chat-model",
        default=None,
        metavar="DEPLOYMENT",
        help="Override chat deployment name (falls back to DEFAULT_MODEL env var).",
    )
    parser.add_argument(
        "--embedding-model",
        default=None,
        metavar="DEPLOYMENT",
        help="Override embedding deployment name (falls back to EMBEDDING_MODEL env var).",
    )


def resolve_models(args) -> tuple[str, str]:
    """Return (chat_model, embedding_model) from CLI args with settings() fallback.

    Args:
        args: argparse.Namespace produced after calling add_lesson_overrides(parser).

    Returns:
        (chat_model, embedding_model) — never empty strings; raises if fallback also unset.
    """
    s = settings()
    chat = getattr(args, "chat_model", None) or s.default_model
    embed = getattr(args, "embedding_model", None) or s.embedding_model
    return chat, embed
