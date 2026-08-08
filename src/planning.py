def decompose(message: str) -> list[str]:
    parts = [part.strip() for part in message.replace(" and ", "|").split("|") if part.strip()]
    return parts or [message]

class SessionMemory:
    def __init__(self, max_turns: int = 10):
        self.max_turns = max_turns
        self.turns = []
    def add(self, user: str, assistant: str):
        self.turns.append({"user": user, "assistant": assistant})
        self.turns = self.turns[-self.max_turns:]
    def reset(self):
        self.turns.clear()
