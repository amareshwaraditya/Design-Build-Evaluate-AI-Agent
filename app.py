import streamlit as st
from pathlib import Path
from src.athena import ATHENA_NAME, COMPANY_NAME, PRODUCT_NAME, PERSONA, PHASES

st.set_page_config(page_title=PRODUCT_NAME, page_icon="🤖", layout="wide")
ROOT = Path(__file__).parent
PAGE_DIR = ROOT / "pages"
LOGO_PATH = ROOT / "assets" / "techgadgets-logo.png"
page_files = [
    ("1_problem_framing.py", "Phase 1 · Athena Understands the Customer Need"),
    ("2_baseline.py", "Phase 2 · Athena’s Basic Support"),
    ("3_llm_integration.py", "Phase 3 · Athena Gains LLM Reasoning"),
    ("4_rag.py", "Phase 4 · Athena Uses Company Knowledge"),
    ("5_mcp_tools.py", "Phase 5 · Athena Uses Support Tools"),
    ("6_planning_memory.py", "Phase 6 · Athena Uses Conversation Context"),
    ("7_adaptation.py", "Phase 7 · Athena Learns from Feedback"),
    ("8_deployment_monitoring.py", "Phase 8 · Athena Runs as a Service"),
    ("9_evaluation_governance.py", "Phase 9 · Athena’s Production Review"),
]
pages = [st.Page(str(PAGE_DIR / filename), title=title) for filename, title in page_files]

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

st.title(f"{ATHENA_NAME} — {COMPANY_NAME}")
st.subheader("Smart Customer Service Agent")
st.write(PERSONA)
st.markdown("### Welcome to Tech Gadgets Inc. customer service")
st.write("I can help customers with returns, refunds, delivery, warranties, product issues, and account concerns. My capabilities improve phase by phase because each new architecture addresses a limitation discovered in the previous one.")
st.table({"Phase": list(range(1, 10)), "What Athena gains": PHASES})
nav = st.navigation({f"{COMPANY_NAME} · {ATHENA_NAME}": pages})
nav.run()
