# Run: uv run python 05-information-extraction/16_cu_multimodal_rag.py [--apply --source <url>]
# Practice-question coverage: Q120, Q146.
"""CU multimodal extraction → bounded provenance-safe RAG records (preflight by default).

Selects the right prebuilt CU analyzer by file extension (prebuilt-layout for docs,
prebuilt-imageSearch for images, prebuilt-videoSearch for video) and converts the
CU result into bounded records ready for an ingestion worker. Records cap at 20 items
and 4,000 chars each; SAS query credentials are stripped from source metadata to
avoid leaking signed URLs in output.

Default run: local preflight (no cloud call). `--apply` submits the HTTPS source URL
to CU and prints records. This lesson deliberately does NOT upload records to Search —
add a validated ingestion worker that generates vectors and provenance fields.

Code path:
  analyzer_for(url) → choose analyzer by extension. source_metadata(url) → strip SAS.
  With --apply: analyze(analyzer, url) → poll → cap records → print JSON.

What to watch. Preflight: config checks. With --apply: JSON records with chunk, title,
source, and CU-extracted content. Extension determines analyzer — rename a PDF to .jpg
to see imageSearch chosen instead.

Prerequisites / env vars:
  CU_ENDPOINT  — https://<resource>.services.ai.azure.com
  CU_API_VERSION — 2025-11-01 (GA)
  --apply      — required for cloud call
  --source     — HTTPS URL to the document/image/video (required with --apply)
"""
import argparse
import json
from pathlib import PurePosixPath
from urllib.parse import urlsplit

from _shared.config import settings
from _shared.cu_client import analyze

_IMAGE_TYPES = {".avif", ".bmp", ".gif", ".heic", ".jpeg", ".jpg", ".png", ".tif", ".tiff", ".webp"}
_VIDEO_TYPES = {".avi", ".m4v", ".mkv", ".mov", ".mp4", ".mpeg", ".mpg", ".webm"}


def analyzer_for(source_url: str) -> str:
    """Choose a documented prebuilt analyzer from the Blob extension."""
    suffix = PurePosixPath(urlsplit(source_url).path).suffix.lower()
    if suffix in _IMAGE_TYPES:
        return "prebuilt-imageSearch"
    if suffix in _VIDEO_TYPES:
        return "prebuilt-videoSearch"
    return "prebuilt-layout"


def source_metadata(source_url: str) -> dict[str, str]:
    """Retain provenance while excluding SAS query credentials."""
    parsed = urlsplit(source_url)
    parts = [part for part in parsed.path.split("/") if part]
    return {
        "host": parsed.netloc,
        "container": parts[0] if parts else "",
        "blob_path": "/".join(parts[1:]),
        "media_type": PurePosixPath(parsed.path).suffix.lower().lstrip("."),
    }


def rag_records(result: dict, analyzer: str, source_url: str, limit: int = 20) -> list[dict[str, object]]:
    """Normalize CU output to bounded, source-grounded records for later ingestion."""
    payload = result.get("result", {})
    contents = payload.get("contents", []) if isinstance(payload, dict) else []
    if not isinstance(contents, list):
        return []
    records = []
    for number, content in enumerate(contents[: max(0, min(limit, 20))]):
        if not isinstance(content, dict):
            continue
        text = content.get("markdown") or content.get("text") or ""
        if not isinstance(text, str) or not text.strip():
            continue
        records.append(
            {
                "id": str(number),
                "content": text.strip()[:4_000],
                "analyzer": analyzer,
                "source": source_metadata(source_url),
                "start_ms": content.get("startTimeMs"),
                "end_ms": content.get("endTimeMs"),
            }
        )
    return records


def preflight(source_url: str = "") -> dict[str, object]:
    return {
        "cu_endpoint_configured": bool(settings().cu_endpoint),
        "search_endpoint_configured": bool(settings().search_endpoint),
        "source_supplied": bool(source_url),
        "analyzer": analyzer_for(source_url) if source_url else "",
    }


def apply(source_url: str) -> list[dict[str, object]]:
    if urlsplit(source_url).scheme != "https":
        raise SystemExit("--source-url must be an HTTPS Blob URL; never use a local path.")
    analyzer = analyzer_for(source_url)
    return rag_records(analyze(analyzer, source_url), analyzer, source_url)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Prepare multimodal CU output for RAG ingestion.")
    parser.add_argument("--source-url", default="", help="HTTPS Blob URL; query credentials are not printed.")
    parser.add_argument("--apply", action="store_true", help="Submit one source to Content Understanding.")
    args = parser.parse_args(argv)
    if not args.apply:
        checks = preflight(args.source_url)
        print("Multimodal CU-to-RAG preflight. No cloud calls made.")
        print(f"- cu_endpoint_configured: {checks['cu_endpoint_configured']}")
        print(f"- analyzer: {checks['analyzer'] or 'selects after --source-url is supplied'}")
        print("- --apply emits at most 20 records of 4,000 characters; review and ingest them separately.")
        return
    if not args.source_url:
        parser.error("--source-url is required with --apply.")
    print(json.dumps(apply(args.source_url), indent=2))


if __name__ == "__main__":
    main()
