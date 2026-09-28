# Run: uv run python 05-information-extraction/29_search_ocr_knowledge_store.py [--apply] [--delete]
# Practice-question coverage: Q94, Q121, Q141.
"""OCR scanned files and embedded images, index the text, and keep enrichments in a knowledge store.

Scanned invoices and PDFs with pictures hold text that document cracking
cannot read: it is pixels. This pipeline makes that text searchable, keeps a
source URL for citations, and persists the enriched output for analytics.

How the pieces fit:
  1. Indexer `imageAction: "generateNormalizedImages"`. While cracking each
     blob, the indexer extracts every image (image files and images embedded
     in PDFs or Office files) into the `/document/normalized_images`
     collection. That collection is the only input the built-in OCR skill
     accepts. A Shaper skill, `outputFieldMappings`, or pointing OCR at
     `/document/content` cannot create it.
  2. OCR skill (`#Microsoft.Skills.Vision.OcrSkill`) runs once per image
     (context `/document/normalized_images/*`) and outputs its `text`. Choose
     OCR for text inside images: Image Analysis returns tags and captions,
     not the text; Text Split and Translation need text that already exists.
  3. Text Merge skill (`#Microsoft.Skills.Text.MergeSkill`) inserts each
     image's OCR text into `/document/content` at the image's
     `contentOffset`, producing one `merged_text` field that is indexed next
     to `source_url` for citations.
  4. Knowledge store (`knowledgeStore` on the skillset) writes enrichments to
     Azure Storage for non-search consumers (Power BI, data science, audit):
        objects  Blob container, one JSON document per source file. Use for
                 JSON and other hierarchical, semi-structured data.
        tables   Table storage rows and columns. Use for extracted text you
                 want to query or analyze as flat records.
        files    Blob container of binary images (normalized images).
     Projections in one group are related through generated keys. A table
     entity property holds at most 64 KB, so the long merged text goes to the
     object projection and the tables hold metadata and per-image OCR text.

Code path:
  Default   validate the index, skillset, and indexer locally, simulate the
            Text Merge skill, and print the REST bodies. No cloud calls made.
  --apply   PUT index -> skillset -> indexer (api-version 2026-04-01). A new
            indexer runs immediately; image extraction and OCR are billable.
  --delete  delete indexer -> skillset -> index. Knowledge-store tables and
            containers stay in Storage; delete them there.

Prerequisites / env vars (for --apply):
  SEARCH_ENDPOINT; data source `northwind-blob-datasource` from lesson 04.
  AZURE_SUBSCRIPTION_ID, AZURE_RESOURCE_GROUP, STORAGE_ACCOUNT for the
  identity-based knowledge-store connection (no account key).
  FOUNDRY_ENDPOINT: AIServices resource billed keylessly for OCR beyond the
  free 20 documents per indexer per day.
  Search managed identity roles: Storage Blob Data Reader (source),
  Storage Blob Data Contributor (object projections), Reader and Data Access
  (table projections), Cognitive Services User (Foundry resource).
  Your identity: Search Service Contributor.
  The knowledge store is a copy of source content: give it the same access
  control, retention, and deletion obligations as the source documents.
"""
import argparse
import json

DATA_SOURCE = "northwind-blob-datasource"
INDEX_NAME = "northwind-ocr-index"
SKILLSET_NAME = "northwind-ocr-skillset"
INDEXER_NAME = "northwind-ocr-indexer"
IMAGE_ACTIONS = ("generateNormalizedImages", "generateNormalizedImagePerPage")
OCR_SKILL = "#Microsoft.Skills.Vision.OcrSkill"

# Which projection type fits which kind of enrichment output.
PROJECTION_FOR = {
    "json_document": "objects",
    "extracted_text": "tables",
    "image": "files",
}

INDEX = {
    "name": INDEX_NAME,
    "fields": [
        {"name": "id", "type": "Edm.String", "key": True, "searchable": False, "filterable": True},
        {"name": "file_name", "type": "Edm.String", "searchable": True, "filterable": True, "sortable": True},
        {"name": "source_url", "type": "Edm.String", "searchable": False, "retrievable": True},
        {"name": "merged_text", "type": "Edm.String", "searchable": True, "retrievable": True},
    ],
}

