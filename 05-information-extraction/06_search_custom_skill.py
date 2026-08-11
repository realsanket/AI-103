# Run: uv run python 05-information-extraction/06_search_custom_skill.py
"""Custom WebApiSkill contract — local demonstration of the Search enrichment payload.

Azure AI Search calls a WebApiSkill with a batch of records: each record has a
`recordId` and a `data` dict. The skill must return the same shape with transformed
data plus optional errors/warnings. This lesson implements that contract as a pure
function and exercises it locally against a sample payload — no cloud call, no HTTP.

This is NOT a hosted custom skill. To use it in Search: host it as an HTTPS Azure
Function, validate the contract, configure `authResourceId` for Entra auth, set
batch size/timeout, and wire it into the skillset JSON. Lesson 17 deploys the
derived pipeline with this contract.

Code path:
  main() builds two sample records → handle_batch() calls transform() per record →
  transform() normalizes text and detects SLA tier (Bronze/Silver/Gold/Platinum) →
  print JSON output.

What to watch. Two output records with `normalized_text` and `sla_tier`. GOLD and
PLATINUM should be detected. A record with no matching tier gets `sla_tier: null`.

Prerequisites / env vars:
  None — runs entirely locally with no cloud dependencies.
"""
import json


def transform(record_data: dict) -> dict:
    """Toy transform: normalize a Northwind product code + flag SLA tier."""
    text = record_data.get("text", "")
    upper = text.upper()
    tier = next((t for t in ("BRONZE", "SILVER", "GOLD", "PLATINUM") if t in upper), None)
    return {
        "normalized_text": text.strip().lower(),
        "sla_tier": tier,
    }


def handle_batch(payload: dict) -> dict:
    """Custom Skill contract handler."""
    out = []
    for record in payload.get("values", []):
        out.append(
            {
                "recordId": record.get("recordId"),
                "data": transform(record.get("data", {})),
                "errors": [],
                "warnings": [],
            }
        )
    return {"values": out}


def main() -> None:
    sample = {
        "values": [
            {"recordId": "0", "data": {"text": "Gold-tier SLA promises 4 hour response."}},
            {"recordId": "1", "data": {"text": "  Ticket for Silver customer  "}},
        ]
    }
    print(json.dumps(handle_batch(sample), indent=2))


if __name__ == "__main__":
    main()
