# Run: uv run python 08-advanced-agents-other/04_routines_preflight.py [--apply [--dispatch] --routine-name <name> --manifest <path>]
"""Validate, then create a Foundry routine (scheduled agent invocation) via azd.

A routine is one trigger + one action. Use for timers, recurring schedules,
or supported events invoking one agent. Use a workflow (not a routine) for
branching, approvals, multiple agents, or stateful coordination.

Default preflight validates the manifest: rejects secret markers (comment
lines are stripped first), asserts required fields (`triggers:`, `type:
schedule`, `cron_expression:`, `time_zone:`, `action:`), and requires the
Responses API action type (`invoke_agent_responses_api`). No cloud call.

`--apply` runs `azd ai routine create <name> --file <manifest>
--project-endpoint <endpoint>`. Never passes prompt input on the command
line — the reviewed manifest owns it. `--dispatch` invokes one controlled
run after creation via `azd ai routine dispatch`.

Routines execute unattended — inputs must not include secrets, personal
access tokens, or delegated user credentials. Use an agent that
authenticates with its own configured identity; routines cannot delegate an
end-user identity.

Code path:
  validate_manifest() → read file, strip comment lines, check secret markers
  + required fields + action type. routine_command() → azd argv. `--apply`:
  subprocess.run(cmd). `--dispatch`: additional `azd ai routine dispatch`
  call.

What to watch. Preflight: `Validated reviewed routine manifest: <path>` +
inspection guidance. `--apply`: azd stream ending `Created routine <name>.
Review its manifest state before enabling recurrence.` `--dispatch`:
`Dispatched once. Review run history before relying on its schedule.`

Prerequisites / env vars:
  PROJECT_ENDPOINT      — Foundry project HTTPS URL
  --routine-name        — routine name (default: weekday-support-summary)
  --manifest PATH       — routine YAML (default: routine.example.yaml)
  --apply               — create routine via azd
  --dispatch            — run once after creation (requires --apply)
"""
import argparse
import os
from pathlib import Path
import subprocess

from _shared.config import load_env


SECRET_MARKERS = ("secret", "password", "api_key", "authorization:", "bearer ")


def validate_manifest(path: Path) -> str:
    if not path.is_file():
        raise ValueError(f"Routine manifest not found: {path}")
    content = path.read_text(encoding="utf-8")
    executable_content = "\n".join(
        line for line in content.splitlines() if not line.lstrip().startswith("#")
    )
    lowered = executable_content.lower()
    if any(marker in lowered for marker in SECRET_MARKERS):
        raise ValueError("Routine manifest cannot include a secret, credential, or bearer token.")
    required = ("triggers:", "type: schedule", "cron_expression:", "time_zone:", "action:")
    missing = [field for field in required if field not in content]
    if missing:
        raise ValueError("Routine manifest is missing: " + ", ".join(missing))
    if "type: invoke_agent_responses_api" not in content:
        raise ValueError("This lab uses a Responses API action for a current agent endpoint.")
    return content


def routine_command(endpoint: str, routine_name: str, manifest: Path) -> list[str]:
    if not endpoint or not endpoint.startswith("https://") or "/api/projects/" not in endpoint:
        raise ValueError("PROJECT_ENDPOINT must be a Foundry project HTTPS URL.")
    if not routine_name or "/" in routine_name:
        raise ValueError("Routine name must be one path segment.")
    return [
        "azd",
        "ai",
        "routine",
        "create",
        routine_name,
        "--file",
        str(manifest),
        "--project-endpoint",
        endpoint,
    ]


def preflight(manifest: Path) -> None:
    print("No cloud calls made.")
    validate_manifest(manifest)
    print(f"Validated reviewed routine manifest: {manifest}")
    print("Routine needs a deployed agent with non-user-delegated authentication.")
    print("Use `azd ai routine run list <name>` after dispatch; inspect trace and output before enabling recurrence.")


def main(argv: list[str] | None = None) -> None:
    load_env()
    parser = argparse.ArgumentParser(description="Preflight or create a Foundry routine.")
    parser.add_argument("--apply", action="store_true", help="Create the routine.")
    parser.add_argument("--dispatch", action="store_true", help="Dispatch once after creating it; requires --apply.")
    parser.add_argument("--routine-name", default="weekday-support-summary")
    parser.add_argument("--manifest", type=Path, default=Path(__file__).with_name("routine.example.yaml"))
    args = parser.parse_args(argv)
    if not args.apply:
        if args.dispatch:
            parser.error("--dispatch requires --apply.")
        preflight(args.manifest)
        return
    endpoint = os.getenv("PROJECT_ENDPOINT")
    if not endpoint:
        parser.error("--apply requires PROJECT_ENDPOINT.")
    validate_manifest(args.manifest)
    environment = {**os.environ, "AZURE_DEV_USER_AGENT": "microsoft_foundry_skill"}
    subprocess.run(routine_command(endpoint, args.routine_name, args.manifest), check=True, env=environment)
    print(f"Created routine {args.routine_name}. Review its manifest state before enabling recurrence.")
    if args.dispatch:
        subprocess.run(
            [
                "azd",
                "ai",
                "routine",
                "dispatch",
                args.routine_name,
                "--project-endpoint",
                endpoint,
            ],
            check=True,
            env=environment,
        )
        print("Dispatched once. Review run history before relying on its schedule.")


if __name__ == "__main__":
    main()
