import streamlit as st
from pathlib import Path

st.set_page_config(page_title="Customer Support AI Resolution Agent", page_icon="🛠️", layout="wide")
ROOT = Path(__file__).parent
PAGE_DIR = ROOT / "pages"
page_files = [
    ("1_problem_framing.py", "Phase 1 · Customer Need"),
    ("2_baseline.py", "Phase 2 · Baseline Assistant"),
    ("3_llm_integration.py", "Phase 3 · LLM Assistant"),
    ("4_rag.py", "Phase 4 · Policy-Grounded Assistant"),
    ("5_mcp_tools.py", "Phase 5 · Support Tools"),
    ("6_planning_memory.py", "Phase 6 · Conversation Context"),
    ("7_adaptation.py", "Phase 7 · Feedback Adaptation"),
    ("8_deployment_monitoring.py", "Phase 8 · Live Service"),
    ("9_evaluation_governance.py", "Phase 9 · Quality & Safety"),
]
pages = [st.Page(str(PAGE_DIR / filename), title=title) for filename, title in page_files]
st.title("Customer Support AI Resolution Agent")
st.subheader("TechGadgets customer service")
st.write("Use the sidebar to experience the agent as it evolves from a simple assistant into a grounded, tool-using, monitored service.")
st.info("The demo runs with safe local data by default. Add live credentials to .env for model and tracing integrations.")
st.markdown("### Customer entry point")
st.write("A customer can ask about a return, refund, delivery, warranty, product issue, or account concern. The agent answers from approved information, verifies order details when needed, and escalates cases it cannot safely resolve.")
nav = st.navigation({"Customer-support workflow": pages})
nav.run()
