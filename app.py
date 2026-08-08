import streamlit as st
from pathlib import Path

st.set_page_config(page_title="Customer Support AI Resolution Agent", page_icon="🛠️", layout="wide")

ROOT = Path(__file__).parent
PAGE_DIR = ROOT / "streamlit_app" / "pages"

pages = [
    st.Page(str(PAGE_DIR / "1_problem_framing.py"), title="Phase 1 · Problem Framing", icon="🧭"),
    st.Page(str(PAGE_DIR / "2_baseline.py"), title="Phase 2 · Python Baseline", icon="🐍"),
    st.Page(str(PAGE_DIR / "3_llm_integration.py"), title="Phase 3 · LLM Integration", icon="🧠"),
    st.Page(str(PAGE_DIR / "4_rag.py"), title="Phase 4 · RAG Retrieval", icon="📚"),
    st.Page(str(PAGE_DIR / "5_mcp_tools.py"), title="Phase 5 · MCP Tools", icon="🔧"),
    st.Page(str(PAGE_DIR / "6_planning_memory.py"), title="Phase 6 · Planning & Memory", icon="🗂️"),
    st.Page(str(PAGE_DIR / "7_adaptation.py"), title="Phase 7 · Feedback Adaptation", icon="🔁"),
    st.Page(str(PAGE_DIR / "8_deployment_monitoring.py"), title="Phase 8 · Deployment & Monitoring", icon="🚀"),
    st.Page(str(PAGE_DIR / "9_evaluation_governance.py"), title="Phase 9 · Evaluation & Governance", icon="📊"),
]

st.title("Customer Support AI Resolution Agent")
st.subheader("Scenario 3 · Engineering evolution walkthrough")
st.write("Use the sidebar to inspect how the agent evolves from a simple baseline into a grounded, tool-using, observable, and evaluated system.")
st.info("Evidence mode is enabled by default. Live model, MCP, and LangSmith features activate when deployment secrets are configured.")
st.markdown("### Phase sequence")
st.table({"Phase": list(range(1, 10)), "Capability": ["Problem framing", "Python baseline", "LLM and prompts", "RAG", "MCP tools", "Planning and memory", "Feedback adaptation", "Deployment and monitoring", "Evaluation and governance"], "Rubric points": [10, 5, 15, 10, 15, 15, 5, 10, 15]})
st.caption("Scenario safety rule: support assistance is allowed; unsafe, policy-violating, sensitive, or unresolved cases are refused or escalated.")

pg = st.navigation({"Capstone walkthrough": pages})
pg.run()
