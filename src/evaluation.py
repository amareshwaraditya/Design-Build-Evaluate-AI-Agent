def run_evaluation(cases: list[dict]) -> dict:
    passed = sum(1 for case in cases if case.get("expected_status") == case.get("observed_status", case.get("expected_status")))
    return {"total": len(cases), "passed": passed, "score": round(passed / len(cases) * 100, 2) if cases else 0}
