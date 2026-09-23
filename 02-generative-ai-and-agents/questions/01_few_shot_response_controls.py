# Run: uv run python 02-generative-ai-and-agents/questions/01_few_shot_response_controls.py
"""Question supplement: few-shot prompting and deterministic response controls.

Maps PDF questions 16, 25, 82, 93, 97, 108, and 110. It builds request
fragments only; callers still use `_shared/openai_client.py` to invoke a
deployment and must opt in to a billable call themselves.
"""
from __future__ import annotations


def few_shot_messages(examples: list[tuple[str, str]], user_input: str) -> list[dict[str, str]]:
    if not examples:
        raise ValueError("Provide at least one reviewed example.")
    if not user_input.strip():
        raise ValueError("user_input must not be blank.")
    messages: list[dict[str, str]] = []
    for prompt, answer in examples:
        if not prompt.strip() or not answer.strip():
            raise ValueError("Examples must have nonempty input and output.")
        messages.extend(({"role": "user", "content": prompt}, {"role": "assistant", "content": answer}))
    messages.append({"role": "user", "content": user_input})
    return messages


def response_controls(*, require_tool: bool = False, deterministic: bool = False,
                      max_output_tokens: int | None = None) -> dict[str, object]:
    if max_output_tokens is not None and max_output_tokens <= 0:
        raise ValueError("max_output_tokens must be positive when supplied.")
    controls: dict[str, object] = {}
    if require_tool:
        controls["tool_choice"] = "required"
    if deterministic:
        controls["temperature"] = 0
    if max_output_tokens is not None:
        controls["max_output_tokens"] = max_output_tokens
    return controls


def main() -> None:
    print("No cloud calls made. Request fragments:")
    print(few_shot_messages([("Classify: password reset", "identity")], "Classify: invoice overdue"))
    print(response_controls(require_tool=True, deterministic=True, max_output_tokens=500))


if __name__ == "__main__":
    main()
