# Run: uv run python 06-model-customization-other/11_priority_processing.py --model <deployment> --apply
"""Send one priority-tier Responses request only with explicit opt-in."""
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
