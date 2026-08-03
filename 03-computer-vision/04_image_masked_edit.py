"""Mask-based image edit — only the transparent pixels of the mask are editable."""
import base64

from _shared.config import SAMPLE_DATA, settings
from _shared.openai_client import openai_client

_PROMPT = """
In the editable area, add a small modern wall display showing a simple quarterly sales chart.
Keep the rest of the image unchanged.
The style should match the lighting and perspective of the original photo.
"""


def main() -> None:
    client = openai_client()
    src = SAMPLE_DATA / "images" / "product_photo.png"
    mask = SAMPLE_DATA / "images" / "mask.png"
    dst = SAMPLE_DATA / "generated" / "masked_edit_product_photo.png"

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
    dst.write_bytes(base64.b64decode(r.data[0].b64_json))
    print(f"saved: {dst}")


if __name__ == "__main__":
    main()
