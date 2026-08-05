"""Static hosted-agent checks; no Azure calls and no deployment mutation."""
import argparse
from pathlib import Path


ROOT = Path(__file__).parent
TARGET = "Foundry remote build target: Linux x86_64 (amd64)."


def collect_errors(root: Path = ROOT) -> list[str]:
    azure = (root / "azure.yaml").read_text()
    source = (root / "main.py").read_text()
    requirements = (root / "requirements.txt").read_text()
    checks = {
        "Responses protocol 2.0": "protocol: responses" in azure and "version: 2.0.0" in azure,
        "Python 3.13 source build": "runtime: python_3_13" in azure
        and "dependencyResolution: remote_build" in azure,
        "platform endpoint is not shadowed": "\n      FOUNDRY_PROJECT_ENDPOINT:" not in azure,
        "port 8088 default": 'setdefault("PORT", "8088")' in source,
        "Responses adapter": "ResponsesAgentServerHost" in source,
        "agent server dependency": "azure-ai-agentserver-responses" in requirements,
    }
    return [name for name, passed in checks.items() if not passed]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--a2a", action="store_true", help="show A2A boundary check")
    args = parser.parse_args()
    errors = collect_errors()
    print(TARGET)
    if errors:
        print("Preflight failed: " + "; ".join(errors))
        return 1
    print("Preflight passed: Responses adapter owns :8088, /readiness, and SIGTERM shutdown.")
    if args.a2a:
        azure = (ROOT / "azure.yaml").read_text()
        if "protocol: a2a" in azure:
            print("A2A preflight failed: this Responses-only sample must not advertise A2A.")
            return 1
        print("A2A boundary passed: POST /responses is not A2A; add protocol: a2a and its auth/discovery design first.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
