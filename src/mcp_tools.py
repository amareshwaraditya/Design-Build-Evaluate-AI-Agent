TOOLS = {
    "lookup_order": "Read-only lookup of order status using an order ID.",
    "check_warranty": "Read-only check of warranty eligibility using an order ID.",
    "escalate_to_human": "Creates an escalation recommendation for sensitive or unresolved cases.",
}

MOCK_ORDERS = {
    "ORD-10001": {"status": "shipped", "product": "Wireless Earbuds", "warranty": "active"},
    "ORD-10002": {"status": "delivered", "product": "SmartWatch", "warranty": "active"},
}

def call_tool(name: str, arguments: dict) -> dict:
    if name == "lookup_order":
        order = MOCK_ORDERS.get(arguments.get("order_id"))
        return order or {"status": "not_found", "message": "Order could not be verified."}
    if name == "check_warranty":
        order = MOCK_ORDERS.get(arguments.get("order_id"))
        return {"warranty": order["warranty"]} if order else {"status": "not_found"}
    if name == "escalate_to_human":
        return {"status": "escalation_recommended", "reason": arguments.get("reason", "unresolved case")}
    return {"status": "tool_not_allowed"}
