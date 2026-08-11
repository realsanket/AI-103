# Run: uv run python 06-model-customization-other/11_priority_processing.py --model <deployment> --apply
"""Send one priority-tier Responses request only with explicit opt-in.

Priority processing charges a premium per token to lower latency on supported
Global Standard or US Data Zone Standard deployments. Shares quota with
Standard. Under ramp/peak/long-context conditions requests can fall back to
Standard tier — inspect `service_tier` in the response to confirm.

Priority is not the dedicated-capacity choice — PTU is. Use Priority when a
supported online workload needs lower latency without a capacity commitment.
Do not assume priority is a hard SLA guarantee.

Code path:
  --apply: openai_client().responses.create(model=deployment, input=text,
  service_tier="priority") → print response.model, service_tier, output_text.

What to watch. `Service tier: priority` in response — confirms tier honored.
Falls back to `standard` under contention. Monitor via Azure Monitor request
latency + service_tier dimensions to see rate of fallback.

Prerequisites / env vars:
  --model  — supported Global/Data Zone Standard deployment name (required)
  --input  — prompt text (default provided)
  --apply  — send billable request
  AZURE_OPENAI_ENDPOINT
"""
from __future__ import annotations

import argparse

from _shared.openai_client import openai_client
from lab_common import print_preflight


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Exercise priority processing for one reviewed request.")
    parser.add_argument("--model", required=True)
    parser.add_argument("--input", default="Reply with exactly: priority check.")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    if not args.apply:
        print_preflight([
            f"Would send one billable Responses request to {args.model} with service_tier=priority.",
            "Priority requires current supported Global Standard or US Data Zone Standard deployment configuration.",
            "Inspect returned service tier and Azure Monitor metrics; priority requests can fall back to standard.",
        ])
        return
    response = openai_client().responses.create(model=args.model, input=args.input, service_tier="priority")
    print(f"Response model: {response.model}\nService tier: {getattr(response, 'service_tier', '?')}\n{response.output_text}")


if __name__ == "__main__":
    main()
