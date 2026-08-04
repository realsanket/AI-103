"""LangChain agent using Foundry as the model backend.

Beginner note:
  Uses `create_agent()` (the modern LangChain agent constructor) with two
  local `@tool`-decorated Python functions. Auth is keyless — `ChatOpenAI`
  is pointed at the Foundry `openai/v1` endpoint with a bearer token from
  `DefaultAzureCredential`, same shape as the plain OpenAI SDK.

  Use this pattern when you already have LangChain chains/tools you want
  to reuse. For a graph-shaped agent with conditional edges and stateful
  routing, see L22 (LangGraph).

What to watch:
  The final assistant message answers both sub-questions (order + inventory)
  after the model has invoked both tools.
"""
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_openai import ChatOpenAI

from _shared.config import settings

_SCOPE = "https://cognitiveservices.azure.com/.default"


@tool
def get_order_status(order_id: str) -> str:
    """Get the current status of a Northwind order by order ID."""
    orders = {
        "ORD-001": "Dispatched — arriving tomorrow.",
        "ORD-002": "Processing — not yet shipped.",
        "ORD-003": "Delivered on June 12, 2026.",
    }
    return orders.get(order_id, f"Order {order_id} not found.")


@tool
def get_inventory(product_id: str) -> str:
    """Check the available inventory for a Northwind product by product ID."""
    inventory = {"PRD-A1": "142 units in stock.", "PRD-B2": "0 units — out of stock.", "PRD-C3": "37 units in stock."}
    return inventory.get(product_id, f"Product {product_id} not found.")


def main() -> None:
    s = settings()
    token_provider = get_bearer_token_provider(DefaultAzureCredential(), _SCOPE)
    model = ChatOpenAI(
        base_url=f"{s.foundry_endpoint}/openai/v1",
        api_key=token_provider(),
        model=s.default_model,
    )
    agent = create_agent(
        model=model,
        tools=[get_order_status, get_inventory],
        system_prompt=(
            "You are a helpful Northwind operations assistant. "
            "Use the available tools to answer questions accurately."
        ),
    )
    response = agent.invoke(
        {"messages": [{"role": "user", "content": "What is the status of order ORD-002 and how many units of PRD-A1 do we have?"}]}
    )
    print(response["messages"][-1].content)


if __name__ == "__main__":
    main()
