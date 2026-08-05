"""Text-to-image via `images.generate` — write PNG to _shared/sample_data/generated/."""

from _shared.config import SAMPLE_DATA, settings
from _shared.openai_client import openai_client
from _shared.vision_inputs import save_generated_image

_PROMPT = (
    "Create a professional training image for an online course. "
    "Show a modern AI application dashboard with charts, documents, "
    "and an AI assistant helping business users. "
    "Use a clean corporate style suitable for a Microsoft Azure AI course."
)


def main() -> None:
    client = openai_client()
    r = client.images.generate(
        model=settings().image_model,
        prompt=_PROMPT,
        n=1,
        size="1024x1024",
        quality="medium",
        output_format="png",
    )
    out = SAMPLE_DATA / "generated" / "training_image.png"
    save_generated_image(r, out)
    print(f"saved: {out}")


if __name__ == "__main__":
    main()
