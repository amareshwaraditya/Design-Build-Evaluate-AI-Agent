"""Phase 3 — LLM integration: a real LangChain `ChatOpenAI` call behind versioned system prompts."""
import time

from .config import settings
from .safety import safety_precheck

PROMPT_VARIANTS = {
    "v1_basic": "You are a customer support assistant for Tech Gadgets Inc. Answer the customer's question helpfully.",
    "v2_structured": (
        "You are a Tech Gadgets Inc. support agent. First identify the customer's intent. "
        "Answer only using the policy context provided below — if it is missing or insufficient, say so "
        "explicitly instead of guessing. Close with one concrete next step for the customer."
    ),
    "v3_safety_first": (
        "You are Athena, the friendly and professional Tech Gadgets Inc. customer-support assistant.\n"
        "Rules you must always follow:\n"
        "1. NEVER fabricate policy, pricing, or product information — use only the supplied policy context.\n"
        "2. If the context does not cover the question, say so honestly and offer to connect them with a human agent.\n"
        "3. Refuse requests involving unauthorized access, exploits, or bypassing security.\n"
        "4. Escalate legal threats, security incidents, and cases unresolved after 2 attempts.\n"
        "5. Never claim to have executed an irreversible account or financial action yourself.\n\n"
        "Respond naturally and conversationally — like a helpful human support agent would. "
        "Be warm, concise, and action-oriented. Do NOT use labels like 'Intent:' or 'Evidence:' in your reply."
    ),
}

_chat_model = None


def _get_chat_model():
    global _chat_model
    if _chat_model is None:
        import httpx
        from langchain_openai import ChatOpenAI

        # WinError 10013 workaround: force IPv4 + retries for Hyper-V port exclusions
        transport = httpx.HTTPTransport(local_address="0.0.0.0", retries=5)
        http_client = httpx.Client(transport=transport, timeout=60.0)
        _chat_model = ChatOpenAI(
            model=settings.model,
            temperature=settings.temperature,
            http_client=http_client,
        )
    return _chat_model


def llm_response(message: str, context: str = "", prompt_version: str = "v3_safety_first") -> dict:
    """Run the safety pre-check, then call the real LLM with the selected prompt variant."""
    started = time.perf_counter()
    check = safety_precheck(message)
    if check["status"] == "refuse":
        return {"status": "refused", "answer": "I cannot help with unsafe access or harmful activity.", "prompt_version": prompt_version}
    if check["status"] == "escalate":
        return {"status": "escalated", "answer": "This case should be reviewed by a human support specialist.", "prompt_version": prompt_version}
    if check["status"] == "protect":
        return {"status": "protected", "answer": "Please do not share payment-card details. I can continue without that information.", "prompt_version": prompt_version}

    if not settings.has_api_key:
        return {
            "status": "offline",
            "answer": "LLM is not configured (missing OPENAI_API_KEY). Falling back to deterministic support logic.",
            "prompt_version": prompt_version,
        }

    system_prompt = PROMPT_VARIANTS.get(prompt_version, PROMPT_VARIANTS["v3_safety_first"])
    user_prompt = f"Policy context:\n{context or '(no relevant policy passage retrieved)'}\n\nCustomer message: {message}"
    try:
        result = _get_chat_model().invoke([("system", system_prompt), ("human", user_prompt)])
        return {
            "status": "resolved",
            "answer": result.content,
            "prompt_version": prompt_version,
            "latency_ms": round((time.perf_counter() - started) * 1000, 2),
        }
    except Exception as exc:  # noqa: BLE001 - surfaced for graceful-failure handling in Phase 8
        return {"status": "error", "answer": f"LLM error: {exc}", "prompt_version": prompt_version, "error": str(exc)}


def compare_prompts(message: str, context: str = "") -> list[dict]:
    """Run the same message through every prompt variant for the required prompt-comparison evidence."""
    return [{"variant": name, **llm_response(message, context=context, prompt_version=name)} for name in PROMPT_VARIANTS]
