"""Phase 4 — Embeddings & semantic retrieval: real OpenAI embeddings in a FAISS vector store.

Provides semantic search over the Tech Gadgets Inc. knowledge base. Falls back to
keyword-overlap search when the OpenAI embedding API is unavailable.
"""

from pathlib import Path

from .config import settings

_INDEX_CACHE: dict[str, object] = {}
_RETRIEVAL_STATUS: dict[str, dict[str, object]] = {}


def load_policy_documents(root: str = "knowledge_base") -> list[dict]:
    """Load all markdown policy documents from the knowledge base directory.

    Args:
        root: Path to the knowledge base directory.

    Returns:
        List of dicts with 'source' (filename) and 'text' (content).
        Returns empty list if directory does not exist.
    """
    root_path = Path(root)
    if not root_path.exists():
        return []
    return [{"source": path.name, "text": path.read_text(encoding="utf-8")} for path in sorted(root_path.glob("*.md"))]


def _build_index(root: str):
    if root in _INDEX_CACHE:
        return _INDEX_CACHE[root]
    from langchain_community.vectorstores import FAISS
    from langchain_core.documents import Document
    from langchain_openai import OpenAIEmbeddings
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=80)
    chunks = []
    for item in load_policy_documents(root):
        for piece in splitter.split_text(item["text"]):
            chunks.append(Document(page_content=piece, metadata={"source": item["source"]}))
    index = FAISS.from_documents(chunks, OpenAIEmbeddings(model=settings.embedding_model))
    _INDEX_CACHE[root] = index
    _RETRIEVAL_STATUS[root] = {
        "mode": "faiss",
        "chunk_count": len(chunks),
        "model": settings.embedding_model,
    }
    return index


def retrieval_status(root: str = "knowledge_base") -> dict[str, object]:
    """Return the current retrieval mode for UI status reporting."""
    if root in _INDEX_CACHE:
        return _RETRIEVAL_STATUS[root]
    if not settings.has_api_key:
        return {"mode": "keyword", "reason": "OpenAI API key is not configured"}
    return {"mode": "pending"}


def retrieve(query: str, documents: list[dict] | None = None, top_k: int = 3, root: str = "knowledge_base") -> list[dict]:
    """Semantic search over the knowledge base. Returns [] when nothing is relevant enough (no guessing)."""
    if not settings.has_api_key:
        _RETRIEVAL_STATUS[root] = {"mode": "keyword", "reason": "OpenAI API key is not configured"}
        return _keyword_fallback(query, documents or load_policy_documents(root), top_k)
    try:
        index = _build_index(root)
        matches = index.similarity_search_with_score(query, k=top_k)
        return [
            {"source": doc.metadata["source"], "text": doc.page_content, "distance": round(float(score), 4)}
            for doc, score in matches
        ]
    except Exception as exc:
        _RETRIEVAL_STATUS[root] = {"mode": "keyword", "reason": type(exc).__name__}
        return _keyword_fallback(query, documents or load_policy_documents(root), top_k)


def _keyword_fallback(query: str, documents: list[dict], top_k: int) -> list[dict]:
    """Deterministic term-overlap search used only when embeddings are unavailable (graceful degradation)."""
    terms = set(query.lower().split())
    scored = []
    for document in documents:
        score = sum(term in document["text"].lower() for term in terms)
        scored.append((score, document))
    return [document for score, document in sorted(scored, key=lambda item: item[0], reverse=True)[:top_k] if score > 0]
