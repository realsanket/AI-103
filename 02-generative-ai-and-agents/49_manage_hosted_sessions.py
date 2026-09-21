# Run: uv run python 02-generative-ai-and-agents/49_manage_hosted_sessions.py [--apply]
"""List, inspect, and delete hosted-agent sessions.

A hosted-agent session is a stateful, isolated sandbox tied to one logical
workload (a user's chat, an evaluation, a background job). The platform keeps
`$HOME` and uploaded files across turns and idle periods for up to 30 days.
Sessions and CONVERSATIONS are distinct: conversation IDs thread message
history; `agent_session_id` binds calls to the same sandbox/filesystem.

This lesson uses the Python SDK's session-management surface on
`AIProjectClient.agents`:

    project.agents.list_sessions(agent_name=...)      # read
    project.agents.get_session(agent_name=..., session_id=...)
    project.agents.delete_session(agent_name=..., session_id=...)

Preflight validates env vars, explains isolation-key semantics, and prints the
runbook. `--apply` lists sessions for `HOSTED_AGENT_NAME`; when `HOSTED_SESSION_ID`
is also set, it fetches that session's details and, if `--delete` is passed,
deletes it. Deleting a session terminates its compute and releases resources.

Isolation-key note (doc-verbatim):
  - `Entra` auth scheme: the platform derives the isolation key from the
    caller's token. The `x-ms-user-isolation-key` header is accepted but
    ignored, and each caller only sees their own sessions.
  - `Header` auth scheme: the platform reads `x-ms-user-isolation-key` and
    scopes list/get/delete to that value. Cross-user administration requires
    the Foundry User role at project scope (data actions `sessions/read` and
    `sessions/write`).

Code path:
  Preflight — print session vs. conversation distinction, RBAC, endpoint map.
  --apply   — list sessions for the agent; if HOSTED_SESSION_ID is set, print
              its details. With --delete, also delete that session.

What to watch:
  A caller with only own-sessions scope sees an empty list unless they created
  a session. Regular callers get their own scope automatically under `Entra`
  auth. Deleting a session is irreversible; the sandbox is torn down.

Prerequisites / env vars:
  PROJECT_ENDPOINT       — Foundry project endpoint
  HOSTED_AGENT_NAME      — hosted agent whose sessions we operate on
  HOSTED_SESSION_ID      — optional: specific session to inspect / delete
"""
import argparse
import os

from _shared.config import settings


def _agent_name() -> str:
    name = os.environ.get("HOSTED_AGENT_NAME", "").strip()
    if not name:
        raise SystemExit("Set HOSTED_AGENT_NAME to the hosted agent whose sessions to manage.")
    return name


def preflight() -> None:
    s = settings()
    name = os.environ.get("HOSTED_AGENT_NAME") or "<HOSTED_AGENT_NAME not set>"
    session_id = os.environ.get("HOSTED_SESSION_ID") or "<HOSTED_SESSION_ID not set>"
    print("No cloud calls made.")
    print(f"Project endpoint:  {s.project_endpoint or '<PROJECT_ENDPOINT not set>'}")
    print(f"Hosted agent name: {name}")
    print(f"Target session ID: {session_id}")
    print()
    print("Sessions vs conversations (doc-verbatim distinction):")
    print("  - Session = sandbox compute + persisted filesystem ($HOME, /files).")
    print("  - Conversation = message/tool history threaded via previous_response_id or")
    print("    the `conversation` field (Responses protocol only).")
    print("  - Reusing agent_session_id does NOT replay prior messages; it reuses files/$HOME.")
    print()
    print("Idle timeout: 120s..3600s (default 900s), set on the agent version.")
    print("Sessions persist up to 30 days from last access.")
    print()
    print("RBAC:")
    print("  - Own sessions only: any authenticated caller with project data-plane access.")
    print("  - Cross-user (admin/debug): Foundry User at project scope grants sessions/read")
    print("    and sessions/write; then list/get/delete return every caller's sessions.")
    print()
    print("Run --apply to list sessions for the agent.")
    print("Run --apply with HOSTED_SESSION_ID set to fetch that session.")
    print("Run --apply --delete with HOSTED_SESSION_ID set to delete that session.")


def apply(delete: bool) -> None:
    from _shared.foundry_client import project_client

    agent_name = _agent_name()
    session_id = os.environ.get("HOSTED_SESSION_ID", "").strip()
    client = project_client()

    print(f"Sessions for {agent_name!r}:")
    count = 0
    for item in client.agents.list_sessions(agent_name=agent_name):
        sid = getattr(item, "agent_session_id", "?")
        status = getattr(item, "status", "?")
        created = getattr(item, "created_at", "?")
        print(f"  - {sid}  status={status}  created={created}")
        count += 1
    if count == 0:
        print("  (none visible to this caller)")

    if not session_id:
        print()
        print("Set HOSTED_SESSION_ID to inspect or delete a specific session.")
        return

    print()
    print(f"Details for session {session_id}:")
    session = client.agents.get_session(agent_name=agent_name, session_id=session_id)
    for attr in ("agent_session_id", "status", "created_at", "last_accessed_at", "expires_at"):
        print(f"  {attr}: {getattr(session, attr, '?')}")

    if delete:
        print()
        print(f"Deleting session {session_id}...")
        client.agents.delete_session(agent_name=agent_name, session_id=session_id)
        print("Deleted. Sandbox compute released; persisted filesystem discarded.")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Manage hosted-agent sessions.")
    parser.add_argument("--apply", action="store_true", help="Execute the list/get/delete flow.")
    parser.add_argument("--delete", action="store_true", help="Also delete HOSTED_SESSION_ID.")
    args = parser.parse_args(argv)
    if args.delete and not args.apply:
        parser.error("--delete requires --apply.")
    if not args.apply:
        preflight()
        return
    apply(args.delete)


if __name__ == "__main__":
    main()
