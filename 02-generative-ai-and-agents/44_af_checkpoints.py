# Run: uv run python 02-generative-ai-and-agents/44_af_checkpoints.py [--apply]

"""Microsoft Agent Framework — capture a workflow checkpoint and resume from it.

Checkpoints let a workflow **pause** at a superstep boundary and **resume**
later, on the same process or a different one. The framework serializes the
full workflow state at the end of each superstep: executor state, pending
messages, pending requests/responses, and shared state.

Storage providers (all implement the same `CheckpointStorage` protocol):
  InMemoryCheckpointStorage — tests and demos.
  FileCheckpointStorage    — local disk; survives process restarts (this lesson). Requires an
                             explicit `storage_path` — no default directory.
  CosmosCheckpointStorage  — production, distributed. Needs
                             `agent-framework-azure-cosmos --pre`.

Why this matters
----------------
Long-running workflows, human-in-the-loop pauses, and durable retries all
depend on checkpoints. Without one, a crash restarts the workflow from step
one; with one, it resumes from the last completed superstep.

Code path
---------
1. Two tiny `Executor` subclasses form a 2-node workflow:
   `Uppercaser` → `Reverser`. State is passed via `ctx.send_message`.
2. `FileCheckpointStorage(CHECKPOINT_DIR)` is created — the directory is
   `.checkpoints/` under the repo root. `--apply` runs the two-phase demo:
      Phase A: build workflow with checkpointing → run input → collect
               checkpoint IDs from `list_checkpoints()`.
      Phase B: build a fresh workflow instance (no shared state) → resume
               from the latest checkpoint by passing `checkpoint_id=` and
               `checkpoint_storage=`. Prints the final output.
3. Preflight (no `--apply`) prints checkpoint storage layout only.

What to watch
-------------
- `.checkpoints/` gets populated with one JSON/pickle file per superstep after
  `--apply`. Delete the folder to reset.
- "Resumed from checkpoint" line proves the second workflow picked up where
  the first left off — the input was NOT re-processed by Uppercaser.
- Rehydration reuses executor **identities**, not instances. That's why
  `_build_workflow()` returns a fresh workflow each call.

Env vars
--------
- `AZURE_OPENAI_ENDPOINT`, `DEFAULT_MODEL`, `AZURE_OPENAI_API_KEY` (or
  `DefaultAzureCredential`) — only needed if you swap the toy executors for
  agent-backed ones. This baseline is model-free.
- Local path: `.checkpoints/` under the repo root (auto-created).

Security note
-------------
`FileCheckpointStorage` uses a **restricted unpickler** — only a built-in
allow-list of safe Python types plus framework/OpenAI SDK types can be
restored. For app-defined dataclasses/models, pass their `"module:qualname"`
identifiers via `allowed_checkpoint_types=[...]`. See:
  .context/azure-ai-docs/agent-framework/workflows/checkpoints.md
Checkpoint storage is a trust boundary — never load from untrusted sources.
"""
import argparse
import asyncio
from pathlib import Path

from agent_framework import (
    Executor,
    FileCheckpointStorage,
    WorkflowBuilder,
    WorkflowContext,
    handler,
)

CHECKPOINT_DIR = Path(__file__).resolve().parent.parent / ".checkpoints"


class Uppercaser(Executor):
    """Step 1: uppercase the input string."""

    @handler
    async def handle(self, message: str, ctx: WorkflowContext[str]) -> None:
        upper = message.upper()
        print(f"[Uppercaser] {message!r} → {upper!r}")
        await ctx.send_message(upper)


class Reverser(Executor):
    """Step 2: reverse the string and emit final workflow output."""

    @handler
    async def handle(self, message: str, ctx: WorkflowContext[str]) -> None:
        reversed_ = message[::-1]
        print(f"[Reverser]  {message!r} → {reversed_!r}")
        await ctx.send_message(reversed_)


def _build_workflow(checkpoint_storage: FileCheckpointStorage | None):
    """Return a fresh workflow — do not share executor instances across runs."""
    start = Uppercaser(id="uppercaser")
    tail = Reverser(id="reverser")
    builder = WorkflowBuilder(start_executor=start, checkpoint_storage=checkpoint_storage)
    builder.add_edge(start, tail)
    return builder.build()


def _preflight() -> None:
    print("Checkpoint storage plan:")
    print(f"  path       : {CHECKPOINT_DIR}")
    print("  provider   : FileCheckpointStorage (restricted unpickler)")
    print("  workflow   : Uppercaser → Reverser (2 supersteps)")
    print("Re-run with --apply to execute the two-phase run-then-resume demo.")


async def _run() -> None:
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    storage = FileCheckpointStorage(str(CHECKPOINT_DIR))

    # Phase A — run the workflow with checkpointing enabled.
    print("=== Phase A: initial run ===")
    workflow = _build_workflow(checkpoint_storage=storage)
    async for _event in workflow.run("hello checkpoints", stream=True):
        pass  # events are surfaced via executor prints above

    checkpoints = await storage.list_checkpoints(workflow_name=workflow.name)
    if not checkpoints:
        raise RuntimeError("No checkpoints were captured — check storage path permissions.")
    for c in checkpoints:
        print(f"  checkpoint: {c.checkpoint_id}")

    latest = checkpoints[-1]
    print(f"Latest checkpoint: {latest.checkpoint_id}")

    # Phase B — rehydrate a fresh workflow and resume from the latest checkpoint.
    print("\n=== Phase B: resume from checkpoint ===")
    resumed = _build_workflow(checkpoint_storage=None)
    async for _event in resumed.run(
        checkpoint_id=latest.checkpoint_id,
        checkpoint_storage=storage,
        stream=True,
    ):
        pass
    print("Resumed from checkpoint successfully.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Execute the run-then-resume demo. Without --apply, prints storage plan only.",
    )
    args = parser.parse_args()

    if args.apply:
        asyncio.run(_run())
    else:
        _preflight()


if __name__ == "__main__":
    main()
