from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

endpoint = "https://foundry-dev-eus-01.services.ai.azure.com/"
api_key=""

client = TextAnalyticsClient(
    endpoint=endpoint ,
    credential=AzureKeyCredential(api_key),
)

documents = [
    "Hi, this is Sarah Chen from Acme Logistics writing in again about "
    "ticket TKT-1042. Our Gold-tier SLA promises a 4 hour response time, "
    "and we are now at hour 6 with no update. The VPN client keeps "
    "dropping every 10 minutes on our Windows fleet since the rollout of "
    "CloudXeus Connect v3.2 last Tuesday. If this isn't resolved by end "
    "of day Friday we will be requesting the $500 SLA breach credit "
    "outlined in our contract.",
]

response=client.recognize_entities(documents,language="en")
results = [doc for doc in response if not doc.is_error]

for idx, doc in enumerate(results):
    print(f"--- Document {idx + 1}: Prebuilt NER Results ---")
    for entity in doc.entities:
        subcat = f" / {entity.subcategory}" if entity.subcategory else ""
        print(f"  [{entity.category}{subcat}] '{entity.text}'  (confidence: {entity.confidence_score:.2f})")
    print()