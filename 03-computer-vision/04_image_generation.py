# Run: uv run python 03-computer-vision/04_image_generation.py
"""Text-to-image generation via `client.images.generate` — saves PNG to sample_data/generated/.

Image generation produces pixels from a text prompt. It is creative output, not factual
reproduction. The model does not have access to real brand assets, product photos, or
company data — it generates plausible-looking content. Apply human review and policy
approval before distributing generated images.

What this proves: `IMAGE_MODEL` deployment + credential chain + `images.generate` work.
What it does NOT prove: output accuracy, brand conformance, rights clearance, or
fitness for any specific use.

Code path:
  `images.generate(model=IMAGE_MODEL, prompt=…, n=1, size="1024x1024", quality="medium", output_format="png")`
  → `save_generated_image()` decodes returned base64 bytes and writes `training_image.png`

What to watch:
  "saved: .../training_image.png" — open the file for visual review. Each run overwrites
  the previous output. Latency and cost vary with quality and size settings.

Prerequisites / env vars:
  AZURE_OPENAI_ENDPOINT — Azure OpenAI-compatible base URL
  IMAGE_MODEL           — image-generation deployment name (e.g. gpt-image-2)
"""

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
