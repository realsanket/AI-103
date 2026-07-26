from openai import OpenAI
import base64

endpoint = "https://foundry-dev-eus-01.services.ai.azure.com/openai/v1"
deployment_name = "gpt-5.4"
api_key = ""

client = OpenAI(
    base_url=endpoint,
    api_key=api_key
)

image_path = "Agent_types.png"
with open(image_path, "rb") as image_file:
    image_data = base64.b64encode(image_file.read()).decode("utf-8")

response = client.responses.create(
    model=deployment_name,
    instructions="You are a helpful assistant that reads and extracts information from images.",
    input=[
        {
            "role": "user",
            "content": [
                {
                    "type": "input_image",
                    "image_url": f"data:image/png;base64,{image_data}"
                },
                {
                    "type": "input_text",
                    "text": "Extract all the text from this image and present it in a structured, readable format."
                }
            ]
        }
    ]
)

print(f"answer: {response.output_text}")
