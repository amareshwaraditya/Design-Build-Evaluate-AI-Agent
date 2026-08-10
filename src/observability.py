"""Phase 8 — Deployment & monitoring: latency/error capture, PII-safe logs, graceful degradation."""
import time

from .config import settings
from .safety import sanitize_for_log


def traced_run(function, message: str, **kwargs) -> dict:
    """Run `function(message, **kwargs)`, capturing latency and falling back to deterministic
    support logic if the live call fails (e.g. LLM outage) instead of showing an error to the customer."""
    started = time.perf_counter()
    try:
        result = function(message, **kwargs)
        if isinstance(result, dict) and result.get("status") == "error":
            raise RuntimeError(result.get("error", "live agent error"))
        return {
            "result": result,
            "latency_ms": round((time.perf_counter() - started) * 1000, 2),
            "logged_message": sanitize_for_log(message),
            "error": None,
            "tracing_enabled": settings.langsmith_project is not None,
        }
    except Exception as exc:  # noqa: BLE001 - graceful fallback, never surface raw errors to the customer
        from .runtime import answer as fallback_answer

        fallback = fallback_answer(message)
        return {
            "result": {"status": "degraded", "answer": fallback["response"]},
            "latency_ms": round((time.perf_counter() - started) * 1000, 2),
            "logged_message": sanitize_for_log(message),
            "error": f"sanitized_runtime_error: {type(exc).__name__}",
        }
