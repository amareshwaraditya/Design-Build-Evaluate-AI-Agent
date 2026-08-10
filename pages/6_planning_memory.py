import streamlit as st
from src.planning import SessionMemory, decompose, run_agent_turn

st.title("Phase 6 — Athena Uses Conversation Context")
st.write("Athena now decomposes multi-intent requests and keeps a bounded, session-scoped memory across turns.")

st.subheader("Decomposition preview")
preview_message = st.text_input("Multi-intent request", "Check my order ORD-10001 and tell me whether it is under warranty")
if st.button("Show plan"):
    for i, step in enumerate(decompose(preview_message), start=1):
        st.write(f"{i}. {step}")

st.subheader("Full conversation (planning + RAG + tools + memory)")
if "memory" not in st.session_state:
    st.session_state.memory = SessionMemory()
memory: SessionMemory = st.session_state.memory

for turn in memory.turns:
    st.chat_message("user").write(turn["user"])
    st.chat_message("assistant").write(turn["assistant"])

message = st.chat_input("Tell Athena how she can help")
if message:
    with st.spinner("Athena is planning and responding..."):
        run_agent_turn(message, memory=memory)
    st.rerun()

col1, col2 = st.columns(2)
with col1:
    st.write(f"Stored turns: {len(memory.turns)} / {memory.max_turns}")
with col2:
    if st.button("Reset session memory"):
        memory.reset()
        st.success("Memory reset completed — a new customer session starts clean.")
        st.rerun()
st.caption("Memory is bounded to the last N turns per session; reset explicitly clears it for a new customer conversation.")