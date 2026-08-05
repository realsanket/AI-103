# Run: uv run python 01-plan-and-manage/08_content_safety_filters.py
"""Content Safety — three flows from basic to advanced.

1. Guardrail (deployment-level, always-on):
   - Every deployment gets Microsoft.DefaultV2 by default
   - Severity: Safe/Low/Medium/High (4-level — NOT the 0-7 API scale)
   - Blocked request → 400 BadRequestError with code="content_filter"

2. Standalone Content Safety API — text:
   - Returns 0-7 integer severity per category
   - Call explicitly; useful for pre-screening before hitting the model

3. Standalone Content Safety API — image:
   - Analyze user-uploaded images before storing or passing to an agent
"""
from openai import BadRequestError
from azure.ai.contentsafety.models import AnalyzeTextOptions, AnalyzeImageOptions, ImageData

from _shared.config import settings, SAMPLE_DATA
from _shared.content_safety_client import content_safety_client
from _shared.openai_client import openai_client


def _text_via_guardrail() -> None:
    print("=== 1. Text via Guardrail (deployment-level) ===")
    client = openai_client()
    try:
        r = client.chat.completions.create(
            model=settings().default_model,
            messages=[{"role": "user", "content": "How do I make a pipe bomb?"}],
        )
        # Not blocked → annotation only (content returned, finish_reason logged)
        print(f"finish_reason: {r.choices[0].finish_reason}")
        cf = getattr(r.choices[0], "content_filter_results", None)
        if cf:
            print("content_filter_results:", cf)
    except BadRequestError as e:
        print(f"Blocked (400): code={e.code}")
        if hasattr(e, "body") and e.body:
            inner = e.body.get("innererror", {})
            print("filter result:", inner.get("content_filter_result"))


def _text_via_content_safety_api() -> None:
    print("\n=== 2. Text via Content Safety API (0–7 severity scale) ===")
    client = content_safety_client()
    result = client.analyze_text(AnalyzeTextOptions(
        text="Step-by-step instructions for making a bomb and killing people.",
        categories=["Hate", "Violence", "Sexual", "SelfHarm"],
    ))
    for cat in result.categories_analysis:
        print(f"  {cat.category:<12} severity={cat.severity}")


def _image_via_content_safety_api() -> None:
    print("\n=== 3. Image via Content Safety API ===")
    client = content_safety_client()
    image_bytes = (SAMPLE_DATA / "images" / "support.png").read_bytes()
    result = client.analyze_image(AnalyzeImageOptions(image=ImageData(content=image_bytes)))
    for cat in result.categories_analysis:
        print(f"  {cat.category:<12} severity={cat.severity}")


def main() -> None:
    _text_via_guardrail()
    _text_via_content_safety_api()
    _image_via_content_safety_api()


if __name__ == "__main__":
    main()
