# Run: uv run python 02-generative-ai-and-agents/50_af_approval_workflow.py [--apply] [--coverage-delta 25000] [--answer approved]
# Practice-question coverage: Q33, Q109.
"""Human-in-the-loop approval in a declarative workflow: pause, ask, resume.

Scenario: PolicyWriter drafts a customer-policy change, RiskReviewer rates the
risk, low-risk changes finalize automatically, and high-risk changes need a
person's approval before they finalize. `workflows/policy_approval.yaml`
encodes this as a **sequential** workflow (fixed order, predictable execution)
with a `Question` action as the approval checkpoint — the same concept as the
"Ask a question" node in the Foundry visual workflow builder and an
`ask_question` step in workflow YAML.

How the pause works:
  1. `workflow.run(inputs)` executes until the Question action, then stops and
     returns a request-info event (`ExternalInputRequest`) carrying the
     question text and the variable it will fill (`Local.approval`).
  2. Your application shows the question to an approver.
  3. `workflow.run(responses={request_id: ExternalInputResponse(user_input=...)})`
     resumes the same run. The next step's condition (`Local.approval =
     "approved"`) decides whether the change finalizes or returns to the writer.
The consequential step never runs on the model's say-so alone.

Default preflight loads and validates the YAML. `--apply` runs it locally —
no model, no Azure call — and answers the checkpoint with `--answer`
(or prompts on the terminal when `--answer` is omitted).

Runtime prerequisite: PowerFx expressions need a .NET 8+ runtime
(`dotnet --list-runtimes`); see lesson 43.
"""
import argparse
import asyncio
from pathlib import Path

WORKFLOW_FILE = Path(__file__).parent / "workflows" / "policy_approval.yaml"


def _factory():
    from agent_framework.declarative import WorkflowFactory

    return WorkflowFactory()


async def run_workflow(change: str, coverage_delta: float, answer: str | None) -> list[str]:
    """Run once; if the workflow pauses for approval, answer and resume."""
    from agent_framework.declarative import ExternalInputResponse

    workflow = _factory().create_workflow_from_yaml_path(WORKFLOW_FILE)
    result = await workflow.run({"change": change, "coverage_delta": coverage_delta})
    requests = result.get_request_info_events()
    if requests:
        request = requests[0]
        print(f"Paused for approval: {request.data.message}")
        if answer is None:
            answer = input("Type approved or rejected: ").strip()
        print(f"Approver answered: {answer}")
        result = await workflow.run(responses={request.request_id: ExternalInputResponse(user_input=answer)})
    else:
        print("No approval needed: low-risk update.")
    return [str(output) for output in result.get_outputs()]


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--apply", action="store_true", help="Run the workflow locally.")
    parser.add_argument("--change", default="Add flood cover to the Northwind warehouse policy")
    parser.add_argument("--coverage-delta", type=float, default=25000, help="10000 or more is high risk.")
    parser.add_argument("--answer", help="Approver answer, for example approved or rejected.")
    args = parser.parse_args(argv)

    workflow = _factory().create_workflow_from_yaml_path(WORKFLOW_FILE)
    print(f"Loaded workflow: {workflow.name} ({WORKFLOW_FILE.name})")
    if not args.apply:
        print("Preflight only. Re-run with --apply to execute locally (no model, no Azure call).")
        return
    for output in asyncio.run(run_workflow(args.change, args.coverage_delta, args.answer)):
        print(f"Output: {output}")


if __name__ == "__main__":
    main()
