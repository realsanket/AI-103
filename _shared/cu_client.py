"""Azure Content Understanding — REST wrapper using httpx + Entra bearer token.

CU is a REST-only surface at time of writing; keep this thin so lessons focus
on the analyzer configuration, not the plumbing.
"""
import time
import httpx
from azure.identity import DefaultAzureCredential
from .config import settings

_SCOPE = "https://cognitiveservices.azure.com/.default"


def _headers() -> dict:
    token = DefaultAzureCredential().get_token(_SCOPE).token
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def _base() -> str:
    s = settings()
    return f"{s.cu_endpoint}/contentunderstanding"


def create_analyzer(analyzer_id: str, definition: dict) -> dict:
    s = settings()
    url = f"{_base()}/analyzers/{analyzer_id}?api-version={s.cu_api_version}"
    r = httpx.put(url, headers=_headers(), json=definition, timeout=60.0)
    r.raise_for_status()
    return r.json() if r.text else {}


def analyze(analyzer_id: str, source_url: str) -> dict:
    """Submit an async analyze job and poll until done."""
    s = settings()
    submit = f"{_base()}/analyzers/{analyzer_id}:analyze?api-version={s.cu_api_version}"
    r = httpx.post(submit, headers=_headers(), json={"url": source_url}, timeout=60.0)
    r.raise_for_status()
    op_url = r.headers.get("Operation-Location")
    if not op_url:
        return r.json()
    while True:
        poll = httpx.get(op_url, headers=_headers(), timeout=30.0)
        poll.raise_for_status()
        body = poll.json()
        status = body.get("status", "").lower()
        if status in ("succeeded", "failed", "canceled"):
            return body
        time.sleep(2)
