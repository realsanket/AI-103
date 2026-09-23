# Run: uv run python 05-information-extraction/04_search_indexer_setup.py --run [--wait]
# Practice-question coverage: Q172.
"""Create/update the Blob data source and indexer, then optionally start ingestion.

The indexer is the job that reads Blob files, runs the skillset (chunking +
embedding), and writes index documents. It must be created after the index (00)
and skillset (05). Default run provisions the schema; `--run` also starts the
indexer; `--wait` polls until the run completes or times out (5 min). A started
indexer is not necessarily done ingesting — wait for `success` status before querying.

The Search service's system-assigned managed identity must have Storage Blob Data
Reader on the Blob container and Cognitive Services OpenAI User on the embedding
deployment. Network reachability between Search, Blob, and OpenAI is separate.

Code path:
  load_definition(data_source.json) → PUT /datasources; load_definition(indexer.json)
  → PUT /indexers. With --run: indexer_client().run_indexer(name). With --wait:
  poll get_indexer_status().last_result until terminal status or timeout.

What to watch. `data source saved`, `indexer saved`. With --run: indexer starts
and --wait prints status polls until success/failure/timeout. Watch for 403
(role missing) or network connectivity errors in indexer execution history.

Prerequisites / env vars:
  SEARCH_ENDPOINT       — https://<service>.search.windows.net
  SEARCH_INDEXER        — indexer name
  STORAGE_ACCOUNT, STORAGE_CONTAINER, AZURE_SUBSCRIPTION_ID, AZURE_RESOURCE_GROUP
  AZURE_OPENAI_ENDPOINT, EMBEDDING_MODEL
  --run                 — start indexer after provisioning
  --wait                — poll until terminal status (max 5 min)
"""
import argparse
import time
from pathlib import Path

from _shared.search_client import indexer_client
from _search_rest import load_definition, put

_DATA_SOURCE_JSON = Path(__file__).parent / "skillset_configs" / "data_source.json"
_INDEXER_JSON = Path(__file__).parent / "skillset_configs" / "indexer.json"
_TERMINAL_INDEXER_STATUSES = {"success", "transientfailure", "persistentfailure"}
_SEARCH_SERVICE_RBAC = (
    "Search service identity needs Storage Blob Data Reader on the source container "
    "and Cognitive Services OpenAI User on the embedding resource."
)


def _status_value(status: object) -> str:
    value = getattr(status, "value", status)
    return str(value or "").lower()


def wait_for_indexer(
    client, indexer_name: str, *, timeout: float = 300.0, poll_interval: float = 5.0
) -> object:
    """Wait for the run started by this lesson, then surface indexing failures."""
    if timeout <= 0 or poll_interval <= 0:
        raise ValueError("timeout and poll_interval must be greater than zero.")
    deadline = time.monotonic() + timeout
    while True:
        result = client.get_indexer_status(indexer_name)
        last_result = getattr(result, "last_result", None)
        status = _status_value(getattr(last_result, "status", None))
        if status in _TERMINAL_INDEXER_STATUSES:
            if status != "success":
                detail = getattr(last_result, "error_message", None) or "No service diagnostic returned."
                raise RuntimeError(f"Indexer {indexer_name!r} finished with {status}: {detail}")
            return last_result
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError(f"Indexer {indexer_name!r} did not finish within {timeout:g}s.")
        time.sleep(min(poll_interval, remaining))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true", help="Start indexing after provisioning.")
    parser.add_argument("--wait", action="store_true", help="Wait for the requested indexer run.")
    args = parser.parse_args()

    data_source = load_definition(_DATA_SOURCE_JSON)
    indexer = load_definition(_INDEXER_JSON)
    put("datasources", data_source)
    put("indexers", indexer)
    print(f"data source '{data_source['name']}' and indexer '{indexer['name']}' saved.")
    print(_SEARCH_SERVICE_RBAC)
    if args.run:
        client = indexer_client()
        client.run_indexer(indexer["name"])
        print("indexer run started.")
        if args.wait:
            wait_for_indexer(client, indexer["name"])
            print("indexer run succeeded.")


if __name__ == "__main__":
    main()
