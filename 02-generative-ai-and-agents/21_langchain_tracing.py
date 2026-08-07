# Run: uv run python 02-generative-ai-and-agents/21_langchain_tracing.py

"""LangChain agent with OpenTelemetry traces exported to Azure Monitor.

Beginner note:
  With APPLICATIONINSIGHTS_CONNECTION_STRING set in .env, every model call
  and tool call ships as a span to Application Insights → Transaction Search.
  Without it, the agent still runs — the tracer just isn't attached and a
  warning prints. Matches the same fallback shape as Domain 1's L12 tracing.

  Content recording is intentionally disabled: it otherwise captures user
  messages, tool arguments, and model outputs. Enable it only in development
  after privacy and compliance approval. L30 covers production data lifecycle,
  access, network, region, and cost preflight.
"""
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_openai import ChatOpenAI

from _shared.config import settings
from _shared.openai_client import azure_openai_token_provider


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
        enable_content_recording=False,
    )


def main() -> None:
    s = settings()
    model = ChatOpenAI(
        base_url=f"{s.require('AZURE_OPENAI_ENDPOINT')}/openai/v1",
        api_key=azure_openai_token_provider(),
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
        destination = "not exported — set APPLICATIONINSIGHTS_CONNECTION_STRING in .env to ship spans"

    r = agent.invoke(
        {"messages": [{"role": "user", "content": "Status of ORD-002 and stock of PRD-A1?"}]}
    )
    print(r["messages"][-1].content)
    print(f"\n→ Traces: {destination}")


if __name__ == "__main__":
    main()
