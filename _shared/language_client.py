"""Azure AI Language — TextAnalyticsClient factory (keyless)."""
from azure.ai.textanalytics import TextAnalyticsClient
from azure.identity import DefaultAzureCredential
from .config import settings


def language_client() -> TextAnalyticsClient:
    return TextAnalyticsClient(
        endpoint=settings().require("LANGUAGE_ENDPOINT"),
        credential=DefaultAzureCredential(),
    )
