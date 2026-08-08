import streamlit as st
from src.runtime import tool_call

st.title("Support Tool Execution")
st.write("The assistant can use read-only order and warranty tools and can recommend human escalation.")
tool = st.selectbox("Choose a support operation", ["lookup_order", "check_warranty", "escalate_to_human"])
order_id = st.text_input("Order ID", "ORD-10001")
reason = st.text_input("Escalation reason", "Repeated unresolved issue")
if st.button("Execute tool"):
    args = {"order_id": order_id, "reason": reason}
    st.json(tool_call(tool, args))
st.info("Unknown order IDs return not_found. State-changing actions are not executed automatically.")