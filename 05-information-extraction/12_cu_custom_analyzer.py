# Run: uv run python 05-information-extraction/12_cu_custom_analyzer.py [--propose-schema] [--apply] [--delete]
# Practice-question coverage: Q15, Q41, Q87, Q92.
"""Custom Content Understanding analyzer with confidence, grounding, and review routing.

A custom analyzer combines a `baseAnalyzerId` (prebuilt-document) with a
`fieldSchema` you define. Field methods: `extract` (value as written in the
document), `classify` (map to an enum), `generate` (model-produced value —
not source truth). This lesson builds the `northwind-support-notice` analyzer.

Confidence and grounding are opt-in in GA 2025-11-01:
  - `config.estimateFieldSourceAndConfidence: true` returns a 0–1 `confidence`
    and a `source` location (page + bounding polygon) for every field.
  - Per-field `estimateSourceAndConfidence` overrides the analyzer setting and
    MUST be true for `extract` fields.
  Route fields below 0.80 confidence to human review; show `source` so the
  reviewer jumps to the exact place in the PDF.

Discovering a schema: `--propose-schema` runs the utility analyzer
`prebuilt-documentFieldSchema` on a sample and prints the field schema it
proposes. Review it, then copy the fields you want into `_DEFINITION`.

Code path:
  Default          validate_definition() + print the analyzer JSON; no Azure call.
  --propose-schema analyze("prebuilt-documentFieldSchema", sample) → print proposal.
  --apply          create_analyzer() (persistent) → analyze(sample) when set →
                   review_queue() prints value/confidence/source/needs_review.
  --delete         delete_analyzer() — cleanup for the persistent analyzer.

What to watch. `needs_review=True` for low-confidence fields. `summary` is
generated, so treat it as a draft even when its confidence is high.

Prerequisites / env vars:
  CU_ENDPOINT            — https://<resource>.services.ai.azure.com
  CU_API_VERSION         — 2025-11-01 (GA)
  CU_SUPPORT_NOTICE_URL  — runtime-only HTTPS Blob SAS URL of a sample support
                           notice PDF (secret; never put it in .env.example)
  Roles on the Foundry resource: Cognitive Services Content Understanding
  Reader (analyze only), Contributor (create/update — cannot delete), or Owner
  (includes --delete). Default model deployments must be configured for
  Content Understanding.
"""
import argparse
import json

from _shared.config import env

ANALYZER_ID = "northwind-support-notice"
REVIEW_THRESHOLD = 0.80

_DEFINITION = {
    "description": "Extract Northwind support-notice fields.",
    "baseAnalyzerId": "prebuilt-document",
    "config": {"returnDetails": True, "estimateFieldSourceAndConfidence": True},
    "fieldSchema": {
        "name": "NorthwindSupportNotice",
        "fields": {
            "ticket_id": {
                "type": "string",
                "method": "extract",
                "estimateSourceAndConfidence": True,
                "description": "Support ticket identifier, for example NW-10452.",
            },
            "customer_name": {
                "type": "string",
                "method": "extract",
                "estimateSourceAndConfidence": True,
                "description": "Customer organization named on the notice.",
            },
            "sla_tier": {
                "type": "string",
                "method": "classify",
                "enum": ["Bronze", "Silver", "Gold", "Platinum"],
                "description": "Contracted support tier.",
            },
            "breach_penalty_usd": {
                "type": "number",
                "method": "extract",
                "estimateSourceAndConfidence": True,
                "description": "Penalty in US dollars if the SLA is breached.",
            },
            "summary": {
                "type": "string",
                "method": "generate",
                "description": "Two-sentence summary of the issue and the next step.",
            },
        },
    },
}

_VALUE_KEYS = ("valueString", "valueNumber", "valueInteger", "valueDate", "valueBoolean", "valueTime")


def validate_definition(definition: dict) -> None:
    """Reject definitions GA 2025-11-01 would refuse or that lose grounding."""
    fields = definition["fieldSchema"]["fields"]
    missing = [
        name
        for name, field in fields.items()
        if field.get("method") == "extract" and not field.get("estimateSourceAndConfidence")
    ]
    if missing:
        raise ValueError(f"extract fields need estimateSourceAndConfidence=true: {', '.join(missing)}")
    for name, field in fields.items():
        if field.get("method") == "classify" and not field.get("enum"):
            raise ValueError(f"classify field {name!r} needs an enum")


def review_queue(fields: dict, threshold: float = REVIEW_THRESHOLD) -> list[dict]:
    """One row per field; missing confidence counts as needing review."""
    rows = []
    for name, field in fields.items():
        confidence = field.get("confidence")
        value = next((field[key] for key in _VALUE_KEYS if key in field), None)
        rows.append(
            {
                "field": name,
                "value": value,
                "confidence": confidence,
                "source": field.get("source"),
                "needs_review": confidence is None or confidence < threshold,
            }
        )
    return rows


def _first_content(result: dict) -> dict:
    contents = result.get("result", {}).get("contents") or [{}]
    return contents[0]


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--propose-schema", action="store_true", help="Run prebuilt-documentFieldSchema on the sample.")
    parser.add_argument("--apply", action="store_true", help="Create the analyzer and analyze the sample.")
    parser.add_argument("--delete", action="store_true", help="Delete the custom analyzer.")
    parser.add_argument("--threshold", type=float, default=REVIEW_THRESHOLD)
    args = parser.parse_args(argv)

    validate_definition(_DEFINITION)
    source = env("CU_SUPPORT_NOTICE_URL")

    if args.delete:
        from _shared.cu_client import delete_analyzer

        print("deleted." if delete_analyzer(ANALYZER_ID) else "analyzer not found.")
        return

    if args.propose_schema:
        if not source:
            raise SystemExit("Set CU_SUPPORT_NOTICE_URL in your shell to propose a schema.")
        from _shared.cu_client import analyze

        proposal = _first_content(analyze("prebuilt-documentFieldSchema", source))
        print("Proposed field schema (review before copying into _DEFINITION):")
        print(json.dumps(proposal.get("fields", proposal), indent=2)[:4000])
        return

    if not args.apply:
        print(f"Analyzer '{ANALYZER_ID}' definition (validated; no Azure call):")
        print(json.dumps(_DEFINITION, indent=2))
        print("Re-run with --apply to create it (persistent) and --delete to clean up.")
        return

    from _shared.cu_client import analyze, create_analyzer

    print(f"creating analyzer '{ANALYZER_ID}'...")
    create_analyzer(ANALYZER_ID, _DEFINITION)
    print(f"analyzer '{ANALYZER_ID}' ready.")
    if not source:
        print("Set CU_SUPPORT_NOTICE_URL in your shell to analyze a sample notice.")
        return
    fields = _first_content(analyze(ANALYZER_ID, source)).get("fields", {})
    for row in review_queue(fields, args.threshold):
        flag = "REVIEW" if row["needs_review"] else "auto"
        print(f"{flag:<6} {row['field']:<20} {row['value']!r:<30} confidence={row['confidence']} source={row['source']}")
    print("Delete when finished: uv run python 05-information-extraction/12_cu_custom_analyzer.py --delete")


if __name__ == "__main__":
    main()
