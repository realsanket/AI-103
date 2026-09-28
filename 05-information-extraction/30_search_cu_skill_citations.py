# Run: uv run python 05-information-extraction/30_search_cu_skill_citations.py [--apply] [--delete]
# Practice-question coverage: Q120, Q146.
"""One multimodal skill for page-level citations: the Content Understanding skill in a Search skillset.

Requirement: an indexer ingests PDF policy manuals; clients must show
page-level citations with bounding polygons for text and images, and tables
that span pages must stay whole. The answer is ONE built-in skill,
`#Microsoft.Skills.Util.ContentUnderstandingSkill` (GA in Search REST
2026-04-01):
  - `extractionOptions: ["images", "locationMetadata"]` returns every chunk
    and image with `pageNumberFrom`, `pageNumberTo`, `ordinalPosition`, and
    `source` polygons such as `D(2,0.64,9.26,7.86,9.26,...)`.
  - Cross-page tables come back as a single Markdown table; chunks can span
    pages. It extracts and chunks, so no Text Split skill is needed.
Why not the others: Document Extraction cracks files without layout or
polygons; Document Layout (Document Intelligence) returns tables and figures
as plain text and cannot join a table across pages; GenAI Prompt transforms
text and does not extract layout.

Pipeline contract (lesson 05 pattern, one search document per chunk):
  indexer   `allowSkillsetToReadFileData: true` creates `/document/file_data`,
            the skill's only input; `batchSize: 1` keeps each file under the
            skill's five-minute analysis limit.
  skillset  the skill, `cognitiveServices` (AIServicesByIdentity: the skill
            runs on and bills to your Foundry resource, with no free
            documents), `indexProjections` mapping each `text_sections` item
            and its location metadata to a chunk document, and a knowledge
            store `files` projection so each chunk's `imagePath` resolves to
            an image blob.
  index     chunk_id key (keyword analyzer), parent_id, content, page range,
            ordinal position, polygons, image paths, title, source_url.

Code path:
  Default   validate the definitions locally, turn a sample `text_sections`
            item into a citation, print the REST bodies. No cloud calls made.
  --apply   PUT index -> skillset -> indexer (a new indexer runs at once and
            Content Understanding charges per page).
  --delete  delete indexer -> skillset -> index; image blobs stay in Storage.

Prerequisites / env vars (for --apply):
  SEARCH_ENDPOINT; data source `northwind-blob-datasource` (lesson 04).
  FOUNDRY_ENDPOINT: an AIServices resource in a Content Understanding region.
  AZURE_SUBSCRIPTION_ID, AZURE_RESOURCE_GROUP, STORAGE_ACCOUNT (image store).
  Search managed identity roles: Cognitive Services User (Foundry resource),
  Storage Blob Data Reader (source), Storage Blob Data Contributor (images).
  Preview options (semantic chunking in tokens, `modelName` +
  `modelDeployment` for image descriptions) need 2026-05-01-preview or later
  and are deliberately not used here.
"""
import argparse
import json
import re

DATA_SOURCE = "northwind-blob-datasource"
INDEX_NAME = "northwind-cu-chunks"
SKILLSET_NAME = "northwind-cu-skillset"
INDEXER_NAME = "northwind-cu-indexer"
IMAGE_CONTAINER = "northwind-cu-images"
CU_SKILL = "#Microsoft.Skills.Util.ContentUnderstandingSkill"
_POLYGON = re.compile(r"D\((\d+),([^)]*)\)")

INDEX = {
    "name": INDEX_NAME,
    "fields": [
        {"name": "chunk_id", "type": "Edm.String", "key": True, "searchable": True, "analyzer": "keyword"},
        {"name": "parent_id", "type": "Edm.String", "searchable": False, "filterable": True},
        {"name": "content", "type": "Edm.String", "searchable": True},
        {"name": "title", "type": "Edm.String", "searchable": True, "filterable": True},
        {"name": "source_url", "type": "Edm.String", "searchable": False},
        {"name": "page_from", "type": "Edm.Int32", "filterable": True, "sortable": True},
        {"name": "page_to", "type": "Edm.Int32", "filterable": True},
        {"name": "ordinal_position", "type": "Edm.Int32", "sortable": True},
        {"name": "polygons", "type": "Edm.String", "searchable": False},
        {"name": "image_paths", "type": "Edm.String", "searchable": False},
    ],
}

