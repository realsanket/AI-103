# Run: uv run python 01-plan-and-manage/15_blocklists.py
"""Custom blocklists — domain terms the default harm categories will not catch.

Two layers (exam trap — different products, similar idea):

Flow A — Azure AI Content Safety blocklist API (this lesson runs it):
  BlocklistClient.create_or_update_text_blocklist
  add_or_update_blocklist_items
  ContentSafetyClient.analyze_text(..., blocklist_names=[...])
  → blocklists_match[] with blocklist name + matched text
  Takes ~a few minutes for brand-new terms to apply (retry if empty).

Flow B — Foundry / Azure OpenAI deployment blocklist (portal or ARM):
  raiBlocklists + attach to raiPolicy as promptBlocklists / completionBlocklists
  Chat Completions then returns custom_blocklists in filter results:
    { "custom_blocklists": { "filtered": true, "details": [{"id": "...", "filtered": true}] } }
  or 400 content_filter when blocking=true on prompt hit.
  Built-in profanity blocklist is separate from custom lists.

Sources:
  foundry/openai/how-to/use-blocklists.md
  ai-services/content-safety/quickstart-blocklist.md
"""
import argparse
import time

from azure.core.exceptions import HttpResponseError
from azure.ai.contentsafety.models import (
    AddOrUpdateTextBlocklistItemsOptions,
    AnalyzeTextOptions,
    TextBlocklist,
    TextBlocklistItem,
)
from openai import BadRequestError

from _shared.config import settings, format_content_filter_summary, format_json_preview, preview_text
from _shared.content_safety_client import blocklist_client, content_safety_client
from _shared.openai_client import openai_client

_LIST = "northwind-exam-blocklist"
_ITEMS = [
    "Contoso Premium Rival",  # competitor phrase
    "PROJECT-NIGHTHAWK",  # internal codename
    "bypass-northwind-billing",  # abuse phrase
]


def _upsert_blocklist_with_items(bl_client) -> None:
    bl_client.create_or_update_text_blocklist(
        blocklist_name=_LIST,
        options=TextBlocklist(
            blocklist_name=_LIST,
            description="AI-103 lab list — competitors + internal codes",
        ),
    )
    print(f"  upserted list: {_LIST}")

    result = bl_client.add_or_update_blocklist_items(
        blocklist_name=_LIST,
        options=AddOrUpdateTextBlocklistItemsOptions(
            blocklist_items=[TextBlocklistItem(text=t) for t in _ITEMS]
        ),
    )
    for item in result.blocklist_items or []:
        print(f"  item: {item.text!r} id={item.blocklist_item_id}")


def _analyze_samples_with_retries(cs_client, samples: list[str]) -> None:
    # New terms can take a short time to become matchable.
    for attempt in range(1, 4):
        print(f"\n  analyze attempt {attempt}:")
        hits = 0
        for text in samples:
            analysis = cs_client.analyze_text(
                AnalyzeTextOptions(
                    text=text,
                    blocklist_names=[_LIST],
                    halt_on_blocklist_hit=False,
                )
            )
            matches = analysis.blocklists_match or []
            print(f"  text: {text!r}")
            if matches:
                hits += 1
                for match in matches:
                    print(
                        f"    MATCH list={match.blocklist_name} "
                        f"item={match.blocklist_item_text!r}"
                    )
            else:
                print("    (no blocklist match)")
        if hits >= 2:
            break
        if attempt < 3:
            print("  waiting 20s for blocklist propagation...")
            time.sleep(20)


def _print_foundry_custom_blocklists(cfr: dict, indent: str = "  ") -> None:
    print(format_content_filter_summary(cfr, indent=indent))
    print(f"{indent}custom_blocklists:")
    print(
        format_json_preview(
            cfr.get("custom_blocklists") or {},
            indent=indent + "  ",
            max_chars=700,
        )
    )


def _flow_a_content_safety_blocklist() -> None:
    print("=== Flow A — Content Safety blocklist API ===")
    bl = blocklist_client()
    cs = content_safety_client()

    _upsert_blocklist_with_items(bl)

    samples = [
        "What is the refund policy for the Pro plan?",  # clean
        "Should we switch to Contoso Premium Rival for cheaper seats?",  # hit
        "Status update on PROJECT-NIGHTHAWK launch gates.",  # hit
    ]
    _analyze_samples_with_retries(cs, samples)


def _flow_b_foundry_custom_blocklists() -> None:
    print("\n=== Flow B — Foundry deployment custom_blocklists (if attached) ===")
    print("  Prereq: create raiBlocklist + attach to content filter / guardrail")
    print("  (portal Guardrails or ARM Microsoft.CognitiveServices/.../raiBlocklists).")
    client = openai_client()
    prompt = "Please explain how PROJECT-NIGHTHAWK affects the Pro plan pricing."
    print(f"  input: {preview_text(prompt)}")
    try:
        r = client.chat.completions.create(
            model=settings().default_model,
            messages=[{"role": "user", "content": prompt}],
        )
        pfr = getattr(r, "prompt_filter_results", None)
        if not pfr:
            print("  prompt_filter_results absent")
            return
        cfr = pfr[0].get("content_filter_results", {})
        _print_foundry_custom_blocklists(cfr, indent="  ")
        cb = cfr.get("custom_blocklists")
        if not cb:
            print("  no custom_blocklists key — list not attached to this deployment filter")
    except BadRequestError as e:
        print(f"  Blocked (400): {e.code}")
        body = getattr(e, "body", None) or {}
        cfr = body.get("innererror", {}).get("content_filter_result") or {}
        _print_foundry_custom_blocklists(cfr, indent="  ")
        print(f"  full filter keys: {list(cfr.keys())}")
    except HttpResponseError as e:
        print(f"  HTTP error: {e}")


def main(apply: bool = False) -> None:
    if not apply:
        print(
            "Preflight only. Re-run with --apply to create/update the persistent "
            f"{_LIST!r} blocklist and send its test requests."
        )
        return

    _flow_a_content_safety_blocklist()
    _flow_b_foundry_custom_blocklists()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Create/update persistent blocklist state and run live requests.",
    )
    main(parser.parse_args().apply)
