import streamlit as st
from src.llm_agent import llm_response
from src.rag import load_policy_documents, retrieve
from src.ui import chat_header, evaluation_box, phase_carousel, render_chat

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


def _phase4_insights(result: dict) -> list[str]:
    """Generate success/limitation notes for Phase 4 evaluation box."""
    sources = result.get("sources") or []
    source_names = ", ".join(sorted({p["source"] for p in sources})) if sources else "none"
    extra = [f"<b>Retrieved from:</b> {source_names}"]
    status = result.get("status", "resolved")

    # Success indicators
    if sources:
        extra.append(f"<b>✓ Success:</b> Answer grounded in {len(sources)} policy passage(s) — not hallucinated")
    elif status == "refused":
        extra.append("<b>✓ Success:</b> Unsafe request refused at safety pre-check (RAG not needed)")
    else:
        extra.append("<b>⚠ Note:</b> No relevant policy passages retrieved — answer may lack grounding")

    # Phase 4 limitations
    limitations = []
    if status == "resolved":
        limitations.append("No tool verification — cannot confirm real order/warranty status (→ Phase 5 Tools)")
        limitations.append("No conversation memory — cannot reference previous questions (→ Phase 6 Memory)")
        limitations.append("No tone adaptation based on customer satisfaction (→ Phase 7 Feedback)")

    if limitations:
        extra.append("<b>Phase 4 gaps:</b> " + "; ".join(limitations))
    return extra


def _evidence(result: dict) -> None:
    sources = result.get("sources") or []
    evaluation_box(result, extra_lines=_phase4_insights(result))
    if sources:
        with st.expander("Show retrieved passages"):
            for p in sources:
                st.markdown(f"**{p['source']}**")
                st.write(p["text"])


render_chat(
    session_key="phase4_chat",
    reply_fn=_reply,
    evidence_fn=_evidence,
    placeholder="Ask about a policy — e.g. returns, warranty, shipping, or account rules",
    suggestions={
        "📦 Late return": "Can I return order ORD-10002? I bought it 45 days ago.",
        "🔧 Warranty coverage": "What does the standard warranty cover?",
        "🚚 Shipping policy": "Do you offer free shipping, and how long does delivery take?",
        "🔒 Account security": "What happens if I forget my password — how do I reset it?",
    },
)

with st.expander("Technical evidence: retrieval quality & with/without comparison"):
    query = st.text_input("Search the knowledge base directly", "Can I return an item after 30 days?")
    if st.button("Retrieve policy passages"):
        st.markdown(
            '<div style="border: 2px solid #16a34a; border-radius: 0.5rem; padding: 1rem; margin: 0.5rem 0;">',
            unsafe_allow_html=True,
        )
        for match in retrieve(query, top_k=3):
            st.markdown(f"**{match['source']}** (distance {match.get('distance', '—')})")
            st.write(match["text"])
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("**Compare: answer without retrieval vs. with retrieval**")
    compare_message = st.text_input("Grounded question", "Can I return order ORD-10001 after purchase?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Answer WITHOUT retrieval"):
            result = llm_response(compare_message, context="")
            st.markdown(
                '<div style="border: 2px solid #16a34a; border-radius: 0.5rem; padding: 1rem; margin: 0.5rem 0;">',
                unsafe_allow_html=True,
            )
            st.markdown("**Without RAG (ungrounded)**")
            st.write(result.get("answer", ""))
            st.caption(f"Status: {result.get('status')} | Sources: none")
            st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        if st.button("Answer WITH retrieval"):
            result = _reply(compare_message)
            sources = result.get("sources") or []
            source_names = ", ".join(sorted({p["source"] for p in sources}))
            st.markdown(
                '<div style="border: 2px solid #16a34a; border-radius: 0.5rem; padding: 1rem; margin: 0.5rem 0;">',
                unsafe_allow_html=True,
            )
            st.markdown("**With RAG (grounded)**")
            st.write(result.get("answer", ""))
            st.caption(f"Status: {result.get('status')} | Sources: {source_names}")
            st.markdown("</div>", unsafe_allow_html=True)
