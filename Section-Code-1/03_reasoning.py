from openai import OpenAI

endpoint = "https://foundry-dev-eus-01.services.ai.azure.com/openai/v1"
deployment_name = "gpt-5.4"
api_key = ""

client = OpenAI(
    base_url=endpoint,
    api_key=api_key
)

problem = """
A distributed e-commerce system is experiencing intermittent checkout failures 
during peak traffic. The failures appear random, affect roughly 3 percent of the transactions, 
and only occur when inventory checks and payment processing run concurrently. 
Identify the most likely root cause and propose a solution.
"""

response = client.responses.create(
    model=deployment_name,
    instructions="You are a senior software architect.",
    input=problem,
    reasoning={"effort": "high"}
)

print(f"answer: {response.output_text}")
