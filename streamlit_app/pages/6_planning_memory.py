import streamlit as st
from streamlit_app.components import phase_header, evidence_note
from src.planning import SessionMemory, decompose
phase_header(6, "Planning, Memory & Context", 15)
evidence_note("Show decomposition, multi-turn context, bounded retention, and reset behaviour.")
message = st.text_input("Multi-intent request", "Check my order and tell me whether it is under warranty")
st.write("Planned steps:")
for step in decompose(message): st.write(f"- {step}")
if "memory" not in st.session_state: st.session_state.memory = SessionMemory()
turn = st.text_input("Add a conversation turn", "My order is ORD-10001")
if st.button("Store turn"): st.session_state.memory.add(turn, "Stored response")
st.write(f"Stored turns: {len(st.session_state.memory.turns)} / {st.session_state.memory.max_turns}")
if st.button("Reset session memory"): st.session_state.memory.reset(); st.success("Memory reset completed.")
