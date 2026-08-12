"""Phase 6 — Planning, memory & context: multi-intent decomposition plus a bounded conversation buffer."""
from .config import settings
from .rag import retrieve
from .safety import safety_precheck


def decompose(message: str) -> list[str]:
    """Split a multi-intent request into sub-tasks. Uses the LLM when available, else a heuristic split."""
    if settings.has_api_key:
        try:
            from langchain_openai import ChatOpenAI

            model = ChatOpenAI(model=settings.model, temperature=0)
            prompt = (
                "A support request is 'multi-intent' only if it asks about two or more DIFFERENT topics "
                "(e.g. order status AND warranty AND refund). Restating, clarifying, or adding a supporting "
                "fact (dates, order numbers, symptoms) about the SAME single topic is still one request — "
                "do not split those, even if it is written as two sentences.\n\n"
                "Worked examples (Output is exactly what you must return, nothing else):\n\n"
                "Input: Check my order and explain your warranty policy\n"
                "Output:\n"
                "Check my order\n"
                "Explain your warranty policy\n\n"
                "Input: Someone made unauthorized purchases on my account, I did not make them\n"
                "Output:\n"
                "Someone made unauthorized purchases on my account, I did not make them\n\n"
                "Input: Can I return order ORD-10002? I bought it 45 days ago.\n"
                "Output:\n"
                "Can I return order ORD-10002? I bought it 45 days ago.\n\n"
                "Now split the message below the same way. Return ONLY the resulting line(s) — no labels, "
                "no numbering, no explanation.\n\n"
                f"Input: {message}\n"
                "Output:"
            )
            result = model.invoke([("human", prompt)])
            parts = [line.strip("- ").strip() for line in result.content.splitlines() if line.strip()]
            if parts:
                return parts
        except Exception:
            pass
    parts = [part.strip() for part in message.replace(" and ", "|").split("|") if part.strip()]
    return parts or [message]


class SessionMemory:
    """Session-scoped rolling buffer of the last N complete turns (bounded, explicit reset)."""

    def __init__(self, max_turns: int = 10):
        self.max_turns = max_turns
        self.turns: list[dict] = []

    def add(self, user: str, assistant: str) -> None:
        self.turns.append({"user": user, "assistant": assistant})
        self.turns = self.turns[-self.max_turns :]

    def reset(self) -> None:
        self.turns.clear()

    def as_chat_history(self) -> str:
        return "\n".join(f"Customer: {t['user']}\nAthena: {t['assistant']}" for t in self.turns)


def run_agent_turn(message: str, memory: "SessionMemory | None" = None, feedback: dict | None = None) -> dict:
    """The full pipeline: safety -> decomposition -> per-intent RAG + tool-calling answer -> memory update."""
    from .mcp_tools import run_tool_agent

    check = safety_precheck(message)
    if check["status"] != "allow":
        outcome = {"refuse": ("refused", "I cannot help with unsafe access or harmful activity."),
                   "escalate": ("escalated", "This case has been identified as high risk and should be reviewed by a human support specialist."),
                   "protect": ("protected", "Please do not share payment-card details. I can continue without them.")}[check["status"]]
        status, answer = outcome
        if memory is not None:
            memory.add(message, answer)
        return {"status": status, "answer": answer, "sub_tasks": [message]}

    sub_tasks = decompose(message)
    answers = []
    for sub_task in sub_tasks:
        passages = retrieve(sub_task, top_k=2)
        context = "\n\n".join(f"[{p['source']}] {p['text']}" for p in passages)
        response = run_tool_agent(sub_task, context=context, feedback=feedback)
        answers.append({
            "sub_task": sub_task,
            "status": response["status"],
            "answer": response["answer"],
            "sources": [p["source"] for p in passages],
            "tool_trace": response.get("trace", []),
        })

    combined = "\n\n".join(f"- {a['answer']}" for a in answers)
    if memory is not None:
        memory.add(message, combined)
    overall_status = next((a["status"] for a in answers if a["status"] != "resolved"), "resolved")
    return {"status": overall_status, "answer": combined, "sub_tasks": sub_tasks, "details": answers}
