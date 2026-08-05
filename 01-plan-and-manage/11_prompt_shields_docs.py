# Run: uv run python 01-plan-and-manage/11_prompt_shields_docs.py
"""Prompt Shields — document (indirect injection) attack detection. Two flows:

Flow A — Content Safety API (direct REST):
  Explicit call to /contentsafety/text:shieldPrompt with documents[].
  Returns documentsAnalysis[i].attackDetected per document.
  userPrompt stays clean — attack rides in the data.
  No deployment config needed — just CONTENT_SAFETY_ENDPOINT.

Flow B — Foundry deployment guardrail:
  Requires an actual document-bearing user-input or tool-response path, such as
  a configured `data_sources` integration. A pasted Chat Completions message is
  user-prompt content, so this lesson intentionally does not fake that test.

This lesson uses the Content Safety API's `documents` field with a real,
local OCR extract that contains an indirect prompt injection. Pasting document
text into a chat message is not an equivalent document-channel test.

This lesson covers the DOCUMENT channel (attacker embeds in data the model reads).
Lesson 10 covers the USER PROMPT channel (the user is the attacker).
"""
from pathlib import Path

from azure.ai.contentsafety import ContentSafetyClient
from azure.identity import DefaultAzureCredential

from _shared.config import settings
from _shared.content_safety_client import shield_prompt

_USER_PROMPT = "I uploaded a report PDF. Can you summarize the key findings?"

_CLEAN_DOC = "Q3 sales were up 12% year-over-year. Key drivers: APAC expansion and new Pro plan."

_INJECTED_DOC = (Path(__file__).with_name("data") / "malicious_ocr_sample.txt").read_text()

_MIXED_DOCS = [_INJECTED_DOC, _CLEAN_DOC]


def shield_documents(
    client: ContentSafetyClient, endpoint: str, user_prompt: str, documents: list[str]
) -> dict:
    return shield_prompt(client, endpoint, user_prompt, documents)


def main() -> None:
    endpoint = settings().content_safety_endpoint
    client = ContentSafetyClient(endpoint=endpoint, credential=DefaultAzureCredential())

    print("=== Flow A — Content Safety API direct ===")
    print("\n  Clean documents:")
    result = shield_documents(client, endpoint, _USER_PROMPT, [_CLEAN_DOC])
    for i, doc in enumerate(result.get("documentsAnalysis", [])):
        print(f"  doc[{i}] attackDetected: {doc['attackDetected']}")

    print("\n  Mixed documents (doc[0] injected, doc[1] clean):")
    result = shield_documents(client, endpoint, _USER_PROMPT, _MIXED_DOCS)
    user_attack = result["userPromptAnalysis"]["attackDetected"]
    print(f"  userPrompt attackDetected: {user_attack}")  # False — user is innocent
    for i, doc in enumerate(result.get("documentsAnalysis", [])):
        print(f"  doc[{i}] attackDetected: {doc['attackDetected']}")
    print(f"  raw: {result}")

    print("\n=== Flow B — deployment guardrail integration ===")
    print("  Configure Document attack for user input or tool response, then route")
    print("  this OCR content through your real document integration (for example,")
    print("  Chat Completions `data_sources`). Do not paste it into `messages`.")


if __name__ == "__main__":
    main()
