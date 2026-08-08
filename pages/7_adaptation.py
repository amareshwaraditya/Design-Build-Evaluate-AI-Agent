import streamlit as st
from src.adaptation import FeedbackPolicy

st.set_page_config(page_title="Phase 7 - Adaptive Behaviour")
st.title("Phase 7 — Adaptive Behaviour & Feedback")
st.caption("Rubric: Adaptive Behaviour & Feedback (5 pts)")
if "feedback" not in st.session_state:
    st.session_state.feedback = FeedbackPolicy()
rating = st.slider("Rate the last response", 1, 5, 3)
if st.button("Record feedback"):
    st.session_state.feedback.add(rating)
policy = st.session_state.feedback.instructions()
st.json(policy)
st.table({"Before feedback": ["Professional tone; normal verbosity"], "After repeated low ratings": ["Empathetic tone; detailed explanation; proactive next step"]})