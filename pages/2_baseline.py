import streamlit as st

from src.phase2_chatbot import BaselineChatbot, limitation_tests
from src.ui import chat_header, evaluation_box, phase_carousel

st.set_page_config(page_title="Athena - Basic Support", page_icon="💬", layout="wide")
phase_carousel(2)
chat_header("Phase 2 — this early version classifies your message with simple keyword rules.")

if "phase2_bot" not in st.session_state:
    st.session_state.phase2_bot = BaselineChatbot()

bot = st.session_state.phase2_bot


def _baseline_limitations(turn) -> list[str]:
    """Generate limitation notes for the evaluation box based on what this baseline cannot do."""
    notes = [f"<b>Classified intent:</b> <code>{turn.intent}</code>"]
    limitations = []
    text_lower = turn.user.lower()

    # Check if this is a follow-up / contextual question
    if any(w in text_lower for w in ("also", "and", "as well", "too", "both")):
        limitations.append("Multi-intent not decomposed — only first keyword match used")
    # Check for natural language that keyword rules can't parse well
    if turn.intent == "unknown":
        limitations.append("Intent unrecognized — keyword rules cannot parse natural language nuance")
    # Check for questions asking for steps/details (template can't provide)
    if any(w in text_lower for w in ("how", "steps", "process", "explain", "details", "what should")):
        limitations.append("Cannot provide detailed steps — fixed template response only")
    # Check for context-dependent follow-ups
    if len(text_lower.split()) < 8 and not any(w in text_lower for w in ("order", "refund", "return", "warranty", "cancel", "shipping", "password")):
        limitations.append("No conversation memory — cannot understand follow-up context")
    # Always note the core limitation
    limitations.append("No reasoning — same template returned regardless of specific question phrasing")

    if limitations:
        notes.append("<b>Baseline gaps:</b> " + "; ".join(limitations))
        notes.append("<b>Resolved by:</b> Phase 3 (LLM reasoning), Phase 4 (policy knowledge), Phase 6 (memory)")
    return notes


for turn in bot.turns:
    with st.chat_message("user"):
        st.write(turn.user)
    with st.chat_message("assistant", avatar=":material/support_agent:"):
        st.write(turn.assistant)
        evaluation_box(
            {"status": "resolved", "prompt_version": "keyword-rules"},
            extra_lines=_baseline_limitations(turn),
        )

message = st.chat_input("Ask about a return, refund, delivery, warranty, password, or cancellation")
if message:
    bot.respond(message)
    st.rerun()

col1, col2 = st.columns(2)
with col1:
    if st.button("Start a new customer conversation", icon=":material/refresh:"):
        st.session_state.phase2_bot = BaselineChatbot()
        st.rerun()
with col2:
    st.download_button("Download conversation summary", str(bot.summary()), file_name="athena_basic_support_summary.txt")

with st.expander("Technical evidence: session summary & baseline limitations"):
    st.json(bot.summary())
    st.markdown("**When this basic architecture needs improvement:**")
    if st.button("Test Athena’s limitations"):
        for result in limitation_tests():
            st.write(f"**Customer message:** {result['input']}")
            st.write(f"**What a stronger Athena should do:** {result['expected']}")
            st.write(f"**What Athena classified:** `{result['actual_intent']}`")
            st.write(f"**Athena’s response:** {result['actual_response']}")
            st.divider()
    st.info("This basic Athena cannot reliably handle multi-intent questions, follow-up context, detailed policy reasoning, or verified customer operations. Later phases improve these specific weaknesses.")
