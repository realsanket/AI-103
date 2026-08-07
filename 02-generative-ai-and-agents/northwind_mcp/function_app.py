# Run: uv run python 02-generative-ai-and-agents/northwind_mcp/function_app.py

import json

import azure.functions as func

app = func.FunctionApp()


def _arguments(context) -> dict | None:
    try:
        content = json.loads(context)
    except (TypeError, json.JSONDecodeError):
        return None
    if not isinstance(content, dict):
        return None
    arguments = content.get("arguments", content)
    return arguments if isinstance(arguments, dict) else None


order_status_properties = json.dumps(
    [
        {
            "name": "order_id",
            "type": "string",
            "description": "The order ID",
            "required": True,
        }
    ]
)


@app.mcp_tool_trigger(
    arg_name="context",
    tool_name="get_order_status",
    description="Get the current status of a Northwind order.",
    tool_properties=order_status_properties,
)
def get_order_status(context) -> str:
    arguments = _arguments(context)
    if not arguments or not isinstance(arguments.get("order_id"), str):
        return json.dumps({"error": "order_id must be a string."})
    order_id = arguments["order_id"]
    return f"Order {order_id}: Shipped. Expected delivery: 2 days."


list_orders_properties = json.dumps(
    [
        {
            "name": "customer_id",
            "type": "string",
            "description": "The customer ID",
            "required": True,
        }
    ]
)


@app.mcp_tool_trigger(
    arg_name="context",
    tool_name="list_customer_orders",
    description="List all orders for a Northwind customer.",
    tool_properties=list_orders_properties,
)
def list_customer_orders(context) -> str:
    arguments = _arguments(context)
    if not arguments or not isinstance(arguments.get("customer_id"), str):
        return json.dumps({"error": "customer_id must be a string."})
    return json.dumps(
        [
            {"order_id": "ORD-001", "status": "Shipped"},
            {"order_id": "ORD-002", "status": "Processing"},
        ]
    )
