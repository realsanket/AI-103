from openai import OpenAI
from pathlib import Path
import base64

endpoint = "https://foundry-dev-eus-01.services.ai.azure.com/openai/v1"
api_key = ""
IMAGE_DEPLOYMENT_NAME = "gpt-image-2"

input_image_path = Path("product_photo.png")
output_image_path = Path("edited_product_photo.png")

prompt = """
Update this image so it looks like a professional marketing visual.
Keep the main product unchanged.
Improve the lighting, make the background cleaner, and give it a premium corporate style.
"""

client = OpenAI(
    base_url=endpoint,
    api_key=api_key
)

with input_image_path.open("rb") as image_file:
    response = client.images.edit(
        model=IMAGE_DEPLOYMENT_NAME,
        image=image_file,
        prompt=prompt,
        size="1024x1024",
        n=1,
        quality="medium"
    )

image_base64 = response.data[0].b64_json
image_bytes = base64.b64decode(image_base64)

output_image_path.write_bytes(image_bytes)

print(f"Edited image saved to: {output_image_path}")