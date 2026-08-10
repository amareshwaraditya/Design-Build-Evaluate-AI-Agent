"""Shared UI chrome: the phase carousel navigation and Athena's chat header/renderer.

Used by every page under pages/ so the customer-facing experience (branded header +
an immediately usable chat) and the phase-to-phase navigation are consistent everywhere.
"""
import streamlit as st

# (phase number, short label for the carousel, page path as registered in app.py's st.Page list)
PHASES = [
    (1, "Problem framing", "pages/1_problem_framing.py"),
    (2, "Basic support", "pages/2_baseline.py"),
    (3, "LLM reasoning", "pages/3_llm_integration.py"),
    (4, "Company knowledge", "pages/4_rag.py"),
    (5, "Support tools", "pages/5_mcp_tools.py"),
    (6, "Conversation context", "pages/6_planning_memory.py"),
    (7, "Feedback learning", "pages/7_adaptation.py"),
    (8, "Monitored service", "pages/8_deployment_monitoring.py"),
    (9, "Production review", "pages/9_evaluation_governance.py"),
]


def phase_carousel(current: int) -> None:
    """A left/right carousel for moving between phases, plus a quick numeric jump strip."""
    index = current - 1
    prev_item = PHASES[index - 1] if index > 0 else None
    next_item = PHASES[index + 1] if index < len(PHASES) - 1 else None

    left, mid, right = st.columns([1, 5, 1], vertical_alignment="center")
    with left:
        if st.button(
            "Previous", icon=":material/chevron_left:", width="stretch",
            disabled=prev_item is None, key=f"phase_prev_{current}",
            help=f"Phase {prev_item[0]} · {prev_item[1]}" if prev_item else None,
        ):
            st.switch_page(prev_item[2])
    with mid:
        labels = [str(number) for number, _, _ in PHASES]
        selected = st.segmented_control(
            "Jump to phase", labels, default=str(current),
            key=f"phase_jump_{current}", label_visibility="collapsed",
        )
        if selected and selected != str(current):
            st.switch_page(PHASES[int(selected) - 1][2])
    with right:
        if st.button(
            "Next", icon=":material/chevron_right:", width="stretch",
            disabled=next_item is None, key=f"phase_next_{current}",
            help=f"Phase {next_item[0]} · {next_item[1]}" if next_item else None,
        ):
            st.switch_page(next_item[2])
    st.caption(f"Phase {current} of {len(PHASES)} · {PHASES[index][1]}")
    st.divider()


def chat_header(phase_note: str) -> None:
    """The consistent, customer-facing welcome shown at the top of every chat phase."""
    st.title("Tech Gadgets Inc. – Smart Customer Service")
    st.write(
        "Hi! I am Athena, AI support assistant for Tech Gadgets Inc. "
        "How can I help you with your account or order today?"
    )
    st.caption(phase_note)


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
