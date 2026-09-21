# Run: uv run python 05-information-extraction/23_knowledge_source_web.py [--apply]
"""Create a **remote web** knowledge source backed by Grounding with Bing.

Where blob and search-index knowledge sources (lessons 21-22) are *indexed*,
this one is *remote*: nothing is ingested. At query time, the retrieval
engine asks Bing Custom Search, then summarizes the results with an LLM
before injecting them into the knowledge base response. The knowledge base
must reference an LLM model — web content is always summarized, never
verbatim (see docs' "Limitations and considerations").

Use `allowedDomains` / `blockedDomains` to constrain scope. With no domains,
the source has unrestricted access to the entire public internet. The web
kind is First-Party Consumption Service, waives DPA/geo commitments, and is
billed by Bing — read the warnings in the doc header before enabling.

Code path:
  build_body() sets one allowed domain (learn.microsoft.com) and one blocked
  (bing.com) as the doc's example. Preflight prints JSON. With --apply: PUT
  /knowledgesources/<name>?api-version=2026-08-01-preview.

What to watch. `knowledge source '<name>' saved.` A 403 with "Web knowledge
source not enabled" means an Azure admin has disabled the feature on the
subscription (see agentic-knowledge-source-how-to-web-manage.md). A 400 in a
private/sovereign cloud region means web is public-cloud only.

Prerequisites / env vars:
  SEARCH_ENDPOINT           — https://<service>.search.windows.net
  SEARCH_KNOWLEDGE_SOURCE   — knowledge source name (default northwind-web-ks)
  SEARCH_WEB_ALLOWED_DOMAIN — allowed domain (default learn.microsoft.com)
  SEARCH_WEB_BLOCKED_DOMAIN — blocked domain (default bing.com)
"""
import argparse
import json
import os

from _search_rest import _PREVIEW_API_VERSION, put_named


def configuration() -> dict[str, str]:
    return {
        "name": os.environ.get("SEARCH_KNOWLEDGE_SOURCE", "northwind-web-ks"),
        "allowed": os.environ.get("SEARCH_WEB_ALLOWED_DOMAIN", "learn.microsoft.com"),
        "blocked": os.environ.get("SEARCH_WEB_BLOCKED_DOMAIN", "bing.com"),
    }


def build_body(cfg: dict[str, str]) -> dict:
    return {
        "name": cfg["name"],
        "kind": "web",
        "description": "Remote web knowledge source (Grounding with Bing Custom Search).",
        "encryptionKey": None,
        "webParameters": {
            "domains": {
                "allowedDomains": [{"address": cfg["allowed"], "includeSubpages": True}],
                "blockedDomains": [{"address": cfg["blocked"], "includeSubpages": False}],
            }
        },
    }


def preflight(cfg: dict[str, str]) -> None:
    print("Web knowledge source preflight. No cloud calls made.")
    for key, value in cfg.items():
        print(f"- {key}: {'configured' if value else 'missing'}")
    print(f"- api-version: {_PREVIEW_API_VERSION}")
    print("Planned request body:")
    print(json.dumps(build_body(cfg), indent=2))
    print("- Web knowledge source is billed by Bing and waives DPA/geo commitments.")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Create a web knowledge source (Grounding with Bing).")
    parser.add_argument("--apply", action="store_true", help="Send the PUT request to Search.")
    args = parser.parse_args(argv)
    cfg = configuration()
    if not args.apply:
        preflight(cfg)
        print("- Rerun with --apply to create the knowledge source.")
        return
    put_named("knowledgesources", cfg["name"], build_body(cfg), _PREVIEW_API_VERSION)
    print(f"knowledge source '{cfg['name']}' saved.")


if __name__ == "__main__":
    main()
