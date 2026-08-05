"""Agent grounded in Content Understanding output.

Beginner note:
  Pipeline: invoice PDF → CU `prebuilt-invoice` extracts fields → an
  ephemeral agent reasons over those fields → business-friendly review.

  Two things fixed vs the older version:
  1. Agent is ephemeral (`instructions=` inline) — no missing agent lookup.
  2. Invoice URL comes from `SAMPLE_INVOICE_URL` env var — no `file://`
     (CU cannot fetch local files; upload to Blob and use a SAS URL).
"""
import os

from _shared.config import SAMPLE_DATA, settings
from _shared.cu_client import analyze
from _shared.foundry_client import project_client

_INSTRUCTIONS = (
    "You are a Northwind operations reviewer. Given extracted invoice fields, "
    "produce a business-friendly summary, an approval status, any issues found, "
    "and the recommended next step. Do not invent values that aren't in the fields."
)


def _extract_fields() -> str:
    invoice_url = os.environ.get("SAMPLE_INVOICE_URL")
    if not invoice_url:
        local = SAMPLE_DATA / "invoices" / "northwind_sample_invoice.pdf"
        raise SystemExit(
            "Set SAMPLE_INVOICE_URL to a Blob SAS URL of an invoice PDF.\n"
            f"  Example candidate to upload: {local}"
        )
    if invoice_url.startswith("file://"):
        raise SystemExit("CU cannot fetch file:// URLs — upload to Blob and use a SAS URL.")

    result = analyze("prebuilt-invoice", invoice_url)
    contents = result.get("result", {}).get("contents", [])
    fields = contents[0].get("fields", {}) if contents else {}
    return "\n".join(f"{name}: {data}" for name, data in fields.items())


def main() -> None:
    fields_dump = _extract_fields()

    project = project_client()
    openai = project.get_openai_client()
    r = openai.responses.create(
        model=settings().default_model,
        instructions=_INSTRUCTIONS,
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
