from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain.agents import create_agent

endpoint="https://foundry-dev-eus-01.services.ai.azure.com/openai/v1"
deployment_name="gpt-5.4"
api_key=""

model=ChatOpenAI(
    base_url=endpoint,
    api_key=api_key,
    model=deployment_name
)

@tool
def get_order_status(order_id: str) -> str:
    """Get the current status of a CloudXeus order by order ID."""
    orders = {
        "ORD-001": "Dispatched — arriving tomorrow.",
        "ORD-002": "Processing — not yet shipped.",
        "ORD-003": "Delivered on June 12, 2026.",
    }
    return orders.get(order_id, f"Order {order_id} not found.")

@tool
def get_inventory(product_id: str) -> str:
    """Check the available inventory for a CloudXeus product by product ID."""
    inventory = {
        "PRD-A1": "142 units in stock.",
        "PRD-B2": "0 units — out of stock.",
        "PRD-C3": "37 units in stock.",
    }
    return inventory.get(product_id, f"Product {product_id} not found.")

agent=create_agent(
    model=model,
    tools=[get_order_status,get_inventory],
    system_prompt="You are a helpful CloudXeus operations assistant. Use the available tools to answer questions accurately."

)

response=agent.invoke(
    {
    "messages": [{"role": "user", "content": "What is the status of order ORD-002 and how many units of PRD-A1 do we have?"}]
}
)

print(response["messages"][-1].content)