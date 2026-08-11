# Run: uv run python 05-information-extraction/17_search_custom_skill_deploy.py [--apply] [--run]
"""Deploy a WebApiSkill into the Search skillset and optionally start the indexer.

Bridges lesson 06's local custom-skill contract into Search enrichment. Default run
validates local prerequisites (URL, importability) without any cloud call. `--apply`
clones the base skillset, inserts a WebApiSkill at the custom endpoint URL, and
retargets the indexer to the new skillset. `--run` also starts the indexer after
deployment.

The custom endpoint must: be HTTPS, validate the batch contract from L06, use Entra
auth (`authResourceId`), and return per-record errors — not crash the whole batch.
This lesson does NOT deploy an Azure Function or configure inbound authentication.

Code path:
  Validate SKILL_ENDPOINT_URL. Load skillset.json → clone → insert WebApiSkill →
  PUT derived skillset. Clone indexer.json → retarget skillset → PUT indexer.
  With --run: run_indexer(indexer_name).

What to watch. Preflight: env var checks. With --apply: `skillset saved`, `indexer saved`.
With --run: indexer starts (check execution history in portal for custom-skill errors).

Prerequisites / env vars:
  SEARCH_ENDPOINT       — https://<service>.search.windows.net
  SKILL_ENDPOINT_URL    — HTTPS URL to your deployed WebApiSkill function
  SEARCH_SKILLSET, SEARCH_INDEXER
  --apply               — create/replace skillset + indexer
  --run                 — start indexer after --apply
"""
import argparse
import copy
import importlib.util
import os
from pathlib import Path
from urllib.parse import urlsplit

import httpx
from azure.identity import DefaultAzureCredential

from _shared.config import settings
from _shared.search_client import indexer_client

_API_VERSION = "2025-09-01"
_SCOPE = "https://search.azure.com/.default"
_SKILLSET_JSON = Path(__file__).parent / "skillset_configs" / "skillset.json"
_INDEXER_JSON = Path(__file__).parent / "skillset_configs" / "indexer.json"
_REST_SPEC = importlib.util.spec_from_file_location("_search_rest", Path(__file__).with_name("_search_rest.py"))
assert _REST_SPEC and _REST_SPEC.loader
_REST = importlib.util.module_from_spec(_REST_SPEC)
_REST_SPEC.loader.exec_module(_REST)
load_definition = _REST.load_definition


def custom_skill_url() -> str:
    url = os.environ.get("CUSTOM_SKILL_URL", "")
    parsed = urlsplit(url)
    if parsed.scheme != "https" or not parsed.netloc:
        raise SystemExit("Set CUSTOM_SKILL_URL to a reachable HTTPS endpoint; do not use localhost.")
    return url


def skillset_definition(base: dict, endpoint: str, name: str) -> dict:
    """Insert WebApiSkill before chunking so its normalized text is embedded."""
    definition = copy.deepcopy(base)
    definition["name"] = name
    for skill in definition.get("skills", []):
        if skill.get("name") == "split-document":
            skill["inputs"][0]["source"] = "/document/normalized_text"
    definition["skills"].insert(
        0,
        {
            "@odata.type": "#Microsoft.Skills.Custom.WebApiSkill",
            "name": "normalize-northwind-text",
            "description": "Calls lesson 06's custom-skill endpoint.",
            "context": "/document",
            "uri": endpoint,
            "httpMethod": "POST",
            "timeout": "PT30S",
            "batchSize": 10,
            "degreeOfParallelism": 1,
            "inputs": [{"name": "text", "source": "/document/content"}],
            "outputs": [{"name": "normalized_text", "targetName": "normalized_text"}],
        },
    )
    return definition


def indexer_definition(base: dict, skillset_name: str) -> dict:
    definition = copy.deepcopy(base)
    definition["skillsetName"] = skillset_name
    return definition


def _put(resource: str, definition: dict) -> None:
    endpoint = settings().require("SEARCH_ENDPOINT")
    token = DefaultAzureCredential().get_token(_SCOPE).token
    response = httpx.put(
        f"{endpoint}/{resource}/{definition['name']}?api-version={_API_VERSION}",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=definition,
        timeout=60.0,
    )
    response.raise_for_status()


def preflight() -> dict[str, bool]:
    return {
        "search_endpoint_configured": bool(settings().search_endpoint),
        "custom_skill_url_configured": bool(os.environ.get("CUSTOM_SKILL_URL")),
        "search_indexer_configured": bool(settings().search_indexer),
    }


def apply() -> str:
    endpoint = custom_skill_url()
    base_skillset = load_definition(_SKILLSET_JSON)
    skillset_name = f"{base_skillset['name']}-custom"
    _put("skillsets", skillset_definition(base_skillset, endpoint, skillset_name))
    _put("indexers", indexer_definition(load_definition(_INDEXER_JSON), skillset_name))
    return skillset_name


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Preflight or deploy the custom Search skill pipeline.")
    parser.add_argument("--apply", action="store_true", help="Create/update custom skillset and retarget indexer.")
    parser.add_argument("--run", action="store_true", help="Start the retargeted indexer after --apply.")
    args = parser.parse_args(argv)
    if not args.apply:
        if args.run:
            parser.error("--run requires --apply, so the indexer cannot run an unverified skillset.")
        checks = preflight()
        print("Custom Search skill deployment preflight. No cloud calls made.")
        for name, configured in checks.items():
            print(f"- {name}: {'configured' if configured else 'missing'}")
        print("- Endpoint must validate WebApiSkill batches and authenticate inbound Search requests.")
        return
    name = apply()
    print(f"Skillset '{name}' deployed and indexer retargeted.")
    if args.run:
        indexer_client().run_indexer(settings().search_indexer)
        print(f"Indexer '{settings().search_indexer}' run started.")


if __name__ == "__main__":
    main()
