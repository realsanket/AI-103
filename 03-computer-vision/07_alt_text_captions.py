"""Accessibility alt-text + multi-image captions via a multimodal model.

Two flows:
1. One image → short alt-text + extended description (WCAG-friendly).
2. Multiple images → one narrative caption tying them together.
"""
import base64

from _shared.config import SAMPLE_DATA, settings
from _shared.openai_client import openai_client


def _b64(path) -> str:
    return base64.b64encode(path.read_bytes()).decode("utf-8")


def _alt_text_and_extended(image_b64: str) -> str:
    client = openai_client()
    r = client.responses.create(
        model=settings().default_model,
        input=[
            {
                "role": "system",
                "content": (
                    "Return two labeled paragraphs:\n"
                    "ALT: one sentence, <125 chars, screen-reader friendly.\n"
                    "DESCRIPTION: 2-4 sentences, describe visual details useful for a low-vision user."
                ),
            },
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": "Generate alt-text + extended description."},
                    {"type": "input_image", "image_url": f"data:image/png;base64,{image_b64}"},
                ],
            },
        ],
    )
    return r.output_text


def _multi_image_caption(image_b64s: list[str]) -> str:
    client = openai_client()
    content = [{"type": "input_text", "text": "Write one narrative caption tying these images together."}]
    for b in image_b64s:
        content.append({"type": "input_image", "image_url": f"data:image/png;base64,{b}"})
    r = client.responses.create(
        model=settings().default_model,
        input=[{"role": "user", "content": content}],
    )
    return r.output_text


def main() -> None:
    sales = SAMPLE_DATA / "images" / "sales_data.png"
    portal = SAMPLE_DATA / "images" / "support_ticket_portal.png"
    print("=== Alt-text ===")
    print(_alt_text_and_extended(_b64(sales)))
    print("\n=== Multi-image caption ===")
    print(_multi_image_caption([_b64(sales), _b64(portal)]))


if __name__ == "__main__":
    main()
