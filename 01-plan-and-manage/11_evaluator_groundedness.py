"""Response Completeness / Groundedness evaluator loop.

Ask a grounded RAG agent → have a second call critique the answer against a
completeness checklist → regenerate if MISSING. Same pattern as the built-in
Response Completeness evaluator, but wired inline so you can see the mechanics.
"""
from _shared.config import settings
from _shared.foundry_client import project_client

AGENT_NAME = "northwind-support-rag-agent"
_AGENT_REF = {"type": "agent_reference", "name": AGENT_NAME}

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

    draft = openai.responses.create(
        model=model,
        input=_QUESTION,
        extra_body={"agent_reference": _AGENT_REF},
    )
    print("=== Draft ===")
    print(draft.output_text)

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

    if "MISSING" in verdict.upper():
        improved = openai.responses.create(
            model=model,
            input=(
                "Answer the customer question completely using the available knowledge base. "
                "Cover eligibility, the refund window, how it's measured, what happens after, "
                "and whether any requested details are unavailable. Do not invent policy details.\n\n"
                f"Customer question:\n{_QUESTION}"
            ),
            extra_body={"agent_reference": _AGENT_REF},
        )
        print("\n=== Regenerated ===")
        print(improved.output_text)


if __name__ == "__main__":
    main()
