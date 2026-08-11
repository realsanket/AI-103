# Run: uv run python 03-computer-vision/05_image_prompt_edit.py
"""Prompt-driven full-frame image edit via `client.images.edit` — no mask required.

`images.edit` takes a source image and a natural-language prompt describing the
desired change. Without a mask, the model can interpret the change as full-frame —
"keep the product unchanged" is intent, not a pixel-level preservation guarantee.
Use this when the change intent is broad and exact edit boundaries don't matter.
For precise region control, use lesson 06 (masked edit).

Code path:
  `validate_edit_inputs(src)` → confirms source is readable PNG/JPEG/WebP
  `images.edit(model=IMAGE_MODEL, image=image_file, prompt=…, size, n, quality)`
  → `save_generated_image()` writes `edited_product_photo.png`

What to watch:
  Compare `edited_product_photo.png` to the source `product_photo.png`.
  Logos, text, and product identity may change even with "keep unchanged" instructions.

Prerequisites / env vars:
  AZURE_OPENAI_ENDPOINT — Azure OpenAI-compatible base URL
  IMAGE_MODEL           — image-generation deployment name
  _shared/sample_data/images/product_photo.png — source image (PNG/JPEG/WebP)
"""

from _shared.config import SAMPLE_DATA, settings
from _shared.openai_client import openai_client
from _shared.vision_inputs import save_generated_image, validate_edit_inputs

_PROMPT = """
Update this image so it looks like a professional marketing visual.
Keep the main product unchanged.
Improve the lighting, make the background cleaner, and give it a premium corporate style.
"""


def main() -> None:
    src = SAMPLE_DATA / "images" / "product_photo.png"
    dst = SAMPLE_DATA / "generated" / "edited_product_photo.png"
    validate_edit_inputs(src)

    client = openai_client()
    with src.open("rb") as image_file:
        r = client.images.edit(
            model=settings().image_model,
            image=image_file,
            prompt=_PROMPT,
            size="1024x1024",
            n=1,
            quality="medium",
        )
    save_generated_image(r, dst)
    print(f"saved: {dst}")


if __name__ == "__main__":
    main()
