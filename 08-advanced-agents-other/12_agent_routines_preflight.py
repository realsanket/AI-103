# Run: uv run python 08-advanced-agents-other/12_agent_routines_preflight.py [--policy-file <path>]
"""Validate an agent routines configuration for Foundry scheduled agent triggers.

Agent routines let hosted agents run on a cron schedule or event trigger without
a user initiating the conversation. A routine specifies trigger type (cron/event),
the agent to invoke, and the initial message. This lesson validates a local routine
JSON definition and prints what would happen at trigger time. It does NOT register
the routine — registration happens in the Foundry portal or via az CLI.

Default preflight prints the required JSON schema and a valid example. --policy-file
validates a user-supplied routine definition against required fields and prints
PASS/FAIL per key.

Code path:
  preflight: print required JSON schema + example.
  --policy-file: json.loads(path) → validate agent_name (str), initial_message (str),
  trigger (dict with type in {cron, event, webhook}) → print PASS/FAIL per field.

What to watch. All PASS before registering. trigger.schedule for cron type must
be a valid cron expression. Missing initial_message = agent starts with no context.

Prerequisites / env vars:
  --policy-file  — path to routine JSON to validate (optional)
"""
import argparse
import json
from pathlib import Path

_REQUIRED: dict[str, type] = {
    "agent_name": str,
    "initial_message": str,
    "trigger": dict,
}
_TRIGGER_TYPES = ("cron", "event", "webhook")
_EXAMPLE = {
    "agent_name": "inventory-agent",
    "initial_message": "Run daily inventory check and summarize discrepancies.",
    "trigger": {
        "type": "cron",
        "schedule": "0 8 * * 1-5",
        "timezone": "UTC",
    },
}


def preflight() -> None:
    print("Agent routines preflight (no cloud calls).")
    print("Required routine JSON structure:")
    print(json.dumps(_EXAMPLE, indent=2))
    print()
    print(f"trigger.type options: {', '.join(_TRIGGER_TYPES)}")
    print("Register: Foundry portal → Agent → Routines → Add routine.")
    print("Pass --policy-file <path.json> to validate a routine definition.")


def validate(path: Path) -> None:
    routine = json.loads(path.read_text(encoding="utf-8"))
    print(f"Validating routine: {path}")
    all_pass = True
    for key, expected_type in _REQUIRED.items():
        value = routine.get(key)
        if value is None:
            print(f"  [FAIL] missing key: {key}")
            all_pass = False
        elif not isinstance(value, expected_type):
            print(f"  [FAIL] {key}: expected {expected_type.__name__}, got {type(value).__name__}")
            all_pass = False
        else:
            print(f"  [PASS] {key}: {str(value)[:60]}")

    trigger = routine.get("trigger", {})
    ttype = trigger.get("type", "")
    if ttype not in _TRIGGER_TYPES:
        print(f"  [FAIL] trigger.type: {ttype!r} not in {_TRIGGER_TYPES}")
        all_pass = False
    else:
        print(f"  [PASS] trigger.type: {ttype}")
        if ttype == "cron" and not trigger.get("schedule"):
            print("  [FAIL] trigger.schedule missing for cron type")
            all_pass = False
        elif ttype == "cron":
            print(f"  [PASS] trigger.schedule: {trigger['schedule']}")

    print("Overall:", "PASS" if all_pass else "FAIL")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Validate agent routine definition JSON.")
    parser.add_argument("--policy-file", type=Path, help="Routine JSON to validate.")
    args = parser.parse_args(argv)
    if args.policy_file:
        validate(args.policy_file)
    else:
        preflight()


if __name__ == "__main__":
    main()
