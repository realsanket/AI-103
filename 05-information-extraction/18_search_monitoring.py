# Run: uv run python 05-information-extraction/18_search_monitoring.py [--run]
"""Read Azure AI Search indexer health and document count — read-only snapshot.

Default run is a local preflight (checks env vars). `--run` calls
`get_indexer_status()` and `get_document_count()`, then formats a summary with
redacted error messages (removes SAS tokens/keys from log strings). This is a
diagnostic smoke test, not complete observability — production needs alerts on
failed runs, stale schedules, failed-item ratio, and query latency.

Code path:
  --run: indexer_client().get_indexer_status(name) → status_summary() → print dict.
  _SECRET regex redacts any sig=, token=, key=, code= values from error strings.
  search_client().get_document_count() → print count.

What to watch. `indexer_status: running/succeeded/failed`, `items_processed`,
`items_failed`. A failed run with no items_failed means the indexer itself failed,
not individual records. Check portal execution history for detailed diagnostics.

Prerequisites / env vars:
  SEARCH_ENDPOINT — https://<service>.search.windows.net
  SEARCH_INDEXER  — indexer name
  SEARCH_INDEX_VECTOR — index name (for document count)
  --run           — execute the read-only status check
"""
import argparse
from datetime import datetime
import re

from _shared.config import settings
from _shared.search_client import indexer_client, search_client

_SECRET = re.compile(r"(?i)\b(sig|token|key|code)=([^&\s]+)")


def _time(value: object) -> str:
    return value.isoformat() if isinstance(value, datetime) else ""


def _error(value: object) -> str:
    return _SECRET.sub(r"\1=REDACTED", value) if isinstance(value, str) else ""


def status_summary(status: object, document_count: int) -> dict[str, object]:
    """Keep operational signals, not indexed document content or query logs."""
    latest = getattr(status, "last_result", None)
    return {
        "indexer_status": getattr(status, "status", ""),
        "document_count": document_count,
        "last_status": getattr(latest, "status", "") if latest else "",
        "items_processed": getattr(latest, "items_processed", 0) if latest else 0,
        "items_failed": getattr(latest, "items_failed", 0) if latest else 0,
        "start_time": _time(getattr(latest, "start_time", None)) if latest else "",
        "end_time": _time(getattr(latest, "end_time", None)) if latest else "",
        "error_message": _error(getattr(latest, "error_message", "")) if latest else "",
    }


def run() -> dict[str, object]:
    current = settings()
    status = indexer_client().get_indexer_status(current.search_indexer)
    count = search_client(current.search_index_vector).get_document_count()
    return status_summary(status, count)


def preflight() -> dict[str, bool]:
    current = settings()
    return {
        "search_endpoint_configured": bool(current.search_endpoint),
        "search_indexer_configured": bool(current.search_indexer),
        "vector_index_configured": bool(current.search_index_vector),
        "application_insights_configured": bool(current.app_insights_connection_string),
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Preflight or read Search ingestion health.")
    parser.add_argument("--run", action="store_true", help="Read indexer status and vector-index document count.")
    args = parser.parse_args(argv)
    if not args.run:
        print("Search monitoring preflight. No cloud calls made.")
        for name, configured in preflight().items():
            print(f"- {name}: {'configured' if configured else 'missing'}")
        print("- --run reads status/count only. Alert on failures, stale runs, and unexpected count changes.")
        print("- Grant monitoring identities Search Index Data Reader; redact and retain diagnostic logs deliberately.")
        return
    for name, value in run().items():
        print(f"{name}: {value}")


if __name__ == "__main__":
    main()
