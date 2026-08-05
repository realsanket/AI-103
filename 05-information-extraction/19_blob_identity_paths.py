"""Verify Azure Blob data-plane access through DefaultAzureCredential.

This does not use account keys or connection strings. Search indexers use their
own managed identity when connecting to the ResourceId data source from lesson
04; ``--run`` only verifies the operator/runtime Blob identity path.
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
