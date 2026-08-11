# Run: uv run python 02-generative-ai-and-agents/30_hosted_agent_cicd.py

"""Lesson 30 — inspect hosted-agent CI/CD and explicit deployment guard.

Run from repository root:
    uv run python 02-generative-ai-and-agents/30_hosted_agent_cicd.py

The contained workflow (`hosted_agent_responses/hosted-agent-cd.yml`) is a
reference asset for GitHub OIDC plus azd deploy and smoke test. The deployment
wrapper only mutates cloud state with --apply:
    python hosted_agent_responses/deploy.py --apply
"""
from pathlib import Path


def main() -> None:
    sample = Path(__file__).with_name("hosted_agent_responses")
    print(f"CI/CD reference: {sample / 'hosted-agent-cd.yml'}")
    print(f"Dry run:         python {sample / 'deploy.py'}")
    print(f"Deploy:          python {sample / 'deploy.py'} --apply")


if __name__ == "__main__":
    main()
