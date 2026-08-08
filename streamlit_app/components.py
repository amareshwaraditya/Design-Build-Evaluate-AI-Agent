import streamlit as st

def phase_header(number: int, title: str, points: int):
    st.title(f"Phase {number} — {title}")
    st.caption(f"Rubric allocation: {points} points")

def evidence_note(text: str):
    st.info(f"Evidence focus: {text}")
