import hashlib
import re
import time
from .demo_data import get_order
from .policies import return_guidance

UNSAFE = ("hack", "exploit", "steal", "bypass security", "access another account")

def safety_check(message):
    text = message.lower()
    if any(x in text for x in UNSAFE): return {"status": "refused", "reason": "unsafe request"}
    if re.search(r"(?:\d[ -]?){13,19}", message): return {"status": "protected", "reason": "payment-card data detected"}
    if any(x in text for x in ("sue", "lawyer", "legal action")): return {"status": "escalated", "reason": "high-risk language"}
    return {"status": "allowed", "reason": "passed safety check"}

def sanitize(text):
    def h(value): return hashlib.sha256(value.encode()).hexdigest()[:8]
    text = re.sub(r"[\w.+-]+@[\w.-]+", lambda m: "EMAIL_" + h(m.group()), text)
    return re.sub(r"\bORD-\d+\b", lambda m: "ORDER_" + h(m.group()), text, flags=re.I)

def extract_order_id(message):
    found = re.search(r"ORD-\d+", message.upper())
    return found.group(0) if found else None

def classify(message):
    text = message.lower()
    if "return" in text or "refund" in text: return "return_refund"
    if "warranty" in text: return "warranty"
    if any(x in text for x in ("where", "track", "package", "delivery")): return "order_status"
    if "account" in text or "unauthor" in text: return "account_security"
    return "general_support"

def baseline_answer(message):
    intent = classify(message)
    templates = {"return_refund": "I can provide return and refund information. Please share your order ID for an order-specific check.", "warranty": "I can explain warranty coverage. Please share your order ID for verification.", "order_status": "I can check an order status if you provide the order ID.", "account_security": "Account-security concerns require human review.", "general_support": "Please describe the product or order issue in more detail."}
    return {"stage": "baseline", "intent": intent, "answer": templates[intent]}

def answer(message, context="", live=False, memory=None, feedback=None):
    started = time.perf_counter()
    safety = safety_check(message)
    if safety["status"] == "refused": return result(message, "refused", "I cannot help with unsafe access or harmful activity.", started, safety=safety)
    if safety["status"] == "protected": return result(message, "protected", "Please do not share payment-card details. I can continue without them.", started, safety=safety)
    if safety["status"] == "escalated": return result(message, "escalated", "This case has been identified as high risk and should be reviewed by a human support specialist.", started, safety=safety)
    intent = classify(message)
    order_id = extract_order_id(message)
    if not order_id and memory is not None and hasattr(memory, "resolve_contextual_order_id"):
        order_id = memory.resolve_contextual_order_id(message)
    if intent == "return_refund": response = return_guidance(order_id)
    elif intent == "order_status" and order_id:
        order = get_order(order_id)
        response = f"{order_id}: {order['product']} is {order['status']}." if order else "I could not verify that order ID. I will not invent a status; please check the ID or request human support."
    elif intent == "warranty" and order_id:
        order = get_order(order_id)
        response = f"{order_id}: warranty status is {order['warranty']}." if order else "I could not verify that order ID, so I cannot confirm warranty coverage."
    elif intent == "account_security": response = "For account-security concerns, do not share passwords or payment details. I recommend immediate human escalation."
    else: response = "I can help with that. Please provide an order ID or more detail so I can verify the correct policy or next step."
    if feedback and feedback.get("tone") == "empathetic": response = "I understand this is frustrating. " + response
    return result(
        message,
        "resolved",
        response,
        started,
        safety=safety,
        intent=intent,
        retrieved=bool(context),
        memory_turns=len(getattr(memory, "turns", memory or [])),
    )

def result(message, status, response, started, **extra):
    return {"status": status, "response": response, "latency_ms": round((time.perf_counter()-started)*1000, 2), "logged_message": sanitize(message), **extra}

def tool_call(name, args):
    order_id = args.get("order_id", "").upper()
    if name == "lookup_order": return {"tool": name, "result": get_order(order_id) or {"status": "not_found"}}
    if name == "check_warranty":
        order = get_order(order_id)
        return {"tool": name, "result": {"warranty": order["warranty"]} if order else {"status": "not_found"}}
    if name == "escalate_to_human": return {"tool": name, "result": {"status": "escalation_created", "reason": args.get("reason", "unresolved")}}
    return {"tool": name, "result": {"status": "blocked"}}

def evaluate(cases):
    outputs = []
    for case in cases:
        out = answer(case["input"])
        outputs.append({"id": case["id"], "expected": case["expected"], "observed": out["status"], "pass": out["status"] == case["expected"]})
    passed = sum(x["pass"] for x in outputs)
    return {"total": len(outputs), "passed": passed, "score": round(100*passed/len(outputs), 1), "cases": outputs}
