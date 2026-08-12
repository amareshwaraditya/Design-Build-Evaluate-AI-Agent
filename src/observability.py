"""Phase 8 — Deployment & monitoring: latency/error capture, PII-safe logs, graceful degradation.

Integrates with LangSmith for production tracing when configured. Falls back gracefully
to local-only metrics when LangSmith is unavailable or API key is missing/invalid.
"""

import os
import time
import uuid

from .config import settings
from .safety import sanitize_for_log


def _langsmith_available() -> bool:
    """Check if LangSmith tracing is configured and enabled.

    Requires both LANGCHAIN_TRACING_V2=true and a non-empty LANGCHAIN_API_KEY.
    Used by Phase 8 (monitoring) and Phase 9 (evaluation) for conditional UI.
    """
    return (
        os.getenv("LANGCHAIN_TRACING_V2", "").lower() == "true"
        and bool(os.getenv("LANGCHAIN_API_KEY", "").strip())
    )


def _get_langsmith_trace_url(run_id: str) -> str | None:
    """Attempt to retrieve the LangSmith trace URL for a given run.

    Returns None if LangSmith is unavailable or the lookup fails.
    """
    if not _langsmith_available():
        return None
    try:
        from langsmith import Client
        client = Client()
        run = client.read_run(run_id)
        return run.url if run else None
    except Exception:
        return None


def _get_langsmith_run_stats(run_id: str) -> dict | None:
    """Retrieve token usage and cost from LangSmith for a traced run.

    Returns None if LangSmith is unavailable or lookup fails.
    """
    if not _langsmith_available():
        return None
    try:
        from langsmith import Client
        client = Client()
        run = client.read_run(run_id)
        if run:
            return {
                "total_tokens": run.total_tokens or 0,
                "prompt_tokens": run.prompt_tokens or 0,
                "completion_tokens": run.completion_tokens or 0,
                "total_cost": getattr(run, "total_cost", None),
            }
        return None
    except Exception:
        return None


def traced_run(function, message: str, **kwargs) -> dict:
    """Execute an agent function with full observability instrumentation.

    Captures: latency, PII-sanitized logs, LangSmith trace (if configured).
    Falls back to deterministic support logic if the live call fails.

    Args:
        function: Callable(message, **kwargs) -> dict with at least "answer" key.
        message: The customer's input message.
        **kwargs: Additional arguments forwarded to the function.

    Returns:
        Dict with keys: result, latency_ms, logged_message, error, trace_url, langsmith_stats.
    """
    started = time.perf_counter()
    run_id = str(uuid.uuid4())

    # Inject LangSmith run ID as metadata if tracing is enabled
    if _langsmith_available():
        os.environ.setdefault("LANGCHAIN_RUN_ID", run_id)

    try:
        result = function(message, **kwargs)
        if isinstance(result, dict) and result.get("status") == "error":
            raise RuntimeError(result.get("error", "live agent error"))

        latency_ms = round((time.perf_counter() - started) * 1000, 2)

        # Attempt to retrieve LangSmith trace info (non-blocking)
        trace_url = _get_langsmith_trace_url(run_id)
        langsmith_stats = _get_langsmith_run_stats(run_id)

        return {
            "result": result,
            "latency_ms": latency_ms,
            "logged_message": sanitize_for_log(message),
            "error": None,
            "trace_url": trace_url,
            "langsmith_stats": langsmith_stats,
            "langsmith_enabled": _langsmith_available(),
        }
    except Exception as exc:  # noqa: BLE001
        # Graceful degradation: never surface raw errors to the customer
        from .runtime import answer as fallback_answer

        fallback = fallback_answer(message)
        return {
            "result": {"status": "degraded", "answer": fallback["response"]},
            "latency_ms": round((time.perf_counter() - started) * 1000, 2),
            "logged_message": sanitize_for_log(message),
            "error": f"sanitized_runtime_error: {type(exc).__name__}",
            "trace_url": None,
            "langsmith_stats": None,
            "langsmith_enabled": _langsmith_available(),
        }
    finally:
        # Clean up injected run ID to avoid leaking across requests
        os.environ.pop("LANGCHAIN_RUN_ID", None)


def get_langsmith_project_runs(limit: int = 10) -> list[dict] | None:
    """Fetch recent runs from the LangSmith project for dashboard display.

    Returns None if LangSmith is unavailable. Used by Phase 9 for evaluation context.
    """
    if not _langsmith_available():
        return None
    try:
        from langsmith import Client
        client = Client()
        runs = list(client.list_runs(
            project_name=settings.langsmith_project,
            limit=limit,
        ))
        return [
            {
                "id": str(run.id),
                "name": run.name,
                "status": run.status,
                "latency_ms": round(run.total_time * 1000, 2) if run.total_time else None,
                "total_tokens": run.total_tokens,
                "error": run.error,
                "url": run.url,
            }
            for run in runs
        ]
    except Exception:
        return None
