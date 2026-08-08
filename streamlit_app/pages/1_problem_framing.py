import streamlit as st
from streamlit_app.components import phase_header, evidence_note
phase_header(1, "Problem Framing & Domain Understanding", 10)
evidence_note("Make the user, workflow, inputs, outputs, constraints, assumptions, success criteria, and failure cases explicit.")
st.markdown("**Scenario:** TechGadgets Inc. customer support for consumer electronics.")
st.markdown("**Primary user:** A customer seeking a quick, accurate resolution for an order, product, return, warranty, or account issue.")
st.markdown("**Agent boundary:** It provides information and decision support; it does not invent policy, expose customer data, or perform uncontrolled actions.")
st.table({"Input": ["Customer message", "Optional order ID", "Conversation context"], "Output": ["Grounded answer", "Clarifying question", "Refusal or escalation"]})
st.subheader("Success criteria")
st.table({"Metric": ["Resolution quality", "Safety compliance", "Groundedness", "p95 latency", "Escalation correctness"], "Target": [">80% reviewed cases", "100% safety tests", ">90% policy-supported answers", "<3 seconds target", "100% high-risk cases"]})
st.subheader("Representative failure cases")
st.markdown("- Unknown policy or product: express uncertainty and escalate when necessary.\n- Invalid order ID: do not fabricate status.\n- Multi-intent query: decompose and address every intent.\n- Unsafe request or PII: refuse/protect before tools or model calls.")
