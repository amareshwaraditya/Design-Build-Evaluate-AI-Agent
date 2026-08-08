import streamlit as st
from src.planning import SessionMemory, decompose

st.set_page_config(page_title="Phase 6 - Planning and Memory")
st.title("Phase 6 — Planning, Memory & Context")
st.caption("Rubric: Agent Architecture, Planning & Memory (15 pts)")
message = st.text_input("Multi-intent request", "Check my order and tell me whether it is under warranty")
st.write("Planned steps:")
for step in decompose(message):
    st.write(f"- {step}")
if "memory" not in st.session_state:
    st.session_state.memory = SessionMemory()
turn = st.text_input("Add a conversation turn", "My order is ORD-10001")
if st.button("Store turn"):
    st.session_state.memory.add(turn, "Stored response")
st.write(f"Stored turns: {len(st.session_state.memory.turns)} / {st.session_state.memory.max_turns}")
if st.button("Reset session memory"):
    st.session_state.memory.reset()
    st.success("Memory reset completed.")