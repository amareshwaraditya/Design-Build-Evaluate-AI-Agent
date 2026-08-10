"""Phase 9 — Evaluation & governance: run the real end-to-end agent against a fixed test suite."""
from .planning import run_agent_turn


def run_evaluation(cases: list[dict]) -> dict:
    results = []
    for case in cases:
        observed = run_agent_turn(case["input"])
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
        })
    passed = sum(r["pass"] for r in results)
    return {
        "total": len(results),
        "passed": passed,
        "score": round(passed / len(results) * 100, 2) if results else 0,
        "cases": results,
    }
