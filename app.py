"""Athena — Tech Gadgets Inc. Smart Customer Service Agent.

Entry point for the Streamlit multi-page application.
Configures page layout, sidebar navigation, logo, and global CSS styles.
"""

import streamlit as st
from pathlib import Path
from src.athena import PRODUCT_NAME

# --- Page config (must be first Streamlit call) ---
st.set_page_config(page_title=PRODUCT_NAME, page_icon="🤖", layout="wide")

ROOT = Path(__file__).parent
LOGO_PATH = ROOT / "assets" / "techgadgets-logo.png"

# --- Navigation pages: (file_path, sidebar_title) ---
page_files = [
    ("pages/1_problem_framing.py", "Phase 1 - Athena's Purpose"),
    ("pages/2_baseline.py", "Phase 2 - Athena's Basic Support"),
    ("pages/3_llm_integration.py", "Phase 3 - Athena Gains Reasoning"),
    ("pages/4_rag.py", "Phase 4 - Athena Knows Policy"),
    ("pages/5_mcp_tools.py", "Phase 5 - Athena Uses Tools"),
    ("pages/6_planning_memory.py", "Phase 6 - Athena Uses Context"),
    ("pages/7_adaptation.py", "Phase 7 - Athena Is Adaptive"),
    ("pages/8_deployment_monitoring.py", "Phase 8 - Athena's Deployment"),
    ("pages/9_evaluation_governance.py", "Phase 9 - Athena's Evaluation"),
]
pages = [st.Page(path, title=title) for path, title in page_files]

# --- Global CSS styles ---
st.markdown(
    """
    <style>
        /* Reduce top padding so carousel appears near the top */
        .stMainBlockContainer,
        [data-testid="stAppViewBlockContainer"] {
            padding-top: 3rem !important;
        }

        /* Carousel Previous/Next buttons: match title bar height (42px) */
        [data-testid="stAppViewBlockContainer"] button[kind="secondary"] {
            height: 42px !important;
            font-size: 1.05rem !important;
        }

        /* Sidebar nav links */
        section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a {
            font-size: 1.2rem;
            line-height: 1.4;
            padding: 0.4rem 0.75rem;
            border-radius: 0.5rem;
            margin: 0.1rem 0.25rem;
            color: #1f1f1f !important;
            transition: background-color 0.2s ease;
        }

        /* Active page: blue pill highlight (#007cc3) */
        section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-current="page"],
        section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-selected="true"] {
            background-color: #007cc3 !important;
            color: white !important;
            font-weight: 600 !important;
        }
        section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-current="page"] span,
        section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-selected="true"] span {
            color: white !important;
        }

        /* Hover on non-active links: light blue tint */
        section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a:hover:not([aria-current="page"]) {
            background-color: rgba(0, 124, 195, 0.08) !important;
        }

        /* Hide sidebar collapse arrow and group header */
        [data-testid="stSidebarCollapseButton"],
        button[kind="headerNoPadding"] {
            display: none !important;
        }
        [data-testid="stSidebarNav"] h2,
        [data-testid="stSidebarNavSeparator"] {
            display: none !important;
        }

        /* Sidebar logo: centered with 3D perspective effect */
        section[data-testid="stSidebar"] [data-testid="stImage"] {
            display: flex;
            justify-content: center;
            padding: 1rem 1rem 0.75rem 1rem;
        }
        section[data-testid="stSidebar"] [data-testid="stImage"] img {
            width: 180px !important;
            border-radius: 0.5rem;
            transform: perspective(800px) rotateY(-3deg) rotateX(2deg);
            box-shadow:
                4px 4px 8px rgba(0, 0, 0, 0.25),
                8px 8px 16px rgba(0, 0, 0, 0.12);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        section[data-testid="stSidebar"] [data-testid="stImage"] img:hover {
            transform: perspective(800px) rotateY(0deg) rotateX(0deg) scale(1.02);
            box-shadow:
                2px 2px 4px rgba(0, 0, 0, 0.15),
                6px 6px 12px rgba(0, 0, 0, 0.08);
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Sidebar logo (placed below nav links, above fold) ---
st.sidebar.image(str(LOGO_PATH), use_container_width=False, width=180)

# --- Run the selected page ---
nav = st.navigation({"": pages})
nav.run()
