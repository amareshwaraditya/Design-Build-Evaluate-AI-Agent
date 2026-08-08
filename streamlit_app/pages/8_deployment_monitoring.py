import streamlit as st
from streamlit_app.components import phase_header, evidence_note
from src.llm_agent import llm_response
from src.observability import traced_run
phase_header(8, "Deployment & Monitoring", 10)
evidence_note("Demonstrate a cloud-ready app, secrets discipline, latency/error capture, graceful failures, and PII-safe logs.")
message = st.text_input("Run monitored request", "Where is order ORD-10001?")
run = traced_run(llm_response, message)
st.json(run)
st.markdown("### Deployment assumptions")
st.markdown("- Streamlit Community Cloud runs `app.py` from the GitHub repository.\n- Credentials are configured as deployment secrets.\n- Evidence mode remains available when live services fail.\n- Logs contain sanitized identifiers rather than raw email, phone, card, or order data.")
st.metric("Observed latency (ms)", run["latency_ms"])
