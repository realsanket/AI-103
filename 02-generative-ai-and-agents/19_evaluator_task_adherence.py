"""Agent-specific evaluators — Task Adherence + Tool Call Accuracy.

Runs a small agent trace, then evaluates it with Foundry's built-in
`TaskAdherenceEvaluator` and `ToolCallAccuracyEvaluator`.

Requires the `azure-ai-evaluation` SDK. Prints score + reasoning per evaluator.
"""
import json

from _shared.config import settings
from _shared.foundry_client import project_client
from _shared.openai_client import openai_client


def _run_agent_trace() -> dict:
    """Ask a question; return a minimal agent-trace shape the evaluator can consume."""
    client = openai_client()
    r = client.responses.create(
        model=settings().default_model,
        instructions="You are a CloudXeus support agent. Answer briefly.",
        input="What is the refund window for a Pro plan? If you don't know, say so.",
    )
    return {
        "query": "What is the refund window for a Pro plan?",
        "response": r.output_text,
        "tool_calls": [],  # populate if you drove function calls
        "system_message": "You are a CloudXeus support agent. Answer briefly.",
    }


def main() -> None:
    trace = _run_agent_trace()
    print("=== Trace ===")
    print(json.dumps(trace, indent=2))

    try:
        from azure.ai.evaluation import TaskAdherenceEvaluator, ToolCallAccuracyEvaluator
    except ImportError:  # pragma: no cover
        raise SystemExit("pip install azure-ai-evaluation to run this lesson.")

    model_config = {
        "azure_endpoint": settings().foundry_endpoint,
        "azure_deployment": settings().default_model,
        "api_version": "2024-10-21",
    }
    task_adh = TaskAdherenceEvaluator(model_config=model_config)
    tool_acc = ToolCallAccuracyEvaluator(model_config=model_config)

    print("\n=== Task Adherence ===")
    print(task_adh(query=trace["query"], response=trace["response"]))

    print("\n=== Tool Call Accuracy ===")
    print(tool_acc(query=trace["query"], response=trace["response"], tool_calls=trace["tool_calls"]))


if __name__ == "__main__":
    main()
