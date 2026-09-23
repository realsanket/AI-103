# Run: uv run python 01-plan-and-manage/17_evaluator_groundedness.py
# Practice-question coverage: Q64, Q69, Q98, Q100, Q134.
"""LLM self-critique loop — not a Foundry built-in evaluator.

Beginner story:
  1. An ephemeral agent (instructions live in this file — no portal setup)
     answers a customer question.
  2. A second Responses API call plays the role of an evaluator: it reads the
     answer against a completeness checklist and returns COMPLETE or MISSING.
  3. If MISSING, we regenerate the answer with the checklist in scope.

This is an application-level self-critique pattern. It is not a Foundry
evaluation run and does not implement Response Completeness or Groundedness.
Those built-in evaluators require an evaluation dataset and their documented
input contract; Response Completeness uses `ground_truth` and `response`,
while Groundedness uses `response` and recommended `context`.

What to watch in the output:
  - The self-critique verdict (COMPLETE / MISSING).
  - If regenerated, notice the second draft addresses the missing checklist items.
"""
from _shared.config import settings
from _shared.foundry_client import project_client

_AGENT_INSTRUCTIONS = (
    "You are Northwind Support, a customer support agent for Northwind Inc. "
    "Answer questions about refunds, subscriptions, and billing based on the "
    "policy below. If a detail isn't in the policy, say so — do not invent.\n\n"
    "Refund policy:\n"
    "- Pro plan subscribers can request a refund within 30 days of the charge date.\n"
    "- The window is measured from the charge date on the invoice, not the usage date.\n"
    "- Refunds after 30 days are considered case-by-case by the billing team.\n"
    "- Refunds are issued to the original payment method within 5–10 business days."
)

_QUESTION = (
    "I'm on the Pro plan and want a refund for my last subscription charge. "
    "Am I eligible, and is there anything I should know before I request it?"
)

_CRITIQUE_INSTRUCTIONS = (
    "You are reviewing a customer support answer for completeness.\n\n"
    "A complete refund answer should address:\n"
    "1. Whether the customer appears eligible for a refund.\n"
    "2. The refund window, if one applies.\n"
    "3. How the refund window is measured.\n"
    "4. Whether refunds are available after the normal refund window.\n"
    "5. Whether any requested details are not available in the knowledge base.\n\n"
    "Do not judge based on info not present. If the answer says a detail is not "
    "available in the knowledge base, treat that as acceptable.\n\n"
    "Reply with only COMPLETE or MISSING."
)


def main() -> None:
    project = project_client()
    openai = project.get_openai_client()
    model = settings().default_model

    print("LLM self-critique loop: draft answer -> critique -> optional regeneration")
    print(f"Using deployment: {model}")
    print("\nCustomer question:")
    print(_QUESTION)

    # Step 1 — draft via ephemeral agent (instructions come from this file)
    draft = openai.responses.create(
        model=model,
        instructions=_AGENT_INSTRUCTIONS,
        input=_QUESTION,
    )
    print("\n=== Step 1: Draft answer ===")
    print(draft.output_text)

    # Step 2 — critique the draft against the checklist
    critique = openai.responses.create(
        model=model,
        input=(
            f"{_CRITIQUE_INSTRUCTIONS}\n\n"
            f"Customer question:\n{_QUESTION}\n\n"
            f"Support answer:\n{draft.output_text}\n"
        ),
    )
    verdict = critique.output_text.strip()
    print("\n=== Step 2: Critique verdict ===")
    print(verdict)
    if "COMPLETE" in verdict.upper():
        print("\nInterpretation:")
        print("The evaluator judged the first draft complete, so no second pass was needed.")
        print("This is the happy path: the draft already covered the checklist items.")

    # Step 3 — regenerate if MISSING (feed the checklist back to the agent)
    if "MISSING" in verdict.upper():
        improved = openai.responses.create(
            model=model,
            instructions=_AGENT_INSTRUCTIONS,
            input=(
                "Answer the customer question completely. Cover eligibility, the refund "
                "window, how it's measured, what happens after, and whether any details "
                "are unavailable. Do not invent policy details.\n\n"
                f"Customer question:\n{_QUESTION}"
            ),
        )
        print("\n=== Step 3: Regenerated answer ===")
        print(improved.output_text)
        print("\nInterpretation:")
        print("The first draft missed checklist items, so the app regenerated a more complete answer.")


if __name__ == "__main__":
    main()
