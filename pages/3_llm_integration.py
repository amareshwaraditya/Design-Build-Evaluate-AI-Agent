import streamlit as st
from src.runtime import answer

st.title("LLM Support Assistant")
st.write("The assistant now converts the customer message into an intent, safe response, and next action.")
message = st.text_area("Customer message", "My order ORD-10002 arrived damaged. Can I get a refund?")
if st.button("Ask the assistant"):
    st.json(answer(message, live=True))
st.subheader("Prompt behaviour")
st.write("The response must use verified context, avoid fabricated policy, state uncertainty, and separate information from actions.")