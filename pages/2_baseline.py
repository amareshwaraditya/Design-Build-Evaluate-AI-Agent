import streamlit as st

from src.phase2_chatbot import BaselineChatbot, limitation_tests

st.set_page_config(page_title="Phase 2 - Baseline Chatbot", page_icon="💬", layout="wide")
st.title("Baseline Customer Support Chatbot")
st.write("This is the first working product version. It accepts a customer message, classifies it using simple rules, returns a template response, and records a PII-safe interaction log.")

if "phase2_bot" not in st.session_state:
    st.session_state.phase2_bot = BaselineChatbot()

bot = st.session_state.phase2_bot

st.subheader("Chat with support")
for turn in bot.turns:
    with st.chat_message("user"):
        st.write(turn.user)
    with st.chat_message("assistant"):
        st.write(turn.assistant)
        st.caption(f"Baseline intent: `{turn.intent}`")

message = st.chat_input("Ask about a return, refund, delivery, warranty, or account issue")
if message:
    bot.respond(message)
    st.rerun()

col1, col2 = st.columns(2)
with col1:
    if st.button("Clear conversation"):
        st.session_state.phase2_bot = BaselineChatbot()
        st.rerun()
with col2:
    st.download_button("Download session summary", str(bot.summary()), file_name="phase2_session_summary.txt")

st.subheader("Baseline session summary")
st.json(bot.summary())

st.subheader("Demonstrate baseline limitations")
if st.button("Run limitation tests"):
    results = limitation_tests()
    for result in results:
        with st.expander(result["label"]):
            st.write(f"**Input:** {result['input']}")
            st.write(f"**Expected:** {result['expected']}")
            st.write(f"**Classified intent:** `{result['actual_intent']}`")
            st.write(f"**Response:** {result['actual_response']}")

st.info("Why this is insufficient for real users: one message maps to one keyword intent, follow-up context is not retained, responses do not reason over policy details, and the baseline cannot perform verified order or account operations.")