_SECTION = "/document/text_sections/*"
SKILLSET = {
    "name": SKILLSET_NAME,
    "description": "Content Understanding extraction and chunking with page and polygon metadata.",
    "skills": [
        {
            "@odata.type": CU_SKILL,
            "name": "content-understanding",
            "description": "Markdown chunks, images, and location metadata in one skill.",
            "context": "/document",
            "extractionOptions": ["images", "locationMetadata"],
            "chunkingProperties": {"unit": "characters", "maximumLength": 2000, "overlapLength": 200},
            "inputs": [{"name": "file_data", "source": "/document/file_data"}],
            "outputs": [
                {"name": "text_sections", "targetName": "text_sections"},
                {"name": "normalized_images", "targetName": "normalized_images"},
            ],
        }
    ],
    "cognitiveServices": {
        "@odata.type": "#Microsoft.Azure.Search.AIServicesByIdentity",
        "description": "Content Understanding runs on and bills to this Foundry resource.",
        "subdomainUrl": "${FOUNDRY_ENDPOINT}",
        "identity": None,
    },
    "indexProjections": {
        "selectors": [
            {
                "targetIndexName": INDEX_NAME,
                "parentKeyFieldName": "parent_id",
                "sourceContext": _SECTION,
                "mappings": [
                    {"name": "content", "source": f"{_SECTION}/content"},
                    {"name": "page_from", "source": f"{_SECTION}/locationMetadata/pageNumberFrom"},
                    {"name": "page_to", "source": f"{_SECTION}/locationMetadata/pageNumberTo"},
                    {"name": "ordinal_position", "source": f"{_SECTION}/locationMetadata/ordinalPosition"},
                    {"name": "polygons", "source": f"{_SECTION}/locationMetadata/source"},
                    {"name": "image_paths", "source": f"{_SECTION}/imagePath"},
                    {"name": "title", "source": "/document/metadata_storage_name"},
                    {"name": "source_url", "source": "/document/metadata_storage_path"},
                ],
            }
        ],
        "parameters": {"projectionMode": "skipIndexingParentDocuments"},
    },
    "knowledgeStore": {
        "storageConnectionString": (
            "ResourceId=/subscriptions/${AZURE_SUBSCRIPTION_ID}/resourceGroups/${AZURE_RESOURCE_GROUP}"
            "/providers/Microsoft.Storage/storageAccounts/${STORAGE_ACCOUNT}/;"
        ),
        "projections": [
            {
                "tables": [],
                "objects": [],
                "files": [{"storageContainer": IMAGE_CONTAINER, "source": "/document/normalized_images/*"}],
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
        "batchSize": 1,
        "configuration": {
            "dataToExtract": "contentAndMetadata",
            "parsingMode": "default",
            "allowSkillsetToReadFileData": True,
        },
    },
    "fieldMappings": [],
    "outputFieldMappings": [],
}

# Shape of one `text_sections` item (see the skill reference); values are synthetic.
SAMPLE_SECTION = {
    "id": "2_policy-table",
    "content": "<table><tr><th>Cover</th><th>Limit</th></tr><tr><td>Flood</td><td>25,000</td></tr></table>",
    "locationMetadata": {
        "pageNumberFrom": 2,
        "pageNumberTo": 3,
        "ordinalPosition": 3,
        "source": "D(2,0.64,9.26,7.86,9.26,7.86,10.52,0.64,10.52);D(3,0.65,0.39,7.86,0.39,7.86,4.33,0.65,4.32)",
    },
}


def validate_pipeline(index: dict, skillset: dict, indexer: dict) -> list[str]:
    """Check the skill, indexer, projection, and index contract locally."""
    skill = next((item for item in skillset["skills"] if item["@odata.type"] == CU_SKILL), None)
    if skill is None:
        raise ValueError("the skillset needs the Content Understanding skill")
    options = set(skill.get("extractionOptions", []))
    if "locationMetadata" not in options or not options <= {"images", "locationMetadata"}:
        raise ValueError("extractionOptions must include locationMetadata (and optionally images)")
    chunking = skill["chunkingProperties"]
    if chunking.get("method", "fixedSize") != "fixedSize" or chunking.get("unit") != "characters":
        raise ValueError("GA 2026-04-01 supports fixedSize chunking measured in characters")
    if not 300 <= chunking["maximumLength"] <= 50_000:
        raise ValueError("maximumLength must be between 300 and 50,000 characters")
    if not 0 <= chunking.get("overlapLength", 0) < chunking["maximumLength"] / 2:
        raise ValueError("overlapLength must be less than half of maximumLength")
    if "modelName" in skill or "modelDeployment" in skill:
        raise ValueError("image descriptions are preview-only; keep them out of the GA definition")

    if [item["source"] for item in skill["inputs"]] != ["/document/file_data"]:
        raise ValueError("the skill reads /document/file_data")
    if indexer["parameters"]["configuration"].get("allowSkillsetToReadFileData") is not True:
        raise ValueError("set allowSkillsetToReadFileData so the indexer creates /document/file_data")

    billing = skillset.get("cognitiveServices") or {}
    if billing.get("@odata.type") not in (
        "#Microsoft.Azure.Search.AIServicesByIdentity",
        "#Microsoft.Azure.Search.AIServicesByKey",
    ):
        raise ValueError("attach a Foundry (AIServices) resource: the skill has no free documents")

    fields = {field["name"]: field for field in index["fields"]}
    key = fields.get("chunk_id", {})
    if not key.get("key") or key.get("analyzer") != "keyword":
        raise ValueError("index projections need a chunk_id key field with the keyword analyzer")
    selector = skillset["indexProjections"]["selectors"][0]
    mapped = [mapping["name"] for mapping in selector["mappings"]] + [selector["parentKeyFieldName"]]
    missing = sorted(set(mapped) - set(fields))
    if missing:
        raise ValueError(f"index projection maps to fields missing from the index: {missing}")
    return [
        "Content Understanding skill: fixedSize character chunks with images and location metadata",
        "indexer passes /document/file_data; Foundry resource attached for processing and billing",
        f"{len(selector['mappings'])} projection mappings target existing index fields",
    ]


def parse_polygons(source: str) -> list[dict]:
    """Split a `source` string like D(page,x1,y1,...);D(...) into page polygons."""
    regions = []
    for page, numbers in _POLYGON.findall(source or ""):
        values = [float(value) for value in numbers.split(",")]
        if len(values) < 6 or len(values) % 2:
            raise ValueError(f"polygon on page {page} needs at least three x,y points")
        regions.append({"page": int(page), "points": list(zip(values[::2], values[1::2]))})
    return regions


def citation(section: dict, title: str) -> dict:
    """Build the page-level citation a client renders for one chunk."""
    location = section.get("locationMetadata") or {}
    first, last = location.get("pageNumberFrom"), location.get("pageNumberTo")
    pages = f"page {first}" if first == last else f"pages {first}-{last}"
    return {
        "label": f"{title}, {pages}",
        "highlights": parse_polygons(location.get("source", "")),
        "images": [path for path in (section.get("imagePath") or "").split(";") if path],
    }


def apply() -> None:
    from _search_rest import put_named, resolve_placeholders

    for resource, definition in (("indexes", INDEX), ("skillsets", SKILLSET), ("indexers", INDEXER)):
        body = resolve_placeholders(definition, f"{resource}/{definition['name']}")
        put_named(resource, definition["name"], body)
        print(f"saved {resource}/{definition['name']}")
    print("The new indexer runs now (Content Understanding charges per page). Check it with lesson 18.")
    print("Clean up: uv run python 05-information-extraction/30_search_cu_skill_citations.py --delete")


def delete() -> None:
    from _search_rest import delete_named

    for resource, name in (("indexers", INDEXER_NAME), ("skillsets", SKILLSET_NAME), ("indexes", INDEX_NAME)):
        print(f"{resource}/{name}: {'deleted' if delete_named(resource, name) else 'not found'}")
    print(f"Image blobs in '{IMAGE_CONTAINER}' remain in Storage; delete them there if no longer needed.")


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

    sample = citation(SAMPLE_SECTION, "northwind-policy.pdf")
    print("\nCitation for a synthetic chunk that holds a table spanning pages 2-3:")
    print(f"  {sample['label']}")
    for region in sample["highlights"]:
        print(f"  highlight page {region['page']}: {region['points']}")
    for label, definition in (("Index", INDEX), ("Skillset", SKILLSET), ("Indexer", INDEXER)):
        print(f"\n{label} {definition['name']}:")
        print(json.dumps(definition, indent=2))
    print("\nNo cloud calls made. Re-run with --apply to create the pipeline (billable).")


if __name__ == "__main__":
    main()
