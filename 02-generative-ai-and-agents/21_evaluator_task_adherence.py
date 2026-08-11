# Run: uv run python 02-generative-ai-and-agents/21_evaluator_task_adherence.py

"""Run local SDK evaluators against one complete agent conversation.

This is a local *invocation* of evaluator SDKs, not a persisted Foundry run:
no dataset, evaluation definition, or run record is created. The evaluator is
still an LLM call, so its conversation is sent to the configured Azure OpenAI
deployment and consumes tokens. Use synthetic or redacted traces.

Task Adherence evaluates the whole agent turn: query contains system/user
messages; response contains every assistant message, tool call, tool result,
and final answer. Passing only final text loses evidence needed to assess an
agent. Tool Call Accuracy needs at least one converter-format tool call plus
matching definitions; an empty tool-call list is not a score.

For a reviewed dataset and durable cloud evaluation run, see lesson 29.
"""
from azure.identity import DefaultAzureCredential

from _shared.config import settings

_QUERY = "What is the refund window for a Pro plan?"
_TOOL_CALL = {
    "type": "tool_call",
    "name": "get_refund_policy",
    "arguments": {},
    "tool_call_id": "refund-policy-1",
}
_TOOL_DEFINITIONS = [
    {
        "name": "get_refund_policy",
        "description": "Gets the current Northwind refund policy.",
        "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
    }
]


def agent_conversation() -> dict:
    """Return evaluator-format messages for one complete, redacted agent turn."""
    return {
        "query": [
            {
                "role": "system",
                "content": "You are a Northwind support agent. Use tools for policy facts.",
            },
            {"role": "user", "content": _QUERY},
        ],
        "response": [
            {
                "role": "assistant",
                "content": [{"type": "text", "text": "I will check the current policy."}],
            },
            {"role": "assistant", "content": [_TOOL_CALL]},
            {
                "role": "tool",
                "tool_call_id": _TOOL_CALL["tool_call_id"],
                "content": [
                    {
                        "type": "tool_result",
                        "tool_result": "Pro plans can be refunded within 30 days of charge.",
                    }
                ],
            },
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": "Pro plans can be refunded within 30 days of the charge date.",
                    }
                ],
            },
        ],
        "tool_calls": [_TOOL_CALL],
        "tool_definitions": _TOOL_DEFINITIONS,
    }


def model_config() -> dict[str, str]:
    """Return Azure OpenAI evaluator configuration without reading secrets."""
    current = settings()
    return {
        "azure_endpoint": current.require("AZURE_OPENAI_ENDPOINT"),
        "azure_deployment": current.default_model,
        "api_version": "2024-10-21",
    }


def main() -> None:
    try:
        from azure.ai.evaluation import TaskAdherenceEvaluator, ToolCallAccuracyEvaluator
    except ImportError:  # pragma: no cover
        raise SystemExit("pip install azure-ai-evaluation to run this lesson.")

    trace = agent_conversation()
    credential = DefaultAzureCredential()
    task_adherence = TaskAdherenceEvaluator(
        model_config=model_config(), credential=credential
    )
    tool_accuracy = ToolCallAccuracyEvaluator(
        model_config=model_config(), credential=credential
    )

    print("=== Task Adherence ===")
    print(
        task_adherence(
            query=trace["query"],
            response=trace["response"],
            tool_definitions=trace["tool_definitions"],
        )
    )
    print("\n=== Tool Call Accuracy ===")
    print(
        tool_accuracy(
            query=trace["query"],
            tool_calls=trace["tool_calls"],
            tool_definitions=trace["tool_definitions"],
        )
    )


if __name__ == "__main__":
    main()
