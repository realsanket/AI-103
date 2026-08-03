"""LangChain agent with OpenTelemetry traces exported to Azure Monitor.

Set APPLICATIONINSIGHTS_CONNECTION_STRING in `.env`. Traces show every model
call + tool call in Application Insights → transaction search.
"""
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_azure_ai.callbacks.tracers import AzureAIOpenTelemetryTracer
from langchain_openai import ChatOpenAI

from _shared.config import settings

_SCOPE = "https://cognitiveservices.azure.com/.default"


@tool
def get_order_status(order_id: str) -> str:
    """Get the current status of a Northwind order by order ID."""
    return {"ORD-001": "Dispatched.", "ORD-002": "Processing.", "ORD-003": "Delivered."}.get(
        order_id, f"Order {order_id} not found."
    )


@tool
def get_inventory(product_id: str) -> str:
    """Check the available inventory for a Northwind product by product ID."""
    return {"PRD-A1": "142 units.", "PRD-B2": "0 units.", "PRD-C3": "37 units."}.get(
        product_id, f"Product {product_id} not found."
    )


def main() -> None:
    s = settings()
    if not s.app_insights_connection_string:
        raise SystemExit("Set APPLICATIONINSIGHTS_CONNECTION_STRING in .env to run this lesson.")

    token_provider = get_bearer_token_provider(DefaultAzureCredential(), _SCOPE)
    model = ChatOpenAI(
        base_url=f"{s.foundry_endpoint}/openai/v1",
        api_key=token_provider(),
        model=s.default_model,
    )

    tracer = AzureAIOpenTelemetryTracer(
        connection_string=s.app_insights_connection_string,
        name="Northwind LangChain Ops Agent",
        agent_id="northwind-langchain-ops-agent",
        enable_content_recording=True,
    )

    agent = create_agent(
        model=model,
        tools=[get_order_status, get_inventory],
        system_prompt="You are a helpful Northwind operations assistant. Use tools when needed.",
    ).with_config({"callbacks": [tracer]})

    r = agent.invoke(
        {"messages": [{"role": "user", "content": "Status of ORD-002 and stock of PRD-A1?"}]}
    )
    print(r["messages"][-1].content)
    print("\n→ Look in Application Insights for traces tagged agent_id=northwind-langchain-ops-agent")


if __name__ == "__main__":
    main()
