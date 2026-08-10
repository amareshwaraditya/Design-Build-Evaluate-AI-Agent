import streamlit as st

from src.phase2_chatbot import BaselineChatbot, limitation_tests
from src.ui import chat_header, phase_carousel

st.set_page_config(page_title="Athena - Basic Support", page_icon="💬", layout="wide")
phase_carousel(2)
chat_header("Phase 2 — this early version classifies your message with simple keyword rules.")

if "phase2_bot" not in st.session_state:
    st.session_state.phase2_bot = BaselineChatbot()

bot = st.session_state.phase2_bot
for turn in bot.turns:
    with st.chat_message("user"):
        st.write(turn.user)
    with st.chat_message("assistant", avatar=":material/support_agent:"):
        st.write(turn.assistant)
        st.caption(f"Classified intent: `{turn.intent}`")

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
