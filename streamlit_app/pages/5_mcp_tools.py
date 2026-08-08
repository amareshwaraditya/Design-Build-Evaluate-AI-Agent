import streamlit as st
from streamlit_app.components import phase_header, evidence_note
from src.mcp_tools import TOOLS, call_tool
phase_header(5, "MCP Tool Usage", 15)
evidence_note("Show scoped tools, explainable routing, validation, failure handling, and action safeguards.")
st.table({"MCP tool": list(TOOLS.keys()), "Purpose": list(TOOLS.values())})
selected = st.selectbox("Demonstrate a tool", list(TOOLS.keys()))
order_id = st.text_input("Order ID", "ORD-10001")
if selected in ("lookup_order", "check_warranty"):
    st.json(call_tool(selected, {"order_id": order_id}))
else:
    reason = st.text_input("Escalation reason", "Customer reports an unresolved sensitive issue")
    st.json(call_tool(selected, {"reason": reason}))
st.warning("State-changing operations are not executed automatically. They require explicit confirmation and policy validation.")
