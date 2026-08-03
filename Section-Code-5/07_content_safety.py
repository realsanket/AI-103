# pip install azure.ai.contentsafety
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

from azure.ai.contentsafety import ContentSafetyClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.contentsafety.models import AnalyzeImageOptions, ImageData

CONTENT_SAFETY_ENDPOINT = "https://content-safety-dev-eus-01.cognitiveservices.azure.com/"
CONTENT_SAFETY_KEY=""

content_safety_client = ContentSafetyClient(
    endpoint=CONTENT_SAFETY_ENDPOINT,
    credential=AzureKeyCredential(CONTENT_SAFETY_KEY)
)
IMAGE_PATH = "support.png"

with open(IMAGE_PATH, "rb") as f:
    image_bytes = f.read()

image_request = AnalyzeImageOptions(
    image=ImageData(content=image_bytes)
)

moderation_result = content_safety_client.analyze_image(image_request)

print("Image moderation result:")
for category_result in moderation_result.categories_analysis:
    print(category_result.category, category_result.severity)