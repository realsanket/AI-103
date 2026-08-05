"""Create/update Blob data source and indexer from REST JSON definitions."""
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
