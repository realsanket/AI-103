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
import os
from dataclasses import dataclass

from openai import BadRequestError

from _shared.config import settings, preview_text, format_json_preview, format_hit_categories
from _shared.openai_client import openai_client

# Synthetic examples only — never real personal data in labs.
_SAFE = "Explain Northwind's Pro plan refund window in one sentence."

_PII_PROMPT = (
    "Create a fake support ticket contact card for demo data. "
    "Use these exact synthetic values (not real people): "
    "name Jane Demo, email jane.demo@example.com, phone 555-0100, "
    "SSN 123-45-6789. Print them in plain text."
)

# Default to the dedicated PII-guardrail deployment, but allow easy override.
_PII_MODEL = os.getenv("PII_GUARDRAIL_MODEL", "gpt-5.1-gudrail-test")


@dataclass
class RunObservation:
    label: str
    blocked: bool
    pii_present: bool
    detected: bool | None
    filtered: bool | None
    redacted: bool | None


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
        sub_categories = pii.get("sub_categories")
        if isinstance(sub_categories, list) and sub_categories:
            print(f"  pii.sub_categories.total: {len(sub_categories)}")
            print(
                f"  pii.sub_categories.detected: "
                f"{format_hit_categories(sub_categories, 'detected')}"
            )
            print(
                f"  pii.sub_categories.filtered: "
                f"{format_hit_categories(sub_categories, 'filtered')}"
            )
            print(
                f"  pii.sub_categories.redacted: "
                f"{format_hit_categories(sub_categories, 'redacted')}"
            )
    else:
        print(f"  pii: {pii}")


def _pii_flags(cfr: dict) -> tuple[bool, bool | None, bool | None, bool | None]:
    pii = _extract_pii(cfr)
    if not isinstance(pii, dict) or not pii:
        return False, None, None, None
    return True, pii.get("detected"), pii.get("filtered"), pii.get("redacted")


def _run(prompt: str, label: str) -> RunObservation:
    client = openai_client()
    try:
        print(f"\n=== {label} ===")
        print("  Input text sent:")
        print(f"    {preview_text(prompt)}")
        r = client.chat.completions.create(
            model=_PII_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        text = (r.choices[0].message.content or "")[:240]
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
        pii_present, detected, filtered, redacted = _pii_flags(cf)
        # some gateways also mirror on prompt_filter_results — rare for PII
        pfr = getattr(r, "prompt_filter_results", None)
        if pfr:
            _print_pii(pfr[0].get("content_filter_results", {}), "prompt_filter_results")
            if not pii_present:
                pii_present, detected, filtered, redacted = _pii_flags(
                    pfr[0].get("content_filter_results", {})
                )
        return RunObservation(
            label=label,
            blocked=False,
            pii_present=pii_present,
            detected=detected,
            filtered=filtered,
            redacted=redacted,
        )
    except BadRequestError as e:
        print(f"\n=== {label} ===")
        print("  Input text sent:")
        print(f"    {preview_text(prompt)}")
        print(f"  Blocked (400): {e.code}")
        body = getattr(e, "body", None) or {}
        cfr = body.get("innererror", {}).get("content_filter_result") or {}
        _print_pii(cfr, "error.content_filter_result")
        pii_blob = _extract_pii(cfr)
        if pii_blob:
            print("  raw_pii_preview:")
            print(format_json_preview(pii_blob, indent="    ", max_chars=700))
        pii_present, detected, filtered, redacted = _pii_flags(cfr)
        return RunObservation(
            label=label,
            blocked=True,
            pii_present=pii_present,
            detected=detected,
            filtered=filtered,
            redacted=redacted,
        )


def _print_learning_guide() -> None:
    print("\nWhat this lesson demonstrates:")
    print("  1) Safe prompt: usually no PII signals in output")
    print("  2) Synthetic PII prompt: should trigger detect/filter/redact when enabled")
    print("\nHow to read outcomes:")
    print("  - pii.detected=True: PII found in model output")
    print("  - pii.filtered=True: output policy intervened")
    print("  - pii.redacted=True: sensitive values masked")
    print("  - 400 content_filter: full block mode is active")


def _print_summary(observations: list[RunObservation]) -> None:
    print("\n=== Learner summary ===")
    for obs in observations:
        print(f"  - {obs.label}")
        print(f"    blocked: {obs.blocked}")
        print(f"    pii_present: {obs.pii_present}")
        print(f"    detected: {obs.detected}")
        print(f"    filtered: {obs.filtered}")
        print(f"    redacted: {obs.redacted}")

    pii_seen = any(o.pii_present for o in observations)
    if pii_seen:
        print("\nInterpretation: PII guardrail is active on this deployment path.")
        return

    print("\nInterpretation: PII guardrail metadata was not returned.")
    print("Next checks:")
    print("  1) Confirm PII is enabled and published on this exact deployment")
    print("  2) Wait briefly for policy propagation, then rerun")
    print("  3) Verify the request path/version supports PII preview metadata")


def main() -> None:
    print("PII filter scans MODEL OUTPUT (completion), not the user prompt.")
    print(f"Using deployment: {_PII_MODEL}")
    _print_learning_guide()
    safe_obs = _run(_SAFE, "Safe prompt (no PII expected in output)")
    pii_obs = _run(_PII_PROMPT, "Synthetic PII prompt (expect detect / block / redact)")
    _print_summary([safe_obs, pii_obs])


if __name__ == "__main__":
    main()
