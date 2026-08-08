import streamlit as st

st.set_page_config(page_title="Customer Support AI Resolution Agent", page_icon="🛠️", layout="wide")
st.title("Customer Support AI Resolution Agent")
st.subheader("Scenario 3 · Engineering evolution walkthrough")
st.write("Use the sidebar to inspect how the agent evolves from a simple baseline into a grounded, tool-using, observable, and evaluated system.")
st.info("Evidence mode is enabled by default. Live model, MCP, and LangSmith features activate when deployment secrets are configured.")
st.markdown("### Phase sequence")
st.table({"Phase": list(range(1, 10)), "Capability": ["Problem framing", "Python baseline", "LLM and prompts", "RAG", "MCP tools", "Planning and memory", "Feedback adaptation", "Deployment and monitoring", "Evaluation and governance"], "Rubric points": [10, 5, 15, 10, 15, 15, 5, 10, 15]})
st.caption("Scenario safety rule: support assistance is allowed; unsafe, policy-violating, sensitive, or unresolved cases are refused or escalated.")
