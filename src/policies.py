from pathlib import Path

def load_policies(root="knowledge_base"):
    return [{"source": p.name, "text": p.read_text(encoding="utf-8")} for p in sorted(Path(root).glob("*.md"))]

def search_policies(query, policies, top_k=3):
    terms = {x.lower().strip(".,?!") for x in query.split() if len(x) > 2}
    scored = []
    for doc in policies:
        words = set(doc["text"].lower().split())
        score = len(terms & words)
        scored.append((score, doc))
    return [doc for score, doc in sorted(scored, key=lambda x: x[0], reverse=True)[:top_k] if score > 0]

def return_guidance(order_id=None):
    if not order_id:
        return "Our documented policy allows eligible returns within 30 days. I need an order ID to check an order-specific case."
    from .demo_data import ORDERS
    order = ORDERS.get(order_id.upper())
    if not order:
        return "I could not verify that order ID. I will not guess its status; please check the ID or request human support."
    if order["purchase_days_ago"] <= 30:
        return f"{order_id.upper()} is within the 30-day return window. The item must meet the documented condition requirements. I can explain the next steps, but a human-approved workflow is required to create the return."
    return f"{order_id.upper()} is outside the standard 30-day return window. I cannot promise an exception; this case should be escalated for human review."
