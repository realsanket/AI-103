# Run: uv run python 08-advanced-agents-other/25_computer_use_preflight.py
"""Preflight the preview Computer Use safety-acknowledgement loop.

Computer Use lets a compatible model propose UI actions against a browser or
desktop sandbox. Every action is a proposal, not authorization. Run only in an
isolated disposable VM with restricted network/data access, screenshot review,
bounded steps, and human approval for every pending safety check.

Flows:
  Default - print the model, sandbox, approval, and retention requirements.
  --example-approved - locally build the acknowledgement payload for a synthetic
  call; no UI action or model request occurs.

What to watch. The application must stop on pending_safety_checks, present them
to a human, and return acknowledged_safety_checks only after explicit approval.

Prerequisites / env vars:
  COMPUTER_USE_MODEL  - compatible deployment; defaults to computer-use-preview
"""
import argparse
import os


def acknowledge_safety_checks(
    call_id: str,
    safety_checks: list[dict],
    *,
    approved: bool,
) -> dict:
    if not call_id or not safety_checks:
        raise ValueError("Call ID and pending safety checks are required.")
    if not approved:
        raise PermissionError("Computer action remains blocked without explicit approval.")
    return {
        "type": "computer_call_output",
        "call_id": call_id,
        "acknowledged_safety_checks": safety_checks,
        "output": {
            "type": "computer_screenshot",
            "image_url": "<capture-approved-sandbox-after-action>",
        },
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Preflight Computer Use safety handling.")
    parser.add_argument("--example-approved", action="store_true")
    args = parser.parse_args(argv)
    model = os.getenv("COMPUTER_USE_MODEL") or "computer-use-preview"
    print("No cloud calls made.")
    print(f"- Model deployment: {model}")
    print("- Preview; use only a disposable VM/sandbox with restricted data and egress.")
    print("- Bound action count, duration, domains, downloads, clipboard, and credentials.")
    print("- Stop and require human review for every pending_safety_checks item.")
    print("- Retain screenshots/actions only under an approved sensitive-data policy.")
    if args.example_approved:
        payload = acknowledge_safety_checks(
            "synthetic-call",
            [{"id": "synthetic-check", "code": "human_review_required"}],
            approved=True,
        )
        print(f"- Synthetic acknowledgement payload: {payload}")


if __name__ == "__main__":
    main()
