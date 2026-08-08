import streamlit as st
from src.llm_agent import llm_response
from src.observability import traced_run

st.set_page_config(page_title="Phase 8 - Deployment and Monitoring")
st.title("Phase 8 — Deployment & Monitoring")
st.caption("Rubric: Deployment & Monitoring (10 pts)")
message = st.text_input("Run monitored request", "Where is order ORD-10001?")
run = traced_run(llm_response, message)
st.json(run)
st.markdown("### Deployment assumptions")
st.markdown("- Streamlit Community Cloud runs app.py from the GitHub repository.\n- Credentials are configured as deployment secrets.\n- Evidence mode remains available when live services fail.\n- Logs contain sanitized identifiers rather than raw email, phone, card, or order data.")
st.metric("Observed latency (ms)", run["latency_ms"])