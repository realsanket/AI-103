# Run: uv run python 09-current-ai-services-other/05_custom_neural_preflight.py [--apply]
"""Preflight and (opt-in) build a Document Intelligence v4.0 custom neural model.

Custom neural targets structured + semi-structured documents with labeled
examples. Requires ≥5 labeled samples; training data must represent real
template/language/value/table variation. v4.0 supports signature detection,
table cell confidence, and overlapping fields.

Default preflight validates model ID pattern (1-64 chars, [A-Za-z0-9._~-]),
container HTTPS URL, and training-hour range (0.5-10). No cloud call.
`--apply` starts a persistent + billable model build via
DocumentIntelligenceAdministrationClient and WAITS for the poller to
complete. v4.0 includes 10 free training hours; excess bills, 30-min minimum
per job.

Custom neural training has limited regional availability. Confirm
training-region support before creating the resource. You can copy a
trained model to another region for analysis where supported.

Code path:
  preflight(): validate MODEL_ID regex, DI_TRAINING_CONTAINER_URL shape,
  DI_CUSTOM_NEURAL_MAX_TRAINING_HOURS range. `--apply`:
  build_request() → BuildDocumentModelRequest(build_mode="neural",
  azure_blob_source=AzureBlobContentSource(container_url, prefix),
  max_training_hours) → admin_client.begin_build_document_model(request)
  .result(). Print resulting model_id.

What to watch. Preflight: `Local validation: ready for --apply.` if OK,
otherwise clear error. `--apply`: `Model built: <model_id>` on success
(minutes to hours depending on hours + dataset size).

Prerequisites / env vars:
  DOCUMENT_INTELLIGENCE_ENDPOINT       — custom-subdomain HTTPS URL
  DI_CUSTOM_NEURAL_MODEL_ID            — 1-64 chars [A-Za-z0-9._~-]
  DI_TRAINING_CONTAINER_URL            — HTTPS Blob container URL (SAS)
  DI_CUSTOM_NEURAL_PREFIX              — optional Blob folder prefix
  DI_CUSTOM_NEURAL_MAX_TRAINING_HOURS  — 0.5 to 10 (default 0.5)
  --apply                              — start persistent + billable build
"""
from __future__ import annotations

import argparse
import re

from document_intelligence_common import (
    configured,
    document_intelligence_endpoint,
    https_url,
)

MODEL_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._~-]{1,63}$")


def build_request(model_id: str, container_url: str, prefix: str, max_training_hours: float):
    """Build a v4.0 neural request after local validation."""
    from azure.ai.documentintelligence.models import (
        AzureBlobContentSource,
        BuildDocumentModelRequest,
    )

    if not MODEL_ID.fullmatch(model_id):
        raise ValueError("Model ID must be 1-64 letters, digits, '.', '_', '~', or '-'.")
    container = https_url(container_url, "DI_TRAINING_CONTAINER_URL")
    if not 0.5 <= max_training_hours <= 10:
        raise ValueError("DI_CUSTOM_NEURAL_MAX_TRAINING_HOURS must be from 0.5 through 10.")
    return BuildDocumentModelRequest(
        model_id=model_id,
        description="AI-103 custom neural training lesson",
        build_mode="neural",
        azure_blob_source=AzureBlobContentSource(container_url=container, prefix=prefix or None),
        max_training_hours=max_training_hours,
    )


def preflight() -> None:
    print("No cloud calls made.")
    print("Build mode: neural; API: v4.0 (2024-11-30 GA).")
    required = (
        "DOCUMENT_INTELLIGENCE_ENDPOINT",
        "DI_CUSTOM_NEURAL_MODEL_ID",
        "DI_TRAINING_CONTAINER_URL",
    )
    for name in required:
        print(f"{name}: {'configured' if configured(name) else 'missing'}")
    if all(configured(name) for name in required):
        try:
            document_intelligence_endpoint(configured("DOCUMENT_INTELLIGENCE_ENDPOINT"))
            build_request(
                configured("DI_CUSTOM_NEURAL_MODEL_ID"),
                configured("DI_TRAINING_CONTAINER_URL"),
                configured("DI_CUSTOM_NEURAL_PREFIX"),
                float(configured("DI_CUSTOM_NEURAL_MAX_TRAINING_HOURS") or 0.5),
            )
        except ValueError as error:
            print(f"Local validation: invalid ({error})")
        else:
            print("Local validation: ready for --apply.")
    print("Validate labels, region, Storage access, and training-hour budget before --apply.")


def apply(model_id: str, container_url: str, prefix: str, max_training_hours: float) -> None:
    from azure.ai.documentintelligence import DocumentIntelligenceAdministrationClient
    from azure.identity import DefaultAzureCredential

    request = build_request(model_id, container_url, prefix, max_training_hours)
    endpoint = document_intelligence_endpoint(configured("DOCUMENT_INTELLIGENCE_ENDPOINT"))
    result = DocumentIntelligenceAdministrationClient(
        endpoint, DefaultAzureCredential()
    ).begin_build_document_model(request).result()
    print(f"Model built: {result.model_id}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Preflight or build a custom neural model.")
    parser.add_argument("--model-id", default=configured("DI_CUSTOM_NEURAL_MODEL_ID"))
    parser.add_argument("--container-url", default=configured("DI_TRAINING_CONTAINER_URL"))
    parser.add_argument("--prefix", default=configured("DI_CUSTOM_NEURAL_PREFIX"))
    parser.add_argument(
        "--max-training-hours",
        type=float,
        default=float(configured("DI_CUSTOM_NEURAL_MAX_TRAINING_HOURS") or 0.5),
    )
    parser.add_argument("--apply", action="store_true", help="Create a billable model build.")
    args = parser.parse_args(argv)
    if not args.apply:
        preflight()
        return
    missing = [
        name
        for name, value in (
            ("DOCUMENT_INTELLIGENCE_ENDPOINT", configured("DOCUMENT_INTELLIGENCE_ENDPOINT")),
            ("--model-id", args.model_id),
            ("--container-url", args.container_url),
        )
        if not value
    ]
    if missing:
        parser.error("--apply requires: " + ", ".join(missing))
    apply(args.model_id, args.container_url, args.prefix, args.max_training_hours)


if __name__ == "__main__":
    main()
