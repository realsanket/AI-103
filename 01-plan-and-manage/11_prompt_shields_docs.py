# Run: uv run python 01-plan-and-manage/11_prompt_shields_docs.py
# Practice-question coverage: Q3, Q37, Q38, Q39, Q40, Q42, Q72, Q167.
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

from _shared.config import settings, preview_text, format_json_preview
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


def _scenario_header(name: str) -> None:
    print(f"\n  {name}:")


def _preview(text: str, max_len: int = 220) -> str:
    return preview_text(text, max_len=max_len)


def _print_inputs(user_prompt: str, documents: list[str]) -> None:
    print("  Input text sent:")
    print(f"    user_prompt: {_preview(user_prompt)}")
    for i, doc in enumerate(documents):
        print(f"    document[{i}]: {_preview(doc)}")


def _print_flow_a_result(result: dict) -> None:
    user_attack = bool(result.get("userPromptAnalysis", {}).get("attackDetected", False))
    print(f"  userPrompt attackDetected: {user_attack}")
    for i, doc in enumerate(result.get("documentsAnalysis", [])):
        print(f"  doc[{i}] attackDetected: {bool(doc.get('attackDetected', False))}")


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
    _scenario_header("Clean documents")
    _print_inputs(_USER_PROMPT, [_CLEAN_DOC])
    result = shield_documents(client, endpoint, _USER_PROMPT, [_CLEAN_DOC])
    _print_flow_a_result(result)

    _scenario_header("Mixed documents (doc[0] injected, doc[1] clean)")
    _print_inputs(_USER_PROMPT, _MIXED_DOCS)
    result = shield_documents(client, endpoint, _USER_PROMPT, _MIXED_DOCS)
    _print_flow_a_result(result)
    print("  Raw response:")
    print(format_json_preview(result, indent="    ", max_chars=1100))

    print("\n=== Flow B — deployment guardrail integration ===")
    print("  (Demonstrating why pasting docs into messages hits the user-prompt shield instead)")
    _scenario_header("Clean document")
    _print_inputs(_USER_PROMPT, [_CLEAN_DOC])
    _shield_via_foundry_guardrail(_USER_PROMPT, _CLEAN_DOC)

    _scenario_header("Injected document")
    _print_inputs(_USER_PROMPT, [_INJECTED_DOC])
    _shield_via_foundry_guardrail(_USER_PROMPT, _INJECTED_DOC)


if __name__ == "__main__":
    main()
