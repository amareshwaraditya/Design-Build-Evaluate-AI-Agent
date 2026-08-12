import streamlit as st
from src.planning import SessionMemory, decompose, run_agent_turn
from src.ui import chat_header, evaluation_box, phase_carousel, render_chat

st.set_page_config(page_title="Athena - Conversation Context", page_icon="🧩", layout="wide")
phase_carousel(6)
chat_header("Phase 6 — Athena now plans multi-part requests and remembers this conversation.")

if "phase6_memory" not in st.session_state:
    st.session_state.phase6_memory = SessionMemory()
memory: SessionMemory = st.session_state.phase6_memory


def _evidence(result: dict) -> None:
    sub_tasks = result.get("sub_tasks") or []
    extra = []
    if len(sub_tasks) > 1:
        extra.append("<b>Decomposed into:</b> " + " · ".join(f"<code>{s}</code>" for s in sub_tasks))
    extra.append(f"<b>Memory:</b> {len(memory.turns)} / {memory.max_turns} turns retained this session")
    evaluation_box(result, extra_lines=extra)


render_chat(
    session_key="phase6_chat",
    reply_fn=lambda msg: run_agent_turn(msg, memory=memory),
    evidence_fn=_evidence,
    placeholder="Try a multi-part request, e.g. 'Check order ORD-10001 and explain your warranty policy'",
    suggestions={
        "🧩 Multi-part request": "Check my order ORD-10001 and tell me whether it is under warranty",
        "📦 Simple follow-up": "My order is ORD-10001",
        "🔀 Triple intent": "What's the status of ORD-10001, what's your return policy, and is my warranty still valid?",
        "💬 Context test": "I asked about order ORD-10003 earlier — is it eligible for a refund?",
    },
)

if st.button("Reset session memory", icon=":material/restart_alt:"):
    memory.reset()
    st.session_state.phase6_chat = []
    st.success("Memory reset — a new customer session starts clean.")
    st.rerun()

with st.expander("Technical evidence: decomposition preview & memory bounds"):
    preview_message = st.text_input("Multi-intent request", "Check my order ORD-10001 and tell me whether it is under warranty")
    if st.button("Show plan"):
        for i, step in enumerate(decompose(preview_message), start=1):
            st.write(f"{i}. {step}")
    st.caption("Memory is bounded to the last N turns per session; reset explicitly clears it for a new customer conversation.")
