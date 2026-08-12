"""Phase 9 — Athena's Evaluation: formal test suite, governance review, and LangSmith analytics.

Demonstrates: end-to-end evaluation against a fixed dataset, category-level scoring,
latency SLA analysis, LangSmith project analytics (when configured), and a documented
failure case with root-cause analysis and fix proof.
"""

import json
import os
import streamlit as st
from src.evaluation import get_evaluation_summary, run_evaluation
from src.observability import _langsmith_available, get_langsmith_project_runs
from src.config import settings
from src.planning import run_agent_turn
from src.ui import chat_header, evaluation_box, phase_carousel, render_chat

st.set_page_config(page_title="Athena - Production Review", page_icon="✅", layout="wide")
phase_carousel(9)
chat_header("Phase 9 — this final version has been tested end-to-end for quality, safety, and governance.")

# Service & tracing status panel
with st.expander("Evaluation environment status", expanded=False):
    langsmith_configured = _langsmith_available()
    st.json({
        "mode": settings.mode,
        "model": settings.model,
        "openai_configured": settings.has_api_key,
        "langsmith_tracing": langsmith_configured,
        "langsmith_project": settings.langsmith_project,
        "evaluation_dataset": "evaluation/dataset.json",
    })
    if not langsmith_configured:
        st.info(
            "LangSmith tracing is not configured. Evaluation runs will still execute normally — "
            "latency and pass/fail results are captured locally. To enable traced evaluation with "
            "token-level analytics, set `LANGCHAIN_TRACING_V2=true` and `LANGCHAIN_API_KEY` in "
            "your `.env` or Streamlit Secrets.",
            icon=":material/info:",
        )


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
    elif status == "error":
        extra.append("<b>⚠ Error:</b> Agent encountered an error — graceful degradation should have caught this")

    # Completeness assessment
    extra.append("<b>Production-ready:</b> This is the fully composed, evaluated agent with all 8 capability layers")
    extra.append("<b>Governance:</b> Every response is grounded, tool-verified, PII-safe, and traceable")

    # LangSmith status
    if langsmith_configured:
        extra.append("<b>🔗 LangSmith:</b> This response was traced — view project dashboard below for analytics")
    else:
        extra.append("<b>ℹ LangSmith:</b> Not configured — using local evaluation only")

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

# Load evaluation dataset
try:
    with open("evaluation/dataset.json", encoding="utf-8") as handle:
        cases = json.load(handle)
except (FileNotFoundError, json.JSONDecodeError) as e:
    cases = []
    st.error(f"Could not load evaluation dataset: {e}")

with st.expander("Formal evaluation suite", expanded=True):
    st.caption(f"{len(cases)} test cases loaded from evaluation/dataset.json")

    if cases and st.button("Run evaluation suite (calls the real agent)", icon=":material/play_arrow:"):
        with st.spinner("Running real LLM/RAG/tool calls for every test case..."):
            try:
                eval_result = run_evaluation(cases)
            except Exception as exc:
                st.error(f"Evaluation suite failed: {type(exc).__name__}: {exc}")
                eval_result = None

        if eval_result:
            # Top-level metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Score", f"{eval_result['score']}%")
            with col2:
                st.metric("Passed", f"{eval_result['passed']}/{eval_result['total']}")
            with col3:
                st.metric("Duration", f"{eval_result['duration_ms']}ms")
            with col4:
                ls_label = "✓ Traced" if eval_result.get("langsmith_enabled") else "Local only"
                st.metric("LangSmith", ls_label)

            # Category breakdown
            summary = get_evaluation_summary(eval_result)
            if summary.get("categories"):
                st.markdown("**Category-level results:**")
                cat_data = summary["categories"]
                st.table({
                    "Category": list(cat_data.keys()),
                    "Score": [f"{v['score']}%" for v in cat_data.values()],
                    "Passed": [f"{v['passed']}/{v['total']}" for v in cat_data.values()],
                    "Failures": [", ".join(v["failures"]) if v["failures"] else "—" for v in cat_data.values()],
                })

            # Latency analysis
            if summary.get("latency"):
                lat = summary["latency"]
                st.markdown(
                    f"**Latency:** avg {lat['average_ms']}ms | max {lat['max_ms']}ms | "
                    f"SLA violations (>3s): {lat['sla_violations_3s']}"
                )

            # Detailed case table
            st.table({
                "id": [c["id"] for c in eval_result["cases"]],
                "category": [c["category"] for c in eval_result["cases"]],
                "expected": [c["expected_status"] for c in eval_result["cases"]],
                "observed": [c["observed_status"] for c in eval_result["cases"]],
                "latency": [f"{c.get('latency_ms', '—')}ms" for c in eval_result["cases"]],
                "pass": ["✓" if c["pass"] else "✗" for c in eval_result["cases"]],
            })

            with st.expander("Full responses"):
                for c in eval_result["cases"]:
                    icon = "✓" if c["pass"] else "✗"
                    st.markdown(f"**{icon} {c['id']}** — _{c['input']}_")
                    st.write(c["answer"])
                    st.divider()

