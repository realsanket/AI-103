"""Custom skill contract — Azure Function receiving the AI Search WebApi payload.

Deployed as an Azure Function; wired into a skillset via `WebApiSkill`. The
skill contract is: input `{values: [{recordId, data}]}`; output the same shape
with the transformation added.

This module can also be run locally as `python 06_search_custom_skill.py` to
exercise the pure function against a sample payload — no HTTP needed.
"""
import json


def transform(record_data: dict) -> dict:
    """Toy transform: normalize a CloudXeus product code + flag SLA tier."""
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
