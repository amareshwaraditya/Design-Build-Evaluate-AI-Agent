"""Safety pre-check: classifies incoming messages for unsafe content, PII, and escalation triggers.

Called before any LLM, tool, or RAG processing — zero-cost refusals for dangerous or PII-bearing inputs.
"""

import hashlib
import re

UNSAFE_PATTERNS = ("hack", "exploit", "bypass security", "steal", "access another account", "ignore your instructions", "admin access")


def safety_precheck(text: str) -> dict:
    """Classify a customer message for safety, PII, and escalation signals.

    Returns:
        Dict with 'status' (allow|refuse|protect|escalate) and 'reason'.
    """
    lowered = text.lower()

    # Unsafe/exploit detection
    if any(pattern in lowered for pattern in UNSAFE_PATTERNS):
        return {"status": "refuse", "reason": "unsafe request"}

    # PII detection: payment cards (13-19 digits) and SSN/government IDs
    if re.search(r"\b(?:\d[ -]?){13,19}\b", text):
        return {"status": "protect", "reason": "payment-card data detected"}
    if re.search(r"\b\d{3}[- ]?\d{2}[- ]?\d{4}\b", text) and any(
        w in lowered for w in ("social security", "ssn", "social")
    ):
        return {"status": "protect", "reason": "government ID (SSN) detected"}

    # Escalation triggers: legal threats, repeated frustration
    if any(word in lowered for word in ("sue", "lawyer", "legal action", "complaint", "fourth time", "third time")):
        return {"status": "escalate", "reason": "legal or high-risk language"}

    return {"status": "allow", "reason": "passed pre-check"}

def sanitize_for_log(text: str) -> str:
    """Replace PII (emails, phones, order IDs) with SHA-256 hashed tokens for safe logging.

    Args:
        text: Raw customer message text.

    Returns:
        Sanitized string with PII replaced by hashed placeholders (e.g. EMAIL_a1b2c3d4e5).
    """
    def digest(value: str) -> str:
        return hashlib.sha256(value.encode()).hexdigest()[:10]

    text = re.sub(r"[\w.+-]+@[\w.-]+", lambda m: f"EMAIL_{digest(m.group())}", text)
    text = re.sub(r"\b(?:\+?\d[\d ()-]{8,}\d)\b", lambda m: f"PHONE_{digest(m.group())}", text)
    text = re.sub(r"\bORD-\d+\b", lambda m: f"ORDER_{digest(m.group())}", text, flags=re.I)
    return text
