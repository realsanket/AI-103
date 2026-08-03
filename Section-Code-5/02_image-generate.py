from openai import OpenAI
import base64
from pathlib import Path


endpoint = "https://foundry-dev-eus-01.services.ai.azure.com/openai/v1"
api_key = ""
IMAGE_DEPLOYMENT_NAME = "gpt-image-2"

client = OpenAI(
    base_url=endpoint,
    api_key=api_key
)


response=client.images.generate(
    model=IMAGE_DEPLOYMENT_NAME,
    prompt=(
        "Create a professional training image for an online course. "
        "Show a modern AI application dashboard with charts, documents, "
        "and an AI assistant helping business users. "
        "Use a clean corporate style suitable for a Microsoft Azure AI course."
    ),
    n=1,
    size="1024x1024",
    quality="medium",
    output_format="png"
)

image_base64 = response.data[0].b64_json
image_bytes = base64.b64decode(image_base64)

output_path = Path("generated_image.png")
output_path.write_bytes(image_bytes)

print(f"Image saved to: {output_path}")
