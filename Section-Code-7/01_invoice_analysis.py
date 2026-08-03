# pip install azure.ai.contentunderstanding
from azure.core.credentials import AzureKeyCredential
from azure.ai.contentunderstanding import ContentUnderstandingClient

endpoint="https://foundry-dev-eus-01.services.ai.azure.com/"
api_key=""

client=ContentUnderstandingClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(api_key)
)

file_path = "cloudxeus_sample_invoice.pdf"

with open(file_path, "rb") as file:
    poller=client.begin_analyze_binary(
        analyzer_id="prebuilt-invoice",
        binary_input=file,
        content_type="application/pdf"
    )

result = poller.result()
print("Analysis completed.")

content = result["contents"][0]

# Print extracted text or markdown if available
print("\n--- Document Content ---")
if "markdown" in content:
    print(content["markdown"][:1000])
else:
    print("No markdown content returned.")

fields = content["fields"]

for field_name, field_data in fields.items():
    print(f"{field_name}: {field_data}")

client.close()