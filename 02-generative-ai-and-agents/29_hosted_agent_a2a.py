# Run: uv run python 02-generative-ai-and-agents/29_hosted_agent_a2a.py

"""Lesson 27 — distinguish Responses hosting from A2A before integration.

Run from repository root:
    uv run python 02-generative-ai-and-agents/27_hosted_agent_a2a.py

Responses is an OpenAI-compatible user/application protocol at POST /responses.
A2A is a separate hosted-agent protocol for agent orchestration. This sample
does not advertise A2A, so a caller must not treat its Responses endpoint as an
agent-to-agent contract.
"""
from pathlib import Path
import subprocess
import sys


def main() -> None:
    sample = Path(__file__).with_name("hosted_agent_responses")
    subprocess.run([sys.executable, "preflight.py", "--a2a"], cwd=sample, check=True)


if __name__ == "__main__":
    main()