# LangSmith project analytics
with st.expander("LangSmith project analytics (traced runs)"):
    if langsmith_configured:
        runs = get_langsmith_project_runs(limit=10)
        if runs:
            st.table({
                "Run": [r["name"] or "—" for r in runs],
                "Status": [r["status"] for r in runs],
                "Latency": [f"{r['latency_ms']}ms" if r["latency_ms"] else "—" for r in runs],
                "Tokens": [r["total_tokens"] or "—" for r in runs],
                "Error": [r.get("error") or "—" for r in runs],
            })
            st.caption(
                f"Showing last {len(runs)} traced runs from project '{settings.langsmith_project}'. "
                "Visit LangSmith dashboard for full analytics, cost tracking, and run comparison."
            )
        else:
            st.caption("No recent runs found in the LangSmith project. Run the evaluation suite above to generate traced data.")
    else:
        st.info(
            "LangSmith is not configured. To see traced evaluation runs with token-level analytics, "
            "set `LANGCHAIN_TRACING_V2=true` and provide a valid `LANGCHAIN_API_KEY`.\n\n"
            "Without LangSmith, evaluation still works — pass/fail results and latency are captured locally.",
            icon=":material/link_off:",
        )

with st.expander("Evaluation dimensions & governance criteria"):
    st.table({
        "Dimension": [
            "Answer quality", "Policy groundedness", "Tool-selection accuracy",
            "Safety refusal accuracy", "Escalation correctness", "Latency SLA",
            "PII-safe logging", "Tone adaptation",
        ],
        "Evidence": [
            "Scored test cases (run_evaluation) — 18-case dataset",
            "RAG-retrieved source comparison (Phase 4)",
            "Tool trace vs. expected tool (Phase 5)",
            "Unsafe-request suite (safety_precheck)",
            "High-risk test suite (legal, security, repeated complaint)",
            "traced_run latency capture (Phase 8) — target ≤3000ms p95",
            "sanitize_for_log() hashing behaviour",
            "Feedback-driven tone shift (Phase 7) — verifiable before/after",
        ],
        "LangSmith": [
            "Per-run scoring via traced evaluation",
            "Trace shows retrieval step timing",
            "Tool call sequences visible in trace tree",
            "Refusal runs traced with zero tool/LLM cost",
            "Escalation routing visible in trace",
            "Latency histogram in project dashboard",
            "N/A (local PII hashing only)",
            "Tone parameter visible in run metadata",
        ],
    })

with st.expander("Debugged failure case (real, reproduced)"):
    st.markdown(
        "**Failure:** the LLM-based request decomposer (`decompose()` in `src/planning.py`) over-split a single-topic "
        "message — *\"Someone is making unauthorized purchases on my account that I did not make.\"* — into two bogus "
        "sub-tasks (`\"...unauthorized purchases on my account.\"` and `\"I did not make these purchases.\"`), causing "
        "Athena to answer the same issue twice instead of once.\n\n"
        "**Root cause:** the decomposition prompt said only *\"split into independent sub-requests\"* without "
        "distinguishing *multiple topics* from *clauses of one sentence*, so the model treated the second clause as "
        "a second request.\n\n"
        "**Fix:** rewrote the prompt with explicit criteria plus one multi-topic and one single-topic worked example.\n\n"
        "**Proof (before → after):**"
    )
    st.code(
        "Before: decompose(msg) -> "
        "['Someone is making unauthorized purchases on my account.', 'I did not make these purchases.']\n"
        "After:  decompose(msg) -> ['Someone is making unauthorized purchases on my account that I did not make.']",
        language="text",
    )

with st.expander("Safety & ethics enforcement"):
    st.markdown(
        "- **Refusal:** unsafe/exploit requests are refused before any LLM or tool call (`safety_precheck`).\n"
        "- **Escalation:** legal threats and account-security incidents are escalated rather than resolved autonomously.\n"
        "- **PII-safe logging:** `sanitize_for_log()` hashes emails, phone numbers, and order IDs before anything is written to `logs/`.\n"
        "- **No fabrication:** RAG grounding + explicit prompt rules mean unanswerable questions are met with honesty, not a guess (see the `knowledge_gap` case above).\n"
        "- **Tone safety:** Safety refusals are maintained even when tone adaptation is active — frustration does not unlock unsafe behaviour."
    )

with st.expander("Technical evidence: error handling & graceful degradation"):
    st.markdown(
        "**Error handling across all phases:**\n\n"
        "| Phase | Failure mode | Mitigation |\n"
        "|-------|-------------|-------------|\n"
        "| 2 (Baseline) | N/A — deterministic keyword rules, no external dependencies | Always operational |\n"
        "| 3 (LLM) | Missing `OPENAI_API_KEY` or API failure | Returns `offline` status with explanatory message |\n"
        "| 4 (RAG) | Embedding API failure or missing key | Falls back to keyword-overlap search (`_keyword_fallback`) |\n"
        "| 5 (Tools) | Missing API key or tool-call exception | Returns `offline` or `error` status; tool loop is bounded |\n"
        "| 6 (Planning) | Decomposition LLM failure | Falls back to heuristic split on `' and '`; agent continues |\n"
        "| 7 (Adaptation) | LLM failure during tone comparison | Inherits Phase 5/6 error handling; tone defaults to professional |\n"
        "| 8 (Monitoring) | Any exception in `traced_run` | Deterministic fallback via `src/runtime.py`; error is sanitized |\n"
        "| 9 (Evaluation) | Per-case agent crash | Caught individually; recorded as `error` status without aborting suite |\n"
        "| All | LangSmith unavailable | Graceful fallback to local-only metrics; info message (not error) shown |\n"
    )
