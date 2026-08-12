import streamlit as st
from src.mcp_tools import TOOLS, call_tool, run_tool_agent
from src.ui import chat_header, evaluation_box, phase_carousel, render_chat

st.set_page_config(page_title="Athena - Support Tools", page_icon="🛠️", layout="wide")
phase_carousel(5)
chat_header("Phase 5 — Athena can now call real, scoped, read-only tools to resolve your request.")


def _phase5_insights(result: dict) -> list[str]:
    """Generate success/limitation notes for Phase 5 evaluation box."""
    trace = result.get("trace") or []
    extra = []
    status = result.get("status", "resolved")

    # Tool trace details
    if trace:
        for call in trace:
            extra.append(f"<b>Tool called:</b> <code>{call['tool']}({call['args']})</code> → <code>{call['result']}</code>")
        # Success indicators based on tool results
        tool_results_str = " ".join(str(call.get("result", "")) for call in trace)
        if "not_found" in tool_results_str:
            extra.append("<b>✓ Success:</b> Unknown order handled gracefully — no fabricated data returned")
        elif "escalat" in tool_results_str.lower():
            extra.append("<b>✓ Success:</b> Correctly escalated to human specialist via escalation tool")
        else:
            extra.append("<b>✓ Success:</b> Tool-verified data used in response — no guessing")
    else:
        extra.append("<b>Tool called:</b> none — Athena asked for missing information instead of guessing")
        if status == "refused":
            extra.append("<b>✓ Success:</b> Unsafe request blocked at safety layer — no tools invoked")

    # Phase 5 limitations
    limitations = []
    if status == "resolved":
        limitations.append("No multi-step planning — handles one tool call at a time (→ Phase 6 Planning)")
        limitations.append("No conversation memory — cannot reference earlier turns (→ Phase 6 Memory)")
        limitations.append("No tone adaptation — same tone regardless of customer mood (→ Phase 7 Feedback)")

    if limitations:
        extra.append("<b>Phase 5 gaps:</b> " + "; ".join(limitations))
    return extra


def _evidence(result: dict) -> None:
    evaluation_box(result, extra_lines=_phase5_insights(result))


render_chat(
    session_key="phase5_chat",
    reply_fn=lambda msg: run_tool_agent(msg),
    evidence_fn=_evidence,
    placeholder="Try an order ID, e.g. 'What's the status of order ORD-10001?'",
    suggestions={
        "📦 Order status": "What's the status of order ORD-10001?",
        "❓ Unknown order": "Is order ORD-99999 covered under warranty?",
        "🛡️ Warranty check": "Is my order ORD-10003 still under warranty?",
        "🚨 Escalation": "I've been waiting 2 weeks with no response and I want to speak to a manager.",
    },
)

with st.expander("Technical evidence: available tools & safeguards"):
    st.table({"Tool": list(TOOLS.keys()), "Purpose": list(TOOLS.values())})
    st.markdown("**Manual tool execution**")
    selected = st.selectbox("Demonstrate a tool directly", list(TOOLS.keys()))
    order_id = st.text_input("Order ID", "ORD-10001")
    st.markdown(
        '<div style="border: 2px solid #16a34a; border-radius: 0.5rem; padding: 1rem; margin: 0.5rem 0;">',
        unsafe_allow_html=True,
    )
    try:
        if selected in ("lookup_order", "check_warranty"):
            st.json(call_tool(selected, {"order_id": order_id}))
        else:
            reason = st.text_input("Escalation reason", "Customer reports an unresolved sensitive issue")
            st.json(call_tool(selected, {"reason": reason}))
    except Exception as exc:
        st.error(f"Tool execution failed: {type(exc).__name__}: {exc}")
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown(
        "- Tools are read-only; no order can be modified or refunded automatically.\n"
        "- Unknown order IDs return `not_found` rather than a guessed value.\n"
        "- The tool loop is bounded to `settings.max_tool_iterations` calls to prevent infinite loops.\n"
        "- Unknown tool names are rejected with `tool_not_allowed`."
    )
