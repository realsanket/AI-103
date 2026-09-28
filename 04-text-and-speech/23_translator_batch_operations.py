# Run: uv run python 04-text-and-speech/23_translator_batch_operations.py [--apply ...]
"""Submit, inspect, or cancel Document Translation batches with explicit apply.

Default execution is local-only. `--apply` is required before any request.
Document Translation API version 2026-03-01 requires its documented resource
key, supplied only at runtime through `TRANSLATOR_DOCUMENT_KEY` (or
`--key-env`); this lesson never prints it, source SAS, or target SAS.

Source and target are short-lived HTTPS Blob SAS URLs. Every target container
must be unique for a batch. Submitted output is billable and completed output
remains in Blob Storage, so apply lifecycle, access, retention, and human
review controls before submission.
"""
import argparse
import os
from urllib.parse import parse_qs, urlsplit

import httpx

from _shared.config import load_env

_API_VERSION = "2026-03-01"
_TERMINAL = {"Succeeded", "Failed", "Cancelled", "ValidationFailed"}


def _blob_sas(url: str, role: str) -> str:
    parsed = urlsplit(url)
    permissions = parse_qs(parsed.query).get("sp", [""])[0]
    if parsed.scheme != "https" or not parsed.hostname or "sig" not in parse_qs(parsed.query):
        raise SystemExit(f"{role} must be an HTTPS Blob SAS URL.")
    required = {"r", "l"} if role == "source" else {"w", "l"}
    if missing := required.difference(permissions):
        names = " and ".join({"r": "read", "w": "write", "l": "list"}[permission]
                             for permission in sorted(missing))
        raise SystemExit(f"{role} SAS must include {names} permission(s).")
    return url


def endpoint_url(endpoint: str) -> str:
    parsed = urlsplit(endpoint)
    if parsed.scheme != "https" or not parsed.hostname:
        raise SystemExit("--endpoint must be an HTTPS Translator resource endpoint.")
    return endpoint.rstrip("/")


def batch_payload(source_url: str, target_url: str, language: str) -> dict:
    return {
        "inputs": [
            {
                "source": {"sourceUrl": source_url},
                "targets": [{"targetUrl": target_url, "language": language}],
            }
        ]
    }


def _headers(key: str, content: bool = False) -> dict[str, str]:
    headers = {"Ocp-Apim-Subscription-Key": key}
    if content:
        headers["Content-Type"] = "application/json"
    return headers


def submit(endpoint: str, key: str, source_url: str, target_url: str, language: str) -> str:
    response = httpx.post(
        f"{endpoint_url(endpoint)}/translator/document/batches",
        params={"api-version": _API_VERSION},
        headers=_headers(key, content=True),
        json=batch_payload(_blob_sas(source_url, "source"), _blob_sas(target_url, "target"), language),
        timeout=60.0,
    )
    response.raise_for_status()
    operation_url = response.headers.get("operation-location")
    if not operation_url:
        raise RuntimeError("Batch accepted without an operation-location header.")
    return operation_url


def operation(endpoint: str, key: str, operation_url: str, cancel: bool) -> dict:
    resource = urlsplit(endpoint_url(endpoint))
    parsed = urlsplit(operation_url)
    if parsed.scheme != "https" or parsed.netloc != resource.netloc:
        raise SystemExit("--operation-url must be the HTTPS operation-location from this Translator endpoint.")
    response = (httpx.delete if cancel else httpx.get)(
        operation_url,
        headers=_headers(key),
        timeout=30.0,
    )
    response.raise_for_status()
    return response.json()


def preflight() -> None:
    print("Translator batch preflight. No cloud calls made.")
    print("Required for --apply: HTTPS Translator endpoint, short-lived source/target Blob SAS URLs, runtime key.")
    print("Submit: --apply --endpoint URL --source-url SAS --target-url SAS --language fr")
    print("Inspect/cancel: --apply --endpoint URL --operation-url URL [--cancel]")
    print("Do not log SAS or keys. Monitor terminal status: " + ", ".join(sorted(_TERMINAL)) + ".")


def main(argv: list[str] | None = None) -> None:
    load_env()
    parser = argparse.ArgumentParser(description="Apply reviewed Document Translation batch operations.")
    parser.add_argument("--apply", action="store_true", help="Perform one cloud batch operation.")
    parser.add_argument("--endpoint", help="HTTPS Translator resource endpoint.")
    parser.add_argument("--source-url", help="Short-lived read/list Blob SAS URL.")
    parser.add_argument("--target-url", help="Short-lived write/list Blob SAS URL.")
    parser.add_argument("--language", default="fr")
    parser.add_argument("--operation-url", help="Operation-location returned by a prior submission.")
    parser.add_argument("--cancel", action="store_true", help="Cancel the supplied non-terminal operation.")
    parser.add_argument("--key-env", default="TRANSLATOR_DOCUMENT_KEY")
    args = parser.parse_args(argv)
    if not args.apply:
        preflight()
        return
    if not args.endpoint:
        parser.error("--endpoint is required with --apply.")
    key = os.environ.get(args.key_env)
    if not key:
        parser.error(f"Set {args.key_env} only in the runtime environment.")
    if args.operation_url:
        result = operation(args.endpoint, key, args.operation_url, args.cancel)
        print(f"Operation status: {result.get('status', '<unknown>')}")
        return
    if args.cancel:
        parser.error("--cancel requires --operation-url.")
    if not args.source_url or not args.target_url:
        parser.error("--source-url and --target-url are required to submit.")
    print("Batch submitted. Save operation-location securely:", submit(
        args.endpoint, key, args.source_url, args.target_url, args.language
    ))


if __name__ == "__main__":
    main()
