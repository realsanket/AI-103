# Run: uv run python 02-generative-ai-and-agents/28_hosted_agent_responses.py

"""Lesson 26 — preflight a Foundry Responses hosted-agent source deployment.

Run from repository root:
    uv run python 02-generative-ai-and-agents/26_hosted_agent_responses.py

The contained sample uses the current Responses adapter. The adapter owns the
HTTP runtime contract: Linux amd64 remote build, port 8088, GET /readiness,
POST /responses, and SIGTERM shutdown. Run its preflight before local or cloud
work; it never deploys.
"""
from pathlib import Path
import subprocess
import sys


def main() -> None:
    sample = Path(__file__).with_name("hosted_agent_responses")
    subprocess.run([sys.executable, "preflight.py"], cwd=sample, check=True)


if __name__ == "__main__":
    main()
