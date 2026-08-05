# Run: uv run python 06-model-customization-other/12_router_instant.py --mode router --model model-router --apply
"""Exercise deployed model router or supported instant model only with --apply."""
from __future__ import annotations

import argparse

from _shared.openai_client import openai_client
from lab_common import print_preflight


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Call a model router deployment or instant model.")
    parser.add_argument("--mode", choices=("router", "instant"), required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--input", default="Summarize why model choice affects cost and latency in one sentence.")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    if not args.apply:
        detail = (
            "Router must already be deployed; inspect response.model to see selected model."
            if args.mode == "router"
            else "Instant access is preview; verify West US 3 project, supported model name, global quota, and version policy."
        )
        print_preflight([
            f"Would send one billable {args.mode} Responses request using {args.model}.",
            detail,
            "No deployment is created by this lab.",
        ])
        return
    response = openai_client().responses.create(model=args.model, input=args.input)
    print(f"Requested: {args.model}\nHandled by: {response.model}\n{response.output_text}")


if __name__ == "__main__":
    main()
