"""Prompt-driven image edit — full-frame inpainting via `images.edit`."""
import base64

from _shared.config import SAMPLE_DATA, settings
from _shared.openai_client import openai_client

_PROMPT = """
Update this image so it looks like a professional marketing visual.
Keep the main product unchanged.
Improve the lighting, make the background cleaner, and give it a premium corporate style.
"""


def main() -> None:
    client = openai_client()
    src = SAMPLE_DATA / "images" / "product_photo.png"
    dst = SAMPLE_DATA / "generated" / "edited_product_photo.png"

    with src.open("rb") as image_file:
        r = client.images.edit(
            model=settings().image_model,
            image=image_file,
            prompt=_PROMPT,
            size="1024x1024",
            n=1,
            quality="medium",
        )
    dst.write_bytes(base64.b64decode(r.data[0].b64_json))
    print(f"saved: {dst}")


if __name__ == "__main__":
    main()
