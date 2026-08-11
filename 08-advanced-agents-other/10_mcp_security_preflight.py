# Run: uv run python 08-advanced-agents-other/10_mcp_security_preflight.py [--policy-file <path>]
"""Validate an MCP security policy checklist locally; print security posture.

MCP tools are powerful — they let agents call arbitrary external servers.
Security posture requires: (1) only approved MCP connections, (2) managed
identity auth (no embedded tokens), (3) tool schema reviewed and allowlisted,
(4) network path to MCP server validated. This lesson is a structured
preflight checklist, not a cloud probe.

Default run prints the MCP security checklist with PASS/FAIL for env-driven
items. `--policy-file` validates a JSON policy file describing your MCP
security decisions.

Inspired by the local `.context/azure-ai-docs/articles/foundry/mcp/security-best-practices.md`
guidance: approve server, review schema, minimize scope, validate auth, log
every tool call.

Code path:
  Run checklist: print per-item status (env var present / pattern valid).
  --policy-file: parse JSON, validate required keys: approved_servers[],
  auth_type, logging_enabled, tool_allowlist[]. Print pass/fail per key.

What to watch. All items PASS before wiring MCP to a production agent.
Any FAIL = gap to close before --apply in lesson 09.

Prerequisites / env vars:
  PROJECT_ENDPOINT      — used for URL validation
  MCP_CONNECTION_NAME   — connection name to check
  --policy-file PATH    — optional JSON policy to validate
"""
import argparse
import json
from pathlib import Path

from _shared.config import settings


_REQUIRED_POLICY_KEYS = {
    "approved_servers": list,
    "auth_type": str,
    "logging_enabled": bool,
    "tool_allowlist": list,
}


def run_checklist() -> None:
    current = settings()
    checks = {
        "PROJECT_ENDPOINT configured": bool(current.project_endpoint),
        "MCP_CONNECTION_NAME set": bool(__import__("os").environ.get("MCP_CONNECTION_NAME")),
        "PROJECT_ENDPOINT is HTTPS": (current.project_endpoint or "").startswith("https://"),
        "No embedded bearer in env": not any(
            "bearer" in str(v).lower() for k, v in __import__("os").environ.items()
            if "mcp" in k.lower()
        ),
    }
    print("MCP security preflight checklist:")
    all_pass = True
    for check, passed in checks.items():
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {check}")
        if not passed:
            all_pass = False
    print("Overall: PASS" if all_pass else "Overall: FAIL — resolve items before wiring to production agent.")


def validate_policy(path: Path) -> None:
    policy = json.loads(path.read_text(encoding="utf-8"))
    print(f"MCP security policy: {path}")
    for key, expected_type in _REQUIRED_POLICY_KEYS.items():
        value = policy.get(key)
        if value is None:
            print(f"  [FAIL] missing: {key}")
        elif not isinstance(value, expected_type):
            print(f"  [FAIL] {key}: expected {expected_type.__name__}, got {type(value).__name__}")
        elif key == "approved_servers" and len(value) == 0:
            print(f"  [FAIL] approved_servers is empty — list at least one approved MCP server")
        elif key == "auth_type" and value not in ("managed_identity", "project_managed_identity"):
            print(f"  [WARN] auth_type '{value}' is not managed identity — avoid embedded tokens")
        else:
            print(f"  [PASS] {key}: {value if not isinstance(value, list) else f'{len(value)} items'}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="MCP security posture preflight.")
    parser.add_argument("--policy-file", type=Path, help="Optional JSON security policy to validate.")
    args = parser.parse_args(argv)
    run_checklist()
    if args.policy_file:
        validate_policy(args.policy_file)


if __name__ == "__main__":
    main()
