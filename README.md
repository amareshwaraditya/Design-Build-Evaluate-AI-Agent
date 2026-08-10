# Athena — Tech Gadgets Inc. Smart Customer Service Agent

Athena is a smart, helpful, kind, and just personified AI chatbot working as a customer-service agent for Tech Gadgets Inc.

This repository demonstrates Athena's evolution from a basic rule-based chatbot into a
production-oriented customer-support architecture built on **LangChain + OpenAI (`gpt-4o-mini`) +
FAISS** (Track A). Each phase adds a real capability — not a simulation — because Athena's
previous architecture exposed a specific limitation.

## Athena's evolution

1. Athena understands the customer-support problem.
2. Athena provides basic rule/template support.
3. Athena gains real LLM reasoning via `ChatOpenAI` and versioned prompt design.
4. Athena retrieves Tech Gadgets Inc. policy using OpenAI embeddings + a FAISS vector store.
5. Athena uses controlled, read-only support tools via LangChain tool-calling.
6. Athena gains multi-intent planning and bounded conversation memory.
7. Athena adapts tone/verbosity from explicit customer feedback.
8. Athena runs as a monitored, gracefully-degrading service.
9. Athena is evaluated end-to-end for quality, safety, and governance.

## Running locally

1. `python -m venv .venv` and activate it, then `pip install -r requirements.txt`.
2. Copy `.env.example` to `.env` and fill in `OPENAI_API_KEY` (and optionally `LANGCHAIN_API_KEY`
   for LangSmith tracing). **Never commit the real `.env` file** — it is gitignored.
3. `streamlit run app.py`, then use the sidebar to walk through Phases 1-9.

Without an `OPENAI_API_KEY`, live LLM/RAG/tool pages fall back to the deterministic logic in
`src/runtime.py` instead of failing (see Phase 8 for the graceful-degradation demo).

## Deploying to Streamlit Community Cloud

1. Push this repository to GitHub (already the case here).
2. On [share.streamlit.io](https://share.streamlit.io), create a new app pointing at `app.py` on
   the `main` branch.
3. In the app's **Settings -> Secrets**, paste the same keys as `.env.example` (TOML format), e.g.
   `OPENAI_API_KEY = "sk-..."`. `src/config.py` merges `st.secrets` into the environment
   automatically, so no code changes are needed between local and cloud.

## Repository layout

- `app.py` / `pages/` — the Streamlit UI, one page per phase (loaded via `st.navigation`).
- `src/` — the real agent implementation: `safety.py` (deterministic pre-check), `llm_agent.py`
  (Phase 3 prompt variants), `rag.py` (Phase 4 FAISS retrieval), `mcp_tools.py` (Phase 5
  tool-calling), `planning.py` (Phase 6 decomposition + memory + the composed pipeline),
  `adaptation.py` (Phase 7 feedback), `observability.py` (Phase 8 tracing/fallback),
  `evaluation.py` (Phase 9 test harness). `runtime.py`/`policies.py` are the deterministic
  fallback path used when the LLM is unavailable.
- `knowledge_base/` — the markdown policy documents retrieved by Phase 4.
- `evaluation/dataset.json` — the fixed test suite used by Phase 9.
- `docs/` — the required submission artefacts: `phase1_problem_statement.md`,
  `prompt_comparison.md`, `evaluation_report.md`, `engineering_justification.md`,
  `demo_script.md`.

Athena can explain verified Tech Gadgets Inc. support information and recommend safe next steps. She does not fabricate policies or customer data, expose sensitive information, or execute uncontrolled state-changing actions.

