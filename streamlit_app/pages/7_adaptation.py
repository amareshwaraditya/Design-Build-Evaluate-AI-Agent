import streamlit as st
from streamlit_app.components import phase_header, evidence_note
from src.adaptation import FeedbackPolicy
phase_header(7, "Adaptive Behaviour & Feedback", 5)
evidence_note("Show an explicit feedback signal, persistent policy adjustment, and before/after behaviour.")
if "feedback" not in st.session_state: st.session_state.feedback = FeedbackPolicy()
rating = st.slider("Rate the last response", 1, 5, 3)
if st.button("Record feedback"): st.session_state.feedback.add(rating)
policy = st.session_state.feedback.instructions()
st.json(policy)
st.table({"Before feedback": ["Professional tone; normal verbosity"], "After repeated low ratings": ["Empathetic tone; detailed explanation; proactive next step"]})
