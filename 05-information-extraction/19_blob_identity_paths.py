# Run: uv run python 05-information-extraction/19_blob_identity_paths.py [--run]
# Practice-question coverage: Q48, Q75.
"""Verify the operator/runtime Azure Blob data-plane access via DefaultAzureCredential.

This lesson proves that the current identity (az login on workstation, or managed
identity in Azure) has the required Blob Data Reader role on the configured container.
It does NOT test the Search service's managed identity — those are separate identities
with separate role assignments. If this passes but the indexer still fails, the Search
MI lacks its own role.

Default run: local preflight (checks env vars, validates account name format). `--run`
calls BlobServiceClient with DefaultAzureCredential → get_container_properties() →
print container name and timestamp. No account key used.

Code path:
  account_url(STORAGE_ACCOUNT) → validate no slashes/dots → BlobServiceClient with
  DefaultAzureCredential → get_container_client(STORAGE_CONTAINER) →
  get_container_properties() → print name and last_modified.

What to watch. Preflight: config checks. With --run: container name and last_modified
timestamp. A 403 means the current identity lacks Storage Blob Data Reader. A network
error means the endpoint isn't reachable (check private endpoint/firewall).

Prerequisites / env vars:
  STORAGE_ACCOUNT   — storage account name (not URL or connection string)
  STORAGE_CONTAINER — container name
  --run             — execute the Blob property read
"""
import argparse

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

from _shared.config import settings


def account_url(account_name: str) -> str:
    if not account_name or "/" in account_name or "." in account_name:
        raise ValueError("STORAGE_ACCOUNT must be an Azure Storage account name, not a URL or connection string.")
    return f"https://{account_name}.blob.core.windows.net"


def container_client(account_name: str, container_name: str):
    return BlobServiceClient(account_url(account_name), credential=DefaultAzureCredential()).get_container_client(
        container_name
    )


def preflight() -> dict[str, bool]:
    current = settings()
    return {
        "storage_account_configured": bool(current.storage_account),
        "storage_container_configured": bool(current.storage_container),
        "search_endpoint_configured": bool(current.search_endpoint),
    }


def run() -> dict[str, str]:
    current = settings()
    properties = container_client(
        current.require("STORAGE_ACCOUNT"), current.require("STORAGE_CONTAINER")
    ).get_container_properties()
    return {
        "container": current.storage_container,
        "last_modified": properties.last_modified.isoformat() if properties.last_modified else "",
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Preflight or verify Blob managed-identity access.")
    parser.add_argument("--run", action="store_true", help="Read container properties with DefaultAzureCredential.")
    args = parser.parse_args(argv)
    if not args.run:
        print("Blob identity preflight. No cloud calls made.")
        for name, configured in preflight().items():
            print(f"- {name}: {'configured' if configured else 'missing'}")
        print("- Grant Storage Blob Data Reader at container scope; use Search managed identity for indexer access.")
        return
    result = run()
    print(f"Identity can read container '{result['container']}' (last modified: {result['last_modified']}).")


if __name__ == "__main__":
    main()
