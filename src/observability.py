import time
from .safety import sanitize_for_log

def traced_run(function, message: str, **kwargs):
    started = time.perf_counter()
    try:
        result = function(message, **kwargs)
        return {"result": result, "latency_ms": round((time.perf_counter() - started) * 1000, 2), "logged_message": sanitize_for_log(message), "error": None}
    except Exception:
        return {"result": {"status": "error", "answer": "The service is temporarily unavailable. Please contact a human agent."}, "latency_ms": round((time.perf_counter() - started) * 1000, 2), "logged_message": sanitize_for_log(message), "error": "sanitized_runtime_error"}
