import hashlib
import re

UNSAFE_PATTERNS = ("hack", "exploit", "bypass security", "steal", "access another account")

def safety_precheck(text: str) -> dict:
    lowered = text.lower()
    if any(pattern in lowered for pattern in UNSAFE_PATTERNS):
        return {"status": "refuse", "reason": "unsafe request"}
    if re.search(r"\b(?:\d[ -]?){13,19}\b", text):
        return {"status": "protect", "reason": "payment-card data detected"}
    if any(word in lowered for word in ("sue", "lawyer", "legal action", "complaint")):
        return {"status": "escalate", "reason": "legal or high-risk language"}
    return {"status": "allow", "reason": "passed pre-check"}

def sanitize_for_log(text: str) -> str:
    def digest(value: str) -> str:
        return hashlib.sha256(value.encode()).hexdigest()[:10]
    text = re.sub(r"[\w.+-]+@[\w.-]+", lambda m: f"EMAIL_{digest(m.group())}", text)
    text = re.sub(r"\b(?:\+?\d[\d ()-]{8,}\d)\b", lambda m: f"PHONE_{digest(m.group())}", text)
    text = re.sub(r"\bORD-\d+\b", lambda m: f"ORDER_{digest(m.group())}", text, flags=re.I)
    return text
