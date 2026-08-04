# Run: uv run python 01-plan-and-manage/11_evaluator_groundedness.py
"""Response Completeness / Groundedness evaluator loop — DIY inline.

Beginner story:
  1. An ephemeral agent (instructions live in this file — no portal setup)
     answers a customer question.
  2. A second Responses API call plays the role of an evaluator: it reads the
     answer against a completeness checklist and returns COMPLETE or MISSING.
  3. If MISSING, we regenerate the answer with the checklist in scope.

This is the same pattern the built-in Response Completeness / Groundedness
evaluators use — wired inline so you can see the mechanics.

What to watch in the output:
  - The verdict line (COMPLETE / MISSING).
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

    # Step 1 — draft via ephemeral agent (instructions come from this file)
    draft = openai.responses.create(
        model=model,
        instructions=_AGENT_INSTRUCTIONS,
        input=_QUESTION,
    )
    print("=== Draft ===")
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
    print("\n=== Verdict ===")
    print(verdict)

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
        print("\n=== Regenerated ===")
        print(improved.output_text)


if __name__ == "__main__":
    main()
