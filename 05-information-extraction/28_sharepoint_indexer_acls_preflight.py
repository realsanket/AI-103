# Run: uv run python 05-information-extraction/28_sharepoint_indexer_acls_preflight.py
# Practice-question coverage: Q144.
"""SharePoint indexer + ACL ingestion (preview) — preflight reference.

The SharePoint indexer can preserve per-item permission metadata (ACLs)
alongside content and enforce it at query time. This preflight prints the
end-to-end setup the doc requires — it makes no cloud call and creates no
resource. Use it as a runbook before running any of the REST/`_search_rest.py`
lessons that would actually create the data source, index, skillset, or
indexer against a preview API version (2026-05-01-preview or later; the
examples in the doc use 2026-08-01-preview).

Prints, in order:
  1. Prerequisites (billable Search tier, SharePoint config, preview API).
  2. Permission-by-scenario table (Graph + SharePoint API permissions, and
     the credential type — client secret vs required federated credential).
  3. The data source `indexerPermissionOptions` shape.
  4. The permission-filter fields on the index (`UserIds`, `GroupIds`, and
     optional `SharePointSiteUrl` for SharePoint groups).
  5. Two ways to populate ACLs on chunks: indexer field mappings vs skillset
     `indexProjections.mappings` (required when `projectionMode` is
     `skipIndexingParentDocuments`).
  6. SharePoint groups configuration (`sharePointConnectorAppRegistration`).
  7. Resync options (`/resync options: ["permissions"]`, `/resetdocs`).

Warning callouts (doc-verbatim):
  - The Azure portal doesn't support this feature. All configuration is REST
    or SDK.
  - ACL ingestion requires APPLICATION permissions on the Entra app; delegated
    permissions are NOT supported.
  - Federated credential is required for any scenario that adds SharePoint API
    permissions. Client secrets work only for the Graph-only document-library
    scenario.
  - `FederatedCredentialApplicationId` (data source) and `federatedCredentialId`
    (index) use the MANAGED IDENTITY's application ID, NOT the ingestion app's
    client ID and NOT the federated credential entry's object ID.
  - Parent-scope permission changes (site/library/folder) are NOT picked up
    automatically — call `/resync options=["permissions"]` after such changes.

Prerequisites / env vars:
  SEARCH_ENDPOINT              — https://<service>.search.windows.net
  SEARCH_INDEX                 — target index name
  SEARCH_INDEXER               — target indexer name
  SEARCH_SKILLSET              — target skillset name (if chunked pipeline)
  SHAREPOINT_SITE_URL          — https://<tenant>.sharepoint.com/sites/<site>
"""
import argparse
import json
import os

from _shared.config import settings

REST_API_VERSION_MIN_ACL = "2026-05-01-preview"
REST_API_VERSION_DOC = "2026-08-01-preview"


def _env(name: str) -> str:
    return os.environ.get(name, "") or "<not set>"


def _print_permissions_table() -> None:
    print("Permissions by ACL scenario (Graph + SharePoint APIs, and credential type):")
    rows = [
        (
            "Doc-library files, Entra users/std groups only",
            "Graph: Files.Read.All, Sites.FullControl.All (or Sites.Selected)",
            "Client secret OR federated credential",
        ),
        (
            "Doc-library files, honor SharePoint site groups",
            "Graph: Files.Read.All, Sites.FullControl.All | SharePoint: Sites.FullControl.All",
            "Federated credential (REQUIRED)",
        ),
        (
            "SharePoint list items",
            "Graph: Files.Read.All, Sites.FullControl.All, User.Read.All | SharePoint: Sites.FullControl.All",
            "Federated credential (REQUIRED)",
        ),
        (
            "ASPX site pages",
            "Graph: Sites.FullControl.All, User.Read.All (+ Files.Read.All if also libraries) | SharePoint: Sites.FullControl.All",
            "Federated credential (REQUIRED)",
        ),
        (
            "Query-time SP group resolution via sharePointConnectorAppRegistration",
            "SharePoint: User.Read.All (add to the same app registration)",
            "Federated credential (REQUIRED)",
        ),
    ]
    for scenario, perms, cred in rows:
        print(f"  - {scenario}")
        print(f"      perms: {perms}")
        print(f"      credential: {cred}")


def _print_data_source_shape() -> None:
    payload = {
        "name": "my-sharepoint-acl-datasource",
        "type": "sharepoint",
        "indexerPermissionOptions": ["userIds", "groupIds"],
        "credentials": {"connectionString": "<sharepoint connection string with FederatedCredentialApplicationId>"},
        "container": {"name": "<library-name>", "query": "<optional-folder-path>"},
    }
    print("Data source (PUT /datasources/<name>?api-version=" + REST_API_VERSION_DOC + "):")
    print(json.dumps(payload, indent=2))


