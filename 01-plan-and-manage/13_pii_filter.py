# Run: uv run python 01-plan-and-manage/13_pii_filter.py
"""PII filter (preview) — detect personal data in model OUTPUT.

Foundry guardrail control scans completions for personally identifiable
information (email, phone, SSN, credit card, government IDs, Azure keys, ...).

Annotation shape (choice content_filter_results / error body):
  pii  OR  personally_identifiable_information
    detected: true/false
    filtered: true/false
    redacted: true/false   (when redaction enabled)
  Newer payloads may also include redacted_text + sub_categories.

Modes:
  Annotate           → output returned; PII flagged
  Annotate and block → entire completion blocked (400 content_filter)

Intervention point: model output (not user input).
API version note: PII needs 2025-01-01-preview or later on classic filter APIs.

Prereq: enable PII on deployment guardrail in Foundry portal
  (Guardrails → create/edit → Personally identifiable information).

Sources:
  foundry/openai/concepts/content-filter-personal-information.md
  foundry/guardrails/how-to-create-guardrails.md
"""
import json

from openai import BadRequestError

from _shared.config import settings
from _shared.openai_client import openai_client

# Synthetic examples only — never real personal data in labs.
_SAFE = "Explain Northwind's Pro plan refund window in one sentence."

_PII_PROMPT = (
    "Create a fake support ticket contact card for demo data. "
    "Use these exact synthetic values (not real people): "
    "name Jane Demo, email jane.demo@example.com, phone 555-0100, "
    "SSN 123-45-6789. Print them in plain text."
)


def _extract_pii(cfr: dict) -> dict:
    return cfr.get("pii") or cfr.get("personally_identifiable_information") or {}


def _print_pii(cfr: dict, label: str) -> None:
    pii = _extract_pii(cfr)
    print(f"  [{label}]")
    if not pii:
        print("  pii key absent — enable PII (preview) on deployment guardrail")
        # show what did come back so students can map other keys
        print(f"  keys present: {sorted(cfr.keys())}")
        return
    if isinstance(pii, dict):
        for k in ("detected", "filtered", "redacted"):
            if k in pii:
                print(f"  pii.{k}: {pii.get(k)}")
        if pii.get("redacted_text"):
            print(f"  pii.redacted_text: {pii['redacted_text'][:200]!r}")
        if pii.get("sub_categories"):
            print(f"  pii.sub_categories: {pii['sub_categories']}")
    else:
        print(f"  pii: {pii}")


def _run(prompt: str, label: str) -> None:
    client = openai_client()
    try:
        r = client.chat.completions.create(
            model=settings().default_model,
            messages=[{"role": "user", "content": prompt}],
        )
        text = (r.choices[0].message.content or "")[:240]
        print(f"\n=== {label} ===")
        print(f"  finish_reason: {r.choices[0].finish_reason}")
        print(f"  reply_preview: {text!r}")
        cf = getattr(r.choices[0], "content_filter_results", None) or {}
        if hasattr(cf, "model_dump"):
            cf = cf.model_dump()
        elif hasattr(cf, "to_dict"):
            cf = cf.to_dict()
        elif not isinstance(cf, dict):
            cf = dict(cf) if cf else {}
        _print_pii(cf, "choice.content_filter_results")
        # some gateways also mirror on prompt_filter_results — rare for PII
        pfr = getattr(r, "prompt_filter_results", None)
        if pfr:
            _print_pii(pfr[0].get("content_filter_results", {}), "prompt_filter_results")
    except BadRequestError as e:
        print(f"\n=== {label} ===")
        print(f"  Blocked (400): {e.code}")
        body = getattr(e, "body", None) or {}
        cfr = body.get("innererror", {}).get("content_filter_result") or {}
        _print_pii(cfr, "error.content_filter_result")
        print(f"  raw_inner: {json.dumps(cfr, indent=2)[:800]}")


def main() -> None:
    print("PII filter scans MODEL OUTPUT (completion), not the user prompt.")
    _run(_SAFE, "Safe prompt (no PII expected in output)")
    _run(_PII_PROMPT, "Synthetic PII prompt (expect detect / block / redact)")


if __name__ == "__main__":
    main()
