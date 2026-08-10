import streamlit as st
from src.adaptation import FeedbackPolicy, before_after
from src.planning import run_agent_turn

st.title("Phase 7 — Athena Learns from Feedback")
st.write("Explicit 1-5 star feedback adjusts Athena's tone/verbosity instructions for future responses in the session.")

if "feedback" not in st.session_state:
    st.session_state.feedback = FeedbackPolicy()
policy: FeedbackPolicy = st.session_state.feedback

rating = st.slider("Rate the previous response", 1, 5, 3)
if st.button("Save feedback"):
    policy.add(rating)
st.json({"ratings": policy.ratings, **policy.instructions()})

st.subheader("Adapted response")
message = st.text_input("Repeat a support question", "My package is delayed and I'm frustrated")
if st.button("Generate adapted response"):
    st.json(run_agent_turn(message, feedback=policy.instructions()))

st.subheader("Before vs. after feedback (same message, real LLM calls)")
demo_message = st.text_input("Comparison message", "My earbuds broke after 2 weeks", key="demo_message")
if st.button("Run before/after comparison"):
    result = before_after(demo_message, policy)
    st.table({"Stage": ["Before feedback (neutral)", "After feedback"], "Response": [result["before"][:300], result["after"][:300]]})
    st.caption(f"Feedback policy applied: {result['policy']}")