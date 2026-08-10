import streamlit as st
from src.llm_agent import llm_response
from src.rag import load_policy_documents, retrieve
from src.ui import chat_header, phase_carousel, render_chat

st.set_page_config(page_title="Athena - Company Knowledge", page_icon="📚", layout="wide")
phase_carousel(4)
chat_header("Phase 4 — Athena now grounds answers in Tech Gadgets Inc. policy via FAISS + OpenAI embeddings.")

docs = load_policy_documents()
st.caption(f"{len(docs)} knowledge-base documents indexed (`knowledge_base/*.md`).")


def _reply(message: str) -> dict:
    passages = retrieve(message, top_k=3)
    context = "\n\n".join(f"[{p['source']}] {p['text']}" for p in passages)
    result = llm_response(message, context=context)
    result["sources"] = passages
    return result


def _evidence(result: dict) -> None:
    sources = result.get("sources") or []
    if sources:
        st.caption("Retrieved from: " + ", ".join(sorted({p["source"] for p in sources})))
        with st.expander("Show retrieved passages"):
            for p in sources:
                st.markdown(f"**{p['source']}**")
                st.write(p["text"])
    else:
        st.caption("No relevant policy passage retrieved — Athena said so instead of guessing.")


render_chat(
    session_key="phase4_chat",
    reply_fn=_reply,
    evidence_fn=_evidence,
    placeholder="Ask about a policy — e.g. returns, warranty, shipping, or account rules",
    suggestions={
        "📦 Late return": "Can I return order ORD-10002? I bought it 45 days ago.",
        "🔧 Warranty coverage": "What does the standard warranty cover?",
    },
)

with st.expander("Technical evidence: retrieval quality & with/without comparison"):
    query = st.text_input("Search the knowledge base directly", "Can I return an item after 30 days?")
    if st.button("Retrieve policy passages"):
        for match in retrieve(query, top_k=3):
            st.markdown(f"**{match['source']}** (distance {match.get('distance', '—')})")
            st.write(match["text"])
    st.markdown("**Compare: answer without retrieval vs. with retrieval**")
    compare_message = st.text_input("Grounded question", "Can I return order ORD-10001 after purchase?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Answer WITHOUT retrieval"):
            st.json(llm_response(compare_message, context=""))
    with col2:
        if st.button("Answer WITH retrieval"):
            st.json(_reply(compare_message))
