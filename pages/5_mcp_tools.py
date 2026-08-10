import streamlit as st
from src.mcp_tools import TOOLS, call_tool, run_tool_agent

st.title("Phase 5 — Athena Uses Support Tools")
st.write("Athena can now call real, scoped, read-only tools via LangChain tool-calling (`bind_tools`).")
st.table({"Tool": list(TOOLS.keys()), "Purpose": list(TOOLS.values())})

st.subheader("Manual tool execution")
selected = st.selectbox("Demonstrate a tool directly", list(TOOLS.keys()))
order_id = st.text_input("Order ID", "ORD-10001")
if selected in ("lookup_order", "check_warranty"):
    st.json(call_tool(selected, {"order_id": order_id}))
else:
    reason = st.text_input("Escalation reason", "Customer reports an unresolved sensitive issue")
    st.json(call_tool(selected, {"reason": reason}))

st.subheader("Let the LLM choose the tool (correct vs. incorrect cases)")
st.caption("The model reads the message, decides whether a tool is needed, and which one — it never invents an order ID.")
example = st.selectbox(
    "Try a scenario",
    [
        "What's the status of order ORD-10001?",
        "Is order ORD-99999 covered under warranty?",
        "I need help but I don't have my order number handy",
    ],
)
if st.button("Run tool-calling agent"):
    result = run_tool_agent(example)
    st.json(result)
    if result.get("trace"):
        st.success(f"Correct tool call: {result['trace'][0]['tool']}({result['trace'][0]['args']})")
    else:
        st.info("No tool called — the model correctly asked for missing information instead of guessing.")

st.subheader("Safeguards")
st.markdown(
    "- Tools are read-only; no order can be modified or refunded automatically.\n"
    "- `lookup_order`/`check_warranty` on an unknown order ID return `not_found` rather than a guessed value "
    "(try `ORD-99999` above for the incorrect/failed-lookup case).\n"
    "- The tool loop is bounded to `settings.max_tool_iterations` calls to prevent infinite loops.\n"
    "- Unknown tool names are rejected with `tool_not_allowed`."
)