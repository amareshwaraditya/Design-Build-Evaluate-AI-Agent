"""Phase 8 — Deployment & monitoring: latency/error capture, PII-safe logs, graceful degradation.

Integrates with LangSmith for production tracing when configured. Falls back gracefully
to local-only metrics when LangSmith is unavailable or API key is missing/invalid.
"""

import os
import time
import uuid
from contextlib import nullcontext

from .config import settings
from .safety import sanitize_for_log


def _langsmith_available() -> bool:
    """Check if LangSmith tracing is configured and enabled.

    Accepts both current LANGSMITH_* and legacy LANGCHAIN_* configuration names.
    Tracing is deliberately scoped to phases 8 and 9, rather than enabled globally.
    Used by Phase 8 (monitoring) and Phase 9 (evaluation) for conditional UI.
    """
    return (
        settings.langsmith_tracing_enabled
        and bool(os.getenv("LANGSMITH_API_KEY", os.getenv("LANGCHAIN_API_KEY", "")).strip())
    )


def langsmith_tracing_scope():
    """Return a context that enables tracing only for one monitored operation."""
    if not _langsmith_available():
        return nullcontext()
    try:
        from langchain_core.tracers.context import tracing_v2_enabled

        return tracing_v2_enabled(project_name=settings.langsmith_project)
    except ImportError:
        return nullcontext()


def run_with_langsmith_tracing(function, *args, **kwargs):
    """Run one Phase 8/9 operation with LangSmith tracing enabled."""
    with langsmith_tracing_scope():
        return function(*args, **kwargs)


def _get_langsmith_trace_url(run_id: str) -> str | None:
    """Attempt to retrieve the LangSmith trace URL for a given run.

    Returns None if LangSmith is unavailable or the lookup fails.
    """
    if not _langsmith_available():
        return None
    try:
        client = _langsmith_client()
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
        client = _langsmith_client()
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
        result = run_with_langsmith_tracing(function, message, **kwargs)
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


def _langsmith_client():
    """Create a client from either current LANGSMITH_* or legacy LANGCHAIN_* settings."""
    from langsmith import Client

    api_key = os.getenv("LANGSMITH_API_KEY", os.getenv("LANGCHAIN_API_KEY", ""))
    endpoint = os.getenv("LANGSMITH_ENDPOINT", os.getenv("LANGCHAIN_ENDPOINT", ""))
    return Client(api_key=api_key, api_url=endpoint or None)


def _latency_ms(run) -> float | None:
    """Read a run duration across LangSmith client/API response versions."""
    total_time = getattr(run, "total_time", None)
    if total_time is not None:
        if hasattr(total_time, "total_seconds"):
            return round(total_time.total_seconds() * 1000, 2)
        try:
            return round(float(total_time) * 1000, 2)
        except (TypeError, ValueError):
            pass

    start_time = getattr(run, "start_time", None)
    end_time = getattr(run, "end_time", None)
    if start_time is not None and end_time is not None:
        try:
            return round((end_time - start_time).total_seconds() * 1000, 2)
        except (AttributeError, TypeError):
            pass
    return None


def _start_time_display(run) -> str | None:
    """Format a LangSmith run start timestamp in the machine's local timezone."""
    start_time = getattr(run, "start_time", None)
    if start_time is None:
        return None
    try:
        return start_time.astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    except (AttributeError, ValueError, TypeError):
        return str(start_time)


def get_langsmith_project_runs(limit: int = 10) -> dict:
    """Fetch recent runs from the LangSmith project for dashboard display.

    Returns the runs or a safe diagnostic. Used by Phase 8 and Phase 9 dashboards.
    """
    if not _langsmith_available():
        return {"runs": None, "error": "LangSmith tracing is not enabled or its API key is missing."}
    try:
        client = _langsmith_client()
        runs = list(client.list_runs(
            project_name=settings.langsmith_project,
            limit=limit,
        ))
        normalized_runs = []
        for run in runs:
            try:
                run_url = client.get_run_url(run=run)
            except Exception:  # URL support varies across LangSmith client versions.
                run_url = None
            normalized_runs.append({
                "id": str(getattr(run, "id", "")),
                "name": getattr(run, "name", None),
                "status": getattr(run, "status", None),
                "start_time": _start_time_display(run),
                "latency_ms": _latency_ms(run),
                "total_tokens": getattr(run, "total_tokens", None),
                "error": getattr(run, "error", None),
                "url": run_url,
            })
        return {"runs": normalized_runs, "error": None}
    except Exception as exc:  # noqa: BLE001 - diagnostic is shown without sensitive details
        return {"runs": None, "error": f"Could not load LangSmith runs ({type(exc).__name__})."}
