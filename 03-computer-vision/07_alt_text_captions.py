"""Accessibility alt-text + multi-image captions via a multimodal model.

Two flows:
1. One image → short alt-text + extended description (WCAG-friendly).
2. Multiple images → one narrative caption tying them together.
"""
import re

from _shared.config import SAMPLE_DATA, settings
from _shared.openai_client import openai_client
from _shared.vision_inputs import image_data_url


def _response_text(response: object) -> str:
    text = getattr(response, "output_text", "")
    if not isinstance(text, str) or not text.strip():
        raise RuntimeError("Model response did not include accessibility text.")
    return text.strip()


def _accessibility_draft(response: object) -> str:
    text = _response_text(response)
    match = re.search(r"(?ims)^ALT:\s*(.+?)\s*^DESCRIPTION:\s*(.+)$", text)
    if not match:
        return f"{text}\n\nREVIEW: Expected ALT: and DESCRIPTION: labels."
    alt_text = match.group(1).strip()
    if len(alt_text) > 125:
        return f"{text}\n\nREVIEW: ALT exceeds 125 characters."
    return text


def _alt_text_and_extended(image_url: str) -> str:
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
                    {"type": "input_image", "image_url": image_url},
                ],
            },
        ],
    )
    return _accessibility_draft(r)


def _multi_image_caption(image_urls: list[str]) -> str:
    client = openai_client()
    content = [{"type": "input_text", "text": "Write one narrative caption tying these images together."}]
    for image_url in image_urls:
        content.append({"type": "input_image", "image_url": image_url})
    r = client.responses.create(
        model=settings().default_model,
        input=[{"role": "user", "content": content}],
    )
    return _response_text(r)


def main() -> None:
    sales = SAMPLE_DATA / "images" / "sales_data.png"
    portal = SAMPLE_DATA / "images" / "support_ticket_portal.png"
    sales_url = image_data_url(sales)
    portal_url = image_data_url(portal)
    print("=== Alt-text ===")
    print(_alt_text_and_extended(sales_url))
    print("\n=== Multi-image caption ===")
    print(_multi_image_caption([sales_url, portal_url]))


if __name__ == "__main__":
    main()
