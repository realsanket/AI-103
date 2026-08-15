# Run: uv run python 02-generative-ai-and-agents/14_foundry_memory.py
"""Foundry Memory (preview): store lifecycle, agent recall, remember/forget, and direct APIs.

Memory stores persist user preferences and conversation facts across sessions. The service
extracts memories asynchronously from conversations (via MemorySearchPreviewTool on an agent)
or synchronously via direct begin_update_memories calls. Retrieval is semantic — the tool
injects relevant memories into each agent response.

This is NOT a database, consent platform, or PII vault. Memory extraction and recall are
non-deterministic. Writes are debounced — a stated preference may not be recalled immediately.
Memory stores persist until deleted; clean up test stores to avoid billing drift.

Flows:
  Default   — preflight: validates env vars and prints API structure + scope rules.
  --apply   — full flow (4 parts, all cleaned up after):
    Part 1: Create or reuse a memory store (user_profile + chat_summary + procedural + 30-day TTL).
    Part 2: Create ephemeral agent with MemorySearchPreviewTool(scope={{$userId}}, update_delay=1);
            Conversation 1 states a preference → wait debounce → Conversation 2 attempts recall.
    Part 3: Remember/forget commands — direct responses.create with memory tool; check
            memory_command_call items in response output.
    Part 4: Direct API — begin_update_memories (explicit fact injection) + search_memories
            (retrieve stored memories by semantic query).
    Cleanup: delete scope for test user; delete agent version. Store persists (delete manually).

What to watch in the output:
  Conversation 2 — model may or may not echo preference; async extraction is non-deterministic.
  memory_command_call type — appears in output when model processes a remember/forget instruction.
  memory_operations — from begin_update_memories; shows what the service extracted and stored.
  memories — from search_memories; shows retrieved content ranked by semantic similarity.

Prerequisites / env vars:
  PROJECT_ENDPOINT  — https://<resource>.services.ai.azure.com/api/projects/<project>
  DEFAULT_MODEL     — chat deployment (gpt-5.2 or similar)
  EMBEDDING_MODEL   — embedding deployment (text-embedding-3-small or similar)
  --apply           — runs cloud calls; creates persistent memory store + ephemeral agent
  --skip-wait       — skip 65-second debounce wait (recall turn may miss the preference)
  --store-name      — override memory store name (default: ai-103-memory-lesson)
  --user-id         — x-memory-user-id header value and API scope (default: user-lesson-14)
"""
import argparse
import json
import os
import sys
import time
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from _shared.config import add_lesson_overrides, resolve_models, settings  # noqa: E402
from _shared.foundry_client import resolve_project_client  # noqa: E402

# ---------------------------------------------------------------------------
# Import guard — all azure.ai.projects imports deferred so preflight runs
# without SDK installed
# ---------------------------------------------------------------------------

_AGENT_NAME = "ai-103-memory-lesson-agent"
_DEFAULT_STORE = "ai-103-memory-lesson"
_DEFAULT_USER = "user-lesson-14"


def preflight(store_name: str, user_id: str) -> None:
    s = settings()
    ok = True
    for name, val in [
        ("PROJECT_ENDPOINT", os.environ.get("PROJECT_ENDPOINT", "")),
        ("DEFAULT_MODEL", s.default_model),
        ("EMBEDDING_MODEL", s.embedding_model),
    ]:
        if val:
            display = val[:60] + "..." if len(val) > 60 else val
            print(f"  [OK]   {name} = {display}")
        else:
            print(f"  [FAIL] {name} — not set")
            ok = False

    print()
    print("Memory store options that will be set:")
    print("  MemoryStoreDefaultOptions(")
    print("      chat_summary_enabled=True,")
    print("      user_profile_enabled=True,")
    print("      procedural_memory_enabled=True,")
    print("      default_ttl_seconds=timedelta(days=30),")
    print("      user_profile_details='Store support preferences only. No credentials, PII.'")
    print("  )")
    print()
    print("Scope rules:")
    print("  Tool scope = '{{$userId}}'  → resolves from x-memory-user-id header per request")
    print("  API scope  = explicit string → you pass it in each begin_update/search call")
    print(f"  This lesson uses scope='{user_id}' for direct API calls")
    print(f"  and x-memory-user-id: {user_id} header for agent conversations")
    print()
    print("Four API surfaces covered:")
    print("  1. project.beta.memory_stores.create/list/delete (store lifecycle)")
    print("  2. MemorySearchPreviewTool on agent + openai.responses.create (agent recall)")
    print("  3. openai.responses.create(tools=[memory_tool]) + memory_command_call (remember/forget)")
    print("  4. project.beta.memory_stores.begin_update_memories/.search_memories (direct API)")
    print()
    if not ok:
        print("[WARN] Set missing env vars before running with --apply")
    else:
        print(f"[OK] Ready — run with --apply --store-name {store_name} --user-id {user_id}")


