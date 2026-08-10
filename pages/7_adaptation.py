import streamlit as st
from src.adaptation import FeedbackPolicy, before_after
from src.planning import run_agent_turn
from src.ui import chat_header, phase_carousel, render_chat

st.set_page_config(page_title="Athena - Feedback Learning", page_icon="💬", layout="wide")
phase_carousel(7)
chat_header("Phase 7 — Athena adapts her tone based on how you rate her previous responses.")

if "phase7_feedback" not in st.session_state:
    st.session_state.phase7_feedback = FeedbackPolicy()
policy: FeedbackPolicy = st.session_state.phase7_feedback

rating = st.slider("Rate Athena's last response", 1, 5, 3, key="phase7_rating")
if st.button("Submit rating", icon=":material/thumb_up:"):
    policy.add(rating)
    st.toast(f"Feedback recorded — rolling average now {policy.instructions()['average']}")


def _evidence(result: dict) -> None:
    applied = policy.instructions()
    st.caption(f"Tone applied: `{applied['tone']}` (based on {applied['sample_size']} recent ratings, avg {applied['average']})")


render_chat(
    session_key="phase7_chat",
    reply_fn=lambda msg: run_agent_turn(msg, feedback=policy.instructions()),
    evidence_fn=_evidence,
    placeholder="Ask a support question, then rate the response above",
    suggestions={"😤 Frustrated customer": "My package is delayed and I'm frustrated"},
)

with st.expander("Technical evidence: feedback policy & before/after comparison"):
    st.json({"ratings": policy.ratings, **policy.instructions()})
    demo_message = st.text_input("Comparison message", "My earbuds broke after 2 weeks")
    if st.button("Run before/after comparison"):
        result = before_after(demo_message, policy)
        st.table({"Stage": ["Before feedback (neutral)", "After feedback"], "Response": [result["before"][:300], result["after"][:300]]})
        st.caption(f"Feedback policy applied: {result['policy']}")
