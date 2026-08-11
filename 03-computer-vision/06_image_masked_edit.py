# Run: uv run python 03-computer-vision/06_image_masked_edit.py
"""Mask-based image edit — only transparent pixels of the mask are intended editable region.

A mask constrains the edit request better than prompt alone. Transparent pixels (alpha=0)
mark where the model should generate new content; non-transparent pixels mark regions to
preserve. The constraint is intent, not a pixel lock — generation remains non-deterministic
and outside-mask content can still vary. For full-frame edits, see lesson 05.

Code path:
  `validate_edit_inputs(src, mask)` → checks source + mask have same dims, PNG with alpha,
    at least one transparent pixel
  `images.edit(model=IMAGE_MODEL, image=image_file, mask=mask_file, prompt=…, size, n, quality)`
  → `save_generated_image()` writes `masked_edit_product_photo.png`

What to watch:
  Inspect source, mask, and output together. The generated region should correspond to the
  transparent area of `mask.png`. Check for artifacts at mask boundaries and content
  changes outside the intended edit region.

Prerequisites / env vars:
  AZURE_OPENAI_ENDPOINT — Azure OpenAI-compatible base URL
  IMAGE_MODEL           — image-generation deployment name
  _shared/sample_data/images/product_photo.png — source (PNG/JPEG/WebP)
  _shared/sample_data/images/mask.png — PNG with alpha channel, same dimensions as source
"""

from _shared.config import SAMPLE_DATA, settings
from _shared.openai_client import openai_client
from _shared.vision_inputs import save_generated_image, validate_edit_inputs

_PROMPT = """
In the editable area, add a small modern wall display showing a simple quarterly sales chart.
Keep the rest of the image unchanged.
The style should match the lighting and perspective of the original photo.
"""


def main() -> None:
    src = SAMPLE_DATA / "images" / "product_photo.png"
    mask = SAMPLE_DATA / "images" / "mask.png"
    dst = SAMPLE_DATA / "generated" / "masked_edit_product_photo.png"
    validate_edit_inputs(src, mask)

    client = openai_client()
    with src.open("rb") as image_file, mask.open("rb") as mask_file:
        r = client.images.edit(
            model=settings().image_model,
            image=image_file,
            mask=mask_file,
            prompt=_PROMPT,
            size="1024x1024",
            n=1,
            quality="medium",
        )
    save_generated_image(r, dst)
    print(f"saved: {dst}")


if __name__ == "__main__":
    main()
