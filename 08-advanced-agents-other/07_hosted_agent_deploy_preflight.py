# Run: uv run python 08-advanced-agents-other/07_hosted_agent_deploy_preflight.py [--apply --agent-root <path>]
"""Preflight and (opt-in) deploy a Python hosted agent via azd.

A hosted agent packages your Python code as a container image and deploys
it to Foundry's managed agent hosting. Requires an azd project with
`azure.yaml` declaring the agent service. Default preflight validates the
project root assets; `--apply` runs `azd deploy` in the agent root.

Hosted agents differ from prompt agents (lessons 08-09): you own the
runtime code. Foundry manages hosting, scaling, endpoint routing, and
identity. Code → container → Foundry hosting = three-step mental model.

After deploy, lesson 08's `configure-hosted-agent-env-variables` sets
runtime env vars; lesson 09's telemetry lesson wires App Insights.
NEVER bake secrets into code — use env vars from portal or Azure Key Vault.

Code path:
  preflight(): validate azure.yaml, requirements.txt or pyproject.toml
  exist in agent-root. --apply: subprocess `azd deploy [--service <svc>]`
  from agent-root. Reports deploy stream.

What to watch. Preflight: asset check. --apply: azd output including
`Endpoint: https://<resource>.services.ai.azure.com/...`. Copy that URL
into PROJECT_ENDPOINT for lesson 09.

Prerequisites / env vars:
  --agent-root PATH   — azd project root with azure.yaml (default: .)
  --service NAME      — optional azd service name
  --apply             — deploy hosted agent (persistent, containers bill)
"""
import argparse
import subprocess
from pathlib import Path


REQUIRED = ("azure.yaml",)


def preflight(root: Path) -> None:
    print("Hosted agent deploy preflight (no cloud calls).")
    for name in REQUIRED:
        exists = (root / name).exists()
        print(f"- {name}: {'found' if exists else 'MISSING'}")
    has_deps = (root / "requirements.txt").exists() or (root / "pyproject.toml").exists()
    print(f"- python deps (requirements.txt or pyproject.toml): {'found' if has_deps else 'MISSING'}")
    if not all((root / f).exists() for f in REQUIRED) or not has_deps:
        print("Run `azd init` in agent-root to scaffold missing assets.")


def apply(root: Path, service: str | None) -> None:
    cmd = ["azd", "deploy"]
    if service:
        cmd += ["--service", service]
    subprocess.run(cmd, check=True, cwd=root)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Preflight or deploy a Python hosted agent.")
    parser.add_argument("--apply", action="store_true", help="Run azd deploy.")
    parser.add_argument("--agent-root", type=Path, default=Path("."))
    parser.add_argument("--service")
    args = parser.parse_args(argv)
    root = args.agent_root.resolve()
    if not args.apply:
        preflight(root)
        return
    apply(root, args.service)


if __name__ == "__main__":
    main()
