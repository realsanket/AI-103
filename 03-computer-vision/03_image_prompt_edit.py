"""Prompt-driven image edit — full-frame inpainting via `images.edit`."""

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
