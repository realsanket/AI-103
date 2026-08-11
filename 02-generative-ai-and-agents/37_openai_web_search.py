# Run: uv run python 02-generative-ai-and-agents/37_openai_web_search.py [--apply] [--query "<text>"]
"""Use the built-in web_search_preview tool to ground responses in live web results.

The Responses API exposes a built-in web_search_preview tool that sends queries
to Bing and injects top results as context before the model answers. The model
cites sources via annotations. No external Bing API key is needed — adding the
tool to the request activates it. This is NOT the same as Azure AI Search or
Bing Search SDK; it is a zero-config built-in for the Responses API.

Default preflight checks env. --apply calls the Responses API with
{"type": "web_search_preview"} and prints the answer plus URL citations.
This proves grounding in live results vs static training knowledge.

Code path:
  --apply: openai_client().responses.create(model=..., input=query,
  tools=[{"type": "web_search_preview"}])
  → output_text contains grounded answer
  → output items with annotations holding cited URLs.

What to watch. output_text has up-to-date content. annotations[] holds URLs
the model cited. output items include a web_search_call item showing what
query was sent to Bing.

Prerequisites / env vars:
  PROJECT_ENDPOINT  — Foundry project HTTPS URL
  DEFAULT_MODEL     — deployed chat model (must support web_search_preview)
  --query           — search query (default: recent Azure AI Foundry features)
  --apply           — send request
"""
import argparse

from _shared.config import settings
from _shared.openai_client import openai_client

_DEFAULT_QUERY = "What are the latest Azure AI Foundry features announced this year?"


def preflight() -> None:
    current = settings()
    print("Web search preflight (no cloud calls).")
    print(f"- model: {current.default_model or 'missing DEFAULT_MODEL'}")
    print("- tool: web_search_preview (built-in, no Bing key required)")
    print("- grounding: live Bing results injected as context before model answers")
    print("- citations: returned as annotations on output items")
    print("Run --apply to search and see live-grounded response with URL citations.")


def apply(query: str) -> None:
    client = openai_client()
    model = settings().require("DEFAULT_MODEL")
    print(f"Query: {query!r}")
    response = client.responses.create(
        model=model,
        input=query,
        tools=[{"type": "web_search_preview"}],
    )
    print(f"\nAnswer:\n{response.output_text}")

    urls: list[str] = []
    for item in (response.output or []):
        for ann in getattr(item, "annotations", None) or []:
            url = getattr(ann, "url", None)
            if url and url not in urls:
                urls.append(url)

    if urls:
        print("\nCited URLs:")
        for url in urls:
            print(f"  {url}")
    else:
        print("\n(No URL annotations in this response)")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Use web_search_preview tool for live-grounded answers.")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--query", default=_DEFAULT_QUERY)
    args = parser.parse_args(argv)
    if not args.apply:
        preflight()
        return
    apply(args.query)


if __name__ == "__main__":
    main()
