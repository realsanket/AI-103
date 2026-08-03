# pip install azure.ai.textanalytics
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

endpoint = "https://foundry-dev-eus-01.services.ai.azure.com/"
api_key=""

client = TextAnalyticsClient(
    endpoint=endpoint ,
    credential=AzureKeyCredential(api_key),
)

documents = [
    "Hi, this is Sarah Chen from Acme Logistics. You can reach me at "
    "sarah.chen@acmelogistics.com or call 312-555-1234 regarding ticket TKT-1042.",
]

response=client.recognize_pii_entities(documents,language="en")
results = [doc for doc in response if not doc.is_error]

for idx, doc in enumerate(results):
    print(f"--- Document {idx + 1} ---")
    print(f"Redacted text: {doc.redacted_text}")
    print("Detected entities:")
    for entity in doc.entities:
        print(f"  [{entity.category}] '{entity.text}'  (confidence: {entity.confidence_score:.2f})")
    print()