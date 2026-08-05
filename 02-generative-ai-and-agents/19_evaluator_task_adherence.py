"""Local SDK evaluation — Task Adherence + Tool Call Accuracy (preview).

Runs a small model response, then sends it to the evaluator SDK. This lesson
does not create a Foundry portal evaluation, upload a dataset, or guarantee a
score. Tool Call Accuracy receives tool definitions even though this deliberately
tool-free trace is expected to reveal that no tool call occurred.

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
        instructions="You are a Northwind support agent. Answer briefly.",
        input="What is the refund window for a Pro plan? If you don't know, say so.",
    )
    return {
        "query": "What is the refund window for a Pro plan?",
        "response": r.output_text,
        "tool_calls": [],
        "tool_definitions": [
            {
                "name": "get_refund_policy",
                "description": "Gets the current Northwind refund policy.",
                "parameters": {"type": "object", "properties": {}},
            }
        ],
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
        "azure_endpoint": settings().azure_openai_endpoint,
        "azure_deployment": settings().default_model,
        "api_version": "2024-10-21",
    }
    task_adh = TaskAdherenceEvaluator(model_config=model_config)
    tool_acc = ToolCallAccuracyEvaluator(model_config=model_config)

    print("\n=== Task Adherence ===")
    print(task_adh(query=trace["query"], response=trace["response"]))

    print("\n=== Tool Call Accuracy ===")
    print(
        tool_acc(
            query=trace["query"],
            tool_calls=trace["tool_calls"],
            tool_definitions=trace["tool_definitions"],
        )
    )


if __name__ == "__main__":
    main()
