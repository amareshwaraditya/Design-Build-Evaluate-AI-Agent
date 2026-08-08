import os
import streamlit as st
from dotenv import load_dotenv
from src.runtime import answer

load_dotenv()
st.title("Live Customer Support Service")
st.write("This page exercises the same request path used by a deployed customer-facing service.")
mode = os.getenv("AGENT_MODE", "evidence")
st.write({"mode": mode, "model_configured": bool(os.getenv("OPENAI_API_KEY")), "langsmith_configured": bool(os.getenv("LANGCHAIN_API_KEY"))})
message = st.text_area("Customer message", "Where is my order ORD-10001?")
if st.button("Send monitored request"):
    output = answer(message)
    st.json(output)
st.caption("The response includes latency and a sanitized log message. Raw customer identifiers are not intended for logs.")