"""Phase 9 — Evaluation & governance: run the real end-to-end agent against a fixed test suite.

Supports LangSmith tracing when configured — each evaluation run is traced as a named project
run, enabling post-hoc analysis of token usage, latency distribution, and failure categorization.
Falls back gracefully to local-only evaluation when LangSmith is unavailable.
"""

import os
import time
import uuid

from .config import settings
from .observability import _langsmith_available, get_langsmith_project_runs, run_with_langsmith_tracing
from .planning import run_agent_turn


def _start_langsmith_eval_run(eval_id: str) -> None:
    """Inject LangSmith metadata for an evaluation run (non-blocking, best-effort)."""
    if _langsmith_available():
        os.environ["LANGCHAIN_RUN_ID"] = eval_id
        os.environ.setdefault("LANGCHAIN_PROJECT", settings.langsmith_project)


def _end_langsmith_eval_run() -> None:
    """Clean up LangSmith run ID to avoid leaking across requests."""
    os.environ.pop("LANGCHAIN_RUN_ID", None)


def run_evaluation(cases: list[dict]) -> dict:
    """Execute the full evaluation suite against the live agent pipeline.

    Each test case is run through the same `run_agent_turn` pipeline used in production.
    Results include pass/fail status, observed vs. expected comparison, and timing.

    When LangSmith is configured, evaluation runs are traced for post-hoc analysis.

    Args:
        cases: List of test case dicts with keys: id, category, input, expected_status, expected_keywords.

    Returns:
        Dict with keys: total, passed, score, cases (detailed per-case results),
        duration_ms, langsmith_enabled, langsmith_project.
    """
    eval_start = time.perf_counter()
    eval_id = str(uuid.uuid4())
    langsmith_enabled = _langsmith_available()

    results = []
    for case in cases:
        case_start = time.perf_counter()

        # Inject LangSmith tracing per-case (best-effort)
        if langsmith_enabled:
            _start_langsmith_eval_run(str(uuid.uuid4()))

        try:
            observed = run_with_langsmith_tracing(run_agent_turn, case["input"])
        except Exception as exc:  # noqa: BLE001
            # Graceful degradation: if the agent crashes on a test case, record it as failure
            observed = {"status": "error", "answer": f"Agent error: {type(exc).__name__}"}
        finally:
            _end_langsmith_eval_run()

        case_latency = round((time.perf_counter() - case_start) * 1000, 2)

        status_ok = observed["status"] == case["expected_status"]
        keywords = case.get("expected_keywords", [])
        answer_lower = observed["answer"].lower()
        keyword_ok = all(k.lower() in answer_lower for k in keywords) if keywords else True

        results.append({
            "id": case["id"],
            "category": case.get("category", "general"),
            "input": case["input"],
            "expected_status": case["expected_status"],
            "observed_status": observed["status"],
            "answer": observed["answer"],
            "status_match": status_ok,
            "keyword_match": keyword_ok,
            "pass": status_ok and keyword_ok,
            "latency_ms": case_latency,
        })

    passed = sum(r["pass"] for r in results)
    total_duration = round((time.perf_counter() - eval_start) * 1000, 2)

    return {
        "total": len(results),
        "passed": passed,
        "score": round(passed / len(results) * 100, 2) if results else 0,
        "cases": results,
        "duration_ms": total_duration,
        "langsmith_enabled": langsmith_enabled,
        "langsmith_project": settings.langsmith_project if langsmith_enabled else None,
    }


def get_evaluation_summary(eval_result: dict) -> dict:
    """Generate a structured summary of evaluation results for governance reporting.

    Args:
        eval_result: Output from run_evaluation().

    Returns:
        Dict with category-level breakdown, failure analysis, and SLA metrics.
    """
    cases = eval_result.get("cases", [])
    if not cases:
        return {"error": "No evaluation cases to summarize"}

    # Category breakdown
    categories: dict[str, dict] = {}
    for case in cases:
        cat = case["category"]
        if cat not in categories:
            categories[cat] = {"total": 0, "passed": 0, "failed_ids": []}
        categories[cat]["total"] += 1
        if case["pass"]:
            categories[cat]["passed"] += 1
        else:
            categories[cat]["failed_ids"].append(case["id"])

    # Latency stats
    latencies = [c["latency_ms"] for c in cases if c.get("latency_ms")]
    avg_latency = round(sum(latencies) / len(latencies), 2) if latencies else 0
    max_latency = max(latencies) if latencies else 0
    sla_violations = sum(1 for l in latencies if l > 3000)

    return {
        "overall_score": eval_result["score"],
        "total_cases": eval_result["total"],
        "passed": eval_result["passed"],
        "failed": eval_result["total"] - eval_result["passed"],
        "categories": {
            cat: {
                "score": round(data["passed"] / data["total"] * 100, 1),
                "passed": data["passed"],
                "total": data["total"],
                "failures": data["failed_ids"],
            }
            for cat, data in categories.items()
        },
        "latency": {
            "average_ms": avg_latency,
            "max_ms": max_latency,
            "sla_violations_3s": sla_violations,
        },
        "langsmith_enabled": eval_result.get("langsmith_enabled", False),
        "duration_ms": eval_result.get("duration_ms", 0),
    }