SKILLSET = {
    "name": SKILLSET_NAME,
    "description": "OCR every image, merge the text into the document, and project enrichments to a knowledge store.",
    "skills": [
        {
            "@odata.type": OCR_SKILL,
            "name": "ocr-images",
            "description": "Read printed and handwritten text from each normalized image.",
            "context": "/document/normalized_images/*",
            "defaultLanguageCode": "en",
            "lineEnding": "Space",
            "inputs": [{"name": "image", "source": "/document/normalized_images/*"}],
            "outputs": [{"name": "text", "targetName": "text"}],
        },
        {
            "@odata.type": "#Microsoft.Skills.Text.MergeSkill",
            "name": "merge-ocr-text",
            "description": "Insert each image's OCR text into the document text where the image appeared.",
            "context": "/document",
            "insertPreTag": " ",
            "insertPostTag": " ",
            "inputs": [
                {"name": "text", "source": "/document/content"},
                {"name": "itemsToInsert", "source": "/document/normalized_images/*/text"},
                {"name": "offsets", "source": "/document/normalized_images/*/contentOffset"},
            ],
            "outputs": [{"name": "mergedText", "targetName": "merged_text"}],
        },
        {
            "@odata.type": "#Microsoft.Skills.Util.ShaperSkill",
            "name": "shape-json-object",
            "description": "One hierarchical JSON document per file for the object projection.",
            "context": "/document",
            "inputs": [
                {"name": "file_name", "source": "/document/metadata_storage_name"},
                {"name": "source_url", "source": "/document/metadata_storage_path"},
                {"name": "merged_text", "source": "/document/merged_text"},
                {
                    "name": "images",
                    "sourceContext": "/document/normalized_images/*",
                    "inputs": [
                        {"name": "page_number", "source": "/document/normalized_images/*/pageNumber"},
                        {"name": "ocr_text", "source": "/document/normalized_images/*/text"},
                    ],
                },
            ],
            "outputs": [{"name": "output", "targetName": "ocr_object"}],
        },
    ],
    "cognitiveServices": {
        "@odata.type": "#Microsoft.Azure.Search.AIServicesByIdentity",
        "description": "Keyless billing for OCR beyond the free daily allowance.",
        "subdomainUrl": "${FOUNDRY_ENDPOINT}",
        "identity": None,
    },
    "knowledgeStore": {
        "storageConnectionString": (
            "ResourceId=/subscriptions/${AZURE_SUBSCRIPTION_ID}/resourceGroups/${AZURE_RESOURCE_GROUP}"
            "/providers/Microsoft.Storage/storageAccounts/${STORAGE_ACCOUNT}/;"
        ),
        "projections": [
            {
                "objects": [
                    {
                        "storageContainer": "northwind-ocr-json",
                        "generatedKeyName": "ObjectId",
                        "source": "/document/ocr_object",
                    }
                ],
                "tables": [
                    {
                        "tableName": "northwindOcrDocuments",
                        "generatedKeyName": "DocumentId",
                        "sourceContext": "/document",
                        "inputs": [
                            {"name": "file_name", "source": "/document/metadata_storage_name"},
                            {"name": "source_url", "source": "/document/metadata_storage_path"},
                        ],
                    },
                    {
                        "tableName": "northwindOcrImageText",
                        "generatedKeyName": "ImageTextId",
                        "sourceContext": "/document/normalized_images/*",
                        "inputs": [
                            {"name": "page_number", "source": "/document/normalized_images/*/pageNumber"},
                            {"name": "ocr_text", "source": "/document/normalized_images/*/text"},
                        ],
                    },
                ],
                "files": [],
            }
        ],
    },
}

INDEXER = {
    "name": INDEXER_NAME,
    "dataSourceName": DATA_SOURCE,
    "targetIndexName": INDEX_NAME,
    "skillsetName": SKILLSET_NAME,
    "parameters": {
        "configuration": {
            "dataToExtract": "contentAndMetadata",
            "parsingMode": "default",
            "imageAction": "generateNormalizedImages",
        }
    },
    "fieldMappings": [
        {
            "sourceFieldName": "metadata_storage_path",
            "targetFieldName": "id",
            "mappingFunction": {"name": "base64Encode"},
        },
        {"sourceFieldName": "metadata_storage_name", "targetFieldName": "file_name"},
        {"sourceFieldName": "metadata_storage_path", "targetFieldName": "source_url"},
    ],
    "outputFieldMappings": [{"sourceFieldName": "/document/merged_text", "targetFieldName": "merged_text"}],
}


def projection_for(kind: str) -> str:
    """Knowledge-store projection type for a kind of enrichment output."""
    if kind not in PROJECTION_FOR:
        raise ValueError(f"unknown output kind {kind!r}; choose from {sorted(PROJECTION_FOR)}")
    return PROJECTION_FOR[kind]


def merge_text(content: str, items: list[str], offsets: list[int], pre: str = " ", post: str = " ") -> str:
    """Local model of the Text Merge skill: insert each item at its content offset."""
    if len(items) != len(offsets):
        raise ValueError("itemsToInsert and offsets must have the same length")
    parts, cursor = [], 0
    for offset, item in sorted(zip(offsets, items)):
        if not 0 <= offset <= len(content):
            raise ValueError(f"offset {offset} is outside the content")
        parts += [content[cursor:offset], f"{pre}{item}{post}"]
        cursor = offset
    parts.append(content[cursor:])
    return "".join(parts)


