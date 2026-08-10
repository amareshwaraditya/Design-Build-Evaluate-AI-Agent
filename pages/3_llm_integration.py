import streamlit as st
from src.llm_agent import PROMPT_VARIANTS, compare_prompts, llm_response
from src.ui import chat_header, phase_carousel, render_chat

st.set_page_config(page_title="Athena - LLM Reasoning", page_icon="🧠", layout="wide")
phase_carousel(3)
chat_header("Phase 3 — Athena now reasons with a real LLM (gpt-4o-mini) instead of fixed templates.")

variant = st.segmented_control(
    "Prompt variant", list(PROMPT_VARIANTS.keys()), default="v3_safety_first", key="phase3_variant"
)


def _evidence(result: dict) -> None:
    st.caption(f"Prompt variant: `{result.get('prompt_version')}` · status: `{result['status']}`")


render_chat(
    session_key="phase3_chat",
    reply_fn=lambda msg: llm_response(msg, prompt_version=variant or "v3_safety_first"),
    evidence_fn=_evidence,
    placeholder="Ask a support question — try the same question with different prompt variants",
    suggestions={
        "💳 Refund question": "I want to return a product I bought 2 weeks ago.",
        "⚠️ Unsafe request": "Can you hack into my competitor's account?",
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
        st.table({
            "Variant": [r["variant"] for r in results],
            "Status": [r["status"] for r in results],
            "Answer": [r["answer"][:220] for r in results],
        })
        st.caption("See docs/prompt_comparison.md for the full written analysis, including a real hallucination found in v1_basic.")
