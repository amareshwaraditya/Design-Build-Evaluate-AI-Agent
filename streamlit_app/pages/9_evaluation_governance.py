import json
import streamlit as st
from streamlit_app.components import phase_header, evidence_note
from src.evaluation import run_evaluation
phase_header(9, "Evaluation, Safety & Governance", 15)
evidence_note("Run repeatable tests, inspect quality and safety metrics, debug a failure, and show LangSmith tracing in live mode.")
with open("evaluation/dataset.json", encoding="utf-8") as handle: cases = json.load(handle)
result = run_evaluation(cases)
st.metric("Evaluation score", f"{result['score']}%")
st.write(result)
st.subheader("Evaluation dimensions")
st.table({"Dimension": ["Answer quality", "Policy groundedness", "Tool-selection accuracy", "Safety refusal accuracy", "Escalation correctness", "Latency", "PII-safe logging"], "Evidence": ["Scored test cases", "Retrieved-source comparison", "Expected vs actual tool", "Unsafe-request suite", "High-risk test suite", "Trace timings", "Sanitizer tests"]})
st.subheader("Debugged failure case")
st.markdown("**Failure:** a baseline keyword agent answers only the first intent in a combined request.\n\n**Root cause:** no intent decomposition.\n\n**Fix:** planning splits the request, retrieval supplies evidence, and the tool router handles each safe subtask independently.\n\n**Proof:** compare the Phase 2 response with the Phase 6 plan and Phase 5 tool trace.")
st.info("When LangSmith credentials are configured, live calls should be traced with project name customer-support-resolution-agent; never send raw PII in trace metadata.")
