# Run: uv run python 02-generative-ai-and-agents/hosted_agent_responses/deploy.py

"""Deploy guard. Cloud commands run only after an explicit --apply."""
import argparse
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).parent


def commands(provision: bool) -> list[list[str]]:
    result = [["azd", "deploy", "--no-prompt"]]
    if provision:
        result.insert(0, ["azd", "provision", "--no-prompt"])
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="allow Azure mutations")
    parser.add_argument("--provision", action="store_true", help="provision before deployment")
    args = parser.parse_args()
    subprocess.run([sys.executable, "preflight.py"], cwd=ROOT, check=True)
    planned = commands(args.provision)
    print("Planned: " + " && ".join(" ".join(command) for command in planned))
    if not args.apply:
        print("No deployment made. Re-run with --apply to mutate Azure.")
        return 0
    for command in planned:
        subprocess.run(command, cwd=ROOT, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
