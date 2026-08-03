import azure.functions as func
import json
import logging

app = func.FunctionApp()

# --- Tool 1: Get Order Status ---
order_status_properties = json.dumps([
    {"name": "order_id", "type": "string",
     "description": "The order ID", "required": True}
])

@app.mcp_tool_trigger(
    arg_name="context",
    tool_name="get_order_status",
    description="Get the current status of a CloudXeus order.",
    tool_properties=order_status_properties,
)
def get_order_status(context) -> str:
    # Debug — log the full raw context so we can see its structure
    logging.info(f"RAW CONTEXT: {context}")
    
    content = json.loads(context)
    
    # Debug — log the parsed content
    logging.info(f"PARSED CONTENT: {json.dumps(content, indent=2)}")
    
    # Safe extraction with fallback
    arguments = content.get("arguments", content)
    order_id = arguments.get("order_id") or arguments.get("orderId") or arguments.get("order-id", "UNKNOWN")
    
    logging.info(f"Order lookup: {order_id}")
    return f"Order {order_id}: Shipped. Expected delivery: 2 days."


# --- Tool 2: List Orders by Customer ---
list_orders_properties = json.dumps([
    {"name": "customer_id", "type": "string",
     "description": "The customer ID", "required": True}
])

@app.mcp_tool_trigger(
    arg_name="context",
    tool_name="list_customer_orders",
    description="List all orders for a CloudXeus customer.",
    tool_properties=list_orders_properties,
)
def list_customer_orders(context) -> str:
    logging.info(f"RAW CONTEXT: {context}")
    
    content = json.loads(context)
    customer_id = content.get("arguments", content).get("customer_id", "UNKNOWN")
    
    logging.info(f"Listing orders for customer: {customer_id}")
    return json.dumps([
        {"order_id": "ORD-001", "status": "Shipped"},
        {"order_id": "ORD-002", "status": "Processing"},
    ])