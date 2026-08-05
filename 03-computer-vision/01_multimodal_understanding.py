"""Multimodal understanding — pass an image alongside text, ask for a summary."""

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
