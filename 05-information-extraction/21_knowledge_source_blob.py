# Run: uv run python 05-information-extraction/21_knowledge_source_blob.py [--apply]
"""Create an indexed **blob** knowledge source for agentic retrieval.

A knowledge source is the top-level object that grounds a knowledge base at
query time (agentic retrieval, lessons 24-26). The `azureBlob` kind is
special: unlike the manual pipeline in lessons 04-05 (data source + skillset +
indexer + index as four PUTs), one knowledge source definition tells Search
to auto-generate all four objects. The service uses the embedding and chat
completion models declared in `ingestionParameters` to chunk, vectorize, and
optionally verbalize images inside your blobs. Content lands in an index
whose name defaults to `<ks-name>-index`, and the indexer runs on the
schedule you set (null = manual).

Preview (`2026-08-01-preview`) adds `networkAccessMode`,
`ingestionPermissionOptions` (Purview / ACL propagation), and per-language
analyzers. This lesson defaults to the preview API version because those
features are the reason to prefer a knowledge source over a hand-built
pipeline. Answer synthesis (lesson 26) and web knowledge (lesson 23) also
require preview.

Code path:
  build_body() assembles the JSON exactly matching the docs' preview PUT
  body. Preflight prints the body. With --apply: PUT /knowledgesources/<name>
  ?api-version=2026-08-01-preview via Entra-authenticated REST.

What to watch. Preflight: printed JSON shows connection string as
`ResourceId=...` (managed-identity form) and both embedding/chat model
deployment names. With --apply: `knowledge source '<name>' saved.` A 403
means the calling identity lacks Search Service Contributor. A 400 with
"cannot resolve embedding" means the Search MI lacks Cognitive Services User
on the AOAI/Foundry resource.

Prerequisites / env vars:
  SEARCH_ENDPOINT           — https://<service>.search.windows.net
  SEARCH_KNOWLEDGE_SOURCE   — knowledge source name (default northwind-blob-ks)
  SEARCH_BLOB_CONNECTION    — blob connection string; use ResourceId=... for MI
  SEARCH_BLOB_CONTAINER     — source blob container name
  AZURE_OPENAI_ENDPOINT     — AOAI/Foundry resource endpoint
  EMBEDDING_MODEL           — embedding deployment (also used as model name)
  DEFAULT_MODEL             — chat deployment used for image verbalization
"""
import argparse
import json

from _search_rest import _PREVIEW_API_VERSION, put_named
from _shared.config import env as _env, settings


def configuration() -> dict[str, str]:
    s = settings()
    cfg = {
        "name": _env("SEARCH_KNOWLEDGE_SOURCE", "northwind-blob-ks"),
        "connection": _env("SEARCH_BLOB_CONNECTION"),
        "container": _env("SEARCH_BLOB_CONTAINER", s.storage_container),
        "aoai_endpoint": s.azure_openai_endpoint,
        "embedding": s.embedding_model,
        "chat": s.default_model,
    }
    return cfg


def build_body(cfg: dict[str, str]) -> dict:
    return {
        "name": cfg["name"],
        "kind": "azureBlob",
        "description": "Blob knowledge source auto-generating data source, skillset, index, and indexer.",
        "encryptionKey": None,
        "azureBlobParameters": {
            "connectionString": cfg["connection"] or "ResourceId=<storage-resource-id>",
            "containerName": cfg["container"],
            "folderPath": None,
            "isADLSGen2": False,
            "ingestionParameters": {
                "networkAccessMode": "public",
                "identity": None,
                "disableImageVerbalization": False,
                "chatCompletionModel": {
                    "kind": "azureOpenAI",
                    "azureOpenAIParameters": {
                        "resourceUri": cfg["aoai_endpoint"],
                        "deploymentId": cfg["chat"],
                        "modelName": cfg["chat"],
                    },
                },
                "embeddingModel": {
                    "kind": "azureOpenAI",
                    "azureOpenAIParameters": {
                        "resourceUri": cfg["aoai_endpoint"],
                        "deploymentId": cfg["embedding"],
                        "modelName": cfg["embedding"],
                    },
                },
                "contentExtractionMode": "minimal",
                "ingestionSchedule": None,
            },
        },
    }


def preflight(cfg: dict[str, str]) -> None:
    print("Blob knowledge source preflight. No cloud calls made.")
    for key, value in cfg.items():
        print(f"- {key}: {'configured' if value else 'missing'}")
    print(f"- api-version: {_PREVIEW_API_VERSION}")
    print("Planned request body:")
    print(json.dumps(build_body(cfg), indent=2))


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Create a blob knowledge source for agentic retrieval.")
    parser.add_argument("--apply", action="store_true", help="Send the PUT request to Search.")
    args = parser.parse_args(argv)
    cfg = configuration()
    if not args.apply:
        preflight(cfg)
        print("- Rerun with --apply to create the knowledge source.")
        return
    if not cfg["connection"]:
        raise SystemExit("Set SEARCH_BLOB_CONNECTION (ResourceId=... recommended).")
    put_named("knowledgesources", cfg["name"], build_body(cfg), _PREVIEW_API_VERSION)
    print(f"knowledge source '{cfg['name']}' saved.")


if __name__ == "__main__":
    main()
