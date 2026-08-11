import os
import streamlit as st
from src.config import settings
from src.observability import traced_run
from src.planning import run_agent_turn
from src.ui import chat_header, evaluation_box, phase_carousel, render_chat

st.set_page_config(page_title="Athena - Monitored Service", page_icon="📡", layout="wide")
phase_carousel(8)
chat_header("Phase 8 — this is the same monitored request path used by the deployed service.")

with st.expander("Service status", expanded=False):
    st.json({
        "mode": settings.mode,
        "model": settings.model,
        "openai_configured": settings.has_api_key,
        "langsmith_tracing_configured": bool(os.getenv("LANGCHAIN_API_KEY")),
        "langsmith_project": settings.langsmith_project,
    })


def _reply(message: str) -> dict:
    run = traced_run(run_agent_turn, message)
    inner = run["result"]
    answer = inner.get("answer") if isinstance(inner, dict) else str(inner)
    return {"answer": answer, "latency_ms": run["latency_ms"], "logged_message": run["logged_message"], "error": run["error"]}


def _evidence(result: dict) -> None:
    extra = [f"<b>Sanitized log:</b> <code>{result['logged_message']}</code>"]
    if result.get("error"):
        extra.append(f"<b>Degraded:</b> fell back to deterministic logic — {result['error']}")
    evaluation_box(result, extra_lines=extra)


render_chat(
    session_key="phase8_chat",
    reply_fn=_reply,
    evidence_fn=_evidence,
    placeholder="Send a monitored request, e.g. 'Where is my order ORD-10001?'",
    suggestions={"📦 Order status": "Where is my order ORD-10001? My email is sarah.chen@example.com"},
)

with st.expander("Technical evidence: deployment assumptions & limitations"):
    st.markdown(
        "- Streamlit Community Cloud runs `app.py` from the GitHub repository; secrets (`OPENAI_API_KEY`, "
        "`LANGCHAIN_API_KEY`, etc.) are configured as Streamlit Cloud **Secrets**, never committed to the repo.\n"
        "- `src/config.py` merges `st.secrets` into the process environment so the same code path works locally "
        "(via `.env`) and in the cloud (via Secrets).\n"
        "- If the OpenAI call fails or the key is missing, `observability.traced_run` falls back to the "
        "deterministic `src/runtime.py` logic instead of surfacing a raw error to the customer.\n"
        "- LangSmith tracing is enabled via `LANGCHAIN_TRACING_V2=true`; in this environment trace ingestion to "
        "the configured regional endpoint currently returns HTTP 405 (an account/plan limitation), so local "
        "latency/error logging is the primary monitoring evidence.\n"
        "- Logs are sanitized before being written: emails, phone numbers, and order IDs are hashed, never stored raw."
    )
