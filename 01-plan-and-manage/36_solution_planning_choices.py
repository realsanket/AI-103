# Run: uv run python 01-plan-and-manage/36_solution_planning_choices.py [--needs <need> ...]
# Practice-question coverage: Q85, Q131, Q139, Q140, Q161.
"""Planning choices: model type, Foundry resource type, and responsible AI principle.

Three decisions come before any code, and each has a small set of answers:

1. Model type — match the requirement, not the hype:
     large language model (LLM)    deep multi-step reasoning over long, grounded context;
                                   detailed natural-language answers (RAG agents)
     small language model (SLM)    narrow, well-scoped tasks where latency, cost, or
                                   on-device/offline hosting matter (for example Phi-4-mini)
     reasoning model               math, planning, and multi-step problems where a longer
                                   think time is acceptable (GPT-5 family)
     multimodal model              images or audio in the same prompt as text
     embedding model               vectors for documents and queries (vector search)
     image generation model        pixels from text (GPT-image series)
     Foundry Tool (not a model)    deterministic NLP such as key phrases, PII, or language
                                   detection (Azure Language), speech, translation

2. Resource type — one Microsoft Foundry resource (ARM
   `Microsoft.CognitiveServices/accounts`, `kind: "AIServices"`) gives one endpoint
   and one credential for Speech, Language, Vision, Content Safety, and model
   deployments, with consolidated billing. Single-service resources (a Speech or a
   Language resource) do not. Create it with an idempotent ARM **PUT** to the
   account URI. Older material names the legacy multi-service kind
   `CognitiveServices`; new resources use `AIServices`.

3. Responsible AI principle — Microsoft's six principles are fairness,
   reliability and safety, privacy and security, inclusiveness, transparency,
   and accountability. Telling people that an AI system processes their data,
   and how, is transparency.

Everything here is local: no Azure call, no resource creation.
"""
import argparse
import json

MODEL_TYPES = {
    "llm": "large language model (LLM)",
    "slm": "small language model (SLM)",
    "reasoning": "reasoning model",
    "multimodal": "multimodal model",
    "embedding": "embedding model",
    "image_generation": "image generation model",
    "foundry_tool": "Foundry Tool (Azure Language, Speech, Translator)",
}

# Requirement keyword → model type. Order matters: the first match wins.
_NEED_RULES = (
    ("vectors", "embedding"),
    ("generate_images", "image_generation"),
    ("image_or_audio_input", "multimodal"),
    ("deterministic_nlp", "foundry_tool"),
    ("math_or_planning", "reasoning"),
    ("long_context_grounded_reasoning", "llm"),
    ("detailed_generation", "llm"),
    ("on_device_or_low_cost", "slm"),
    ("narrow_task", "slm"),
)

RAI_PRINCIPLES = {
    "fairness": "treat similar people similarly; test for disparate error rates",
    "reliability_and_safety": "behave as intended under expected and unexpected conditions",
    "privacy_and_security": "protect personal data and resist attacks",
    "inclusiveness": "work for people with a wide range of abilities and backgrounds",
    "transparency": "people understand that an AI system is used, what it does, and how their data is used",
    "accountability": "named humans own the system's outcomes and oversight",
}

_PRACTICE_TO_PRINCIPLE = {
    "notify_users_data_processed": "transparency",
    "disclose_ai_generated_content": "transparency",
    "explain_decision_factors": "transparency",
    "human_review_and_escalation_owner": "accountability",
    "test_error_rates_across_groups": "fairness",
    "support_screen_readers_and_captions": "inclusiveness",
    "encrypt_and_minimize_personal_data": "privacy_and_security",
    "red_team_and_fail_safe_defaults": "reliability_and_safety",
}


def recommend_model_type(needs: list[str]) -> str:
    unknown = sorted(set(needs) - {need for need, _ in _NEED_RULES})
    if unknown:
        raise ValueError(f"unknown needs: {', '.join(unknown)}")
    for need, model_type in _NEED_RULES:
        if need in needs:
            return model_type
    raise ValueError("describe at least one need")


def resource_for(services: set[str], single_endpoint: bool) -> str:
    """Pick the resource type for a set of AI services."""
    if not services:
        raise ValueError("name at least one service")
    if single_endpoint or len(services) > 1:
        return "Microsoft Foundry resource (kind AIServices)"
    return f"single-service {next(iter(services))} resource (or a Foundry resource)"


def foundry_resource_request(subscription: str, group: str, name: str, region: str) -> dict:
    """ARM request that creates (or idempotently updates) a Foundry resource."""
    return {
        "method": "PUT",
        "url": (
            f"https://management.azure.com/subscriptions/{subscription}/resourceGroups/{group}"
            f"/providers/Microsoft.CognitiveServices/accounts/{name}?api-version=2025-06-01"
        ),
        "body": {
            "location": region,
            "kind": "AIServices",
            "sku": {"name": "S0"},
            "identity": {"type": "SystemAssigned"},
            "properties": {
                "customSubDomainName": name,
                "allowProjectManagement": True,
                "disableLocalAuth": True,
            },
        },
    }


def principle_for(practice: str) -> str:
    if practice not in _PRACTICE_TO_PRINCIPLE:
        raise ValueError(f"unknown practice {practice!r}; choose from {sorted(_PRACTICE_TO_PRINCIPLE)}")
    return _PRACTICE_TO_PRINCIPLE[practice]


SCENARIOS = (
    ("RAG support agent: long grounded context, multi-step reasoning, detailed answers",
     ["long_context_grounded_reasoning", "detailed_generation"]),
    ("Policy search: vectors for documents and queries", ["vectors"]),
    ("Kiosk intent classifier: narrow task, low cost, runs offline", ["narrow_task", "on_device_or_low_cost"]),
    ("Extract key phrases from tickets, deterministic output", ["deterministic_nlp"]),
    ("Describe damage in uploaded photos", ["image_or_audio_input", "detailed_generation"]),
)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--needs", nargs="*", choices=[need for need, _ in _NEED_RULES], help="Evaluate your own needs.")
    args = parser.parse_args(argv)

    print("No cloud calls made.\n")
    print("1. Model type")
    scenarios = [("Your requirements", args.needs)] if args.needs else SCENARIOS
    for label, needs in scenarios:
        print(f"  - {label}\n      -> {MODEL_TYPES[recommend_model_type(needs)]}")

    print("\n2. Resource type")
    print(f"  - Speech + Language behind one endpoint and credential -> {resource_for({'Speech', 'Language'}, True)}")
    print(f"  - Language only, separate billing acceptable        -> {resource_for({'Language'}, False)}")
    request = foundry_resource_request("<subscription-id>", "<resource-group>", "<foundry-name>", "eastus2")
    print(f"  - Create it: {request['method']} {request['url']}")
    print("    " + json.dumps(request["body"]))

    print("\n3. Responsible AI principle")
    for practice in ("notify_users_data_processed", "human_review_and_escalation_owner", "test_error_rates_across_groups"):
        principle = principle_for(practice)
        print(f"  - {practice} -> {principle}: {RAI_PRINCIPLES[principle]}")


if __name__ == "__main__":
    main()
