"""Phase 7 — Adaptive behaviour: explicit customer feedback adjusts tone/verbosity of the real agent.

Implements a rolling-window feedback policy that maps star ratings to tone instructions.
The before/after comparison demonstrates the effect of tone parameters on the same query.
"""

from .planning import run_agent_turn


class FeedbackPolicy:
    """Rolling-window feedback tracker that determines tone/verbosity for the agent.

    Maintains the last 10 ratings and computes a running average to select
    between empathetic (low ratings) and professional (high ratings) tone.
    """

    def __init__(self):
        self.ratings: list[int] = []

    def add(self, rating: int) -> None:
        """Record a customer satisfaction rating (clamped to 1-5)."""
        self.ratings.append(max(1, min(5, rating)))

    def instructions(self) -> dict:
        """Compute current tone instructions from the rolling average.

        Returns:
            Dict with tone, verbosity, average, and sample_size.
        """
        recent = self.ratings[-10:]
        average = sum(recent) / len(recent) if recent else 3
        return {
            "tone": "empathetic" if average < 3 else "professional",
            "verbosity": "detailed" if average < 3 else "normal",
            "average": round(average, 2),
            "sample_size": len(recent),
        }


def before_after(message: str, policy: FeedbackPolicy) -> dict:
    """Show the same query answered with contrasting tones to demonstrate adaptation.

    Always uses a clear contrast: professional/concise vs empathetic/detailed,
    so the comparison is meaningful regardless of current feedback state.
    Falls back gracefully if one or both LLM calls fail.

    Args:
        message: The customer query to demonstrate tone contrast on.
        policy: The current FeedbackPolicy instance.

    Returns:
        Dict with before/after answers, tone labels, and current policy state.
    """
    try:
        before = run_agent_turn(message, feedback={"tone": "professional", "verbosity": "concise"})
        before_answer = before.get("answer", "Unable to generate response.")
    except Exception:  # noqa: BLE001
        before_answer = "(Professional tone response unavailable — LLM error)"

    try:
        after = run_agent_turn(message, feedback={"tone": "empathetic", "verbosity": "detailed"})
        after_answer = after.get("answer", "Unable to generate response.")
    except Exception:  # noqa: BLE001
        after_answer = "(Empathetic tone response unavailable — LLM error)"

    return {
        "before": before_answer,
        "after": after_answer,
        "before_tone": "professional + concise",
        "after_tone": "empathetic + detailed",
        "current_policy": policy.instructions(),
    }
