from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

endpoint = "https://foundry-dev-eus-01.services.ai.azure.com/"
api_key=""

client = TextAnalyticsClient(
    endpoint=endpoint ,
    credential=AzureKeyCredential(api_key),
)

documents = [
    "Hi, this is Sarah Chen from Acme Logistics regarding ticket TKT-1042.",
    "Bonjour, je vous écris au sujet du ticket TKT-1042 concernant notre VPN.",
    "こんにちは、TKT-1042のチケットについてVPNの問題をご連絡しています。",
    "OK"
]

response=client.detect_language(documents)
results = [doc for doc in response if not doc.is_error]

for idx, doc in enumerate(results):
    primary = doc.primary_language
    print(f"--- Document {idx + 1}: \"{documents[idx][:40]}...\" ---")
    print(f"  Detected language: {primary.name} ({primary.iso6391_name})")
    print(f"  Confidence score: {primary.confidence_score:.2f}")
    print()

