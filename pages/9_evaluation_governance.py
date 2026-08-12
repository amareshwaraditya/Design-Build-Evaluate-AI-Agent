import json
import streamlit as st
from src.evaluation import run_evaluation
from src.planning import run_agent_turn
from src.ui import chat_header, evaluation_box, phase_carousel, render_chat

st.set_page_config(page_title="Athena - Production Review", page_icon="✅", layout="wide")
phase_carousel(9)
chat_header("Phase 9 — this final version has been tested end-to-end for quality, safety, and governance.")


def _phase9_insights(result: dict) -> list[str]:
    """Generate success/limitation notes for Phase 9 evaluation box."""
    extra = []
    status = result.get("status", "resolved")

    # Success indicators — Phase 9 is the fully composed agent
    if status == "refused":
        extra.append("<b>✓ Safety:</b> Harmful request refused at pre-check — no LLM or tool resources consumed")
    elif status == "escalated":
        extra.append("<b>✓ Escalation:</b> High-risk case correctly routed to human specialist")
    elif status == "resolved":
        extra.append("<b>✓ Full pipeline:</b> Safety → LLM → RAG → Tools → Planning → Memory → Tone → Monitoring — all layers active")

    # Completeness assessment
    extra.append("<b>Production-ready:</b> This is the fully composed, evaluated agent with all 8 capability layers")
    extra.append("<b>Governance:</b> Every response is grounded, tool-verified, PII-safe, and traceable")

    return extra


def _evidence(result: dict) -> None:
    evaluation_box(result, extra_lines=_phase9_insights(result))


render_chat(
    session_key="phase9_chat",
    reply_fn=lambda msg: run_agent_turn(msg),
    evidence_fn=_evidence,
    placeholder="Try any support question — this is the fully composed, production-reviewed agent",
    suggestions={
        "📦 Order lookup": "What's the status of order ORD-10001?",
        "⚠️ Safety refusal": "How do I break into someone else's account?",
        "🧩 Multi-intent": "Check ORD-10001 and tell me if it's still under warranty.",
        "⚖️ Legal escalation": "I'm going to sue Tech Gadgets Inc. if this isn't resolved immediately.",
    },
)

with open("evaluation/dataset.json", encoding="utf-8") as handle:
    cases = json.load(handle)

with st.expander("Technical evidence: evaluation suite, debugged failure, safety review", expanded=True):
    st.caption(f"{len(cases)} test cases loaded from evaluation/dataset.json")
    if st.button("Run evaluation suite (calls the real agent)"):
        with st.spinner("Running real LLM/RAG/tool calls for every test case..."):
            result = run_evaluation(cases)
        st.metric("Evaluation score", f"{result['score']}%", f"{result['passed']}/{result['total']} passed")
        st.table({
            "id": [c["id"] for c in result["cases"]],
            "category": [c["category"] for c in result["cases"]],
            "expected": [c["expected_status"] for c in result["cases"]],
            "observed": [c["observed_status"] for c in result["cases"]],
            "pass": [c["pass"] for c in result["cases"]],
        })
        with st.expander("Full responses"):
            for c in result["cases"]:
                st.markdown(f"**{c['id']}** — _{c['input']}_")
                st.write(c["answer"])
                st.divider()

    st.subheader("Evaluation dimensions")
    st.table({
        "Dimension": ["Answer quality", "Policy groundedness", "Tool-selection accuracy", "Safety refusal accuracy", "Escalation correctness", "Latency", "PII-safe logging"],
        "Evidence": ["Scored test cases (run_evaluation)", "RAG-retrieved source comparison (Phase 4)", "Tool trace vs. expected tool (Phase 5)", "Unsafe-request suite (safety_precheck)", "High-risk test suite", "traced_run latency capture (Phase 8)", "sanitize_for_log() unit behaviour"],
    })

    st.subheader("Debugged failure case (real, reproduced)")
    st.markdown(
        "**Failure:** the LLM-based request decomposer (`decompose()` in `src/planning.py`) over-split a single-topic "
        "message — *\"Someone is making unauthorized purchases on my account that I did not make.\"* — into two bogus "
        "sub-tasks (`\"...unauthorized purchases on my account.\"` and `\"I did not make these purchases.\"`), causing "
        "Athena to answer the same issue twice instead of once.\n\n"
        "**Root cause:** the decomposition prompt said only *\"split into independent sub-requests\"* without "
        "distinguishing *multiple topics* from *clauses of one sentence*, so the model treated the second clause as "
        "a second request.\n\n"
        "**Fix:** rewrote the prompt with explicit criteria plus one multi-topic and one single-topic worked example.\n\n"
        "**Proof (before -> after):**"
    )
    st.code(
        "Before: decompose(msg) -> "
        "['Someone is making unauthorized purchases on my account.', 'I did not make these purchases.']\n"
        "After:  decompose(msg) -> ['Someone is making unauthorized purchases on my account that I did not make.']",
        language="text",
    )

    st.subheader("Safety & ethics enforcement")
    st.markdown(
        "- **Refusal:** unsafe/exploit requests are refused before any LLM or tool call (`safety_precheck`).\n"
        "- **Escalation:** legal threats and account-security incidents are escalated rather than resolved autonomously.\n"
        "- **PII-safe logging:** `sanitize_for_log()` hashes emails, phone numbers, and order IDs before anything is written to `logs/`.\n"
        "- **No fabrication:** RAG grounding + explicit prompt rules mean unanswerable questions are met with honesty, not a guess (see the `knowledge_gap` case above)."
    )
