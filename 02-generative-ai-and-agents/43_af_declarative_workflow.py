# Run: uv run python 02-generative-ai-and-agents/43_af_declarative_workflow.py [--apply]
# Practice-question coverage: Q43.

"""Microsoft Agent Framework — load and execute a declarative YAML workflow.

Declarative workflows describe orchestration in YAML (`workflows/declarative_intake.yaml`)
instead of Python code. The framework parses the file into an executable
workflow graph, resolves variable references (`Local.*`, `Workflow.Inputs.*`,
`Workflow.Outputs.*`, `System.*`), evaluates PowerFx expressions prefixed with
`=`, and runs the actions in order. Non-developers can edit the YAML without
touching Python.

Contrast with the other workflow lessons:
  Lesson 15/16 — Foundry preview workflow YAML (retires Dec 1, 2026), authored
                 as a Foundry agent version and executed by the service.
  Lesson 17    — Programmatic Agent Framework — one Python `Agent(...)` object.
  This lesson  — Local Agent Framework declarative workflow — the YAML replaces
                 hand-written orchestration code. `WorkflowFactory` loads it;
                 `.register_agent(name, agent)` binds any `InvokeAzureAgent`
                 actions to real chat clients.

Code path
---------
1. `WorkflowFactory()` — the entry point to the declarative package.
2. Optionally register named agents so `InvokeAzureAgent` actions in YAML can
   resolve them. This lesson keeps the workflow model-free (no agent calls),
   so registration is shown for reference only.
3. `factory.create_workflow_from_yaml_path(path)` — parse + validate YAML.
4. `--apply` → `await workflow.run({"message": ..., "amount": ...})`
   Prints `Workflow.Outputs.routing` and any intermediate outputs.
5. Preflight (no `--apply`) prints the loaded workflow name and inputs only —
   no state changes, no model tokens.

What to watch
-------------
- `Loaded workflow: northwind-intake-triage` confirms the YAML parsed.
- The `Output:` line contains the routing decision dict built by the YAML
  (`category` + `priority` + `team`). Change the sample `message`/`amount`
  and re-run to see the ConditionGroup + If branches take different paths.
- Editing the YAML alone (no Python change) alters routing behavior — this is
  the whole point of the declarative model.

Env vars
--------
- `PROJECT_ENDPOINT` and `DEFAULT_MODEL` — only needed if you extend the YAML
  with `InvokeAzureAgent` actions and register a `FoundryChatClient`-backed
  agent. This baseline workflow is model-free and needs neither.
- `AZURE_OPENAI_API_KEY` or `DefaultAzureCredential` — same conditional note.
"""
import argparse
import asyncio
from pathlib import Path

from agent_framework.declarative import WorkflowFactory

WORKFLOW_FILE = Path(__file__).parent / "workflows" / "declarative_intake.yaml"

_SAMPLE_INPUT = {
    "message": "Please issue a refund for order #4521 — I was charged twice.",
    "amount": 750,
}


def _preflight() -> None:
    """Load the YAML and print structure without running any action."""
    factory = WorkflowFactory()
    workflow = factory.create_workflow_from_yaml_path(WORKFLOW_FILE)
    print(f"Loaded workflow: {workflow.name}")
    print(f"YAML: {WORKFLOW_FILE}")
    print("Sample input that --apply will use:")
    for key, value in _SAMPLE_INPUT.items():
        print(f"  {key}: {value!r}")
    print("Re-run with --apply to execute the workflow locally.")


async def _run() -> None:
    factory = WorkflowFactory()
    # If you extend the YAML with InvokeAzureAgent actions, register the
    # targets here so the workflow can resolve them by name:
    #   from agent_framework import Agent
    #   from agent_framework.foundry import FoundryChatClient
    #   from azure.identity import DefaultAzureCredential
    #   client = FoundryChatClient(project_endpoint=..., model=..., credential=DefaultAzureCredential())
    #   factory.register_agent("IntakeAgent", Agent(client=client, instructions="..."))
    workflow = factory.create_workflow_from_yaml_path(WORKFLOW_FILE)
    print(f"Loaded workflow: {workflow.name}")
    print("-" * 40)

    result = await workflow.run(_SAMPLE_INPUT)
    for output in result.get_outputs():
        print(f"Output: {output}")
    for intermediate in result.get_intermediate_outputs():
        print(f"Intermediate: {intermediate}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Execute the workflow locally. Without --apply, only preflight prints.",
    )
    args = parser.parse_args()

    if args.apply:
        asyncio.run(_run())
    else:
        _preflight()


if __name__ == "__main__":
    main()
