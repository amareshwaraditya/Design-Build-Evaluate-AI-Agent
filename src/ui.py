"""Shared UI chrome: the phase carousel navigation and Athena's chat header/renderer.

Used by every page under pages/ so the customer-facing experience (branded header +
an immediately usable chat) and the phase-to-phase navigation are consistent everywhere.
"""
import streamlit as st

# (phase number, carousel title, page path as registered in app.py's st.Page list)
PHASES = [
    (1, "Phase 1 — Understanding Tech Gadgets Inc.'s Support Problem", "pages/1_problem_framing.py"),
    (2, "Phase 2 — Athena's Basic Support", "pages/2_baseline.py"),
    (3, "Phase 3 — Athena Gains LLM Reasoning", "pages/3_llm_integration.py"),
    (4, "Phase 4 — Athena Uses Company Knowledge", "pages/4_rag.py"),
    (5, "Phase 5 — Athena Uses Support Tools", "pages/5_mcp_tools.py"),
    (6, "Phase 6 — Athena Uses Conversation Context", "pages/6_planning_memory.py"),
    (7, "Phase 7 — Athena Learns from Feedback", "pages/7_adaptation.py"),
    (8, "Phase 8 — Athena Runs as a Service", "pages/8_deployment_monitoring.py"),
    (9, "Phase 9 — Athena's Production Review", "pages/9_evaluation_governance.py"),
]


def phase_carousel(current: int) -> None:
    """A labelled, one-phase-at-a-time carousel with Previous/Next controls."""
    st.markdown(
        """<style>
        section[data-testid="stSidebar"],
        [data-testid="stSidebar"],
        [data-testid="stSidebar"] > div {
            background-color: #007cc3 !important;
        }
        section[data-testid="stSidebar"] *,
        [data-testid="stSidebar"] * {
            color: white !important;
        }
        section[data-testid="stSidebar"] img,
        [data-testid="stSidebar"] img {
            background-color: white;
            border-radius: 0.25rem;
            padding: 4px;
        }
        </style>""",
        unsafe_allow_html=True,
    )
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
            f'<div style="background-color:#007cc3; border-radius:0.5rem; padding:0.45rem 1rem; text-align:center; color:white; line-height:1.6; height:38px; display:flex; align-items:center; justify-content:center;"><strong>{PHASES[index][1]}</strong></div>',
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
    """The consistent, customer-facing welcome shown at the top of every chat phase."""
    st.markdown(
        """<style>
        /* Carousel title bar */
        .carousel-title {
            background-color: #007cc3;
            border-radius: 0.5rem;
            padding: 0.6rem 1rem;
            text-align: center;
            margin: 0;
            color: white;
        }
        .carousel-title strong {
            color: white;
        }
        .carousel-title p {
            margin: 0;
            text-align: center;
            color: white;
        }
        /* Reduce gap between carousel and main title */
        [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"]:first-child {
            margin-bottom: -1rem;
        }
        /* Assistant avatar */
        [data-testid="stChatMessageAvatarAssistant"],
        [data-testid="stChatMessageAvatarCustom"] {
            background-color: #16a34a !important;
        }
        /* Chat input red border + button */
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
    """Render a consistent colored evaluation metadata box below a chat response."""
    status = result.get("status", "resolved")
    color = {"resolved": "green", "refused": "red", "escalated": "orange", "error": "red", "degraded": "orange", "offline": "gray"}.get(status, "gray")
    latency = result.get("latency_ms", "—")
    variant = result.get("prompt_version", "—")
    lines_html = f"<b>Prompt variant:</b> {variant} &nbsp;|&nbsp; <b>Status:</b> {status} &nbsp;|&nbsp; <b>Latency:</b> {latency} ms"
    if extra_lines:
        lines_html += "<br>" + "<br>".join(extra_lines)
    st.markdown(
        f"""<div style="background-color: #f0f2f6; border-left: 4px solid {color}; padding: 0.75rem 1rem; margin-top: 0.5rem; border-radius: 0.25rem; font-size: 0.85rem;">
        <strong>Evaluation metadata</strong><br>
        {lines_html}
        </div>""",
        unsafe_allow_html=True,
    )


def render_chat(session_key: str, reply_fn, evidence_fn=None, placeholder=None, suggestions=None) -> None:
    """A consistent chat loop: history, optional starter suggestions, input, and a spinner.

    reply_fn(user_text) -> dict with at least an "answer" key (and anything evidence_fn needs).
    evidence_fn(reply_dict) -> renders supporting technical evidence under the assistant's reply.
    """
    if session_key not in st.session_state:
        st.session_state[session_key] = []
    history = st.session_state[session_key]

    for turn in history:
        with st.chat_message("user"):
            st.write(turn["user"])
        with st.chat_message("assistant", avatar=":material/support_agent:"):
            st.write(turn["answer"])
            if evidence_fn and turn.get("evidence") is not None:
                evidence_fn(turn["evidence"])

    prompt = None
    if suggestions and not history:
        choice = st.pills(
            "Try asking", list(suggestions.keys()),
            label_visibility="collapsed", key=f"{session_key}_suggestions",
        )
        if choice:
            prompt = suggestions[choice]

    typed = st.chat_input(placeholder or "Ask Athena about an order, return, warranty, or account issue")
    prompt = typed or prompt

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
