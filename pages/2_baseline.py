import streamlit as st
from src.baseline import baseline_response

st.set_page_config(page_title="Phase 2 - Baseline Agent")
st.title("Phase 2 — Python Foundations & Baseline")
st.caption("Rubric: Python Foundations & Baseline Prototype (5 pts)")
message = st.text_input("Try the rule-based agent", "I want a refund and tracking for my order")
st.write(baseline_response(message))
st.subheader("Baseline limitations")
st.table({"Observed limitation": ["Keyword dependence", "Multi-intent queries are not decomposed", "No semantic retrieval", "No conversation memory", "No explicit evidence trail"], "Why it matters": ["Natural language is missed", "Part of the customer request may be ignored", "Policy answers can be incomplete", "Follow-ups require repetition", "Failures are difficult to investigate"]})