"""Keyless auth end-to-end — DefaultAzureCredential + list agents.

Passes iff (a) you're logged in with `az login`, (b) your identity has the
"Azure AI User" role on the Foundry project, and (c) `.env` is filled in.

If this fails, everything else in the codebase will fail the same way — this
is the smoke test for the auth chain.
"""
from _shared.foundry_client import project_client


def main() -> None:
    client = project_client()
    agents = list(client.agents.list_versions())
    print(f"auth OK. {len(agents)} agent version(s) visible.")
    for a in agents[:10]:
        print(f"  {a.name:<40} v{getattr(a, 'version', '?')}")


if __name__ == "__main__":
    main()
