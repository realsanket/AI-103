"""Shared local validation and v4.0 GA client helpers for Document Intelligence."""
from __future__ import annotations

from urllib.parse import urlparse

from _shared.config import env

API_VERSION = "2024-11-30"


def configured(name: str) -> str:
    return env(name)


def https_url(value: str, name: str) -> str:
    parsed = urlparse(value)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or parsed.fragment
    ):
        raise ValueError(f"{name} must be an HTTPS URL without credentials or a fragment.")
    return value.rstrip("/")


def document_intelligence_endpoint(value: str) -> str:
    endpoint = https_url(value, "DOCUMENT_INTELLIGENCE_ENDPOINT")
    parsed = urlparse(endpoint)
    if parsed.query or parsed.path not in ("", "/"):
        raise ValueError("DOCUMENT_INTELLIGENCE_ENDPOINT must not include a path or query.")
    if not parsed.hostname.endswith(".cognitiveservices.azure.com"):
        raise ValueError(
            "DOCUMENT_INTELLIGENCE_ENDPOINT must use a custom "
            "*.cognitiveservices.azure.com subdomain for Microsoft Entra authentication."
        )
    return endpoint


def source_url(value: str, name: str) -> str:
    return https_url(value, name)


def preflight(model_id: str, source_env: str) -> None:
    endpoint = configured("DOCUMENT_INTELLIGENCE_ENDPOINT")
    source = configured(source_env)
    print("No cloud calls made.")
    print(f"Model: {model_id}; API: v4.0 ({API_VERSION} GA).")
    print(
        "DOCUMENT_INTELLIGENCE_ENDPOINT: "
        + ("configured" if endpoint else "missing")
    )
    print(f"{source_env}: " + ("configured" if source else "missing"))


def analyze(
    model_id: str, document_url: str, *, markdown: bool = False
):
    """Submit one remote analysis only after the caller's --apply gate."""
    from azure.ai.documentintelligence import DocumentIntelligenceClient
    from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
    from azure.identity import DefaultAzureCredential

    endpoint = document_intelligence_endpoint(configured("DOCUMENT_INTELLIGENCE_ENDPOINT"))
    request = AnalyzeDocumentRequest(url_source=source_url(document_url, "document URL"))
    options = {"output_content_format": "markdown"} if markdown else {}
    poller = DocumentIntelligenceClient(endpoint, DefaultAzureCredential()).begin_analyze_document(
        model_id, request, **options
    )
    return poller.result()


def print_fields(result, *, show_values: bool) -> None:
    documents = result.documents or []
    print(f"documents: {len(documents)}")
    for document_number, document in enumerate(documents, start=1):
        fields = document.fields or {}
        print(f"document {document_number} fields: {', '.join(fields) or 'none'}")
        if show_values:
            for name, field in fields.items():
                print(f"  {name}: {getattr(field, 'value', None)!r}")
