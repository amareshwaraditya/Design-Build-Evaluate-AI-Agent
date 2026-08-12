"""Shared UI components for the Athena Streamlit application.

Provides:
- phase_carousel(): Previous/Title/Next navigation bar shown on every page.
- chat_header(): Branded welcome message and page-level CSS for chat styling.
- evaluation_box(): Colored metadata box displayed below each agent response.
- render_chat(): Reusable chat loop with history, suggestions, and evidence rendering.
"""

import streamlit as st

# Phase registry: (number, carousel_title, page_path)
# Keep titles short to avoid sidebar truncation.
PHASES = [
    (1, "Phase 1 - Athena's Purpose", "pages/1_problem_framing.py"),
    (2, "Phase 2 - Athena's Basic Support", "pages/2_baseline.py"),
    (3, "Phase 3 - Athena Gains Reasoning", "pages/3_llm_integration.py"),
    (4, "Phase 4 - Athena Knows Policy", "pages/4_rag.py"),
    (5, "Phase 5 - Athena Uses Tools", "pages/5_mcp_tools.py"),
    (6, "Phase 6 - Athena Uses Context", "pages/6_planning_memory.py"),
    (7, "Phase 7 - Athena Is Adaptive", "pages/7_adaptation.py"),
    (8, "Phase 8 - Athena's Deployment", "pages/8_deployment_monitoring.py"),
    (9, "Phase 9 - Athena's Evaluation", "pages/9_evaluation_governance.py"),
]


def phase_carousel(current: int) -> None:
    """Render the phase navigation bar: [Previous] [Title] [Next].

    Args:
        current: The 1-based phase number of the active page.
    """
    index = current - 1
    prev_item = PHASES[index - 1] if index > 0 else None
    next_item = PHASES[index + 1] if index < len(PHASES) - 1 else None

    left, mid, right = st.columns([1.2, 5, 1.2], vertical_alignment="center")
    with left:
        if st.button(
            "Previous", icon=":material/chevron_left:", width="stretch",
            disabled=prev_item is None, key=f"phase_prev_{current}",
            help=f"Phase {prev_item[0]} · {prev_item[1]}" if prev_item else None,
        ):
            st.switch_page(prev_item[2])
    with mid:
        st.markdown(
            f'<div style="background-color:#007cc3; border-radius:0.5rem; padding:0.45rem 1rem;'
            f' text-align:center; color:white; font-size:1.2rem; line-height:1.6;'
            f' height:42px; display:flex; align-items:center; justify-content:center;">'
            f'<strong>{PHASES[index][1]}</strong></div>',
            unsafe_allow_html=True,
        )
    with right:
        if st.button(
            "Next", icon=":material/chevron_right:", width="stretch",
            disabled=next_item is None, key=f"phase_next_{current}",
            help=f"Phase {next_item[0]} · {next_item[1]}" if next_item else None,
        ):
            st.switch_page(next_item[2])
    st.caption(f"Phase {current} of {len(PHASES)}")


def chat_header(phase_note: str) -> None:
    """Render the branded welcome header and inject chat-specific CSS.

    Args:
        phase_note: Short description shown below the title (e.g. phase capability summary).
    """
    st.markdown(
        """<style>
        /* Green assistant avatar */
        [data-testid="stChatMessageAvatarAssistant"],
        [data-testid="stChatMessageAvatarCustom"] {
            background-color: #16a34a !important;
        }
        /* Red-bordered chat input box */
        [data-testid="stChatInput"] {
            border: 2px solid #e53e3e !important;
            border-radius: 0.5rem;
        }
        [data-testid="stChatInputSubmitButton"] button,
        [data-testid="stChatInput"] button {
            background-color: #e53e3e !important;
            color: white !important;
            border-radius: 0.375rem;
        }
        </style>""",
        unsafe_allow_html=True,
    )
    st.title("Tech Gadgets Inc. – Smart Customer Service")
    st.write(
        "Hi! I am Athena, AI support assistant for Tech Gadgets Inc. "
        "How can I help you with your account or order today?"
    )
    st.caption(phase_note)


def evaluation_box(result: dict, extra_lines: list[str] | None = None) -> None:
    """Render a colored metadata box below a chat response for evaluators.

    The left border color reflects the response status:
    - green: resolved successfully
    - red: refused (safety) or error
    - orange: escalated or degraded
    - gray: offline

    Args:
        result: Dict with at least 'status'; optionally 'latency_ms' and 'prompt_version'.
        extra_lines: Additional HTML lines to display (e.g. tool traces, limitations).
    """
    status = result.get("status", "resolved")
    color_map = {
        "resolved": "green", "refused": "red", "escalated": "orange",
        "error": "red", "degraded": "orange", "offline": "gray",
    }
    color = color_map.get(status, "gray")
    latency = result.get("latency_ms", "—")
    variant = result.get("prompt_version", "—")

    lines_html = (
        f"<b>Prompt variant:</b> {variant} &nbsp;|&nbsp; "
        f"<b>Status:</b> {status} &nbsp;|&nbsp; "
        f"<b>Latency:</b> {latency} ms"
    )
    if extra_lines:
        lines_html += "<br>" + "<br>".join(extra_lines)

    st.markdown(
        f"""<div style="background-color: #f0f2f6; border-left: 4px solid {color};
        padding: 0.75rem 1rem; margin-top: 0.5rem; border-radius: 0.25rem; font-size: 0.85rem;">
        <strong>Evaluation metadata</strong><br>
        {lines_html}
        </div>""",
        unsafe_allow_html=True,
    )


def render_chat(session_key: str, reply_fn, evidence_fn=None, placeholder=None, suggestions=None) -> None:
    """Reusable chat interface with message history and optional suggestion pills.

    Args:
        session_key: Unique key for storing chat history in st.session_state.
        reply_fn: Callable(user_text) -> dict with at least an "answer" key.
        evidence_fn: Optional callable(result_dict) that renders evaluation evidence.
        placeholder: Custom placeholder text for the chat input box.
        suggestions: Dict of {pill_label: message_text} shown before first interaction.
    """
    if session_key not in st.session_state:
        st.session_state[session_key] = []
    history = st.session_state[session_key]

    # Render conversation history
    for turn in history:
        with st.chat_message("user"):
            st.write(turn["user"])
        with st.chat_message("assistant", avatar=":material/support_agent:"):
            st.write(turn["answer"])
            if evidence_fn and turn.get("evidence") is not None:
                evidence_fn(turn["evidence"])

    # Suggestion pills (shown only when chat is empty)
    prompt = None
    if suggestions and not history:
        choice = st.pills(
            "Try asking", list(suggestions.keys()),
            label_visibility="collapsed", key=f"{session_key}_suggestions",
        )
        if choice:
            prompt = suggestions[choice]

    # Chat input
    typed = st.chat_input(placeholder or "Ask Athena about an order, return, warranty, or account issue")
    prompt = typed or prompt

    # Process new message
    if prompt:
        with st.chat_message("user"):
            st.write(prompt)
        with st.chat_message("assistant", avatar=":material/support_agent:"):
            with st.spinner("Athena is looking into that..."):
                result = reply_fn(prompt)
            st.write(result["answer"])
            if evidence_fn:
                evidence_fn(result)
        history.append({"user": prompt, "answer": result["answer"], "evidence": result})
        st.rerun()
