import streamlit as st
from streamlit_app.components import phase_header, evidence_note
from src.llm_agent import PROMPT_VARIANTS, llm_response
phase_header(3, "LLM Integration & Prompt Design", 15)
evidence_note("Compare prompt strategies using the same test set and select a default based on safety, quality, grounding, and latency tradeoffs.")
for name, prompt in PROMPT_VARIANTS.items():
    with st.expander(name): st.code(prompt)
st.table({"Variant": ["basic", "structured", "safety_first"], "Strength": ["Low complexity", "Better task structure", "Safety, uncertainty, escalation and action boundaries"], "Tradeoff": ["Weak controls", "More prompt tokens", "Potentially longer responses and latency"], "Selection": ["Baseline comparison", "Intermediate", "Recommended default"]})
message = st.text_input("Try the LLM stage in evidence mode", "I need help with an unresolved refund")
st.json(llm_response(message, context="Refund policy context", prompt_version="safety_first"))
