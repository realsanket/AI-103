"""Content Understanding — domain-specific `prebuilt-invoice` analyzer.

Beginner note:
  `prebuilt-invoice` extracts vendor / customer / total / line items /
  dates from any invoice PDF. Same async pattern as other CU analyzers:
  submit URL → poll → read `result.contents[0].fields`.

  IMPORTANT: CU fetches the URL server-side. `file://` URLs won't work.
  Upload your invoice PDF to Blob Storage, generate a SAS URL, and set
  `SAMPLE_INVOICE_URL` in your environment.
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
