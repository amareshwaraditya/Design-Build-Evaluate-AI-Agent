from pathlib import Path


def load_policy_documents(root: str = "knowledge_base") -> list[dict]:
    return [{"source": path.name, "text": path.read_text(encoding="utf-8")} for path in sorted(Path(root).glob("*.md"))]

def retrieve(query: str, documents: list[dict], top_k: int = 3) -> list[dict]:
    terms = set(query.lower().split())
    scored = []
    for document in documents:
        score = sum(term in document["text"].lower() for term in terms)
        scored.append((score, document))
    return [document for score, document in sorted(scored, key=lambda item: item[0], reverse=True)[:top_k] if score > 0]
