"""Multimodal understanding — pass an image alongside text, ask for a summary."""
import base64

from _shared.config import SAMPLE_DATA, settings
from _shared.openai_client import openai_client


def main() -> None:
    image_path = SAMPLE_DATA / "images" / "sales_data.png"
    b64 = base64.b64encode(image_path.read_bytes()).decode("utf-8")

    client = openai_client()
    r = client.responses.create(
        model=settings().default_model,
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": "Summarize the content in the attached image."},
                    {"type": "input_image", "image_url": f"data:image/png;base64,{b64}"},
                ],
            }
        ],
    )
    print(r.output_text)


if __name__ == "__main__":
    main()
