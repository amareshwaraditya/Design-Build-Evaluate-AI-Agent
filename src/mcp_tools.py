"""Phase 5 — Tool-using agent: scoped, read-only support tools plus a real LangChain tool-calling loop."""
from .config import settings
from .demo_data import ORDERS

TOOLS = {
    "lookup_order": "Read-only lookup of order status using an order ID.",
    "check_warranty": "Read-only check of warranty eligibility using an order ID.",
    "escalate_to_human": "Creates an escalation recommendation for sensitive or unresolved cases.",
}


def call_tool(name: str, arguments: dict) -> dict:
    """Direct, scoped tool execution (used for manual demos and as the agent's tool implementation)."""
    if name == "lookup_order":
        order_id = str(arguments.get("order_id", "")).upper()
        order = ORDERS.get(order_id)
        return order or {"status": "not_found", "message": "Order could not be verified. I will not guess its status."}
    if name == "check_warranty":
        order_id = str(arguments.get("order_id", "")).upper()
        order = ORDERS.get(order_id)
        return {"warranty": order["warranty"]} if order else {"status": "not_found"}
    if name == "escalate_to_human":
        return {"status": "escalation_recommended", "reason": arguments.get("reason", "unresolved case")}
    return {"status": "tool_not_allowed", "message": f"'{name}' is not in the approved tool list."}


def _build_tools():
    from langchain_core.tools import tool

    @tool
    def lookup_order(order_id: str) -> dict:
        """Look up the shipping status of a Tech Gadgets Inc. order by its order ID (format ORD-#####)."""
        return call_tool("lookup_order", {"order_id": order_id})

    @tool
    def check_warranty(order_id: str) -> dict:
        """Check whether a Tech Gadgets Inc. order is still under warranty, by order ID (format ORD-#####)."""
        return call_tool("check_warranty", {"order_id": order_id})

    @tool
    def escalate_to_human(reason: str) -> dict:
        """Recommend escalation to a human support specialist for sensitive or unresolved cases."""
        return call_tool("escalate_to_human", {"reason": reason})

    return [lookup_order, check_warranty, escalate_to_human], {
        "lookup_order": lookup_order,
        "check_warranty": check_warranty,
        "escalate_to_human": escalate_to_human,
    }


def run_tool_agent(message: str, context: str = "", feedback: dict | None = None) -> dict:
    """Let a real LLM choose and call tools, bounded by max_tool_iterations to prevent loops."""
    if not settings.has_api_key:
        return {"status": "offline", "trace": [], "answer": "LLM is not configured (missing OPENAI_API_KEY)."}

    from langchain_openai import ChatOpenAI

    tools, by_name = _build_tools()
    model = ChatOpenAI(model=settings.model, temperature=0).bind_tools(tools)

    # Build tone instruction based on feedback
    tone_instruction = ""
    if feedback:
        tone = feedback.get("tone", "professional")
        verbosity = feedback.get("verbosity", "normal")
        if tone == "empathetic":
            tone_instruction = (
                "\n\nTONE INSTRUCTION: The customer has expressed dissatisfaction. Respond with extra empathy "
                "and understanding. Acknowledge their frustration explicitly. Be warm, apologetic, and thorough "
                "in your explanation. Use phrases like 'I completely understand your frustration', "
                "'I sincerely apologize for the inconvenience', 'Let me make this right for you'."
            )
        elif verbosity == "concise":
            tone_instruction = (
                "\n\nTONE INSTRUCTION: The customer is satisfied and prefers efficiency. "
                "Keep your response brief and to-the-point. No unnecessary pleasantries — just the facts and next steps."
            )

    system = (
        "You are Athena, a Tech Gadgets Inc. support agent with read-only tools: lookup_order, check_warranty, "
        "and escalate_to_human. Call a tool only when the customer supplies information the tool needs "
        "(such as an order ID). Never invent an order ID or policy detail. If no order ID is given, ask for "
        "one instead of calling a tool. Ground policy answers only in the context below; if it does not "
        "answer the question, say so explicitly.\n\nPolicy context:\n" + (context or "(no relevant policy passage retrieved)")
        + tone_instruction
    )
    messages: list = [("system", system), ("human", message)]
    trace = []
    try:
        for _ in range(settings.max_tool_iterations):
            response = model.invoke(messages)
            if not response.tool_calls:
                return {"status": "resolved", "trace": trace, "answer": response.content}
            messages.append(response)
            for call in response.tool_calls:
                from langchain_core.messages import ToolMessage

                tool_fn = by_name.get(call["name"])
                result = tool_fn.invoke(call["args"]) if tool_fn else {"status": "tool_not_allowed"}
                trace.append({"tool": call["name"], "args": call["args"], "result": result})
                messages.append(ToolMessage(content=str(result), tool_call_id=call["id"]))
        return {"status": "loop_guard_triggered", "trace": trace, "answer": "Reached the maximum tool-call iterations; escalating to a human agent."}
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "trace": trace, "answer": "Tool execution failed.", "error": str(exc)}
