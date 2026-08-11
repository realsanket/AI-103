# Run: uv run python 01-plan-and-manage/24_human_feedback.py
"""Append consented end-user feedback to an already active agent trace.

Prerequisites: OpenTelemetry instrumentation, Foundry project connected to
Application Insights, and `azure-ai-projects>=2.0.0` plus
`azure-monitor-opentelemetry`. Call `emit_end_user_feedback` from the same
active trace/span that produced the agent response. Foundry's default
task-completion template renders binary pass/fail feedback; builder templates
need Foundry Project Manager, while reviewers need Foundry User and Reader on
the account. Application Insights retention and ingestion affect cost.

Use this after a user voluntarily rates a response. It records a human signal,
not an LLM evaluator result and not proof that the response is correct. The
event uses the `task_completion` binary schema: thumbs up is `1.0`/`pass`;
thumbs down is `0.0`/`fail`.

Safety boundary: `apply=False` is an exact dry run. `apply=True` appends one
event only to a valid, recording current response span; it never overwrites
feedback. Do not emit a new trace later to imitate correlation, infer a rating,
send feedback without user action, or include secrets, sensitive text, or
unnecessary personal data in the optional explanation.
"""
from __future__ import annotations

from typing import Any


def feedback_attributes(
    *,
    thumbs_up: bool,
    response_id: str,
    agent_id: str,
    agent_name: str,
    agent_version: str,
    explanation: str = "",
) -> dict[str, Any]:
    """Build documented binary-feedback attributes without emitting telemetry."""
    score = 1.0 if thumbs_up else 0.0
    attributes: dict[str, Any] = {
        "gen_ai.evaluation.name": "task_completion",
        "gen_ai.evaluation.score.value": score,
        "gen_ai.evaluation.score.label": "pass" if thumbs_up else "fail",
        "gen_ai.response.id": response_id,
        "microsoft.gen_ai.human_evaluation.source": "end_user",
        "microsoft.gen_ai.evaluation.actor.type": "human",
        "gen_ai.agent.id": agent_id,
        "gen_ai.agent.name": agent_name,
        "gen_ai.agent.version": agent_version,
        "internal_properties.gen_ai.evaluation.type": "boolean",
        "internal_properties.gen_ai.evaluation.min_value": 0.0,
        "internal_properties.gen_ai.evaluation.max_value": 1.0,
        "internal_properties.gen_ai.evaluation.threshold": 1.0,
        "internal_properties.gen_ai.evaluation.desirable_direction": "increase",
    }
    if explanation:
        attributes["gen_ai.evaluation.explanation"] = explanation
    return attributes


def preflight(attributes: dict[str, Any]) -> str:
    """Return exact telemetry side effect for user review."""
    return "\n".join(
        [
            "PREVIEW: no telemetry event appended.",
            "Would append gen_ai.evaluation.result to current response span.",
            f"Would record task_completion: {attributes['gen_ai.evaluation.score.label']}",
            "Would set source: end_user and actor type: human.",
            "Call again with apply=True inside original recording response span.",
        ]
    )


def emit_end_user_feedback(span: Any, *, apply: bool = False, **feedback: Any) -> str:
    """Append feedback to original response span only when explicitly applied."""
    attributes = feedback_attributes(**feedback)
    if not apply:
        return preflight(attributes)
    if not span.is_recording() or not span.get_span_context().is_valid:
        raise RuntimeError(
            "No valid recording response span. Do not emit uncorrelated feedback."
        )
    span.add_event("gen_ai.evaluation.result", attributes=attributes)
    return "APPLIED: appended one end_user task_completion event to current response span."


def main() -> None:
    print(
        "No CLI emission: invoke emit_end_user_feedback from response handling "
        "while its original OpenTelemetry span remains active."
    )


if __name__ == "__main__":
    main()
