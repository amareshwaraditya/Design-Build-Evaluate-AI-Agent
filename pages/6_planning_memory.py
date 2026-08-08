import streamlit as st
from src.runtime import answer

st.title("Multi-step Support Conversation")
if "conversation" not in st.session_state: st.session_state.conversation = []
message = st.text_input("Customer message", "Please check order ORD-10001")
if st.button("Send message"):
    output = answer(message, memory=st.session_state.conversation)
    st.session_state.conversation.append({"user": message, "assistant": output["response"]})
for turn in st.session_state.conversation:
    st.chat_message("user").write(turn["user"])
    st.chat_message("assistant").write(turn["assistant"])
if st.button("Reset customer session"):
    st.session_state.conversation = []
    st.rerun()
st.caption("Memory is session-scoped and bounded by the application session. Reset starts a new customer conversation.")