# Run: uv run python 06-model-customization-other/13_cost_review.py --ptu 50 --hourly-rate 1.23
"""Calculate transparent planning estimates locally; never queries billing data."""
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