def _sources(skill: dict) -> list[str]:
    return [item["source"] for item in skill.get("inputs", []) if "source" in item]


def validate_pipeline(index: dict, skillset: dict, indexer: dict) -> list[str]:
    """Check the cross-resource contract before anything reaches Azure."""
    fields = {field["name"] for field in index["fields"]}
    if [field["name"] for field in index["fields"] if field.get("key")] != ["id"]:
        raise ValueError("the index needs exactly one key field named 'id'")

    configuration = indexer["parameters"]["configuration"]
    reads_images = any(
        source.startswith("/document/normalized_images") for skill in skillset["skills"] for source in _sources(skill)
    )
    if reads_images and configuration.get("imageAction") not in IMAGE_ACTIONS:
        raise ValueError("skills read /document/normalized_images, so the indexer must set imageAction")
    for skill in skillset["skills"]:
        if skill["@odata.type"] == OCR_SKILL and _sources(skill) != ["/document/normalized_images/*"]:
            raise ValueError("the OCR skill reads only /document/normalized_images/*")

    targets = [mapping["targetFieldName"] for mapping in indexer["fieldMappings"] + indexer["outputFieldMappings"]]
    missing = sorted(set(targets) - fields)
    if missing:
        raise ValueError(f"indexer maps to fields missing from the index: {missing}")

    store = skillset["knowledgeStore"]
    connection = store["storageConnectionString"]
    if not connection.startswith("ResourceId=") or "AccountKey=" in connection:
        raise ValueError("use an identity-based ResourceId= connection for the knowledge store, not an account key")
    for group in store["projections"]:
        for table in group.get("tables", []):
            if not table.get("tableName") or not table.get("generatedKeyName"):
                raise ValueError("each table projection needs tableName and generatedKeyName")
            if not table.get("source") and not (table.get("sourceContext") and table.get("inputs")):
                raise ValueError(f"table {table['tableName']} needs source, or sourceContext with inputs")
        for obj in group.get("objects", []):
            if not obj.get("storageContainer") or not obj.get("source"):
                raise ValueError("each object projection needs storageContainer and source")
    return [
        f"indexer imageAction={configuration['imageAction']} feeds /document/normalized_images to OCR",
        f"{len(targets)} indexer mappings target existing index fields",
        "knowledge store uses an identity-based connection with object and table projections",
    ]


def apply() -> None:
    from _search_rest import put_named, resolve_placeholders

    for resource, definition in (("indexes", INDEX), ("skillsets", SKILLSET), ("indexers", INDEXER)):
        body = resolve_placeholders(definition, f"{resource}/{definition['name']}")
        put_named(resource, definition["name"], body)
        print(f"saved {resource}/{definition['name']}")
    print("The new indexer runs now. Check it with lesson 18, then query merged_text and cite source_url.")
    print("Clean up: uv run python 05-information-extraction/29_search_ocr_knowledge_store.py --delete")


def delete() -> None:
    from _search_rest import delete_named

    for resource, name in (("indexers", INDEXER_NAME), ("skillsets", SKILLSET_NAME), ("indexes", INDEX_NAME)):
        print(f"{resource}/{name}: {'deleted' if delete_named(resource, name) else 'not found'}")
    print("Knowledge-store tables and containers remain in Storage; delete them there if no longer needed.")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--apply", action="store_true", help="Create the index, skillset, and indexer (billable).")
    parser.add_argument("--delete", action="store_true", help="Delete the indexer, skillset, and index.")
    args = parser.parse_args(argv)

    for line in validate_pipeline(INDEX, SKILLSET, INDEXER):
        print(f"ok  {line}")
    if args.delete:
        delete()
        return
    if args.apply:
        apply()
        return

    content = "Invoice INV-1042 for Northwind.  Total due in 30 days."
    print("\nText Merge simulation (OCR text inserted at the image offset):")
    print("  " + merge_text(content, ["[scan: AMOUNT 1,250.00 USD]"], [32]))
    print("\nProjection choice:")
    for kind in PROJECTION_FOR:
        print(f"  {kind:<15} -> {projection_for(kind)}")
    for label, definition in (("Index", INDEX), ("Skillset", SKILLSET), ("Indexer", INDEXER)):
        print(f"\n{label} {definition['name']}:")
        print(json.dumps(definition, indent=2))
    print("\nNo cloud calls made. Re-run with --apply to create the pipeline (billable).")


if __name__ == "__main__":
    main()
