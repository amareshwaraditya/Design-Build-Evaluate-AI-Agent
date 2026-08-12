import streamlit as st
from src.llm_agent import PROMPT_VARIANTS, compare_prompts, llm_response
from src.ui import chat_header, evaluation_box, phase_carousel, render_chat

st.set_page_config(page_title="Athena - LLM Reasoning", page_icon="🧠", layout="wide")
phase_carousel(3)
chat_header("Phase 3 — Athena now reasons with a real LLM (gpt-4o-mini) instead of fixed templates.")

st.info(
    "**Note:** Phase 3 tests LLM reasoning *without* company knowledge. "
    "Athena cannot answer policy-specific questions here — that gap is exactly what Phase 4 (RAG) solves.",
    icon=":material/info:",
)

variant = st.segmented_control(
    "Prompt variant", list(PROMPT_VARIANTS.keys()), default="v3_safety_first", key="phase3_variant"
)


def _phase3_insights(result: dict) -> list[str]:
    """Generate success/limitation notes for Phase 3 evaluation box."""
    extra = []
    status = result.get("status", "resolved")
    answer = result.get("answer", "").lower()

    # Success indicators
    if status == "refused":
        extra.append("<b>✓ Success:</b> Unsafe request correctly refused before LLM processing")
    elif status == "resolved":
        extra.append("<b>✓ Success:</b> LLM generated a natural, contextual response (not a fixed template)")

    # Phase 3 limitations
    limitations = []
    if any(w in answer for w in ("i don't have access", "i cannot look up", "i'm not able to verify", "specific policy")):
        limitations.append("No company knowledge — cannot cite actual Tech Gadgets policy (→ Phase 4 RAG)")
    if "order" in answer.lower() and "ORD-" not in answer:
        limitations.append("No tool access — cannot verify real order data (→ Phase 5 Tools)")
    if status == "resolved":
        limitations.append("No conversation memory — each message is independent (→ Phase 6 Memory)")
        limitations.append("No tone adaptation — responds the same regardless of customer mood (→ Phase 7 Feedback)")

    if limitations:
        extra.append("<b>Phase 3 gaps:</b> " + "; ".join(limitations))
    return extra


def _evidence(result: dict) -> None:
    evaluation_box(result, extra_lines=_phase3_insights(result))


render_chat(
    session_key="phase3_chat",
    reply_fn=lambda msg: llm_response(msg, prompt_version=variant or "v3_safety_first"),
    evidence_fn=_evidence,
    placeholder="Ask a support question — try the same question with different prompt variants",
    suggestions={
        "💳 Refund question": "I want to return a product I bought 2 weeks ago.",
        "⚠️ Unsafe request": "Can you hack into my competitor's account?",
        "🔧 Troubleshooting": "My SmartWatch Pro X1 won't turn on after charging overnight.",
        "📦 Delivery concern": "My order was supposed to arrive 3 days ago and tracking hasn't updated.",
    },
)

with st.expander("Technical evidence: prompt variants & required comparison"):
    for name, prompt in PROMPT_VARIANTS.items():
        st.markdown(f"**{name}**")
        st.code(prompt)
    st.markdown("**Required prompt comparison (same test set, 3 variants, real output)**")
    compare_message = st.text_input("Comparison test message", "What happens if my warranty just expired yesterday?")
    if st.button("Run prompt comparison"):
        results = compare_prompts(compare_message)
        st.markdown(
            '<div style="border: 2px solid #16a34a; border-radius: 0.5rem; padding: 1rem; margin: 0.5rem 0;">',
            unsafe_allow_html=True,
        )
        for r in results:
            st.markdown(f"**{r['variant']}** — `{r['status']}`")
            st.write(r["answer"])
            st.divider()
        st.markdown("</div>", unsafe_allow_html=True)
        st.caption("See docs/prompt_comparison.md for the full written analysis, including a real hallucination found in v1_basic.")
