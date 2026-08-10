import streamlit as st
from pathlib import Path
from src.athena import PRODUCT_NAME

st.set_page_config(page_title=PRODUCT_NAME, page_icon="🤖", layout="wide")
ROOT = Path(__file__).parent
LOGO_PATH = ROOT / "assets" / "techgadgets-logo.png"
page_files = [
    ("pages/1_problem_framing.py", "Phase 1 · Athena Understands the Customer Need"),
    ("pages/2_baseline.py", "Phase 2 · Athena’s Basic Support"),
    ("pages/3_llm_integration.py", "Phase 3 · Athena Gains LLM Reasoning"),
    ("pages/4_rag.py", "Phase 4 · Athena Uses Company Knowledge"),
    ("pages/5_mcp_tools.py", "Phase 5 · Athena Uses Support Tools"),
    ("pages/6_planning_memory.py", "Phase 6 · Athena Uses Conversation Context"),
    ("pages/7_adaptation.py", "Phase 7 · Athena Learns from Feedback"),
    ("pages/8_deployment_monitoring.py", "Phase 8 · Athena Runs as a Service"),
    ("pages/9_evaluation_governance.py", "Phase 9 · Athena’s Production Review"),
]
pages = [st.Page(path, title=title) for path, title in page_files]

st.markdown(
    """
    <style>
        [data-testid="stLogo"],
        [data-testid="stLogo"] img,
        img.stLogo {
            width: min(260px, calc(100vw - 6rem)) !important;
            height: auto !important;
            max-width: calc(100vw - 6rem) !important;
            max-height: none !important;
        }

        section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a {
            font-size: 18px;
            line-height: 1.45;
            padding-top: 0.45rem;
            padding-bottom: 0.45rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)
st.logo(str(LOGO_PATH), size="large")

nav = st.navigation({"Tech Gadgets Inc. · Athena": pages})
nav.run()
