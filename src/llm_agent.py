from .safety import safety_precheck

PROMPT_VARIANTS = {
    "basic": "Answer the customer support question.",
    "structured": "Act as a support agent. Identify intent, use only supplied policy context, state uncertainty, and propose the next safe step.",
    "safety_first": "Act as a customer-support resolution agent. Never fabricate policy or customer data. Refuse unsafe requests, escalate sensitive or unresolved cases, and distinguish information from actions. Return intent, evidence, answer, and next step.",
}

def llm_response(message: str, context: str = "", prompt_version: str = "safety_first") -> dict:
    check = safety_precheck(message)
    if check["status"] == "refuse":
        return {"status": "refused", "answer": "I cannot help with unsafe access or harmful activity."}
    if check["status"] == "escalate":
        return {"status": "escalated", "answer": "This case should be reviewed by a human support specialist."}
    if check["status"] == "protect":
        return {"status": "protected", "answer": "Please do not share payment-card details. I can continue without that information."}
    return {"status": "evidence_mode", "answer": f"Using prompt '{prompt_version}', I would answer from verified support context only. Context available: {bool(context)}."}
