import streamlit as st
from src.adaptation import FeedbackPolicy, before_after
from src.planning import run_agent_turn
from src.ui import chat_header, evaluation_box, phase_carousel, render_chat

st.set_page_config(page_title="Athena - Feedback Learning", page_icon="💬", layout="wide")
phase_carousel(7)
chat_header("Phase 7 — Athena adapts her tone based on how you rate her previous responses.")

if "phase7_feedback" not in st.session_state:
    st.session_state.phase7_feedback = FeedbackPolicy()
policy: FeedbackPolicy = st.session_state.phase7_feedback

st.markdown("#### How it works")
st.markdown(
    "After each response, rate your satisfaction using the stars below. "
    "Athena tracks your rolling average and adapts her tone:\n"
    "- **Low ratings (1–2):** Athena becomes more empathetic, detailed, and apologetic\n"
    "- **Mid ratings (3):** Athena uses a balanced, professional tone\n"
    "- **High ratings (4–5):** Athena becomes concise and friendly\n\n"
    "Try rating a few responses, then ask the same question again to see the tone shift."
)

# Star rating — immediate click, no submit button
st.markdown("**Rate Athena's last response:**")
star_cols = st.columns([1, 1, 1, 1, 1, 4])
for i, col in enumerate(star_cols[:5], start=1):
    with col:
        if st.button(f"{'⭐' * i}", key=f"star_{i}", use_container_width=True):
            policy.add(i)
            st.toast(f"Rated {i}/5 — rolling average now {policy.instructions()['average']}")
            st.rerun()

# Show current feedback state
applied = policy.instructions()
if applied["sample_size"] > 0:
    st.caption(
        f"Current tone: **{applied['tone']}** | Verbosity: **{applied['verbosity']}** | "
        f"Rolling avg: **{applied['average']}** ({applied['sample_size']} ratings)"
    )
else:
    st.caption("No ratings yet — Athena uses default professional tone. Rate a response to see adaptation.")


def _phase7_insights(result: dict) -> list[str]:
    """Generate success/limitation notes for Phase 7 evaluation box."""
    extra = [f"<b>Tone applied:</b> {applied['tone']} (based on {applied['sample_size']} recent ratings, avg {applied['average']})"]
    status = result.get("status", "resolved")

    # Success indicators
    if applied['sample_size'] > 0:
        if applied['average'] <= 2.0:
            extra.append("<b>✓ Adapted:</b> Low ratings detected — using empathetic, detailed tone to recover satisfaction")
        elif applied['average'] >= 4.0:
            extra.append("<b>✓ Adapted:</b> High ratings detected — using concise, friendly tone for efficiency")
        else:
            extra.append("<b>✓ Adapted:</b> Mixed ratings — using balanced, neutral tone")
    else:
        extra.append("<b>ℹ No feedback yet:</b> Using default neutral tone — rate a response to see adaptation")

    if status == "refused":
        extra.append("<b>✓ Success:</b> Safety refusal maintained even under tone adaptation")

    # Phase 7 limitations
    limitations = []
    if status == "resolved":
        limitations.append("No production monitoring — latency and errors untracked (→ Phase 8 Observability)")
        limitations.append("No PII-safe logging — customer data may appear in raw logs (→ Phase 8 Sanitization)")
        limitations.append("No formal evaluation against test suite (→ Phase 9 Governance)")

    if limitations:
        extra.append("<b>Phase 7 gaps:</b> " + "; ".join(limitations))
    return extra


def _evidence(result: dict) -> None:
    evaluation_box(result, extra_lines=_phase7_insights(result))


render_chat(
    session_key="phase7_chat",
    reply_fn=lambda msg: run_agent_turn(msg, feedback=policy.instructions()),
    evidence_fn=_evidence,
    placeholder="Ask a support question, then rate the response using the stars above",
    suggestions={
        "😤 Frustrated customer": "My package is delayed and I'm frustrated — this is unacceptable!",
        "😊 Happy inquiry": "Hi! Just wondering when my SmartWatch Pro X1 will arrive — so excited!",
        "😐 Neutral question": "Can you tell me the status of order ORD-10001?",
        "😡 Very unhappy": "This is the THIRD time I've asked about my refund and nobody helps me!",
    },
)

with st.expander("Technical evidence: feedback policy & before/after comparison"):
    st.json({"ratings": policy.ratings, **policy.instructions()})
    st.markdown("**Tone adaptation demo** — same question, two contrasting tones:")
    demo_message = st.text_input("Comparison message", "My earbuds broke after 2 weeks")
    if st.button("Run before/after comparison"):
        try:
            result = before_after(demo_message, policy)
        except Exception as exc:
            st.error(f"Comparison failed: {type(exc).__name__}: {exc}")
            result = None
        if result is None:
            st.stop()
        st.markdown(
            f"""<div style="background-color: #f0f2f6; border-left: 4px solid #007cc3; border-radius: 0.25rem; padding: 0.75rem 1rem; margin: 0.5rem 0;">
            <strong>Professional + concise tone:</strong><br>{result["before"]}
            </div>""",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""<div style="background-color: #f0f2f6; border-left: 4px solid #007cc3; border-radius: 0.25rem; padding: 0.75rem 1rem; margin: 0.5rem 0;">
            <strong>Empathetic + detailed tone:</strong><br>{result["after"]}
            <br><br><small>This demonstrates how Athena's output changes based on customer satisfaction signals.</small>
            </div>""",
            unsafe_allow_html=True,
        )