# ---------------------------------------------------------------------------
# Part 1 — Create or reuse memory store
# ---------------------------------------------------------------------------

def _ensure_store(project, store_name: str, chat_model: str, embedding_model: str):
    from azure.ai.projects.models import MemoryStoreDefaultDefinition, MemoryStoreDefaultOptions

    for store in project.beta.memory_stores.list():
        if store.name == store_name:
            print(f"[store] Reusing existing: {store_name}")
            return store

    options = MemoryStoreDefaultOptions(
        chat_summary_enabled=True,
        user_profile_enabled=True,
        procedural_memory_enabled=True,
        default_ttl_seconds=timedelta(days=30),
        user_profile_details=(
            "Store customer support preferences only. "
            "Do not store credentials, financial information, precise location, or PII."
        ),
    )
    definition = MemoryStoreDefaultDefinition(
        chat_model=chat_model,
        embedding_model=embedding_model,
        options=options,
    )
    store = project.beta.memory_stores.create(
        name=store_name,
        definition=definition,
        description="AI-103 lesson 14 memory store — procedural + user_profile + 30-day TTL",
    )
    print(f"[store] Created: {store.name}  (chat={chat_model}, embedding={embedding_model})")
    return store


# ---------------------------------------------------------------------------
# Part 2 — Agent conversation recall
# ---------------------------------------------------------------------------

def _run_agent_conversation(project, store_name: str, user_id: str, skip_wait: bool, chat_model: str) -> str:
    from azure.ai.projects.models import MemorySearchPreviewTool, PromptAgentDefinition

    agent = project.agents.create_version(
        agent_name=_AGENT_NAME,
        definition=PromptAgentDefinition(
            model=chat_model,
            instructions=(
                "You are a customer support assistant. "
                "Use memory to recall stated preferences. "
                "Never claim a preference you cannot retrieve from memory."
            ),
            tools=[
                MemorySearchPreviewTool(
                    memory_store_name=store_name,
                    scope="{{$userId}}",   # resolved from x-memory-user-id header
                    update_delay=1,        # 1s inactivity before memory update fires
                    # Production: use 300 (5 min default) to avoid premature extraction
                )
            ],
        ),
    )
    print(f"[agent] Created: {agent.name} v{agent.version}")

    openai = project.get_openai_client()
    headers = {"x-memory-user-id": user_id}
    agent_ref = {"name": agent.name, "type": "agent_reference"}

    # Conversation 1 — state a preference
    conv1 = openai.conversations.create()
    resp1 = openai.responses.create(
        input="For all my orders, I prefer dairy-free catering and email updates.",
        conversation=conv1.id,
        extra_body={"agent_reference": agent_ref},
        extra_headers=headers,
    )
    print(f"[conv1] {resp1.output_text}")

    # Wait for debounce — memory writes happen after update_delay seconds of inactivity
    if skip_wait:
        print("[wait] Skipped (--skip-wait); second conversation may not recall preference.")
    else:
        print("[wait] Sleeping 65s for memory extraction debounce...")
        time.sleep(65)

    # Conversation 2 — new conversation, same user scope → model may recall preference
    conv2 = openai.conversations.create()
    resp2 = openai.responses.create(
        input="What catering preference do I have on file?",
        conversation=conv2.id,
        extra_body={"agent_reference": agent_ref},
        extra_headers=headers,
    )
    print(f"[conv2] {resp2.output_text}")

    return str(agent.version)


