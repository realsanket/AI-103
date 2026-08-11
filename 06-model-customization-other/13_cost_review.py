# Run: uv run python 06-model-customization-other/13_cost_review.py --ptu 50 --hourly-rate 1.23
"""Calculate transparent planning estimates locally; never queries billing data.

Pure arithmetic: `PTU × hourly_rate × hours`. Zero cloud calls; supply your
verified current price for target model/SKU/region. Not a bill and not a
forecast — the result is a lower bound because it excludes training tokens,
grader calls, distillation teacher calls, hosting for evaluation deployments,
priority premium, batch, storage, monitoring, egress, and reservation terms.

Use to sanity-check whether PTU commitment makes sense vs pay-per-token
Standard. Compare estimate against actual Cost Management data with resource
+ deployment tags. Delete idle evaluation deployments and expired datasets
under your retention policy — they bill while present.

Code path:
  ptu_monthly_cost(ptu, hourly_rate, hours=730) → validate positive → return
  ptu * hourly_rate * hours. Print formula and result.

What to watch. Result line: `PTU hourly estimate: 50 × 1.23 × 730 = 44895.00`.
Sanity-check by re-verifying hourly_rate in current Foundry pricing page for
the exact model + region + SKU.

Prerequisites / env vars:
  --ptu           — reserved PTU count (required)
  --hourly-rate   — current verified price per PTU-hour (required)
  --hours         — hours per month (default 730)
"""
from __future__ import annotations

import argparse


def ptu_monthly_cost(ptu: int, hourly_rate: float, hours: int = 730) -> float:
    if ptu <= 0 or hourly_rate < 0 or hours <= 0:
        raise ValueError("PTU, hourly rate, and hours must be positive (rate can be zero).")
    return ptu * hourly_rate * hours


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Calculate a PTU planning estimate locally.")
    parser.add_argument("--ptu", type=int, required=True)
    parser.add_argument("--hourly-rate", type=float, required=True, help="Current price you verified for target SKU/region.")
    parser.add_argument("--hours", type=int, default=730)
    args = parser.parse_args(argv)
    estimate = ptu_monthly_cost(args.ptu, args.hourly_rate, args.hours)
    print("LOCAL COST REVIEW: no cloud calls, billing queries, or changes.")
    print(f"PTU hourly estimate: {args.ptu} × {args.hourly_rate:.6g} × {args.hours} = {estimate:.2f}")
    print("Add training tokens, grader calls, distillation teacher calls, hosting, evaluation,")
    print("priority, batch, storage, monitoring, and network charges from current official pricing.")
    print("Use Cost Management and resource/deployment tags for actual cost, not this estimate.")


if __name__ == "__main__":
    main()
