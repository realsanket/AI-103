from azure.core.credentials import AzureKeyCredential
from azure.ai.contentunderstanding import ContentUnderstandingClient

endpoint="https://foundry-dev-eus-01.services.ai.azure.com/"
api_key=""

client=ContentUnderstandingClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(api_key)
)

file_path = "support_ticket_portal.png"

with open(file_path, "rb") as file:
    poller=client.begin_analyze_binary(
        analyzer_id="prebuilt-imageSearch",
        binary_input=file,
        content_type="image/png"
    )
result = poller.result()
print("Analysis completed.")

content = result["contents"][0]

print("\n--- Image Analysis Result ---")
print(content)

client.close()