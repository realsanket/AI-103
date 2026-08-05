"""Image moderation — two flows: direct Content Safety API + guardrail-through-model.

Beginner note:
  Two ways to moderate visual content:
  1. **Direct**: call the Content Safety `analyze_image` API. Returns 0-7
     severity per category (Hate / Sexual / Violence / SelfHarm). Use when
     you want to inspect an image BEFORE any model sees it.
  2. **Guardrail**: send the image to a multimodal model; the deployment's
     guardrail evaluates both prompt and completion. `content_filters` on
     the response shows what got flagged.

  This lesson uses an ephemeral agent (instructions in the code — no portal
  setup, no broken agent references). Same pattern as Domain 1 L11.

Prereqs:
  - CONTENT_SAFETY_ENDPOINT in .env (for flow 1).
  - A multimodal model deployment (`DEFAULT_MODEL` — gpt-4.1-mini, gpt-4o).
"""
import base64

from azure.ai.contentsafety.models import AnalyzeImageOptions, ImageData

from _shared.config import SAMPLE_DATA, settings
from _shared.content_safety_client import content_safety_client
from _shared.foundry_client import project_client

_IMAGE_PATH = SAMPLE_DATA / "images" / "support.png"

_AGENT_INSTRUCTIONS = (
    "You are Northwind IT support. The user will send a screenshot of an error. "
    "Read any visible text, identify the error, and give one clear fix step."
)


def _direct_content_safety() -> None:
    """Flow 1: Content Safety API — 0-7 severity per category."""
    print("=== Flow 1: Content Safety API (0-7 severity) ===")
    client = content_safety_client()
    image_bytes = _IMAGE_PATH.read_bytes()
    result = client.analyze_image(AnalyzeImageOptions(image=ImageData(content=image_bytes)))
    for cat in result.categories_analysis:
        print(f"  {cat.category.value:<12} severity={cat.severity}")


def _guardrail_through_model() -> None:
    """Flow 2: multimodal call — deployment guardrail evaluates both sides."""
    print("\n=== Flow 2: Multimodal call (ephemeral agent, guardrail inspection) ===")
    b64 = base64.b64encode(_IMAGE_PATH.read_bytes()).decode("utf-8")

    project = project_client()
    openai = project.get_openai_client()
    r = openai.responses.create(
        model=settings().default_model,
        instructions=_AGENT_INSTRUCTIONS,
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": "What does this error mean and how do I fix it?"},
                    {"type": "input_image", "image_url": f"data:image/png;base64,{b64}"},
                ],
            }
        ],
    )
    print(r.output_text)

    filters = getattr(r, "model_extra", {}).get("content_filters") if hasattr(r, "model_extra") else None
    if filters:
        print("\n--- content_filters ---")
        print(filters)
    else:
        print("\n(no content_filters block on response — clean image)")


def main() -> None:
    _direct_content_safety()
    _guardrail_through_model()


if __name__ == "__main__":
    main()
