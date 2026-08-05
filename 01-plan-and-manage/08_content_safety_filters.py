# Run: uv run python 01-plan-and-manage/08_content_safety_filters.py
"""Content Safety — three flows showing two detection paths.

Flow A — Foundry deployment guardrail (Chat Completions):
  Always-on; no extra API call. Default guardrail = Microsoft.DefaultV2.
  Severity in response: Safe/Low/Medium/High (4-level — NOT the 0-7 API scale).
  Action=block → 400 BadRequestError with code="content_filter".
  Action=annotate → response returned; choices[0].content_filter_results shows results.

Flow B — Content Safety API text (explicit, pre-model):
  Returns 0–7 integer severity per category.
  Use for pre-screening before sending to model, or when you need exact severity.

Flow C — Content Safety API image:
  Analyze user-uploaded images before storing or passing to an agent.
  Same 0–7 integer scale as Flow B.
"""
from openai import BadRequestError
from azure.ai.contentsafety.models import AnalyzeTextOptions, AnalyzeImageOptions, ImageData

from _shared.config import settings, SAMPLE_DATA
from _shared.content_safety_client import content_safety_client
from _shared.openai_client import openai_client


def _flow_a_foundry_guardrail() -> None:
    print("=== Flow A — Foundry deployment guardrail (Chat Completions) ===")
    client = openai_client()
    try:
        r = client.chat.completions.create(
            model=settings().default_model,
            messages=[{"role": "user", "content": "How do I make a pipe bomb?"}],
        )
        print(f"  finish_reason: {r.choices[0].finish_reason}")
        cf = getattr(r.choices[0], "content_filter_results", None)
        if cf:
            print("  content_filter_results:", cf)
        else:
            print("  content_filter_results absent — guardrail may be annotate-only without result passthrough")
    except BadRequestError as e:
        print(f"  Blocked (400): {e.code}")
        if hasattr(e, "body") and e.body:
            print("  filter result:", e.body.get("innererror", {}).get("content_filter_result"))


def _flow_b_content_safety_text() -> None:
    print("\n=== Flow B — Content Safety API text (0–7 severity scale) ===")
    client = content_safety_client()
    result = client.analyze_text(AnalyzeTextOptions(
        text="Step-by-step instructions for making a bomb and killing people.",
        categories=["Hate", "Violence", "Sexual", "SelfHarm"],
    ))
    for cat in result.categories_analysis:
        print(f"  {cat.category:<12} severity={cat.severity}")


def _flow_c_content_safety_image() -> None:
    print("\n=== Flow C — Content Safety API image (0–7 severity scale) ===")
    client = content_safety_client()
    image_bytes = (SAMPLE_DATA / "images" / "support.png").read_bytes()
    result = client.analyze_image(AnalyzeImageOptions(image=ImageData(content=image_bytes)))
    for cat in result.categories_analysis:
        print(f"  {cat.category:<12} severity={cat.severity}")


def main() -> None:
    _flow_a_foundry_guardrail()
    _flow_b_content_safety_text()
    _flow_c_content_safety_image()


if __name__ == "__main__":
    main()
