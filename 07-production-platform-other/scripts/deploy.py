"""Run a non-mutating IaC plan; use --apply for the actual mutation."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str]) -> None:
    print("+", " ".join(command))
    subprocess.run(command, check=True, cwd=ROOT)


def bicep_command(args: argparse.Namespace) -> list[str]:
    action = "create" if args.apply else "what-if"
    return [
        "az",
        "deployment",
        "group",
        action,
        "--resource-group",
        args.resource_group,
        "--template-file",
        "bicep/main.bicep",
        "--parameters",
        f"location={args.location}",
        f"prefix={args.prefix}",
        f"projectName={args.project_name}",
    ]


def terraform_command(args: argparse.Namespace) -> list[str]:
    return [
        "terraform",
        f"-chdir={ROOT / 'terraform'}",
        "apply" if args.apply else "plan",
        "-auto-approve" if args.apply else "-input=false",
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", choices=("bicep", "terraform"), required=True)
    parser.add_argument("--apply", action="store_true", help="Allow persistent Azure changes.")
    parser.add_argument("--resource-group", help="Required for Bicep.")
    parser.add_argument("--location", help="Required for Bicep.")
    parser.add_argument("--prefix", help="Required for Bicep.")
    parser.add_argument("--project-name", default="production")
    args = parser.parse_args()

    if args.engine == "bicep":
        missing = [name for name in ("resource_group", "location", "prefix") if not getattr(args, name)]
        if missing:
            parser.error(f"Bicep requires: {', '.join('--' + item.replace('_', '-') for item in missing)}")
        run(bicep_command(args))
        return

    run(["terraform", f"-chdir={ROOT / 'terraform'}", "init"])
    run(terraform_command(args))


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as error:
        raise SystemExit(error.returncode)
    except FileNotFoundError as error:
        print(f"Required command not found: {error.filename}", file=sys.stderr)
        raise SystemExit(1)
