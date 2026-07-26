import azure.functions as func
import json

app = func.FunctionApp()

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
           auth_level=func.AuthLevel.ANONYMOUS)
def list_orders(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(
        json.dumps(list(ORDERS.values())),
        mimetype="application/json",
    )

@app.route(route="orders/{order_id}", methods=["GET"],
           auth_level=func.AuthLevel.ANONYMOUS)
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