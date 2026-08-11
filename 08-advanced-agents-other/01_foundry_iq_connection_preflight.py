# Run: uv run python 08-advanced-agents-other/01_foundry_iq_connection_preflight.py [--apply]
"""Validate, then create a keyless Foundry IQ project connection to a Search knowledge base.

Foundry IQ is a managed knowledge layer on Azure AI Search with agentic
retrieval. It combines sources, enforces permissions, plans retrieval, and
returns citations. Connect agents to it via its MCP endpoint, NOT via
embedded Search credentials. Default preflight validates env identifiers and
prints the resulting MCP URL — no cloud call.

`--apply` invokes `azd ai connection create <name> --kind remote-tool
--target <mcp> --auth-type project-managed-identity --audience
https://search.azure.com/ --project-endpoint <endpoint>`. Creates or updates
the RemoteTool project connection. Does NOT create the knowledge base or
upload content — those are separate reviewed Search operations.

Confirm `Search Index Data Reader` is assigned to the project managed
identity BEFORE apply; add `Search Index Data Contributor` only when writes
are needed. Never accept API keys — this lab rejects credentials in URLs.

Code path:
  project_endpoint() → validate HTTPS + `.services.ai.azure.com` +
  `/api/projects/` + no credentials. knowledge_base_mcp_endpoint() → build
  `https://<search>/knowledgebases/<kb>/mcp?api-version=2026-05-01-preview`.
  connection_command() → azd argv list. `--apply`: subprocess.run(cmd).

What to watch. Preflight: `Validated Foundry IQ MCP endpoint: <url>` +
`Apply command: azd ai connection create ...`. `--apply`: azd stream ending
`Connection created. Continue with Lab 02 to expose it through a toolbox.`

Prerequisites / env vars:
  PROJECT_ENDPOINT               — Foundry project HTTPS URL
  FOUNDRY_IQ_SEARCH_ENDPOINT     — Search resource HTTPS URL
  FOUNDRY_IQ_KNOWLEDGE_BASE      — knowledge-base name (one segment)
  FOUNDRY_IQ_CONNECTION_NAME     — connection name (no whitespace)
  --apply                        — create/update connection via azd
"""
import argparse
import os
import subprocess
from urllib.parse import quote, urlparse

from dotenv import load_dotenv


def _https_url(value: str, host_suffix: str) -> str:
    parsed = urlparse(value)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or not parsed.hostname.endswith(host_suffix)
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError(f"Expected an HTTPS {host_suffix} URL without credentials, query, or fragment.")
    return value.rstrip("/")


def project_endpoint(value: str) -> str:
    endpoint = _https_url(value, ".services.ai.azure.com")
    if "/api/projects/" not in endpoint:
        raise ValueError("PROJECT_ENDPOINT must be a Foundry project endpoint.")
    return endpoint


def knowledge_base_mcp_endpoint(search_endpoint: str, knowledge_base: str) -> str:
    search = _https_url(search_endpoint, ".search.windows.net")
    if not knowledge_base or "/" in knowledge_base:
        raise ValueError("FOUNDRY_IQ_KNOWLEDGE_BASE must be one knowledge-base name.")
    return (
        f"{search}/knowledgebases/{quote(knowledge_base, safe='')}/mcp"
        "?api-version=2026-05-01-preview"
    )


def connection_command(
    endpoint: str, connection_name: str, mcp_endpoint: str
) -> list[str]:
    if not connection_name or any(character.isspace() for character in connection_name):
        raise ValueError("Connection name must be nonempty and contain no whitespace.")
    return [
        "azd",
        "ai",
        "connection",
        "create",
        connection_name,
        "--kind",
        "remote-tool",
        "--target",
        mcp_endpoint,
        "--auth-type",
        "project-managed-identity",
        "--audience",
        "https://search.azure.com/",
        "--project-endpoint",
        endpoint,
    ]


def preflight() -> None:
    print("No cloud calls made.")
    required = (
        "PROJECT_ENDPOINT",
        "FOUNDRY_IQ_SEARCH_ENDPOINT",
        "FOUNDRY_IQ_KNOWLEDGE_BASE",
        "FOUNDRY_IQ_CONNECTION_NAME",
    )
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        print("Set non-secret identifiers before --apply: " + ", ".join(missing))
        return
    endpoint = project_endpoint(os.environ["PROJECT_ENDPOINT"])
    mcp = knowledge_base_mcp_endpoint(
        os.environ["FOUNDRY_IQ_SEARCH_ENDPOINT"],
        os.environ["FOUNDRY_IQ_KNOWLEDGE_BASE"],
    )
    command = connection_command(endpoint, os.environ["FOUNDRY_IQ_CONNECTION_NAME"], mcp)
    print(f"Validated Foundry IQ MCP endpoint: {mcp}")
    print("Apply command: " + " ".join(command))
    print("Confirm Search Index Data Reader is assigned to project managed identity first.")


def apply() -> None:
    endpoint = project_endpoint(os.environ["PROJECT_ENDPOINT"])
    mcp = knowledge_base_mcp_endpoint(
        os.environ["FOUNDRY_IQ_SEARCH_ENDPOINT"],
        os.environ["FOUNDRY_IQ_KNOWLEDGE_BASE"],
    )
    command = connection_command(endpoint, os.environ["FOUNDRY_IQ_CONNECTION_NAME"], mcp)
    environment = {**os.environ, "AZURE_DEV_USER_AGENT": "microsoft_foundry_skill"}
    subprocess.run(command, check=True, env=environment)
    print("Connection created. Continue with Lab 02 to expose it through a toolbox.")


def main(argv: list[str] | None = None) -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Preflight or create a keyless Foundry IQ connection.")
    parser.add_argument("--apply", action="store_true", help="Create or update the project connection.")
    args = parser.parse_args(argv)
    if not args.apply:
        preflight()
        return
    required = (
        "PROJECT_ENDPOINT",
        "FOUNDRY_IQ_SEARCH_ENDPOINT",
        "FOUNDRY_IQ_KNOWLEDGE_BASE",
        "FOUNDRY_IQ_CONNECTION_NAME",
    )
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        parser.error("--apply requires: " + ", ".join(missing))
    apply()


if __name__ == "__main__":
    main()
