import streamlit as st
from src.runtime import baseline_answer

st.title("Baseline Support Assistant")
st.write("This is the first working version: simple intent classification and fixed responses.")
message = st.text_area("Customer message", "I want a refund and I also need to track my order")
if st.button("Run baseline"):
    st.json(baseline_answer(message))
st.subheader("Try the known limitations")
st.write("Use a multi-intent message, an unusual wording, or a follow-up without context. Observe which part the simple assistant misses.")