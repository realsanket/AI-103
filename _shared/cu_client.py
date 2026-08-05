"""Azure Content Understanding — REST wrapper using httpx + Entra bearer token.

CU is a REST-only surface at time of writing; keep this thin so lessons focus
on the analyzer configuration, not the plumbing.
"""
import time
from urllib.parse import parse_qs, urlsplit

import httpx
from azure.identity import DefaultAzureCredential
from .config import settings

_SCOPE = "https://cognitiveservices.azure.com/.default"
_POLL_INTERVAL_SECONDS = 2.0
_POLL_TIMEOUT_SECONDS = 300.0
_TERMINAL_STATUSES = {"succeeded", "failed", "canceled", "cancelled"}


def _headers() -> dict:
    token = DefaultAzureCredential().get_token(_SCOPE).token
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def _base() -> str:
    s = settings()
    return f"{s.require('CU_ENDPOINT')}/contentunderstanding"


def validate_source_url(source_url: str) -> str:
    """Require an HTTPS URL CU can fetch, validating supplied Blob SAS tokens."""
    if not isinstance(source_url, str):
        raise ValueError("CU input URL must be a string.")
    parsed = urlsplit(source_url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("CU input must be an HTTPS URL without embedded credentials.")
    query = parse_qs(parsed.query, keep_blank_values=True)
    is_blob = parsed.hostname.endswith(".blob.core.windows.net")
    sas_keys = {"sv", "se", "sp", "sig"}
    if is_blob and sas_keys.intersection(query) and any(
        not query.get(key) or not query[key][0] for key in sas_keys
    ):
        raise ValueError("Blob SAS URL must include sv, se, sp, and sig parameters.")
    return source_url


def _operation_url(operation_url: str) -> str:
    endpoint = urlsplit(settings().require("CU_ENDPOINT"))
    operation = urlsplit(operation_url)
    if operation.scheme != "https" or operation.netloc != endpoint.netloc:
        raise RuntimeError("CU returned an Operation-Location outside the configured endpoint.")
    return operation_url


def result_diagnostic(result: dict) -> str:
    """Return a useful terminal-status diagnostic without exposing request URLs."""
    error = result.get("error") or result.get("failureReason") or result.get("failure_reason")
    if isinstance(error, dict):
        return str(error.get("message") or error.get("code") or error)
    return str(error or "No service diagnostic returned.")


def create_analyzer(analyzer_id: str, definition: dict) -> dict:
    s = settings()
    url = f"{_base()}/analyzers/{analyzer_id}?api-version={s.cu_api_version}"
    r = httpx.put(url, headers=_headers(), json=definition, timeout=60.0)
    r.raise_for_status()
    return r.json() if r.text else {}


def analyze(
    analyzer_id: str,
    source_urls: str | list[str],
    *,
    poll_timeout: float = _POLL_TIMEOUT_SECONDS,
    poll_interval: float = _POLL_INTERVAL_SECONDS,
) -> dict:
    """Submit an async analyze job and poll until done."""
    s = settings()
    if isinstance(source_urls, str):
        source_urls = [source_urls]
    if len(source_urls) != 1:
        raise ValueError("CU API version 2025-11-01 accepts exactly one source URL.")
    source_url = validate_source_url(source_urls[0])
    if poll_timeout <= 0 or poll_interval <= 0:
        raise ValueError("poll_timeout and poll_interval must be greater than zero.")
    submit = f"{_base()}/analyzers/{analyzer_id}:analyze?api-version={s.cu_api_version}"
    r = httpx.post(
        submit,
        headers=_headers(),
        json={"inputs": [{"url": source_url}]},
        timeout=60.0,
    )
    r.raise_for_status()
    op_url = r.headers.get("Operation-Location")
    if not op_url:
        return r.json()
    op_url = _operation_url(op_url)
    deadline = time.monotonic() + poll_timeout
    while True:
        poll = httpx.get(op_url, headers=_headers(), timeout=30.0)
        poll.raise_for_status()
        body = poll.json()
        status = str(body.get("status") or "").lower()
        if status in _TERMINAL_STATUSES:
            return body
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError(
                f"CU analysis did not finish within {poll_timeout:g}s; "
                f"last status: {status or 'unknown'}."
            )
        time.sleep(min(poll_interval, remaining))
