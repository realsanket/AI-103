# Run: uv run python 05-information-extraction/11_cu_invoice.py
"""Content Understanding `prebuilt-invoice` — extract structured invoice fields.

`prebuilt-invoice` extracts vendor name/address, customer name/address, invoice
date, due date, invoice total, subtotal, tax, and line items from any invoice PDF.
Fields come back as a structured dict in `result.contents[0].fields`. Same async
submit-poll pattern as other CU analyzers.

This is extraction, not payment approval. A field's presence doesn't prove
correctness — validate totals/dates against deterministic business rules. Lesson 15
shows how to pass extracted fields to a model for bounded review.

CU fetches the URL server-side. `file://` paths don't work. Upload your invoice
PDF to Blob Storage, generate a read-only SAS URL, set SAMPLE_INVOICE_URL.

Code path:
  SAMPLE_INVOICE_URL → validate (no file://) → analyze("prebuilt-invoice") → poll →
  print status and contents[0].fields.

What to watch. A dict with VendorName, InvoiceTotal, InvoiceDate, Items, etc.
Confidence scores appear per field when configured. Missing fields mean the layout
couldn't extract them — inspect the source PDF.

Prerequisites / env vars:
  CU_ENDPOINT        — https://<resource>.services.ai.azure.com
  CU_API_VERSION     — 2025-11-01 (GA)
  SAMPLE_INVOICE_URL — HTTPS Blob SAS URL to an invoice PDF (required)
"""
import os

from _shared.config import SAMPLE_DATA
from _shared.cu_client import analyze


def main() -> None:
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
    print("status:", result.get("status"))
    contents = result.get("result", {}).get("contents", [])
    if not contents:
        return
    fields = contents[0].get("fields", {})
    for name, data in fields.items():
        print(f"  {name}: {data}")


if __name__ == "__main__":
    main()
