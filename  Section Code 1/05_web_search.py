from openai import OpenAI

endpoint = "https://foundry-dev-eus-01.services.ai.azure.com/openai/v1"
deployment_name = "gpt-5.4"
api_key = ""

client = OpenAI(
    base_url=endpoint,
    api_key=api_key
)

response = client.responses.create(
    model=deployment_name,
    instructions="You are a helpful research assistant. Always cite your sources.",
    input="What are the latest developments in AI regulation in the European Union?",
    tools=[{"type": "web_search"}],
    tool_choice="auto"
)

print(f"answer: {response.output_text}")
