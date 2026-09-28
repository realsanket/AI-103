# Run: uv run python 02-generative-ai-and-agents/azure_functions_orders/function_app.py

import azure.functions as func
import json
import os

app = func.FunctionApp()

# App setting ORDERS_REQUIRE_KEY=true switches both routes to function-key auth,
# so callers must send the x-functions-key header (lesson 12 --auth connection).
_AUTH_LEVEL = (
    func.AuthLevel.FUNCTION
    if os.environ.get("ORDERS_REQUIRE_KEY", "").lower() == "true"
    else func.AuthLevel.ANONYMOUS
)

ORDERS = {
    "1001": {
        "order_id": "1001",
        "customer": "Northgate Retail",
        "status": "shipped",
        "total": 2450.00,
    },
    "1002": {
        "order_id": "1002",
        "customer": "Aurora Logistics",
        "status": "processing",
        "total": 815.50,
    },
    "1003": {
        "order_id": "1003",
        "customer": "Brightline Media",
        "status": "delivered",
        "total": 129.99,
    },
}

@app.route(route="orders", methods=["GET"],
           auth_level=_AUTH_LEVEL)
def list_orders(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(
        json.dumps(list(ORDERS.values())),
        mimetype="application/json",
    )

@app.route(route="orders/{order_id}", methods=["GET"],
           auth_level=_AUTH_LEVEL)
def get_order(req: func.HttpRequest) -> func.HttpResponse:
    order_id = req.route_params.get("order_id")
    order = ORDERS.get(order_id)

    if order is None:
        return func.HttpResponse(
            json.dumps({"error": f"Order {order_id} not found"}),
            status_code=404,
            mimetype="application/json",
        )

    return func.HttpResponse(
        json.dumps(order),
        mimetype="application/json",
    )