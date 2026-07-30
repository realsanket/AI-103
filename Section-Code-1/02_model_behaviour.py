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
    instructions="You are a creative copywriter.",
    input="Write a two-sentence tagline for a new AI-powered productivity app.",
     temperature=2
)


print(f"answer: {response.output_text}")
