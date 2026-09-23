# Run: uv run python 03-computer-vision/01_multimodal_understanding.py
# Practice-question coverage: Q126.
"""Multimodal understanding — ask a question about a local image via the Responses API.

The Responses API accepts `input_image` content items alongside text. The image is
encoded as a base64 data URL and sent inline with the request — no Azure Blob Storage
or CU service needed. This is the simplest path for visual Q&A: one call, one answer.

What this proves: a visual-capable deployment + credential chain work for image+text input.
What it does NOT prove: structured extraction, reliable OCR, object coordinates, or
factual verification of image content.

What to watch:
  Free-form prose summary of `sales_data.png`. The model may misread numbers or small
  text — treat all visual output as an unreviewed draft until validated against source.

Prerequisites / env vars:
  AZURE_OPENAI_ENDPOINT — Azure OpenAI-compatible base URL
  DEFAULT_MODEL         — deployment name for a visual-capable model (gpt-4.1, gpt-4o)
  _shared/sample_data/images/sales_data.png — source image
"""

from _shared.config import SAMPLE_DATA, settings
from _shared.openai_client import openai_client
from _shared.vision_inputs import image_data_url


def main() -> None:
    image_path = SAMPLE_DATA / "images" / "sales_data.png"
    image_url = image_data_url(image_path)

    client = openai_client()
    r = client.responses.create(
        model=settings().default_model,
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": "Summarize the content in the attached image."},
                    {"type": "input_image", "image_url": image_url},
                ],
            }
        ],
    )
    print(r.output_text)


if __name__ == "__main__":
    main()
