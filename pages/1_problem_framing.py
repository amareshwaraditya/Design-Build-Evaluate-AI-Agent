import streamlit as st
from src.runtime import answer

st.title("Customer Support Assistant")
st.subheader("What can I help you with?")
st.write("Ask about a return, refund, delivery, warranty, product issue, or account concern.")
message = st.text_area("Customer message", "I want to return my order ORD-10001")
if st.button("Submit support request"):
    st.session_state["first_request"] = message
    st.json(answer(message))
st.markdown("### Customer workflow")
st.write("1. Customer describes the issue → 2. Agent identifies the request → 3. Verified information is returned → 4. Unclear, sensitive, or unsafe cases are protected or escalated.")