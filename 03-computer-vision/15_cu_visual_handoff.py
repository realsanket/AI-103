"""Normalize Content Understanding visual output for a bounded production handoff.

Run without --apply for a no-cloud preflight. With --apply, submit one HTTPS
source to the selected prebuilt analyzer, then emit only bounded summaries,
warnings, time segments, and SAS-free source metadata.
"""
import argparse
import json
import re
from pathlib import PurePosixPath
from urllib.parse import urlsplit

from _shared.config import settings
from _shared.cu_client import analyze

_IMAGE_SUFFIXES = {".avif", ".bmp", ".gif", ".heic", ".jpeg", ".jpg", ".png", ".tif", ".tiff", ".webp"}
_VIDEO_SUFFIXES = {".avi", ".m4v", ".mkv", ".mov", ".mp4", ".mpeg", ".mpg", ".webm"}
_SECRET_QUERY_VALUE = re.compile(
    r"(?i)\b(sig|se|sp|sv|skoid|sktid|skt|ske|sks|skv|token|key)=([^&\s]+)"
)


def select_analyzer(source_url: str) -> str:
    """Select a visual prebuilt analyzer from the source extension."""
    suffix = PurePosixPath(urlsplit(source_url).path).suffix.lower()
    if suffix in _IMAGE_SUFFIXES:
        return "prebuilt-imageSearch"
    if suffix in _VIDEO_SUFFIXES:
        return "prebuilt-videoSearch"
    raise ValueError(f"Unsupported visual source extension {suffix or '<none>'}; use an image or video URL.")


def source_metadata(source_url: str) -> dict[str, str]:
    """Keep provenance fields while deliberately dropping query credentials."""
    parsed = urlsplit(source_url)
    parts = [part for part in parsed.path.split("/") if part]
    return {
        "scheme": parsed.scheme,
        "host": parsed.netloc,
        "container": parts[0] if parts else "",
        "blob_path": "/".join(parts[1:]),
        "media_type": PurePosixPath(parsed.path).suffix.lower().lstrip("."),
    }


def _bounded_text(value: object, limit: int = 400) -> str:
    if not isinstance(value, str):
        return ""
    text = _SECRET_QUERY_VALUE.sub(r"\1=REDACTED", value).strip()
    return text[:limit]


def _warning_text(warning: object) -> str:
    if isinstance(warning, dict):
        warning = warning.get("message") or warning.get("code") or ""
    return _bounded_text(warning, 240)


def _list(value: object) -> list:
    return value if isinstance(value, list) else []


def _summary(content: dict) -> tuple[str, str]:
    fields = content.get("fields", {})
    if not isinstance(fields, dict):
        return "", ""
    field = fields.get("Summary") or fields.get("summary") or {}
    if not isinstance(field, dict):
        return "", ""
    return _bounded_text(field.get("valueString") or field.get("value")), _bounded_text(
        field.get("source"), 240
    )


def normalize_result(
    result: dict, analyzer: str, source_url: str, max_segments: int = 20
) -> dict[str, object]:
    """Keep a small, stable payload instead of forwarding opaque CU response JSON."""
    payload = result.get("result", {})
    if not isinstance(payload, dict):
        payload = {}
    contents = payload.get("contents", [])
    if not isinstance(contents, list):
        contents = []
    warnings = [
        text
        for warning in [*_list(result.get("warnings")), *_list(payload.get("warnings"))]
        if (text := _warning_text(warning))
    ][:10]
    segments = []
    segment_limit = max(0, min(max_segments, 20))
    for index, content in enumerate(contents[:segment_limit]):
        if not isinstance(content, dict):
            continue
        summary, field_source = _summary(content)
        segments.append(
            {
                "index": index,
                "start_ms": content.get("startTimeMs"),
                "end_ms": content.get("endTimeMs"),
                "summary": summary or _bounded_text(content.get("markdown")),
                "source": field_source,
            }
        )
    return {
        "status": _bounded_text(result.get("status"), 80),
        "analyzer": analyzer,
        "source": source_metadata(source_url),
        "warnings": warnings,
        "segments": segments,
        "segments_truncated": len(contents) > segment_limit,
    }


def preflight(source_url: str = "") -> dict[str, object]:
    analyzer = select_analyzer(source_url) if source_url else ""
    return {
        "cu_endpoint_configured": bool(settings().cu_endpoint),
        "source_supplied": bool(source_url),
        "analyzer": analyzer,
        "source": source_metadata(source_url) if source_url else None,
    }


def production_handoff(source_url: str) -> dict[str, object]:
    if urlsplit(source_url).scheme != "https":
        raise ValueError("Source URL must use HTTPS.")
    analyzer = select_analyzer(source_url)
    return normalize_result(analyze(analyzer, source_url), analyzer, source_url)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Preflight or run a bounded CU visual handoff.")
    parser.add_argument("--source-url", default="", help="HTTPS Blob SAS URL; never printed.")
    parser.add_argument("--apply", action="store_true", help="Submit one CU analyze request.")
    args = parser.parse_args(argv)
    if not args.apply:
        checks = preflight(args.source_url)
        print("CU visual handoff preflight (no cloud calls made)")
        print(f"- cu_endpoint_configured: {'configured' if checks['cu_endpoint_configured'] else 'missing'}")
        print(f"- analyzer: {checks['analyzer'] or 'selected after --source-url is supplied'}")
        print("- output bounds: 20 segments, 10 warnings, 400 summary characters; SAS query is omitted.")
        print("- review warnings, segment timings, source grounding, retention, quota, private DNS, and egress.")
        return
    if not args.source_url:
        parser.error("--source-url is required with --apply.")
    print(json.dumps(production_handoff(args.source_url), indent=2))


if __name__ == "__main__":
    main()
