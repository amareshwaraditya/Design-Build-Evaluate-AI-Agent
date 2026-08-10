"""Phase 7 — Adaptive behaviour: explicit customer feedback adjusts tone/verbosity of the real agent."""
from .planning import run_agent_turn


class FeedbackPolicy:
    def __init__(self):
        self.ratings: list[int] = []

    def add(self, rating: int) -> None:
        self.ratings.append(max(1, min(5, rating)))

    def instructions(self) -> dict:
        recent = self.ratings[-10:]
        average = sum(recent) / len(recent) if recent else 3
        return {
            "tone": "empathetic" if average < 3 else "professional",
            "verbosity": "detailed" if average < 3 else "normal",
            "average": round(average, 2),
            "sample_size": len(recent),
        }


def before_after(message: str, policy: FeedbackPolicy) -> dict:
    """Show the same query answered before feedback (neutral) and after feedback (adapted), for evidence."""
    before = run_agent_turn(message, feedback={"tone": "professional"})
    after = run_agent_turn(message, feedback=policy.instructions())
    return {"before": before["answer"], "after": after["answer"], "policy": policy.instructions()}
