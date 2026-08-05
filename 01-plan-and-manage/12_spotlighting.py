# Run: uv run python 01-plan-and-manage/12_spotlighting.py
"""Spotlighting (preview) — extra document-attack defense on Chat Completions.

What it is:
  Tags third-party document content as lower-trust by base64-encoding it before
  the model sees it. Additive to Prompt Shields document attack detection (L10).

Where it lives:
  Foundry guardrail → risk = Document attack → Spotlighting toggle ON.
  Models only (not agents). Chat Completions only (not Responses API).

Two views in this lesson:
  Flow A — Request shape: show prompt_shield.documents.spotlighting_enabled body
            (per-request override when calling Chat Completions with data_sources).
  Flow B — Configuration boundary: explain why a plain chat message is not a
            document channel. Use the Flow A shape with a configured document
            source to exercise Spotlighting.

Sources:
  foundry/openai/concepts/content-filter-prompt-shields.md (Spotlighting)
  foundry/guardrails/guardrails-overview.md (models ✅ agents ❌)
"""
import json

_USER = "Summarize the key findings in the attached report."
def _flow_a_request_shape() -> None:
    print("=== Flow A — Chat Completions request shape (Spotlighting) ===")
    # Documented per-request body when using document-bearing calls (e.g. data_sources).
    # Spotlighting is usually set on the deployment guardrail; this shows the API field.
    body = {
        "messages": [{"role": "user", "content": _USER}],
        "data_sources": ["{... Azure AI Search / on-your-data source ...}"],
        "prompt_shield": {
            "user_prompt": {"enabled": True, "action": "annotate"},
            "documents": {
                "enabled": True,
                "action": "annotate",
                "spotlighting_enabled": True,
            },
        },
    }
    print(json.dumps(body, indent=2))
    print("  notes:")
    print("  - spotlighting_enabled only meaningful with document channel content")
    print("  - Chat Completions only; not Responses API; not agents")
    print("  - no direct $ cost; base64 expands tokens → higher usage cost")
    print("  - side effect: model may mention that content was base64-encoded")


def _flow_b_configuration_boundary() -> None:
    print("\n=== Flow B — configuration boundary ===")
    print("  Do not paste a document into `messages` to test Spotlighting.")
    print("  It is user-prompt content, not document-channel content.")
    print("  Configure Document attack + Spotlighting on a Chat Completions")
    print("  deployment, then send document content through `data_sources` or")
    print("  another configured document-bearing integration.")


def main() -> None:
    _flow_a_request_shape()
    _flow_b_configuration_boundary()


if __name__ == "__main__":
    main()
