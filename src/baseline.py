RULES = {
    "refund": "Our standard return policy allows eligible returns within 30 days. I can explain the policy, but I cannot approve a refund automatically.",
    "shipping": "I can help with shipping information. Please provide an order ID if you want an order-specific status check.",
    "warranty": "I can explain warranty coverage. Please provide an order ID for an order-specific check.",
}

def baseline_response(message: str) -> str:
    lowered = message.lower()
    for keyword, response in RULES.items():
        if keyword in lowered or (keyword == "shipping" and "package" in lowered):
            return response
    return "I could not classify this request using the baseline rules. Please provide more detail or request human support."
