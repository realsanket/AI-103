"""Text-to-image via `images.generate` — write PNG to _shared/sample_data/generated/."""
import base64

from _shared.config import SAMPLE_DATA, settings
from _shared.openai_client import openai_client

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
    out.write_bytes(base64.b64decode(r.data[0].b64_json))
    print(f"saved: {out}")


if __name__ == "__main__":
    main()