def _print_index_shape() -> None:
    payload = {
        "name": "my-sharepoint-acl-index",
        "sharePointConnectorAppRegistration": {
            "applicationId": "<ingestion-app-client-id>",
            "federatedCredentialId": "<managed-identity-application-id>",
            "tenantId": "<sharepoint-tenant-id>",
        },
        "fields": [
            {"name": "UserIds", "type": "Collection(Edm.String)", "permissionFilter": "userIds",
             "filterable": True, "retrievable": False},
            {"name": "GroupIds", "type": "Collection(Edm.String)", "permissionFilter": "groupIds",
             "filterable": True, "retrievable": False},
            {"name": "SharePointSiteUrl", "type": "Edm.String", "sharepointSiteUrl": True,
             "filterable": False, "retrievable": False},
        ],
        "permissionFilterOption": "enabled",
    }
    print("Index (PUT /indexes/<name>?api-version=" + REST_API_VERSION_DOC + "):")
    print(json.dumps(payload, indent=2))


def _print_field_mappings() -> None:
    payload = {
        "fieldMappings": [
            {"sourceFieldName": "metadata_user_ids", "targetFieldName": "UserIds"},
            {"sourceFieldName": "metadata_group_ids", "targetFieldName": "GroupIds"},
            {"sourceFieldName": "metadata_spo_site_url", "targetFieldName": "SharePointSiteUrl"},
        ]
    }
    print("Indexer field mappings (one-document-per-file OR parent-index path):")
    print(json.dumps(payload, indent=2))


def _print_index_projections() -> None:
    payload = {
        "indexProjections": {
            "selectors": [
                {
                    "targetIndexName": "chunks-index",
                    "parentKeyFieldName": "parentId",
                    "sourceContext": "/document/chunks/*",
                    "mappings": [
                        {"name": "chunkId", "source": "/document/chunks/*/id"},
                        {"name": "content", "source": "/document/chunks/*/text"},
                        {"name": "parentId", "source": "/document/id"},
                        {"name": "UserIds", "source": "/document/metadata_user_ids"},
                        {"name": "GroupIds", "source": "/document/metadata_group_ids"},
                        {"name": "SharePointSiteUrl", "source": "/document/metadata_spo_site_url"},
                    ],
                }
            ],
            "parameters": {"projectionMode": "skipIndexingParentDocuments"},
        }
    }
    print("Skillset indexProjections (REQUIRED when chunking with skipIndexingParentDocuments):")
    print(json.dumps(payload, indent=2))
    print("If projectionMode is skipIndexingParentDocuments, indexer field mappings for the")
    print("ACL fields are BYPASSED — chunks must carry ACLs via indexProjections.mappings.")


def _print_resync_options() -> None:
    print("Synchronize after parent-scope permission changes or when enabling ACLs later:")
    print(json.dumps({"url": "POST /indexers/<indexer>/resync?api-version=" + REST_API_VERSION_DOC,
                      "body": {"options": ["permissions"]}}, indent=2))
    print("Or refresh specific items:")
    print(json.dumps({"url": "POST /indexers/<indexer>/resetdocs?api-version=" + REST_API_VERSION_DOC,
                      "body": {"documentKeys": ["doc123", "doc456"]}}, indent=2))


def preflight() -> None:
    s = settings()
    print("No cloud calls made. This is a reference runbook.")
    print(f"REST API version (minimum for incremental ACLs and SP groups): {REST_API_VERSION_MIN_ACL}")
    print(f"REST API version in doc examples: {REST_API_VERSION_DOC}")
    print()
    print("Environment check:")
    print(f"  SEARCH_ENDPOINT      : {s.search_endpoint or '<not set>'}")
    print(f"  SEARCH_INDEX         : {s.search_index or '<not set>'}")
    print(f"  SEARCH_INDEXER       : {s.search_indexer or '<not set>'}")
    print(f"  SEARCH_SKILLSET      : {s.search_skillset or '<not set>'}")
    print(f"  SHAREPOINT_SITE_URL  : {_env('SHAREPOINT_SITE_URL')}")
    print()
    _print_permissions_table()
    print()
    _print_data_source_shape()
    print()
    _print_index_shape()
    print()
    _print_field_mappings()
    print()
    _print_index_projections()
    print()
    _print_resync_options()
    print()
    print("Verify ACL ingestion: temporarily set retrievable=true on UserIds/GroupIds and run")
    print("an elevated-read query; confirm collections aren't empty on every chunk. Return")
    print("retrievable=false after verification (no index rebuild required).")
    print()
    print("Non-support notes (doc-verbatim):")
    print("  - Portal doesn't support this feature.")
    print("  - Not supported: Anyone/Org-scoped share links, external/guest users,")
    print("    Information Management policies, Purview sensitivity labels (separate feature).")
    print("  - Custom Web API skill, Knowledge Store, enrichment cache, and Debug Sessions")
    print("    do NOT preserve document-level permissions on indexed content.")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="SharePoint indexer + ACL ingestion preflight.")
    parser.parse_args(argv)
    preflight()


if __name__ == "__main__":
    main()
