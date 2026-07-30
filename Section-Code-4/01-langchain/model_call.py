# pip install langchain langchain-openai
from langchain_openai import ChatOpenAI

endpoint="https://foundry-dev-eus-01.services.ai.azure.com/openai/v1"
deployment_name="gpt-5.4"
api_key=""

client=ChatOpenAI(
    base_url=endpoint,
    api_key=api_key,
    model=deployment_name
)

response=client.invoke("What are the three main benefits of using managed AI endpoints in the cloud?")
print(response.content)