# ---------------------------------------------------------------------------
# Part 3 — Remember / forget commands
# ---------------------------------------------------------------------------

def _run_remember_forget(project, store_name: str, user_id: str, chat_model: str) -> None:
    openai = project.get_openai_client()

    # memory_search_preview used as a direct tool (no agent reference)
    tools = [
        {
            "type": "memory_search_preview",
            "memory_store_name": store_name,
            "scope": user_id,
        }
    ]

    # Remember — model returns memory_command_call item in output
    remember_resp = openai.responses.create(
        model=chat_model,
        tools=tools,
        input="Please remember that I prefer aisle seats on all flights.",
    )
    print("[remember] Response output items:")
    for item in remember_resp.output:
        item_type = getattr(item, "type", None)
        if item_type == "memory_command_call":
            raw_args = getattr(item, "arguments", "{}")
            try:
                args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
            except (json.JSONDecodeError, TypeError):
                args = raw_args
            status = getattr(item, "status", "?")
            print(f"  type:      {item_type}")
            print(f"  action:    {args.get('action', '?') if isinstance(args, dict) else args}")
            print(f"  content:   {args.get('content', '?') if isinstance(args, dict) else ''}")
            print(f"  status:    {status}")
        elif item_type == "message":
            content = getattr(item, "content", None)
            if content:
                text = content[0].text if hasattr(content[0], "text") else str(content[0])
                print(f"  message:   {text}")

    # Forget — confirms removal; memory_command_call with action=forget
    forget_resp = openai.responses.create(
        model=chat_model,
        tools=tools,
        input="Please forget my seat preference.",
    )
    print("[forget] Response output items:")
    for item in forget_resp.output:
        item_type = getattr(item, "type", None)
        if item_type == "memory_command_call":
            raw_args = getattr(item, "arguments", "{}")
            try:
                args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
            except (json.JSONDecodeError, TypeError):
                args = raw_args
            print(f"  type:   {item_type}")
            print(f"  action: {args.get('action', '?') if isinstance(args, dict) else args}")
            print(f"  status: {getattr(item, 'status', '?')}")


# ---------------------------------------------------------------------------
# Part 4 — Direct API: begin_update_memories + search_memories
# ---------------------------------------------------------------------------

def _run_direct_api(project, store_name: str, user_id: str) -> None:
    from azure.ai.projects.models import MemorySearchOptions

    # Add facts directly — synchronous long-running operation (may take ~1 min)
    msg1 = {"type": "message", "role": "user",
             "content": "I prefer dark roast coffee and usually drink it in the morning."}
    print("[update] Submitting begin_update_memories (update_delay=0, waits ~1 min)...")
    update_poller = project.beta.memory_stores.begin_update_memories(
        name=store_name,
        scope=user_id,
        items=[msg1],
        update_delay=0,  # trigger immediately, no inactivity wait
    )
    try:
        update_result = update_poller.result()
    except Exception as e:
        msg = str(e)
        if "401" in msg or "Authentication" in msg:
            print(f"[update] FAIL — 401 from memory service backend.")
            print("  begin_update_memories runs server-side: the project's managed identity")
            print("  calls the model on your behalf. Fix:")
            print("  → Enable system-assigned managed identity on the Foundry project.")
            print("  → Assign 'Cognitive Services OpenAI User' to that MI on the OpenAI resource.")
            print(f"  Raw error: {msg[:300]}")
        else:
            print(f"[update] FAIL — {msg[:300]}")
        return
    ops = getattr(update_result, "memory_operations", []) or []
    print(f"[update] {len(ops)} memory operation(s):")
    for op in ops:
        mi = getattr(op, "memory_item", None)
        mid = getattr(mi, "memory_id", "?") if mi else "?"
        content = getattr(mi, "content", "?") if mi else "?"
        kind = getattr(op, "kind", "?")
        print(f"  [{kind}] id={mid}  content={content!r}")

    # Chain a second update from the first
    msg2 = {"type": "message", "role": "user",
             "content": "I also enjoy cappuccinos in the afternoon."}
    update_id = getattr(update_poller, "update_id", None)
    print("[update] Chaining second update...")
    new_poller = project.beta.memory_stores.begin_update_memories(
        name=store_name,
        scope=user_id,
        items=[msg2],
        previous_update_id=update_id,
        update_delay=0,
    )
    new_result = new_poller.result()
    new_ops = getattr(new_result, "memory_operations", []) or []
    print(f"[update] {len(new_ops)} additional memory operation(s):")
    for op in new_ops:
        mi = getattr(op, "memory_item", None)
        content = getattr(mi, "content", "?") if mi else "?"
        kind = getattr(op, "kind", "?")
        print(f"  [{kind}] {content!r}")

    # Semantic search
    query = {"type": "message", "role": "user", "content": "What are my coffee preferences?"}
    search_resp = project.beta.memory_stores.search_memories(
        name=store_name,
        scope=user_id,
        items=[query],
        options=MemorySearchOptions(max_memories=5),
    )
    memories = getattr(search_resp, "memories", []) or []
    print(f"[search] Found {len(memories)} memory item(s):")
    for m in memories:
        mi = getattr(m, "memory_item", None)
        mid = getattr(mi, "memory_id", "?") if mi else "?"
        content = getattr(mi, "content", "?") if mi else "?"
        print(f"  id={mid}  content={content!r}")


# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------

def _cleanup(project, agent_version: str) -> None:
    # Delete the test user's scope (removes their memory data from the store)
    try:
        project.beta.memory_stores.delete_scope(
            name=_DEFAULT_STORE,
            scope=_DEFAULT_USER,
        )
        print("[cleanup] Deleted scope for test user")
    except Exception as e:
        print(f"[cleanup] Scope delete skipped: {e}")

    # Delete the ephemeral agent version
    try:
        project.agents.delete_version(
            agent_name=_AGENT_NAME,
            agent_version=agent_version,
        )
        print(f"[cleanup] Deleted agent version {agent_version}")
    except Exception as e:
        print(f"[cleanup] Agent delete skipped: {e}")

    print("[note] Memory store itself persists — delete manually to stop billing:")
    print(f"       project.beta.memory_stores.delete('{_DEFAULT_STORE}')")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true",
                        help="Run live cloud calls (creates/modifies cloud resources)")
    parser.add_argument("--skip-wait", action="store_true",
                        help="Skip 65s debounce wait (recall turn may miss the preference)")
    parser.add_argument("--store-name", default=_DEFAULT_STORE)
    parser.add_argument("--user-id", default=_DEFAULT_USER)
    add_lesson_overrides(parser)   # --project-endpoint, --chat-model, --embedding-model
    args = parser.parse_args()

    if not args.apply:
        preflight(args.store_name, args.user_id)
        return

    chat_model, embedding_model = resolve_models(args)
    print(f"[models] chat={chat_model}  embedding={embedding_model}")

    project = resolve_project_client(args.project_endpoint)
    if args.project_endpoint:
        print(f"[project] endpoint={args.project_endpoint}")

    print("=== Part 1: Memory store ===")
    _ensure_store(project, args.store_name, chat_model, embedding_model)

    stores = list(project.beta.memory_stores.list())
    print(f"[store] {len(stores)} store(s) in project:")
    for st in stores:
        print(f"  - {st.name}  (id={getattr(st, 'id', '?')}, description={getattr(st, 'description', '')})")

    agent_version = None
    try:
        print("\n=== Part 2: Agent conversation recall ===")
        agent_version = _run_agent_conversation(
            project, args.store_name, args.user_id, args.skip_wait, chat_model
        )

        print("\n=== Part 3: Remember / forget commands ===")
        _run_remember_forget(project, args.store_name, args.user_id, chat_model)

        print("\n=== Part 4: Direct API — update + search ===")
        _run_direct_api(project, args.store_name, args.user_id)

    finally:
        print("\n=== Cleanup ===")
        if agent_version:
            _cleanup(project, agent_version)
        else:
            print("[cleanup] Agent was not created — nothing to delete.")


if __name__ == "__main__":
    main()
