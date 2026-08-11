# Run: uv run python 05-information-extraction/15_cu_content_agent.py
"""CU invoice extraction → ephemeral Foundry agent → bounded business review.

Two-stage pipeline: (1) CU `prebuilt-invoice` extracts structured fields from
an invoice PDF, (2) an ephemeral Foundry agent with inline instructions reasons
over those fields to produce a business-friendly summary, approval status, issues
found, and recommended next step. The agent is created inline — no pre-created
agent from lesson 07 needed.

This separates extraction from reasoning. CU does extraction; the model does bounded
business analysis. Model output is a proposed review, NOT an automated approval —
validate extracted fields against deterministic rules and require human approval
for consequential actions.

Code path:
  _extract_fields() → analyze("prebuilt-invoice") → format fields as prompt text.
  project_client() → create_version(PromptAgentDefinition with inline instructions) →
  responses.create() with formatted invoice fields → print output_text.

What to watch. Business summary, approval status (e.g., "Approved / Issues found"),
any discrepancies flagged, and next step. If the agent invents values not in the
fields, the instructions aren't working — tighten them.

Prerequisites / env vars:
  CU_ENDPOINT        — https://<resource>.services.ai.azure.com
  PROJECT_ENDPOINT   — Foundry project endpoint
  DEFAULT_MODEL      — deployed chat model
  SAMPLE_INVOICE_URL — HTTPS Blob SAS URL to an invoice PDF (required)
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
