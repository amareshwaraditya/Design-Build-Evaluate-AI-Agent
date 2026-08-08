import streamlit as st
from streamlit_app.components import phase_header, evidence_note
from src.baseline import baseline_response
phase_header(2, "Python Foundations & Baseline", 5)
evidence_note("Show a reliable, modular baseline and make its limitations observable.")
message = st.text_input("Try the rule-based agent", "I want a refund and tracking for my order")
st.write(baseline_response(message))
st.subheader("Baseline limitations")
st.table({"Observed limitation": ["Keyword dependence", "Multi-intent queries are not decomposed", "No semantic retrieval", "No conversation memory", "No explicit evidence trail"], "Why it matters": ["Natural language is missed", "Part of the customer request may be ignored", "Policy answers can be incomplete", "Follow-ups require repetition", "Failures are difficult to investigate"]})
