from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

PROJECT_ENDPOINT = "https://foundry-dev-eus-01.services.ai.azure.com/api/projects/ai-103-project"
AGENT_NAME = "cloudxeus-support-rag-agent"

project = AIProjectClient(
    endpoint=PROJECT_ENDPOINT,
    credential=DefaultAzureCredential(),
)

openai = project.get_openai_client()

AGENT_REF = {
    "name": AGENT_NAME,
    "type": "agent_reference"
}

user_question = (
    "I'm on the Pro plan and want a refund for my last subscription charge. "
    "Am I eligible, and is there anything I should know before I request it?"
)

# First pass: ask the grounded agent
draft_response = openai.responses.create(
    model="gpt-5.4",
    input=user_question,
    extra_body={"agent_reference": AGENT_REF},
)

answer = draft_response.output_text

print("Draft response")
print(answer)

# Second pass: check whether the answer is complete
critique_response = openai.responses.create(
    model="gpt-5.4",
    input=(
        "You are reviewing a customer support answer for completeness.\n\n"
        "A complete refund answer should address:\n"
        "1. Whether the customer appears eligible for a refund.\n"
        "2. The refund window, if one applies.\n"
        "3. How the refund window is measured.\n"
        "4. Whether refunds are available after the normal refund window.\n"
        "5. Whether any requested details are not available in the knowledge base.\n\n"
        "Do not judge the answer based on information that is not present. "
        "If the answer clearly says that a detail is not available in the knowledge base, "
        "treat that as acceptable.\n\n"
        f"Customer question:\n{user_question}\n\n"
        f"Support answer:\n{answer}\n\n"
        "Reply with only COMPLETE or MISSING."
    ),
)

critique = critique_response.output_text

print("Critique")
print(critique)

# Third pass: regenerate only if the answer is incomplete
if "MISSING" in critique.upper():
    print("Regenerated response")

    improved_response = openai.responses.create(
        model="gpt-5.4",
        input=(
            "Answer the customer question completely using the available knowledge base. "
            "Cover refund eligibility, the refund window, how the window is measured, "
            "what happens after the refund window, and whether any requested details "
            "are not available in the knowledge base. "
            "Do not invent policy details.\n\n"
            f"Customer question:\n{user_question}"
        ),
        extra_body={"agent_reference": AGENT_REF},
    )

    print(improved_response.output_text)