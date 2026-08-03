"""Content Understanding — domain-specific `prebuilt-invoice` analyzer.

Reads a sample Northwind invoice, extracts vendor/amount/line items, then
prints the structured field dump the agent can consume.
"""
from _shared.config import SAMPLE_DATA
from _shared.cu_client import analyze

# For a demo, host the invoice publicly (SAS URL / static site) — CU's REST
# route takes a URL, not raw bytes for `analyzers/{id}:analyze`. If you want
# a fully local demo, use the ContentUnderstandingClient SDK's begin_analyze_binary.
# We keep the file path here for reference in the docs.
_INVOICE_LOCAL = SAMPLE_DATA / "invoices" / "northwind_sample_invoice.pdf"


def main() -> None:
    # Replace with the accessible URL of the invoice PDF (Blob SAS is easiest).
    invoice_url = f"file://{_INVOICE_LOCAL}"  # placeholder; upload + swap
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
