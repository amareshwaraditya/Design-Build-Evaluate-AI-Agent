from __future__ import annotations

import hashlib
import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "phase2_baseline.jsonl"
logging.basicConfig(filename=LOG_DIR / "phase2_baseline.log", level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

@dataclass
class ChatTurn:
    user: str
    assistant: str
    intent: str
    timestamp: str

@dataclass
class BaselineChatbot:
    turns: list[ChatTurn] = field(default_factory=list)

    def classify(self, message: str) -> str:
        text = message.lower()
        if any(word in text for word in ("hack", "exploit", "steal", "bypass security")):
            return "unsafe"
        if any(word in text for word in ("lawyer", "legal action", "sue", "attorney", "complaint")):
            return "escalation"
        rules = {
            "return_refund": ("refund", "return", "money back", "reimburse"),
            "shipping": ("shipping", "delivery", "track", "tracking", "package", "shipped"),
            "warranty": ("warranty", "broken", "defective", "repair", "replacement"),
            "password": ("password", "login", "locked out", "reset"),
            "cancellation": ("cancel", "subscription", "unsubscribe"),
        }
        for intent, keywords in rules.items():
            if any(keyword in text for keyword in keywords):
                return intent
        return "unknown"

    def respond(self, message: str) -> str:
        intent = self.classify(message)
        responses = {
            "return_refund": "Our standard policy supports eligible returns within 30 days. Items should meet the documented condition requirements. I can explain the process, but this baseline cannot create a return or approve a refund.",
            "shipping": "We offer standard, express, and next-day shipping options. Please provide an order number for an order-specific status check.",
            "warranty": "Products may have limited warranty coverage for manufacturing defects. Please provide an order number and describe the issue.",
            "password": "Use the account password-reset flow and never share your password with support. A human agent can help if the reset flow fails.",
            "cancellation": "I can explain the cancellation process, but this baseline cannot change subscriptions or execute account actions.",
            "unsafe": "I cannot help with unauthorized access, exploitation, or harmful activity. Please ask a legitimate support question.",
            "escalation": "This request should be reviewed by a human support specialist. I will not make a high-risk decision automatically.",
            "unknown": "I could not classify that request using the baseline rules. Please ask about a return, refund, delivery, warranty, password, or cancellation.",
        }
        response = responses[intent]
        turn = ChatTurn(message, response, intent, datetime.now(timezone.utc).isoformat())
        self.turns.append(turn)
        self._log(turn)
        return response

    def _log(self, turn: ChatTurn) -> None:
        def token(value: str) -> str:
            return hashlib.sha256(value.encode()).hexdigest()[:10]
        sanitized = re.sub(r"[\w.+-]+@[\w.-]+", lambda match: f"EMAIL_{token(match.group())}", turn.user)
        sanitized = re.sub(r"\bORD-\d+\b", lambda match: f"ORDER_{token(match.group())}", sanitized, flags=re.I)
        record = {"timestamp": turn.timestamp, "intent": turn.intent, "user_hash": token(sanitized), "turn_number": len(self.turns)}
        with LOG_FILE.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record) + "\n")
        logging.info("Phase 2 interaction=%s intent=%s", len(self.turns), turn.intent)

    def summary(self) -> dict:
        counts: dict[str, int] = {}
        for turn in self.turns:
            counts[turn.intent] = counts.get(turn.intent, 0) + 1
        return {"interactions": len(self.turns), "intent_counts": counts}


def limitation_tests() -> list[dict]:
    chatbot = BaselineChatbot()
    cases = [
        {"label": "Multi-intent limitation", "input": "I want a refund and also need to track another order", "expected": "Both refund and tracking should be addressed"},
        {"label": "Natural-language limitation", "input": "My earbuds keep disconnecting every few minutes", "expected": "Troubleshooting should be identified"},
        {"label": "Context limitation", "input": "What about express shipping?", "expected": "Requires context from a previous turn"},
        {"label": "Policy-reasoning limitation", "input": "My screen cracked after three days; can I get a refund?", "expected": "Physical-damage policy should be checked"},
    ]
    results = []
    for case in cases:
        results.append({**case, "actual_intent": chatbot.classify(case["input"]), "actual_response": chatbot.respond(case["input"])})
    return results
