# Run: uv run python 08-advanced-agents-other/06_agent_optimizer_preflight.py [--agent-root <path>] [--apply --optimize-model <name> | --apply --apply-candidate <id>]
"""Run Agent Optimizer against a Python hosted-agent root; local-only apply.

Agent Optimizer generates candidate agent configurations from a baseline
and evaluates them. Targets ONLY Python hosted agents in an azd project.
Requires `azure.yaml`, `eval.yaml`, and `.agent_configs/baseline/` in the
agent root. Default preflight fails clearly if any required asset is
missing rather than generating unreviewed scaffolding.

`--apply --optimize-model <deployment>` runs `azd ai agent optimize` — this
starts an optimization job that generates and scores candidates. Monitor
via `azd ai agent optimize status <op-id> --watch`. `--apply
--apply-candidate <id>` applies ONE selected candidate to local source
only — never deploys. Deployment is an intentional separate `azd deploy`
after diff review.

Neither mode deploys automatically. Review candidate diff, evaluator
results, safety behavior, tool changes, latency, and cost before promoting.

Code path:
  validate_hosted_agent_root() → check for azure.yaml, eval.yaml,
  .agent_configs/baseline/. `--apply --optimize-model`: `azd ai agent
  optimize --optimize-model <model> [--service <svc>]`. `--apply
  --apply-candidate <id>`: `azd ai agent optimize apply --candidate <id>
  [--service <svc>]`.

What to watch. Preflight: `Validated optimizer-ready hosted-agent root:
<path>` OR missing-asset list. `--apply --optimize-model`: `Optimization
started. Use azd ai agent optimize status <op-id> --watch.` `--apply
--apply-candidate`: `Candidate applied locally. Review diff and deploy
separately.`

Prerequisites / env vars:
  --agent-root PATH        — hosted-agent root (default: cwd)
  --optimize-model NAME    — approved optimizer model deployment
  --service NAME           — optional azd service selector
  --apply                  — run optimizer OR apply candidate
  --apply-candidate ID     — apply selected candidate locally (with --apply)
"""
import argparse
import os
from pathlib import Path
import subprocess

from dotenv import load_dotenv


def validate_hosted_agent_root(root: Path) -> list[str]:
    required = (
        root / "azure.yaml",
        root / "eval.yaml",
        root / ".agent_configs" / "baseline",
    )
    return [str(path.relative_to(root)) for path in required if not path.exists()]


def optimize_command(root: Path, model: str, service: str | None) -> list[str]:
    if not model:
        raise ValueError("Optimizer model deployment is required.")
    command = ["azd", "ai", "agent", "optimize", "--optimize-model", model]
    if service:
        command.extend(["--service", service])
    return command


def preflight(root: Path) -> None:
    print("No cloud calls made.")
    missing = validate_hosted_agent_root(root)
    if missing:
        print(f"{root} is not optimizer-ready. Missing: {', '.join(missing)}")
    else:
        print(f"Validated optimizer-ready hosted-agent root: {root}")
    print("Review eval.yaml ownership, seed data, evaluators, and baseline before starting a job.")
    print("Optimizer targets Python hosted agents only. Apply candidate locally, review diff, then deploy separately.")


def main(argv: list[str] | None = None) -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Preflight or operate Agent Optimizer.")
    parser.add_argument("--apply", action="store_true", help="Start an optimization job or apply selected candidate.")
    parser.add_argument("--agent-root", type=Path, required=False, default=Path("."))
    parser.add_argument("--optimize-model")
    parser.add_argument("--service")
    parser.add_argument("--apply-candidate", help="Apply this reviewed candidate locally; never deploys.")
    args = parser.parse_args(argv)
    root = args.agent_root.resolve()
    if not args.apply:
        preflight(root)
        return
    missing = validate_hosted_agent_root(root)
    if missing:
        parser.error("Optimizer root missing: " + ", ".join(missing))
    environment = {**os.environ, "AZURE_DEV_USER_AGENT": "microsoft_foundry_skill"}
    if args.apply_candidate:
        command = ["azd", "ai", "agent", "optimize", "apply", "--candidate", args.apply_candidate]
        if args.service:
            command.extend(["--service", args.service])
        subprocess.run(command, check=True, cwd=root, env=environment)
        print("Candidate applied locally. Review diff and deploy separately.")
        return
    if not args.optimize_model:
        parser.error("--apply requires --optimize-model unless --apply-candidate is supplied.")
    subprocess.run(optimize_command(root, args.optimize_model, args.service), check=True, cwd=root, env=environment)
    print("Optimization started. Use `azd ai agent optimize status <operation-id> --watch` to monitor it.")


if __name__ == "__main__":
    main()
