from openai import OpenAI
from pathlib import Path
import base64

endpoint = "https://foundry-dev-eus-01.services.ai.azure.com/openai/v1"
api_key = ""
IMAGE_DEPLOYMENT_NAME = "gpt-image-2"

input_image_path = Path("product_photo.png")
mask_image_path = Path("mask.png")
output_image_path = Path("masked_edit_product_photo.png")

client = OpenAI(
    base_url=endpoint,
    api_key=api_key
)

prompt = """
In the editable area, add a small modern wall display showing a simple quarterly sales chart.
Keep the rest of the image unchanged.
The style should match the lighting and perspective of the original photo.
"""

with input_image_path.open("rb") as image_file, mask_image_path.open("rb") as mask_file:
    response = client.images.edit(
        model=IMAGE_DEPLOYMENT_NAME,
        image=image_file,
        mask=mask_file,
        prompt=prompt,
        size="1024x1024",
        n=1,
        quality="medium"
    )

image_base64 = response.data[0].b64_json
image_bytes = base64.b64decode(image_base64)

output_image_path.write_bytes(image_bytes)

print(f"Masked edited image saved to: {output_image_path}")