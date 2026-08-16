"""Read-only order persistence layer backed by ``data/orders.json``."""

import json
from pathlib import Path


ORDER_STORE_PATH = Path(__file__).resolve().parents[1] / "data" / "orders.json"
_REQUIRED_FIELDS = {"product", "status", "purchase_days_ago", "warranty"}


def load_orders() -> dict[str, dict]:
    """Load and validate the authoritative order records from disk."""
    with ORDER_STORE_PATH.open(encoding="utf-8") as handle:
        orders = json.load(handle)

    if not isinstance(orders, dict):
        raise ValueError("Order store must contain an object keyed by order ID.")
    for order_id, order in orders.items():
        if not isinstance(order_id, str) or not order_id.startswith("ORD-"):
            raise ValueError(f"Invalid order ID in order store: {order_id!r}")
        if not isinstance(order, dict) or _REQUIRED_FIELDS - order.keys():
            raise ValueError(f"Order {order_id} is missing required fields.")
    return orders


def get_order(order_id: str) -> dict | None:
    """Return a verified order record, or ``None`` when it is not stored."""
    order = load_orders().get(order_id.upper())
    return dict(order) if order else None
