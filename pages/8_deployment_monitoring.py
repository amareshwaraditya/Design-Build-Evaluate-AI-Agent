import os
import streamlit as st
from src.config import settings
from src.observability import traced_run
from src.planning import run_agent_turn

st.title("Phase 8 — Athena Runs as a Monitored Service")
st.write("This page exercises the same request path used by the deployed customer-facing service, with latency capture, PII-safe logging, and graceful degradation.")

st.json({
    "mode": settings.mode,
    "model": settings.model,
    "openai_configured": settings.has_api_key,
    "langsmith_tracing_configured": bool(os.getenv("LANGCHAIN_API_KEY")),
    "langsmith_project": settings.langsmith_project,
})

message = st.text_area("Customer message", "Where is my order ORD-10001? My email is sarah.chen@example.com")
if st.button("Send monitored request"):
    run = traced_run(run_agent_turn, message)
    st.json(run)
    st.metric("Observed latency (ms)", run["latency_ms"])
    if run["error"]:
        st.warning(f"Live call degraded gracefully and fell back to deterministic support logic: {run['error']}")
    st.caption(f"Sanitized log line actually written to storage: `{run['logged_message']}`")

st.markdown("### Deployment assumptions & limitations")
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