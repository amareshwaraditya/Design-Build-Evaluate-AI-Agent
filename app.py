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
    ("pages/1_problem_framing.py", "Phase 1: Understand the Problem & Define Success"),
    ("pages/2_baseline.py", "Phase 2: Build a Basic Working Agent"),
    ("pages/3_llm_integration.py", "Phase 3: Make the Agent Smarter"),
    ("pages/4_rag.py", "Phase 4: Add Knowledge & Retrieval"),
    ("pages/5_mcp_tools.py", "Phase 5: Enable Tool Usage"),
    ("pages/6_planning_memory.py", "Phase 6: Planning, Memory & Context"),
    ("pages/7_adaptation.py", "Phase 7: Adaptive Behaviour"),
    ("pages/8_deployment_monitoring.py", "Phase 8: Deployment Readiness"),
    ("pages/9_evaluation_governance.py", "Phase 9: Evaluation & Engineering Review"),
]
pages = [st.Page(path, title=title) for path, title in page_files]
judge_pages = [st.Page("pages/demo_data.py", title="Order & Scenarios", icon="🗂️")]

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

        /* Keep long technical prompts readable without horizontal scrolling. */
        [data-testid="stCode"],
        [data-testid="stCode"] pre,
        [data-testid="stCode"] code {
            max-width: 100% !important;
            white-space: pre-wrap !important;
            overflow-wrap: anywhere !important;
            word-break: break-word !important;
        }
        [data-testid="stCode"] {
            overflow-x: hidden !important;
        }

        /* Sidebar nav links */
        section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a {
            font-size: 1.05rem;
            line-height: 1.3;
            padding: 0.35rem 0.75rem;
            border-radius: 0.5rem;
            margin: 0.08rem 0.25rem;
            color: #1f1f1f !important;
            transition: background-color 0.2s ease;
            white-space: normal;
            overflow-wrap: anywhere;
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
nav = st.navigation({"Phases": pages, "Demo Reference Data": judge_pages})
nav.run()
