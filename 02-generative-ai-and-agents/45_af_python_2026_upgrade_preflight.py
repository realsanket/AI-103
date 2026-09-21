# Run: uv run python 02-generative-ai-and-agents/45_af_python_2026_upgrade_preflight.py
# Preflight only — no --apply. This lesson never changes state or calls Azure.

"""Microsoft Agent Framework — Python 2026 breaking-changes preflight.

The 2026 Python release train restructured several public surfaces of the
Agent Framework. Lessons 15/16/17/18 in this repo were authored against that
new shape, but if you upgrade an existing project you may be sitting on the
old one. This lesson is a **read-only** checklist: it enumerates the
breaking changes from
  `.context/azure-ai-docs/agent-framework/support/upgrade/python-2026-significant-changes.md`
and, for each, prints:
  - what changed,
  - the "am I affected?" question you should ask,
  - which lesson in this repo shows the correct 2026 shape.

Nothing here runs a workflow, imports optional providers, or contacts Azure.
It's safe to run on any machine with Python installed.

Why a preflight?
----------------
The most expensive bugs after an SDK bump are the ones that "look like" the
old API still works — a `Message(text=...)` that silently loses payload, a
`middleware=hooks` that suddenly type-errors, a `SecretString` that stops
being accepted by `json.dumps`. Reading the change list before you install
`--upgrade` catches most of these.

Code path
---------
1. `_CHANGES` — a hand-curated list mirroring the doc, one entry per
   breaking change with a `check` question grounded in the patterns used
   by lessons 15–18.
2. `main()` iterates the list and prints a numbered checklist. That's it.

Env vars
--------
None. This is a preflight-only lesson.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class BreakingChange:
    version: str
    title: str
    summary: str
    ask: str
    relevance: str


_CHANGES: list[BreakingChange] = [
    BreakingChange(
        version="Unreleased",
        title="Lab installs separately; Foundry pins azure-ai-projects 2.6",
        summary=(
            "`agent-framework` and `agent-framework-core[all]` no longer pull "
            "`agent-framework-lab`. Install each Lab module explicitly "
            "(gaia / tau2 / lightning). `agent-framework-foundry` now supports "
            "`azure-ai-projects>=2.2.0,<2.7.0`."
        ),
        ask="Does your requirements file assume Lab is transitive? Does it pin azure-ai-projects outside 2.2–2.6?",
        relevance="Affects any lesson that imports from `agent_framework.foundry` (17, 18) if the environment pins azure-ai-projects tightly.",
    ),
    BreakingChange(
        version="Unreleased",
        title="GitHub Copilot workspace file hooks are opt-in",
        summary=(
            "`GitHubCopilotAgent` no longer loads `.github/hooks/` by default. "
            "Set `GitHubCopilotOptions(enable_file_hooks=True)` for a trusted "
            "working directory."
        ),
        ask="Do you use `GitHubCopilotAgent`? Do you rely on file hooks running automatically?",
        relevance="Not used in lessons 15/16/17/18 directly, but any downstream Copilot agent code needs the explicit opt-in.",
    ),
    BreakingChange(
        version="Unreleased",
        title="File-backed storage uses shared path normalization",
        summary=(
            "File-backed sessions, memory, and todo storage now derive folder "
            "names through one shared storage-key mapping. IDs with "
            "uppercase, path separators, or Unicode may resolve to a "
            "different location after upgrade. Existing data is NOT migrated."
        ),
        ask="Do you use `FileMemoryProvider`, `TodoFileStore`, or file-backed sessions with non-lowercase scope IDs?",
        relevance="Local dev flows only. Lessons 17/18 don't use file storage, but any custom scope IDs in your own code may relocate.",
    ),
    BreakingChange(
        version="Unreleased",
        title="`SecretString` no longer inherits from `str`",
        summary=(
            "`SecretString` masks string conversion, formatting, and "
            "concatenation. `json.dumps` and other APIs that expect a real "
            "`str` no longer accept the wrapper. Call `.get_secret_value()` "
            "at the boundary."
        ),
        ask="Do you serialize credentials, headers, or config objects containing `SecretString`?",
        relevance="Anywhere `AZURE_OPENAI_API_KEY` or similar wraps into a `SecretString` before being sent to a client — extract the value before JSON serialization.",
    ),
    BreakingChange(
        version="Unreleased",
        title="Middleware inputs require a sequence; Agent Hooks installs separately",
        summary=(
            "`Agent(client=..., middleware=hooks)` no longer accepts a single "
            "middleware value. Pass a sequence: `middleware=[hooks]`. The "
            "`agent-framework-core[agent-hooks]` extra is removed — install "
            "`agent-hooks-sdk` directly."
        ),
        ask="Do you construct `Agent(..., middleware=<single_value>)` anywhere?",
        relevance="Lesson 17 constructs `Agent(client=..., instructions=...)` with no middleware, so it is unaffected. Fix your own code paths.",
    ),
    BreakingChange(
        version="1.14.0",
        title="Build functional workflow definitions before running them",
        summary=(
            "`@workflow` now returns a stateless `FunctionalWorkflowDefinition`. "
            "Call `.build(checkpoint_storage=...)` to create a stateful "
            "`FunctionalWorkflow`, then `.run()` or `.as_agent()`."
        ),
        ask="Do you use the `@workflow` decorator and call `.run(...)` directly on it?",
        relevance="Lesson 44 uses `WorkflowBuilder` (imperative) — unaffected. If you have functional workflows, insert an explicit `.build()` step.",
    ),
    BreakingChange(
        version="1.14.0",
        title="[Beta] Foundry Hosted Agent state moves to Foundry State Store",
        summary=(
            "`FoundrySessionStore(path)` removed from beta "
            "`agent-framework-foundry-hosting`. `ResponsesHostServer` now uses "
            "`FoundryAgentSessionStore` and Foundry State Store-backed defaults."
        ),
        ask="Do you host agents via `ResponsesHostServer` with a custom `FoundrySessionStore(path)`?",
        relevance="Hosted-agent lessons 28–30 in this repo. If you customized session/checkpoint providers, switch to `agent_session_store_provider` / `checkpoint_store_provider`.",
    ),
    BreakingChange(
        version="1.15.0",
        title="OpenTelemetry GenAI semantic conventions consolidated",
        summary=(
            "Agent Framework now defaults to the latest experimental GenAI "
            "span attributes (`gen_ai.provider.name` replaces `gen_ai.system`). "
            "Set `OTEL_SEMCONV_STABILITY_OPT_IN` without `gen_ai_latest_experimental` "
            "to pin v1.36 attributes."
        ),
        ask="Do your traces/dashboards filter on `gen_ai.system`?",
        relevance="Lessons 23/24 (tracing/observability). Update Application Insights queries to the new attribute name.",
    ),
    BreakingChange(
        version="1.6.0",
        title="Instrumentation enabled by default",
        summary=(
            "`agent-framework-core` and `agent-framework-foundry` now emit "
            "OpenTelemetry spans automatically. Pass "
            "`enable_instrumentation=False` to opt out."
        ),
        ask="Do you run parallel telemetry pipelines that could double-count spans?",
        relevance="Lesson 17 relies on this default so App Insights spans appear without extra code. Confirmed behavior; no code change required.",
    ),
    BreakingChange(
        version="1.1.0",
        title="`CosmosCheckpointStorage` restricted pickle deserialization",
        summary=(
            "Matches `FileCheckpointStorage`: only a safe built-in type set "
            "and framework types deserialize by default. Pass "
            "`allowed_checkpoint_types=['my_app.models:MyState']` for app types."
        ),
        ask="Do your checkpoints contain custom dataclasses / Pydantic models?",
        relevance="Lesson 44 (checkpoints). The demo uses only stdlib strings, so no `allowed_checkpoint_types` is needed. Real workflows with custom state must list them.",
    ),
    BreakingChange(
        version="1.0.1",
        title="`FileCheckpointStorage` restricted pickle deserialization",
        summary=(
            "Same restricted-unpickler hardening as CosmosCheckpointStorage. "
            "`storage_path` is required — there is no default directory."
        ),
        ask="Do you call `FileCheckpointStorage(directory=...)` (the old keyword) or omit the path?",
        relevance="Lesson 44 passes `storage_path` positionally — matches the new signature.",
    ),
    BreakingChange(
        version="1.0.0",
        title="`Message(..., text=...)` removed — use `contents=[...]`",
        summary=(
            "Build text messages as `Message(role='user', contents=['Hello'])`. "
            "Plain strings inside `contents=[...]` are normalized to text content."
        ),
        ask="Do you construct `Message(role=..., text=...)` in workflow inputs, middleware responses, or migration code?",
        relevance="Lessons 15/16 emit JSON schemas — unaffected. Custom middleware and orchestration helpers may still use the old shape.",
    ),
    BreakingChange(
        version="1.0.0",
        title="Foundry now owns Python embeddings and models-endpoint settings",
        summary=(
            "`agent-framework-azure-ai` was removed. Use "
            "`FoundryEmbeddingClient` from `agent_framework.foundry`. New env "
            "vars: `FOUNDRY_MODELS_ENDPOINT`, `FOUNDRY_MODELS_API_KEY`, "
            "`FOUNDRY_EMBEDDING_MODEL`."
        ),
        ask="Do you import `AzureAIInferenceEmbeddingClient` or read `AZURE_AI_SERVICES_ENDPOINT`?",
        relevance="Not used by lessons 15/16/17/18. Any Foundry embedding code in your own repo needs the namespace + env var rename.",
    ),
    BreakingChange(
        version="1.0.0",
        title="Workflows route runtime kwargs through explicit buckets",
        summary=(
            "`workflow.run(...)` no longer forwards generic `**kwargs`. Use "
            "`function_invocation_kwargs=` and `client_kwargs=`. Flat mappings "
            "are global; executor-ID-keyed mappings are per-executor."
        ),
        ask="Do you pass extra kwargs to `workflow.run(...)` expecting them to reach agent executors?",
        relevance="Lessons 43/44 pass only positional input / typed input dicts — unaffected. Multi-agent workflows in your own code need the explicit buckets.",
    ),
    BreakingChange(
        version="1.0.0rc6",
        title="Model selection is standardized on `model`",
        summary=(
            "Use `model=` everywhere. `model_id`, `deployment_name`, and "
            "`model_deployment_name` are removed. Env vars renamed: "
            "`OPENAI_MODEL`, `AZURE_OPENAI_MODEL`, `FOUNDRY_MODEL`, "
            "`ANTHROPIC_CHAT_MODEL`, `FOUNDRY_LOCAL_MODEL`."
        ),
        ask="Do any clients pass `model_id=` or `deployment_name=`? Any env var still called `AZURE_OPENAI_DEPLOYMENT`?",
        relevance="Lesson 17 uses `FoundryChatClient(model=settings().default_model, ...)` — matches the new shape.",
    ),
    BreakingChange(
        version="1.0.0rc6",
        title="Deprecated Azure/OpenAI compatibility surfaces removed",
        summary=(
            "`AzureOpenAI*` and older `AzureAI*` client/agent classes are gone. "
            "Use `OpenAIChatClient` / `OpenAIChatCompletionClient` / "
            "`OpenAIEmbeddingClient` / `FoundryChatClient` / `FoundryAgent`."
        ),
        ask="Do you import from `agent_framework.azure` for chat/embedding clients?",
        relevance="Lesson 17 imports `FoundryChatClient` — correct 2026 shape. Any leftover `AzureOpenAIResponsesClient` usage must be migrated.",
    ),
    BreakingChange(
        version="1.0.0rc6",
        title="Provider-leading client design and package split",
        summary=(
            "OpenAI clients live in `agent-framework-openai` / "
            "`agent_framework.openai`. Foundry clients live in "
            "`agent-framework-foundry` / `agent_framework.foundry`. Install "
            "only what you import."
        ),
        ask="Does your install manifest bring the correct provider packages, not just `agent-framework-core`?",
        relevance="Lessons 43/44/45 need `agent-framework` (which pulls in declarative + core). Lessons 15/16/17/18 additionally need `agent-framework-foundry`.",
    ),
    BreakingChange(
        version="1.7.0",
        title="Declarative: Python-only actions removed; alias kinds renamed to C# canonical",
        summary=(
            "Python-only declarative action kinds are removed. Alias kinds are "
            "renamed to match the C# canonical names for cross-language "
            "consistency."
        ),
        ask="Do your YAML workflows use action `kind:` names that no longer appear in the current declarative docs?",
        relevance="Lesson 43 uses only current canonical kinds (`SetVariable`, `ConditionGroup`, `If`, `SendActivity`) — safe. Audit any pre-1.7 YAML you carry forward.",
    ),
]


def main() -> None:
    print("Microsoft Agent Framework — Python 2026 upgrade preflight")
    print("=" * 60)
    print(
        "Read-only checklist. No env vars, no imports of optional providers, "
        "no Azure calls."
    )
    print("Source: .context/azure-ai-docs/agent-framework/support/upgrade/python-2026-significant-changes.md")
    print()

    for i, change in enumerate(_CHANGES, start=1):
        print(f"[{i:02d}] {change.version:>12} — {change.title}")
        print(f"     summary : {change.summary}")
        print(f"     ask     : {change.ask}")
        print(f"     lessons : {change.relevance}")
        print()

    print(f"Total breaking changes reviewed: {len(_CHANGES)}")
    print("Next step: for every 'ask' that answers yes, grep your codebase and apply the matching fix from the doc.")


if __name__ == "__main__":
    main()
