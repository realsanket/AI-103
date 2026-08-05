"""Blob, SAS, and identity preflight for Content Understanding visual inputs.

Run without flags for a local-only check. Content Understanding retrieves source
media server-side, so a local path cannot be analyzed. Pass a short-lived,
read-only Blob SAS with --source-url when preparing a real request; this lesson
never prints the query string or makes an Azure request.
"""
import argparse
from urllib.parse import parse_qs, urlsplit

from _shared.config import settings


def source_metadata(source_url: str) -> dict[str, str]:
    """Return provenance useful for handoff without exposing SAS parameters."""
    parsed = urlsplit(source_url)
    parts = [part for part in parsed.path.split("/") if part]
    return {
        "scheme": parsed.scheme,
        "host": parsed.netloc,
        "container": parts[0] if parts else "",
        "blob_path": "/".join(parts[1:]),
    }


def validate_source_url(source_url: str) -> list[str]:
    """Report locally detectable source-access problems without logging its SAS."""
    parsed = urlsplit(source_url)
    sas = parse_qs(parsed.query)
    warnings = []
    if parsed.scheme != "https":
        warnings.append("Source URL must use HTTPS; CU cannot fetch local file paths.")
    if not parsed.netloc.endswith(".blob.core.windows.net"):
        warnings.append("Use an Azure Blob URL for production source storage and retention control.")
    if "sig" not in sas:
        warnings.append("No SAS signature detected; verify the blob is intentionally reachable by CU.")
    elif "r" not in sas.get("sp", [""])[0]:
        warnings.append("SAS lacks read permission (`sp=r`); CU needs read access to the source blob.")
    if "se" not in sas:
        warnings.append("SAS has no expiry (`se`); use a short-lived SAS.")
    return warnings


def preflight(source_url: str = "") -> dict[str, object]:
    current = settings()
    return {
        "storage_account_configured": bool(current.storage_account),
        "storage_container_configured": bool(current.storage_container),
        "cu_endpoint_configured": bool(current.cu_endpoint),
        "source_supplied": bool(source_url),
        "source": source_metadata(source_url) if source_url else None,
        "warnings": validate_source_url(source_url) if source_url else [],
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Prepare secure Blob media for Content Understanding.")
    parser.add_argument("--source-url", default="", help="HTTPS Blob URL; SAS is never printed.")
    args = parser.parse_args(argv)

    checks = preflight(args.source_url)
    print("Blob / SAS / managed-identity preflight (local only; no cloud calls made)")
    for name in ("storage_account_configured", "storage_container_configured", "cu_endpoint_configured"):
        print(f"- {name}: {'configured' if checks[name] else 'missing'}")
    if checks["source"]:
        source = checks["source"]
        print(f"- source: {source['host']}/{source['container']}/{source['blob_path']}")
    else:
        print("- source: supply --source-url before an analysis handoff.")
    for warning in checks["warnings"]:
        print(f"- warning: {warning}")
    print(
        "Identity: use DefaultAzureCredential for upload/inspection, not account keys or connection "
        "strings. Assign uploader Storage Blob Data Contributor and runtime Storage Blob Data Reader "
        "at the narrowest container scope; verify CU and Blob private-network DNS/egress separately."
    )
    print("Handoff: pass a short-lived read-only Blob SAS to lesson 15; do not log, commit, or reuse it.")


if __name__ == "__main__":
    main()
