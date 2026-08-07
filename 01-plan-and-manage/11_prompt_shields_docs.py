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
  evaluated as user-prompt content. This lesson intentionally tests this by
  pasting a document to show that it trips the `jailbreak` key rather than
  the `indirect_attack` key.

This lesson uses the Content Safety API's `documents` field (Flow A) with a real,
local OCR extract that contains an indirect prompt injection. Pasting document
text into a chat message (Flow B) proves why channel separation is critical.

This lesson covers the DOCUMENT channel (attacker embeds in data the model reads).
Lesson 10 covers the USER PROMPT channel (the user is the attacker).
"""
from pathlib import Path

from azure.ai.contentsafety import ContentSafetyClient
from azure.identity import DefaultAzureCredential

from _shared.config import settings
from openai import BadRequestError
from _shared.content_safety_client import shield_prompt
from _shared.openai_client import openai_client

_USER_PROMPT = "I uploaded a report PDF. Can you summarize the key findings?"

_CLEAN_DOC = "Q3 sales were up 12% year-over-year. Key drivers: APAC expansion and new Pro plan."

_INJECTED_DOC = (Path(__file__).with_name("data") / "malicious_ocr_sample.txt").read_text()

_MIXED_DOCS = [_INJECTED_DOC, _CLEAN_DOC]


def shield_documents(
    client: ContentSafetyClient, endpoint: str, user_prompt: str, documents: list[str]
) -> dict:
    return shield_prompt(client, endpoint, user_prompt, documents)


def _print_shield_keys(cfr: dict) -> None:
    indirect = cfr.get("indirect_attack") or {}
    jailbreak = cfr.get("jailbreak") or {}
    if indirect:
        print(f"  indirect_attack.detected: {indirect.get('detected', 'n/a')}")
        print(f"  indirect_attack.filtered: {indirect.get('filtered', 'n/a')}")
    else:
        print("  indirect_attack key absent — enable Document attack on deployment guardrail")
    if jailbreak:
        print(f"  jailbreak.detected: {jailbreak.get('detected', 'n/a')} (user-prompt channel)")
        print(f"  jailbreak.filtered: {jailbreak.get('filtered', 'n/a')}")


def _shield_via_foundry_guardrail(user_prompt: str, document: str) -> None:
    client = openai_client()
    content = f"{user_prompt}\n\n--- Document ---\n{document}"
    try:
        r = client.chat.completions.create(
            model=settings().default_model,
            messages=[{"role": "user", "content": content}],
        )
        pfr = getattr(r, "prompt_filter_results", None)
        if not pfr:
            print("  prompt_filter_results absent — assign Prompt Shields guardrail to deployment")
            return
        _print_shield_keys(pfr[0].get("content_filter_results", {}))
    except BadRequestError as e:
        print(f"  Blocked (400): {e.code} — guardrail action=block triggered")
        body = getattr(e, "body", None) or {}
        cfr = body.get("innererror", {}).get("content_filter_result") or {}
        if cfr:
            _print_shield_keys(cfr)


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
    print("  (Demonstrating why pasting docs into messages hits the user-prompt shield instead)")
    print("\n  Clean document:")
    _shield_via_foundry_guardrail(_USER_PROMPT, _CLEAN_DOC)

    print("\n  Injected document:")
    _shield_via_foundry_guardrail(_USER_PROMPT, _INJECTED_DOC)


if __name__ == "__main__":
    main()
