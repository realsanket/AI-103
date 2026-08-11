# Run: uv run python 06-model-customization-other/12_router_instant.py --mode router --model model-router --apply
"""Exercise deployed model router or supported instant model only with --apply.

Two delivery patterns in one lab. `--mode router` calls a deployed
model-router alias; router picks between allowed models per request. `--mode
instant` calls a supported preview model name directly with no deployment —
Instant Access uses global quota, currently requires a West US 3 project,
Foundry User access, and a supported instant model.

Both modes make ONE billable request under --apply and print requested vs
handled-by model. Router is for mixed prompt complexity where hard-coding
one model wastes cost or quality. Instant is for preview prototyping when
you don't want to create a deployment. Neither replaces PTU for dedicated
capacity or custom filters/residency requirements.

Code path:
  --apply: openai_client().responses.create(model=name, input=text) →
  print "Requested: <name>" and "Handled by: <response.model>". For router
  the two often differ (the point).

What to watch. Router: `Handled by:` shows the router's per-request
selection. Instant: same client/API works with no deployment. Pin an instant
model version when stability matters.

Prerequisites / env vars:
  --mode router|instant — pattern (required)
  --model NAME          — router deployment or instant model name (required)
  --input TEXT          — prompt (default provided)
  --apply               — send billable request
  AZURE_OPENAI_ENDPOINT
"""
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
