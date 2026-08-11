# Run: uv run python 08-advanced-agents-other/02_toolbox_publish_preflight.py [--apply --toolbox-name <name> --manifest <path>]
"""Validate, then create a Foundry Toolbox and its first immutable version.

Toolbox centralizes approved tools behind one MCP-compatible endpoint.
Connections own authentication + token renewal — the manifest must never
embed credentials. Toolbox versions are immutable; test a version-specific
developer endpoint before flipping the default consumer endpoint.

Default preflight scans the manifest for secret markers (`client_secret`,
`api_key`, `authorization=`, `connection_string`, `password:`) and fails if
any appear. Also asserts the manifest declares at least one of
`connections:`, `tools:`, `skills:`. Prints both endpoint URL templates.

`--apply` invokes `azd ai toolbox create <name> --from-file <manifest>
--project-endpoint <endpoint>`. Creates the toolbox and its first version;
that version becomes the default. After apply, test against the
version-specific developer endpoint before consumer rollout.

Code path:
  validate_manifest() → assert file exists, contains no secret markers, has
  connections/tools/skills. toolbox_endpoint() builds either consumer
  (`.../mcp?api-version=v1`) or developer (`.../versions/<v>/mcp?...`) URL.
  create_command() → azd argv. `--apply`: subprocess.run(cmd).

What to watch. Preflight: `Validated credential-free manifest: <path>` +
endpoint format templates. `--apply`: azd stream ending `Created Toolbox
<name>. Test its version-specific endpoint before consumer rollout.`

Prerequisites / env vars:
  PROJECT_ENDPOINT       — Foundry project HTTPS URL
  FOUNDRY_TOOLBOX_NAME   — toolbox name (or pass --toolbox-name)
  --manifest PATH        — toolbox manifest (default: toolbox.example.yaml)
  --apply                — create toolbox + first version via azd
"""
import argparse
import os
from pathlib import Path
import subprocess
from urllib.parse import urlparse

from dotenv import load_dotenv


DISALLOWED_SECRET_MARKERS = (
    "client_secret",
    "api_key",
    "authorization=",
    "connection_string",
    "password:",
)


def project_endpoint(value: str) -> str:
    parsed = urlparse(value)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or not parsed.hostname.endswith(".services.ai.azure.com")
        or "/api/projects/" not in parsed.path
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError("PROJECT_ENDPOINT must be a credential-free Foundry project HTTPS URL.")
    return value.rstrip("/")


def validate_manifest(path: Path) -> str:
    if not path.is_file():
        raise ValueError(f"Manifest not found: {path}")
    content = path.read_text(encoding="utf-8")
    lowered = content.lower()
    if any(marker in lowered for marker in DISALLOWED_SECRET_MARKERS):
        raise ValueError("Toolbox manifest must reference project connections, never embed credentials.")
    if not any(marker in content for marker in ("connections:", "tools:", "skills:")):
        raise ValueError("Toolbox manifest needs at least one connection, tool, or skill.")
    return content


def toolbox_endpoint(endpoint: str, toolbox_name: str, version: str | None = None) -> str:
    if not toolbox_name or "/" in toolbox_name:
        raise ValueError("Toolbox name must be one path segment.")
    suffix = f"/versions/{version}" if version else ""
    return f"{project_endpoint(endpoint)}/toolboxes/{toolbox_name}{suffix}/mcp?api-version=v1"


def create_command(endpoint: str, toolbox_name: str, manifest: Path) -> list[str]:
    return [
        "azd",
        "ai",
        "toolbox",
        "create",
        toolbox_name,
        "--from-file",
        str(manifest),
        "--project-endpoint",
        project_endpoint(endpoint),
    ]


def preflight(manifest: Path) -> None:
    print("No cloud calls made.")
    validate_manifest(manifest)
    print(f"Validated credential-free manifest: {manifest}")
    print("First version becomes default. Test its version-specific MCP endpoint before promotion.")
    print("Consumer endpoint format: {PROJECT_ENDPOINT}/toolboxes/{TOOLBOX_NAME}/mcp?api-version=v1")
    print("Developer endpoint format: {PROJECT_ENDPOINT}/toolboxes/{TOOLBOX_NAME}/versions/{VERSION}/mcp?api-version=v1")


def main(argv: list[str] | None = None) -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Preflight or create a current Foundry Toolbox.")
    parser.add_argument("--apply", action="store_true", help="Create the Toolbox and first version.")
    parser.add_argument("--manifest", type=Path, default=Path(__file__).with_name("toolbox.example.yaml"))
    parser.add_argument("--toolbox-name", default=os.getenv("FOUNDRY_TOOLBOX_NAME"))
    args = parser.parse_args(argv)
    if not args.apply:
        preflight(args.manifest)
        return
    if not os.getenv("PROJECT_ENDPOINT") or not args.toolbox_name:
        parser.error("--apply requires PROJECT_ENDPOINT and --toolbox-name or FOUNDRY_TOOLBOX_NAME.")
    validate_manifest(args.manifest)
    command = create_command(os.environ["PROJECT_ENDPOINT"], args.toolbox_name, args.manifest)
    environment = {**os.environ, "AZURE_DEV_USER_AGENT": "microsoft_foundry_skill"}
    subprocess.run(command, check=True, env=environment)
    print(f"Created Toolbox {args.toolbox_name}. Test its version-specific endpoint before consumer rollout.")


if __name__ == "__main__":
    main()
