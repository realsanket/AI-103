"""Agent grounded in Content Understanding output.

Pipe an invoice through CU → feed extracted fields to an agent → agent
produces business-friendly review + recommended next step. Demonstrates the
"CU as data prep, agent as reasoning layer" pattern.
"""
from _shared.config import SAMPLE_DATA
from _shared.cu_client import analyze
from _shared.foundry_client import project_client

AGENT_NAME = "cloudxeus-support"

_INVOICE_LOCAL = SAMPLE_DATA / "invoices" / "cloudxeus_sample_invoice.pdf"


def _extract_fields() -> str:
    invoice_url = f"file://{_INVOICE_LOCAL}"
    result = analyze("prebuilt-invoice", invoice_url)
    contents = result.get("result", {}).get("contents", [])
    fields = contents[0].get("fields", {}) if contents else {}
    return "\n".join(f"{name}: {data}" for name, data in fields.items())


def main() -> None:
    fields_dump = _extract_fields()
    project = project_client()
    openai = project.get_openai_client()

    r = openai.responses.create(
        extra_body={"agent_reference": {"type": "agent_reference", "name": AGENT_NAME}},
        input=(
            "Review this invoice using only the extracted fields below.\n\n"
            "Your task:\n"
            "1. Summarize the invoice in business-friendly language.\n"
            "2. Provide an approval status.\n"
            "3. Identify any issues found.\n"
            "4. Recommend the next step.\n\n"
            f"Extracted invoice fields:\n{fields_dump}\n"
        ),
    )
    print("\n--- Agent Invoice Review ---")
    print(r.output_text)


if __name__ == "__main__":
    main()
