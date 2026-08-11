# Run: uv run python 03-computer-vision/02_alt_text_captions.py
"""Accessibility alt-text and multi-image captions — two flows using a multimodal model.

AI-generated alt text can accelerate accessibility authoring but requires human review.
The model generates text from pixels; it cannot know the intended page context, decorative
vs informative intent, or how a screen-reader user will experience the surrounding content.

Flow A — Single image: model returns `ALT:` (≤125 chars) and `DESCRIPTION:` (2–4 sentences).
  `_accessibility_draft()` checks the 125-char ALT ceiling and expected labels.
Flow B — Multiple images: model returns one narrative caption tying both images together.

What to watch:
  ALT text under 125 characters in the `ALT:` block. If the `REVIEW:` warning appears,
  the draft needs human editing before publication. Never publish AI alt text without a
  human reviewer checking it against the actual page context and user intent.

Prerequisites / env vars:
  AZURE_OPENAI_ENDPOINT — Azure OpenAI-compatible base URL
  DEFAULT_MODEL         — visual-capable model deployment name
  _shared/sample_data/images/sales_data.png, support_ticket_portal.png — source images
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
