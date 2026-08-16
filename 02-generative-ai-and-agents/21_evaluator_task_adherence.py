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
    """Return evaluator-format data for one complete, redacted agent turn.

    TaskAdherenceEvaluator and ToolCallAccuracyEvaluator expect:
      query      — plain string (the user's question)
      response   — plain string (full agent response text including tool call narrative)
      tool_calls — list of dicts in OpenAI tool_call format
      tool_definitions — list of function definition dicts
    Passing query as a list of messages causes 'Conversation history could not be
    parsed' fallback and degrades evaluator accuracy.
    """
    return {
        "query": _QUERY,
        "response": (
            "I will check the current policy.\n"
            "[TOOL_CALL] get_refund_policy()\n"
            "[TOOL_RESULT] Pro plans can be refunded within 30 days of charge.\n"
            "Pro plans can be refunded within 30 days of the charge date."
        ),
        "tool_calls": [_TOOL_CALL],
        "tool_definitions": _TOOL_DEFINITIONS,
    }


def model_config() -> dict[str, str]:
    """Return Azure OpenAI evaluator configuration without reading secrets.

    azure.ai.evaluation's prompty layer sends max_tokens which gpt-5 family
    models reject (they require max_completion_tokens). Use a gpt-4.x judge
    deployment that still accepts max_tokens until the SDK is updated.
    """
    current = settings()
    # gpt-4.1 accepts max_tokens; gpt-5.x rejects it (SDK bug — prompty layer hardcodes max_tokens)
    judge = "gpt-4.1"
    return {
        "azure_endpoint": current.require("AZURE_OPENAI_ENDPOINT"),
        "azure_deployment": judge,
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
