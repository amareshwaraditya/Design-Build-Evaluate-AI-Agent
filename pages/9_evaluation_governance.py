import json
import streamlit as st
from src.evaluation import run_evaluation

st.set_page_config(page_title="Phase 9 - Evaluation and Governance")
st.title("Phase 9 — Evaluation, Safety & Governance")
st.caption("Rubric: Safety, Evaluation & Governance (15 pts)")
with open("evaluation/dataset.json", encoding="utf-8") as handle:
    cases = json.load(handle)
result = run_evaluation(cases)
st.metric("Evaluation score", f"{result['score']}%")
st.write(result)
st.table({"Dimension": ["Answer quality", "Policy groundedness", "Tool-selection accuracy", "Safety refusal accuracy", "Escalation correctness", "Latency", "PII-safe logging"], "Evidence": ["Scored test cases", "Retrieved-source comparison", "Expected vs actual tool", "Unsafe-request suite", "High-risk test suite", "Trace timings", "Sanitizer tests"]})
st.markdown("**Failure:** a baseline keyword agent answers only the first intent in a combined request.\n\n**Root cause:** no intent decomposition.\n\n**Fix:** planning splits the request, retrieval supplies evidence, and the tool router handles each safe subtask independently.\n\n**Proof:** compare the Phase 2 response with the Phase 6 plan and Phase 5 tool trace.")
st.info("When LangSmith credentials are configured, live calls should be traced with project name customer-support-resolution-agent; never send raw PII in trace metadata.")