# Customer Support AI Resolution Agent

Scenario 3 — Customer Support Resolution Agent. This repository presents the agent as an engineering evolution: problem framing, Python baseline, LLM integration, RAG, MCP tools, planning and memory, adaptive behaviour, deployment monitoring, and LangSmith evaluation.

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

The application starts in deterministic evidence mode. Configure secrets only when live LLM, MCP, or LangSmith demonstrations are required.

## Repository design

- `src/` contains reusable agent components.
- `streamlit_app/pages/` contains the evaluator-facing nine-page walkthrough.
- `docs/` contains problem framing, demo flow, and evaluation design.
- `knowledge_base/` contains support policies used by retrieval.
- `evaluation/` contains the repeatable evaluation dataset.

## Deployment

Deploy `app.py` from this GitHub repository using Streamlit Community Cloud. Add secrets through the deployment settings, not source control:

```toml
OPENAI_API_KEY = "..."
LANGCHAIN_API_KEY = "..."
LANGCHAIN_TRACING_V2 = "true"
LANGCHAIN_PROJECT = "customer-support-resolution-agent"
```

The deployed application remains usable in evidence mode if live credentials are unavailable.

## Safety scope

The agent provides support information and decision support only. It refuses unsafe requests, does not fabricate policies or customer data, escalates sensitive or unresolved issues, and sanitizes logs before persistence. State-changing support actions require confirmation or remain disabled in demonstration mode.
