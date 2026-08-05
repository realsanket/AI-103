"""LangChain agent with OpenTelemetry traces exported to Azure Monitor.

Beginner note:
  With APPLICATIONINSIGHTS_CONNECTION_STRING set in .env, every model call
  and tool call ships as a span to Application Insights → Transaction Search.
  Without it, the agent still runs — the tracer just isn't attached and a
  warning prints. Matches the same fallback shape as Domain 1's L12 tracing.
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
    return {"ORD-001": "Dispatched.", "ORD-002": "Processing.", "ORD-003": "Delivered."}.get(
        order_id, f"Order {order_id} not found."
    )


@tool
def get_inventory(product_id: str) -> str:
    """Check the available inventory for a Northwind product by product ID."""
    return {"PRD-A1": "142 units.", "PRD-B2": "0 units.", "PRD-C3": "37 units."}.get(
        product_id, f"Product {product_id} not found."
    )


def _build_tracer(connection_string: str):
    from langchain_azure_ai.callbacks.tracers import AzureAIOpenTelemetryTracer

    return AzureAIOpenTelemetryTracer(
        connection_string=connection_string,
        name="Northwind LangChain Ops Agent",
        agent_id="northwind-langchain-ops-agent",
        enable_content_recording=True,
    )


def main() -> None:
    s = settings()
    token_provider = get_bearer_token_provider(DefaultAzureCredential(), _SCOPE)
    model = ChatOpenAI(
        base_url=f"{s.azure_openai_endpoint}/openai/v1",
        api_key=token_provider(),
        model=s.default_model,
    )

    agent = create_agent(
        model=model,
        tools=[get_order_status, get_inventory],
        system_prompt="You are a helpful Northwind operations assistant. Use tools when needed.",
    )

    if s.app_insights_connection_string:
        agent = agent.with_config({"callbacks": [_build_tracer(s.app_insights_connection_string)]})
        destination = "Application Insights → Transaction Search (agent_id=northwind-langchain-ops-agent)"
    else:
        destination = "stdout only — set APPLICATIONINSIGHTS_CONNECTION_STRING in .env to ship spans"

    r = agent.invoke(
        {"messages": [{"role": "user", "content": "Status of ORD-002 and stock of PRD-A1?"}]}
    )
    print(r["messages"][-1].content)
    print(f"\n→ Traces: {destination}")


if __name__ == "__main__":
    main()
