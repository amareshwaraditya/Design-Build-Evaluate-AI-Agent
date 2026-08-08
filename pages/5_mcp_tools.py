import streamlit as st
from src.mcp_tools import TOOLS, call_tool

st.set_page_config(page_title="Phase 5 - MCP Tool Usage")
st.title("Phase 5 — MCP Tool Usage")
st.caption("Rubric: Tool-Using Agent Implementation (15 pts)")
st.table({"MCP tool": list(TOOLS.keys()), "Purpose": list(TOOLS.values())})
selected = st.selectbox("Demonstrate a tool", list(TOOLS.keys()))
order_id = st.text_input("Order ID", "ORD-10001")
if selected in ("lookup_order", "check_warranty"):
    st.json(call_tool(selected, {"order_id": order_id}))
else:
    reason = st.text_input("Escalation reason", "Customer reports an unresolved sensitive issue")
    st.json(call_tool(selected, {"reason": reason}))
st.warning("State-changing operations are not executed automatically. They require explicit confirmation and policy validation.")