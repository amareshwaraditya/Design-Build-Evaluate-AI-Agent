import streamlit as st
from src.mcp_tools import TOOLS, call_tool, run_tool_agent
from src.ui import chat_header, evaluation_box, phase_carousel, render_chat

st.set_page_config(page_title="Athena - Support Tools", page_icon="🛠️", layout="wide")
phase_carousel(5)
chat_header("Phase 5 — Athena can now call real, scoped, read-only tools to resolve your request.")


def _evidence(result: dict) -> None:
    trace = result.get("trace") or []
    extra = []
    if trace:
        for call in trace:
            extra.append(f"<b>Tool called:</b> <code>{call['tool']}({call['args']})</code> → <code>{call['result']}</code>")
    else:
        extra.append("<b>Tool called:</b> none — Athena asked for missing information instead of guessing")
    evaluation_box(result, extra_lines=extra)


render_chat(
    session_key="phase5_chat",
    reply_fn=lambda msg: run_tool_agent(msg),
    evidence_fn=_evidence,
    placeholder="Try an order ID, e.g. 'What's the status of order ORD-10001?'",
    suggestions={
        "📦 Order status": "What's the status of order ORD-10001?",
        "❓ Unknown order": "Is order ORD-99999 covered under warranty?",
    },
)

with st.expander("Technical evidence: available tools & safeguards"):
    st.table({"Tool": list(TOOLS.keys()), "Purpose": list(TOOLS.values())})
    st.markdown("**Manual tool execution**")
    selected = st.selectbox("Demonstrate a tool directly", list(TOOLS.keys()))
    order_id = st.text_input("Order ID", "ORD-10001")
    if selected in ("lookup_order", "check_warranty"):
        st.json(call_tool(selected, {"order_id": order_id}))
    else:
        reason = st.text_input("Escalation reason", "Customer reports an unresolved sensitive issue")
        st.json(call_tool(selected, {"reason": reason}))
    st.markdown(
        "- Tools are read-only; no order can be modified or refunded automatically.\n"
        "- Unknown order IDs return `not_found` rather than a guessed value.\n"
        "- The tool loop is bounded to `settings.max_tool_iterations` calls to prevent infinite loops.\n"
        "- Unknown tool names are rejected with `tool_not_allowed`."
    )
